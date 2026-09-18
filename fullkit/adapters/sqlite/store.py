from pathlib import Path
import sqlite3

from packages.domain.errors import StoreError


def connect_store(path: Path, *, create=False, readonly=False):
    """Never accidentally create a missing selected store."""
    mode = "ro" if readonly else "rwc" if create else "rw"
    con = sqlite3.connect(path.resolve().as_uri() + "?mode=" + mode, uri=True,
                          isolation_level=None, timeout=5)
    try:
        con.row_factory = sqlite3.Row
        con.execute("PRAGMA foreign_keys=ON")
        con.execute("PRAGMA synchronous=FULL")
        if not readonly:
            if con.execute("PRAGMA journal_mode=WAL").fetchone()[0] != "wal":
                raise StoreError("WAL unavailable")
        if con.execute("PRAGMA foreign_keys").fetchone()[0] != 1:
            raise StoreError("Foreign keys unavailable")
        return con
    except BaseException:
        con.close()
        raise
