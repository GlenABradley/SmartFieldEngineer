"""Home provision/index foundation. Not the unfinished JSON-RPC application."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from dataclasses import asdict
import hashlib
import json
import os
import shutil
import uuid

from adapters.sqlite.store import connect_store
from apps.edge.writer_lock import WriterLock
from packages.application.store import StoreIdentity, StoreSession
from packages.domain.errors import DomainError, StoreError


class HomeWorkspace:
    def __init__(self, owner_root):
        self.root = Path(owner_root).absolute()
        self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="fullkit-maintenance")
        self._closed = False

    def provision(self, labels, operation_id):
        """Internal named maintenance command; replay never invents new Homes."""
        return self.execute_command("home.provision", labels, operation_id)

    def execute_command(self, name, labels, operation_id):
        """Maintenance writes use this serialized execution boundary, never GUI SQL."""
        if name != "home.provision":
            raise ValueError("Unimplemented maintenance command")
        if self._closed:
            raise StoreError("Workspace is closed")
        if not isinstance(labels, (tuple, list)) or len(labels) != 2:
            raise ValueError("Initial provisioning requires two Home labels")
        if any(not isinstance(label, str) or not label.strip() for label in labels):
            raise ValueError("Home labels must be nonempty")
        operation_id = str(uuid.UUID(operation_id))
        return self._executor.submit(self._execute_provision, tuple(labels), operation_id).result()

    def _execute_provision(self, labels, operation_id):
        if self.root.is_symlink():
            raise StoreError("Owner root must not be a symlink")
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        index = self.root / "private-home-index"
        for candidate in (index, self.root / "private-home-index-wal", self.root / "private-home-index-shm"):
            if candidate.is_symlink() or (candidate.exists() and candidate.stat().st_nlink != 1):
                raise StoreError("Index aliases are unsupported")
        if (self.root / "backups").is_symlink():
            raise StoreError("Backup root aliases are unsupported")
        fingerprint = hashlib.sha256(json.dumps({"labels": labels}, ensure_ascii=False,
                                                sort_keys=True, separators=(",", ":")).encode()).hexdigest()
        created = []
        commit_started = False
        with WriterLock(self.root / "owner.lock", self.root):
            # A crash may leave unpublished stores. Do not silently adopt or delete them.
            con = connect_store(index, create=True)
            try:
                con.execute("BEGIN IMMEDIATE")
                con.execute("CREATE TABLE IF NOT EXISTS homes (home_id TEXT NOT NULL, store_instance_id TEXT UNIQUE NOT NULL, label TEXT NOT NULL, relative_root TEXT UNIQUE NOT NULL, active INTEGER NOT NULL CHECK(active IN (0,1)), recovery INTEGER NOT NULL CHECK(recovery IN (0,1)), PRIMARY KEY(home_id,store_instance_id), CHECK(recovery=0 OR active=0))")
                con.execute("CREATE UNIQUE INDEX IF NOT EXISTS one_active_home ON homes(home_id) WHERE active=1")
                con.execute("CREATE TABLE IF NOT EXISTS provisioning_operations (operation_id TEXT PRIMARY KEY, fingerprint TEXT NOT NULL, result_json TEXT NOT NULL)")
                prior = con.execute("SELECT * FROM provisioning_operations WHERE operation_id=?", (operation_id,)).fetchone()
                if prior:
                    if prior["fingerprint"] != fingerprint:
                        raise DomainError("OPERATION_ID_CONFLICT")
                    con.rollback()
                    return json.loads(prior["result_json"])
                if con.execute("SELECT COUNT(*) FROM homes").fetchone()[0]:
                    raise StoreError("Workspace already provisioned")
                if any(self.root.glob("home-*")):
                    raise StoreError("Unpublished Home directories require explicit recovery review")
                homes = []
                for label in labels:
                    identity = StoreIdentity(str(uuid.uuid4()), str(uuid.uuid4()))
                    relative = "home-" + identity.home_id
                    directory = self.root / relative
                    directory.mkdir(mode=0o700)
                    created.append(directory)
                    for subdir in ("blobs/sha256", "staging", "read-cache", "client-intents"):
                        (directory / subdir).mkdir(parents=True, mode=0o700)
                    backup = self.root / "backups" / relative
                    backup.mkdir(parents=True, mode=0o700)
                    created.append(backup)
                    with StoreSession(directory, self.root, identity, create=True):
                        pass
                    con.execute("INSERT INTO homes VALUES(?,?,?,?,?,?)",
                                (identity.home_id, identity.store_instance_id, label, relative, True, False))
                    homes.append(dict(asdict(identity), label=label))
                result = {"status": "confirmed", "homes": homes}
                con.execute("INSERT INTO provisioning_operations VALUES(?,?,?)",
                            (operation_id, fingerprint, json.dumps(result)))
                self._flush_directories(created)
                commit_started = True
                con.commit()
                return result
            except BaseException:
                con.rollback()
                # Commit acknowledgement can fail after durable publication. Never
                # delete stores potentially referenced by a committed index.
                if not commit_started:
                    for directory in reversed(created):
                        shutil.rmtree(directory)
                raise
            finally:
                con.close()

    def _flush_directories(self, directories):
        # Windows directory durability and ACLs remain target qualification work.
        if os.name != "nt":
            roots = set(directories) | {p.parent for p in directories} | {self.root}
            for root in sorted(roots):
                fd = os.open(root, os.O_RDONLY | os.O_DIRECTORY)
                try:
                    os.fsync(fd)
                finally:
                    os.close(fd)

    def _index_rows(self):
        index = self.root / "private-home-index"
        if not index.exists():
            return []
        if index.is_symlink():
            raise StoreError("Index aliases are unsupported")
        con = connect_store(index, readonly=True)
        try:
            if not con.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='homes'").fetchone():
                return []
            return [dict(row) for row in con.execute("SELECT * FROM homes ORDER BY rowid")]
        finally:
            con.close()

    def list_homes(self):
        return [{key: bool(row[key]) if key in {"active", "recovery"} else row[key]
                 for key in ("home_id", "store_instance_id", "label", "active", "recovery")}
                for row in self._index_rows()]

    def open_store(self, home_id, store_instance_id, *, readonly=False):
        home_id, store_instance_id = str(uuid.UUID(home_id)), str(uuid.UUID(store_instance_id))
        row = next((row for row in self._index_rows()
                    if row["home_id"] == home_id and row["store_instance_id"] == store_instance_id), None)
        if row is None:
            raise DomainError("HOME_CONTEXT")
        relative = Path(row["relative_root"])
        expected = Path("recovery") / store_instance_id if row["recovery"] else Path("home-" + home_id)
        if relative != expected:
            raise StoreError("Invalid private index path")
        identity = StoreIdentity(home_id, store_instance_id, bool(row["active"]), bool(row["recovery"]))
        return StoreSession(self.root / relative, self.root, identity, readonly=readonly)

    def close(self):
        if not self._closed:
            self._executor.shutdown(wait=True)
            self._closed = True

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        self.close()
