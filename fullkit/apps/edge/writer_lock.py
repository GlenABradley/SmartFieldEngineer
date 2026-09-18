"""Handle-owned Windows lock; POSIX advisory lock is development only."""
from dataclasses import dataclass
from pathlib import Path
import os
import stat
import sys

from packages.domain.errors import DomainError, StoreError


@dataclass(frozen=True)
class LockIdentity:
    volume: int
    file_id: int
    final_path: Path
    backend: str


class WriterLock:
    def __init__(self, path: Path, approved_root: Path):
        self._handle = None
        self.identity = None
        path, root = Path(path), Path(approved_root).resolve(strict=True)
        if not path.parent.resolve(strict=True).is_relative_to(root):
            raise StoreError("Lock is outside the approved root")
        try:
            if os.name == "nt":
                self._acquire_windows(path, root)
            elif sys.platform in {"darwin", "linux"}:
                self._acquire_posix(path, root)
            else:
                raise StoreError("Unsupported lock platform")
        except BaseException:
            self.close()
            raise

    def _acquire_posix(self, path, root):
        import fcntl
        fd = os.open(path, os.O_RDWR | os.O_CREAT | os.O_NOFOLLOW | os.O_CLOEXEC, 0o600)
        self._handle = fd
        try:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise DomainError("HOME_WRITER_EXISTS") from None
        info = os.fstat(fd)
        if not stat.S_ISREG(info.st_mode) or info.st_nlink != 1:
            raise StoreError("Lock must be a single regular file")
        if sys.platform == "darwin":
            final = Path(os.fsdecode(fcntl.fcntl(fd, 50, bytes(1024)).split(b"\0", 1)[0]))
        else:
            final = Path(os.readlink(f"/proc/self/fd/{fd}"))
        if not final.is_relative_to(root):
            raise StoreError("Opened lock is outside approved root")
        self.identity = LockIdentity(info.st_dev, info.st_ino, final, "posix_dev")

    def _acquire_windows(self, path, root):
        import ctypes as c
        from ctypes import wintypes as w
        api = c.WinDLL("kernel32", use_last_error=True)
        api.CreateFileW.argtypes = [w.LPCWSTR, w.DWORD, w.DWORD, c.c_void_p, w.DWORD, w.DWORD, w.HANDLE]
        api.CreateFileW.restype = w.HANDLE
        api.CloseHandle.argtypes = [w.HANDLE]
        api.CloseHandle.restype = w.BOOL
        api.GetFinalPathNameByHandleW.argtypes = [w.HANDLE, w.LPWSTR, w.DWORD, w.DWORD]
        api.GetFinalPathNameByHandleW.restype = w.DWORD

        class Info(c.Structure):
            _fields_ = [("attributes", w.DWORD), ("created", w.FILETIME),
                        ("accessed", w.FILETIME), ("written", w.FILETIME),
                        ("volume", w.DWORD), ("size_hi", w.DWORD), ("size_lo", w.DWORD),
                        ("links", w.DWORD), ("index_hi", w.DWORD), ("index_lo", w.DWORD)]

        api.GetFileInformationByHandle.argtypes = [w.HANDLE, c.POINTER(Info)]
        api.GetFileInformationByHandle.restype = w.BOOL
        invalid = c.c_void_p(-1).value

        def final_path(handle):
            size = api.GetFinalPathNameByHandleW(handle, None, 0, 0)
            if not size:
                raise StoreError("Cannot identify lock path")
            buf = c.create_unicode_buffer(size + 1)
            count = api.GetFinalPathNameByHandleW(handle, buf, len(buf), 0)
            if not count or count >= len(buf):
                raise StoreError("Cannot identify lock path")
            value = buf.value
            if value.startswith("\\\\?\\UNC\\"):
                raise StoreError("Network stores are unsupported")
            return Path(value.removeprefix("\\\\?\\"))

        handle = api.CreateFileW(str(path), 0xC0000000, 0, None, 4, 0x80, None)
        if handle == invalid:
            if c.get_last_error() in {32, 33}:
                raise DomainError("HOME_WRITER_EXISTS") from None
            raise StoreError("Cannot acquire writer handle")
        self._handle = handle
        self._windows_api = api
        info = Info()
        if not api.GetFileInformationByHandle(handle, c.byref(info)) or info.links != 1:
            raise StoreError("Cannot establish lock identity")
        final = final_path(handle)
        # Compare paths obtained from handles, so subst/junction aliases do not define identity.
        root_handle = api.CreateFileW(str(root), 0, 7, None, 3, 0x02000000, None)
        if root_handle == invalid:
            raise StoreError("Cannot identify approved root")
        try:
            canonical_root = final_path(root_handle)
        finally:
            api.CloseHandle(root_handle)
        if not final.is_relative_to(canonical_root):
            raise StoreError("Opened lock is outside approved root")
        api.GetVolumePathNameW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD]
        api.GetVolumePathNameW.restype = w.BOOL
        api.GetDriveTypeW.argtypes = [w.LPCWSTR]
        api.GetDriveTypeW.restype = w.UINT
        api.GetVolumeInformationW.argtypes = [w.LPCWSTR, w.LPWSTR, w.DWORD, c.POINTER(w.DWORD),
                                              c.POINTER(w.DWORD), c.POINTER(w.DWORD), w.LPWSTR, w.DWORD]
        api.GetVolumeInformationW.restype = w.BOOL
        volume_path, fs = c.create_unicode_buffer(32768), c.create_unicode_buffer(32)
        serial, max_component, flags = w.DWORD(), w.DWORD(), w.DWORD()
        if not api.GetVolumePathNameW(str(final), volume_path, len(volume_path)):
            raise StoreError("Cannot establish volume root")
        if api.GetDriveTypeW(volume_path.value) != 3:
            raise StoreError("Writable stores require a fixed local volume")
        if not api.GetVolumeInformationW(volume_path.value, None, 0, c.byref(serial),
                                         c.byref(max_component), c.byref(flags), fs, len(fs)):
            raise StoreError("Cannot establish filesystem support")
        if fs.value != "NTFS" or serial.value != info.volume:
            raise StoreError("Unqualified store filesystem")
        self.identity = LockIdentity(info.volume, (info.index_hi << 32) | info.index_lo, final, "windows_handle")

    def close(self):
        if self._handle is not None:
            if os.name == "nt":
                self._windows_api.CloseHandle(self._handle)
            else:
                os.close(self._handle)
            self._handle = None

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
