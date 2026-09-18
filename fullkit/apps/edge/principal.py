"""Principal is observed from the process, never accepted from request payloads."""
import os
from packages.domain.errors import StoreError


def current_principal():
    if os.name != "nt":
        return f"posix_dev:uid={os.getuid()}"
    import ctypes as c
    from ctypes import wintypes as w
    kernel, security = c.WinDLL("kernel32", use_last_error=True), c.WinDLL("advapi32", use_last_error=True)
    kernel.GetCurrentProcess.restype = w.HANDLE
    kernel.CloseHandle.argtypes = [w.HANDLE]
    kernel.CloseHandle.restype = w.BOOL
    kernel.LocalFree.argtypes = [c.c_void_p]
    kernel.LocalFree.restype = c.c_void_p
    security.OpenProcessToken.argtypes = [w.HANDLE, w.DWORD, c.POINTER(w.HANDLE)]
    security.OpenProcessToken.restype = w.BOOL
    security.GetTokenInformation.argtypes = [w.HANDLE, c.c_int, c.c_void_p, w.DWORD, c.POINTER(w.DWORD)]
    security.GetTokenInformation.restype = w.BOOL
    security.ConvertSidToStringSidW.argtypes = [c.c_void_p, c.POINTER(w.LPWSTR)]
    security.ConvertSidToStringSidW.restype = w.BOOL
    token, size, text = w.HANDLE(), w.DWORD(), w.LPWSTR()
    if not security.OpenProcessToken(kernel.GetCurrentProcess(), 8, c.byref(token)):
        raise StoreError("Cannot observe local principal")
    try:
        security.GetTokenInformation(token, 1, None, 0, c.byref(size))
        if not size.value:
            raise StoreError("Cannot observe local principal")
        buf = c.create_string_buffer(size.value)
        if not security.GetTokenInformation(token, 1, buf, len(buf), c.byref(size)):
            raise StoreError("Cannot observe local principal")
        sid = c.cast(buf, c.POINTER(c.c_void_p))[0]
        if not security.ConvertSidToStringSidW(sid, c.byref(text)):
            raise StoreError("Cannot observe local principal")
        try:
            return text.value
        finally:
            kernel.LocalFree(c.cast(text, c.c_void_p))
    finally:
        kernel.CloseHandle(token)
