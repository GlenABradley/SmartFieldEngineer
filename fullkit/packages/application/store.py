"""Serialized store lifecycle. No public RPC or fake application test driver."""
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from importlib.resources import files
from pathlib import Path
import hashlib
import json
import sqlite3
import uuid

from adapters.sqlite.store import connect_store
from apps.edge.writer_lock import WriterLock
from packages.domain.errors import DomainError, StoreError
from packages.application.commands import execute_command, operation_get, jobs_page


@dataclass(frozen=True)
class StoreIdentity:
    home_id: str
    store_instance_id: str
    active: bool = True
    recovery: bool = False

    def __post_init__(self):
        for name in ("home_id", "store_instance_id"):
            object.__setattr__(self, name, str(uuid.UUID(getattr(self, name))))
        if type(self.active) is not bool or type(self.recovery) is not bool:
            raise ValueError("Identity flags must be boolean")
        if self.recovery and self.active:
            raise ValueError("Recovery begins inactive")


def _statements(sql):
    statement = ""
    for line in sql.splitlines(keepends=True):
        statement += line
        if sqlite3.complete_statement(statement):
            yield statement
            statement = ""
    if statement.strip():
        raise StoreError("Incomplete migration")


def _migration_plan(con, identity):
    resource = files("migrations.local")
    migrations = sorted((p for p in resource.iterdir() if p.name.endswith(".sql")), key=lambda p: p.name)
    for number, migration in enumerate(migrations, 1):
        if not migration.name.startswith(f"{number:03d}_"):
            raise StoreError("Nonsequential migration")
    version = con.execute("PRAGMA user_version").fetchone()[0]
    if version > len(migrations):
        raise StoreError("Store schema is newer than this application")
    if version:
        row = con.execute("SELECT * FROM store_meta WHERE singleton=1").fetchone()
        if row is None or dict(row) != dict(singleton=1, **asdict(identity)):
            raise DomainError("HOME_CONTEXT")
        history = con.execute("SELECT version, sha256 FROM schema_history ORDER BY version").fetchall()
        if len(history) != version:
            raise StoreError("Incomplete migration history")
        for index, row in enumerate(history, 1):
            if row["version"] != index or row["sha256"] != hashlib.sha256(migrations[index-1].read_bytes()).hexdigest():
                raise StoreError("Migration history mismatch")
    return migrations, version


def _migrate(con, identity):
    """Called only by the serialized maintenance execution boundary with a lock."""
    migrations, version = _migration_plan(con, identity)
    for number, migration in enumerate(migrations, 1):
        if number <= version:
            continue
        op, now = str(uuid.uuid4()), datetime.now(timezone.utc).isoformat()
        con.execute("BEGIN IMMEDIATE")
        try:
            # executescript would implicitly commit, breaking atomic migration receipts.
            for statement in _statements(migration.read_text(encoding="utf-8")):
                con.execute(statement)
            if number == 1:
                con.execute("INSERT INTO store_meta VALUES(1,?,?,?,?)",
                            (identity.home_id, identity.store_instance_id, identity.active, identity.recovery))
            digest = hashlib.sha256(migration.read_bytes()).hexdigest()
            con.execute("INSERT INTO schema_history VALUES(?,?,?,?)", (number, digest, now, op))
            con.execute("INSERT INTO maintenance_receipts VALUES(?,?,?,?,?)",
                        (op, "store.migrate", "confirmed", json.dumps({"schema_version": number}), now))
            con.execute(f"PRAGMA user_version={number}")
            con.commit()
        except BaseException:
            con.rollback()
            raise


