"""Real local persistence/lock tests. Not Windows or full RPC acceptance evidence."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
import hashlib
import json
import os
import sqlite3
import subprocess
import sys
import uuid

import pytest

from apps.edge.writer_lock import WriterLock
from packages.application.homes import HomeWorkspace
from packages.application.store import StoreIdentity, StoreSession
from packages.domain.errors import DomainError, StoreError


APP = Path(__file__).resolve().parents[2]


def uid():
    return str(uuid.uuid4())


def create_store(root):
    root.mkdir()
    identity = StoreIdentity(uid(), uid())
    with StoreSession(root, root.parent, identity, create=True):
        pass
    return identity


def test_provision_persists_two_homes_and_replays_exact_intent(tmp_path):
    root, operation = tmp_path / "owner", uid()
    with HomeWorkspace(root) as app:
        result = app.provision(["A", "B"], operation)
        assert result["status"] == "confirmed"
        assert app.list_homes() == result["homes"]
        assert len({row["home_id"] for row in result["homes"]}) == 2
        for home in app.list_homes():
            assert set(home) == {"home_id", "store_instance_id", "label", "active", "recovery"}
            with app.open_store(home["home_id"], home["store_instance_id"]) as store:
                evidence = store.inspect()
                assert evidence["schema_version"] == 2
                assert evidence["journal_mode"] == "wal"
                assert evidence["synchronous"] == 2
                assert evidence["foreign_keys"] == 1
                history, receipts = evidence["migration_history"], evidence["maintenance_receipts"]
                assert len(history) == len(receipts) == 2
                assert history[0]["operation_id"] == receipts[0]["operation_id"]
                assert receipts[0]["state"] == "confirmed"
                assert json.loads(receipts[0]["result_json"]) == {"schema_version": 1}
            directory = root / ("home-" + home["home_id"])
            assert all((directory / part).is_dir() for part in ("blobs/sha256", "staging", "read-cache", "client-intents"))
            assert (root / "backups" / directory.name).is_dir()
    with HomeWorkspace(root) as restarted:
        assert restarted.provision(["A", "B"], operation) == result
        with pytest.raises(DomainError) as conflict:
            restarted.provision(["changed", "B"], operation)
        assert conflict.value.code == "OPERATION_ID_CONFLICT"
        with pytest.raises(StoreError, match="already provisioned"):
            restarted.provision(["A", "B"], uid())


def test_migration_and_receipt_roll_back_together(tmp_path, monkeypatch):
    root = tmp_path / "store"
    root.mkdir()
    identity = StoreIdentity(uid(), uid())

    real_connect = sqlite3.connect

    class CommitFailure(sqlite3.Connection):
        def commit(self):
            raise sqlite3.OperationalError("injected commit fault")

    # Test-only instrumentation of a real SQLite connection; no shipped fault hook.
    with monkeypatch.context() as patch:
        patch.setattr(sqlite3, "connect", lambda *a, **kw: real_connect(*a, factory=CommitFailure, **kw))
        with pytest.raises(sqlite3.OperationalError, match="injected"):
            StoreSession(root, tmp_path, identity, create=True)
    with sqlite3.connect(root / "ledger.sqlite") as con:
        assert con.execute("PRAGMA user_version").fetchone()[0] == 0
        assert con.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall() == []
    # A failed open releases its lock; the persistent lock file is never removed.
    with WriterLock(root / "home.lock", tmp_path):
        pass


def test_failed_provision_has_no_registered_or_partial_homes(tmp_path, monkeypatch):
    root = tmp_path / "owner"
    operation = uid()

    def fail(directories):
        raise RuntimeError("injected publication fault")

    with HomeWorkspace(root) as app:
        with monkeypatch.context() as patch:
            patch.setattr(app, "_flush_directories", fail)
            with pytest.raises(RuntimeError):
                app.provision(["A", "B"], operation)
        assert app.list_homes() == []
        assert list(root.glob("home-*")) == []
        assert list((root / "backups").iterdir()) == []
        assert len(app.provision(["A", "B"], operation)["homes"]) == 2


def test_foreign_store_identity_is_denied_without_touching_ledger(tmp_path):
    root = tmp_path / "store"
    identity = create_store(root)
    before = hashlib.sha256((root / "ledger.sqlite").read_bytes()).hexdigest()
    wrong = StoreIdentity(uid(), identity.store_instance_id)
    with pytest.raises(DomainError) as error:
        StoreSession(root, tmp_path, wrong)
    assert error.value.code == "HOME_CONTEXT"
    assert hashlib.sha256((root / "ledger.sqlite").read_bytes()).hexdigest() == before
    with StoreSession(root, tmp_path, identity) as store:
        assert len(store.inspect()["maintenance_receipts"]) == 2


def test_missing_selected_ledger_is_not_created(tmp_path):
    root = tmp_path / "missing"
    root.mkdir()
    with pytest.raises(sqlite3.OperationalError):
        StoreSession(root, tmp_path, StoreIdentity(uid(), uid()))
    assert not (root / "ledger.sqlite").exists()


def test_two_sessions_cannot_write_same_store_and_peer_is_independent(tmp_path):
    a, b = tmp_path / "a", tmp_path / "b"
    ia, ib = create_store(a), create_store(b)
    with StoreSession(a, tmp_path, ia), StoreSession(b, tmp_path, ib):
        with pytest.raises(DomainError) as error:
            StoreSession(a, tmp_path, ia)
        assert error.value.code == "HOME_WRITER_EXISTS"
    assert (a / "home.lock").exists()
    with StoreSession(a, tmp_path, ia):
        pass


def test_real_subprocess_writer_is_excluded_and_process_exit_releases_lock(tmp_path):
    path = tmp_path / "home.lock"
    env = dict(os.environ, PYTHONPATH=str(APP))
    code = """import sys
from pathlib import Path
from apps.edge.writer_lock import WriterLock
from packages.domain.errors import DomainError
try:
    with WriterLock(Path(sys.argv[1]), Path(sys.argv[2])):
        print('acquired', flush=True)
        if len(sys.argv) > 3: sys.stdin.read()
except DomainError as error:
    print(error.code, flush=True)
    sys.exit(7)
"""
    args = [sys.executable, "-c", code, str(path), str(tmp_path)]
    with WriterLock(path, tmp_path):
        rejected = subprocess.run(args, env=env, capture_output=True, text=True, timeout=10)
        assert rejected.returncode == 7
        assert rejected.stdout.strip() == "HOME_WRITER_EXISTS"
    held = subprocess.Popen(args + ["hold"], env=env, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    try:
        # Poll the actual OS lock instead of an unbounded pipe read.
        import time
        deadline = time.monotonic() + 10
        while time.monotonic() < deadline:
            try:
                with WriterLock(path, tmp_path):
                    pass
            except DomainError:
                break
            time.sleep(.02)
        else:
            pytest.fail("Child failed to acquire lock")
        held.kill()
        held.communicate(timeout=10)
        with WriterLock(path, tmp_path):
            pass
        assert path.exists()
    finally:
        if held.poll() is None:
            held.kill()
            held.communicate(timeout=10)


@pytest.mark.skipif(os.name == "nt", reason="POSIX directory alias test; Windows junction/subst requires target qualification")
def test_directory_alias_reaches_same_lock_identity(tmp_path):
    root = tmp_path / "actual"
    root.mkdir()
    alias = tmp_path / "alias"
    alias.symlink_to(root, target_is_directory=True)
    with WriterLock(root / "home.lock", tmp_path) as original:
        with pytest.raises(DomainError) as error:
            WriterLock(alias / "home.lock", tmp_path)
        assert error.value.code == "HOME_WRITER_EXISTS"
        identity = original.identity
    with WriterLock(alias / "home.lock", tmp_path) as other:
        assert (identity.volume, identity.file_id) == (other.identity.volume, other.identity.file_id)


def test_outside_approved_root_is_rejected_before_ledger_creation(tmp_path):
    approved, outside = tmp_path / "approved", tmp_path / "outside"
    approved.mkdir()
    outside.mkdir()
    with pytest.raises(StoreError, match="outside approved"):
        StoreSession(outside, approved, StoreIdentity(uid(), uid()), create=True)
    assert not (outside / "ledger.sqlite").exists()


def test_readonly_inspection_does_not_migrate_and_cannot_execute(tmp_path):
    root = tmp_path / "store"
    identity = create_store(root)
    before = {p.name: p.read_bytes() for p in root.iterdir() if p.name != "home.lock"}
    with StoreSession(root, tmp_path, identity, readonly=True) as session:
        assert session.inspect()["schema_version"] == 2
        assert session.inspect()["lock_backend"] is None
        with pytest.raises(DomainError) as error:
            session.execute_command("store.migrate")
        assert error.value.code == "RECOVERY_INACTIVE"
    # SQLite may create read-only WAL bookkeeping sidecars; original closed files unchanged.
    assert all((root / name).read_bytes() == contents for name, contents in before.items())


def test_unknown_home_and_foreign_store_return_identical_denial(tmp_path):
    with HomeWorkspace(tmp_path / "owner") as app:
        app.provision(["A", "B"], uid())
        a, b = app.list_homes()
        for home, store in [(uid(), uid()), (a["home_id"], b["store_instance_id"])]:
            with pytest.raises(DomainError) as error:
                app.open_store(home, store)
            assert error.value.code == "HOME_CONTEXT"


def test_serialized_parallel_provision_retries_create_only_two_homes(tmp_path):
    with HomeWorkspace(tmp_path / "owner") as app, ThreadPoolExecutor(max_workers=4) as callers:
        operation = uid()
        replies = list(callers.map(lambda _: app.provision(["A", "B"], operation), range(4)))
        assert all(result == replies[0] for result in replies)
        assert len(app.list_homes()) == 2


def test_killed_provision_leaves_unpublished_stores_for_explicit_review(tmp_path):
    root = tmp_path / "owner"
    code = """import os, sys, uuid