class StoreSession:
    """One connection and lock owned by a single executor thread for its lifetime."""

    def __init__(self, root, approved_root, identity, *, create=False, readonly=False):
        self.root, self.identity = Path(root), identity
        self.readonly = readonly
        self._con = self._lock = None
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fullkit-store")
        self._closed = False
        try:
            self._executor.submit(self._open, Path(approved_root), create).result()
        except BaseException:
            self._executor.shutdown(wait=True)
            self._closed = True
            raise

    def _open(self, approved_root, create):
        try:
            if self.root.is_symlink() or not self.root.resolve(strict=True).is_relative_to(approved_root.resolve(strict=True)):
                raise StoreError("Store is outside approved root")
            ledger = self.root / "ledger.sqlite"
            for candidate in (ledger, self.root / "ledger.sqlite-wal", self.root / "ledger.sqlite-shm"):
                if candidate.is_symlink() or (candidate.exists() and candidate.stat().st_nlink != 1):
                    raise StoreError("Ledger aliases are unsupported")
            if self.readonly:
                if create:
                    raise ValueError("Read-only open cannot create")
            else:
                if self.identity.recovery or not self.identity.active:
                    raise DomainError("RECOVERY_INACTIVE")
                self._lock = WriterLock(self.root / "home.lock", approved_root)
                # Mismatches must not alter an existing store via migrations or WAL setup.
            if not create:
                check = connect_store(ledger, readonly=True)
                try:
                    row = check.execute("SELECT * FROM store_meta WHERE singleton=1").fetchone()
                    if row is None or dict(row) != dict(singleton=1, **asdict(self.identity)):
                        raise DomainError("HOME_CONTEXT")
                finally:
                    check.close()
            elif ledger.exists():
                raise StoreError("Create cannot overwrite an existing ledger")
            self._con = connect_store(ledger, create=create, readonly=self.readonly)
            if self.readonly:
                self._con.execute("PRAGMA query_only=ON")
                _migration_plan(self._con, self.identity)
            else:
                self._execute_maintenance("store.migrate")
        except BaseException:
            self._close_on_writer()
            raise

    def execute_command(self, name):
        """Internal maintenance boundary; ordinary RPC command semantics come next."""
        if self.readonly:
            raise DomainError("RECOVERY_INACTIVE")
        if self._closed:
            raise StoreError("Store is closed")
        return self._executor.submit(self._execute_maintenance, name).result()

    def _execute_maintenance(self, name):
        if name != "store.migrate":
            raise ValueError("Foundation implements migration maintenance only")
        return _migrate(self._con, self.identity)

    def submit_command(self, cmd, principal):
        if self.readonly or self.identity.recovery or not self.identity.active:
            raise DomainError("RECOVERY_INACTIVE")
        if self._closed:
            raise StoreError("Store is closed")
        return self._executor.submit(execute_command, self._con, self.identity, cmd, principal).result()

    def get_operation(self, operation_id):
        if self._closed:
            raise StoreError("Store is closed")
        return self._executor.submit(operation_get, self._con, operation_id).result()

    def list_jobs(self, high_water, last_key, limit):
        if self._closed:
            raise StoreError("Store is closed")
        return self._executor.submit(jobs_page, self._con, high_water, last_key, limit).result()

    def inspect(self):
        """Read-only tooling evidence, without exposing connections or ledger mutation."""
        def read():
            return {"identity": asdict(self.identity),
                    "schema_version": self._con.execute("PRAGMA user_version").fetchone()[0],
                    "journal_mode": self._con.execute("PRAGMA journal_mode").fetchone()[0],
                    "synchronous": self._con.execute("PRAGMA synchronous").fetchone()[0],
                    "foreign_keys": self._con.execute("PRAGMA foreign_keys").fetchone()[0],
                    "migration_history": [dict(row) for row in self._con.execute("SELECT * FROM schema_history ORDER BY version")],
                    "maintenance_receipts": [dict(row) for row in self._con.execute("SELECT * FROM maintenance_receipts ORDER BY completed_at")],
                    "lock_backend": self._lock.identity.backend if self._lock else None}
        if self._closed:
            raise StoreError("Store is closed")
        return self._executor.submit(read).result()

    def _close_on_writer(self):
        try:
            if self._con:
                self._con.close()
                self._con = None
        finally:
            if self._lock:
                self._lock.close()
                self._lock = None

    def close(self):
        if not self._closed:
            try:
                self._executor.submit(self._close_on_writer).result()
            finally:
                self._executor.shutdown(wait=True)
                self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