from packages.application.homes import HomeWorkspace
with HomeWorkspace(sys.argv[1]) as app:
    app._flush_directories = lambda directories: os._exit(81)
    app.provision(['A', 'B'], str(uuid.uuid4()))
"""
    killed = subprocess.run([sys.executable, "-c", code, str(root)],
                            env=dict(os.environ, PYTHONPATH=str(APP)), timeout=15)
    assert killed.returncode == 81
    abandoned = sorted(root.glob("home-*"))
    assert len(abandoned) == 2
    snapshots = [(p / "ledger.sqlite").read_bytes() for p in abandoned]
    with HomeWorkspace(root) as app:
        assert app.list_homes() == []
        with pytest.raises(StoreError, match="explicit recovery review"):
            app.provision(["A", "B"], uid())
    assert [(p / "ledger.sqlite").read_bytes() for p in abandoned] == snapshots
    with WriterLock(root / "owner.lock", root):
        pass


def test_tampered_migration_history_rejects_open_and_releases_lock(tmp_path):
    root = tmp_path / "store"
    identity = create_store(root)
    # Deliberate corruption fixture, never a success path or arbitrary application write.
    with sqlite3.connect(root / "ledger.sqlite") as con:
        con.execute("UPDATE schema_history SET sha256=?", ("0" * 64,))
    with pytest.raises(StoreError, match="history mismatch"):
        StoreSession(root, tmp_path, identity)
    with WriterLock(root / "home.lock", tmp_path):
        pass


def test_newer_schema_is_not_downgraded(tmp_path):
    root = tmp_path / "store"
    identity = create_store(root)
    with sqlite3.connect(root / "ledger.sqlite") as con:
        con.execute("PRAGMA user_version=3")
    with pytest.raises(StoreError, match="newer"):
        StoreSession(root, tmp_path, identity)
    with sqlite3.connect(root / "ledger.sqlite") as con:
        assert con.execute("PRAGMA user_version").fetchone()[0] == 3


def test_symlinked_ledger_cannot_escape_home_root(tmp_path):
    outside = tmp_path / "outside"
    create_store(outside)
    root = tmp_path / "alias-store"
    root.mkdir()
    (root / "ledger.sqlite").symlink_to(outside / "ledger.sqlite")
    with pytest.raises(StoreError, match="aliases"):
        StoreSession(root, tmp_path, StoreIdentity(uid(), uid()))


def test_invalid_provision_request_has_no_filesystem_side_effects(tmp_path):
    root = tmp_path / "owner"
    with HomeWorkspace(root) as app:
        for labels, operation in [(["A"], uid()), (["A", " "], uid()), (["A", "B"], "not-a-uuid")]:
            with pytest.raises(ValueError):
                app.execute_command("home.provision", labels, operation)
        assert not root.exists()


def test_lost_index_commit_ack_does_not_delete_published_stores(tmp_path, monkeypatch):
    root, operation = tmp_path / "owner", uid()
    real_connect = sqlite3.connect

    class LostAcknowledgement(sqlite3.Connection):
        def commit(self):
            filename = self.execute("PRAGMA database_list").fetchone()[2]
            super().commit()
            if Path(filename).name == "private-home-index":
                raise sqlite3.OperationalError("injected lost commit acknowledgement")

    with HomeWorkspace(root) as app:
        with monkeypatch.context() as patch:
            patch.setattr(sqlite3, "connect", lambda *a, **kw: real_connect(*a, factory=LostAcknowledgement, **kw))
            with pytest.raises(sqlite3.OperationalError, match="lost commit acknowledgement"):
                app.provision(["A", "B"], operation)
        homes = app.list_homes()
        assert len(homes) == 2
        assert app.provision(["A", "B"], operation) == {"status": "confirmed", "homes": homes}
        for home in homes:
            with app.open_store(home["home_id"], home["store_instance_id"]) as store:
                assert store.inspect()["schema_version"] == 2
