"""Real frame/authorization/transaction tests of the implemented job-create slice."""
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from importlib.resources import files
import copy
import json
import os
import sqlite3
import subprocess
import sys
import uuid

import pytest
from jsonschema import Draft202012Validator, FormatChecker

from apps.edge.rpc import Core, MAX_FRAME
from packages.application.homes import HomeWorkspace

APP = Path(__file__).resolve().parents[2]
JOB = "22222222-2222-4222-8222-222222222222"


def uid():
    return str(uuid.uuid4())


def call(core, method, params):
    request = {"jsonrpc": "2.0", "id": uid(), "method": method, "params": params}
    response = json.loads(core.raw_frame((json.dumps(request) + "\n").encode()))
    assert response["id"] == request["id"]
    validator = Draft202012Validator(core.schema, format_checker=FormatChecker())
    validator.evolve(schema={"$ref": "#/$defs/response"}).validate(response)
    return response


def select(core, home):
    return call(core, "session.select_home", {key: home[key] for key in ("home_id", "store_instance_id")})["result"]


def create(context, *, operation=None, job=JOB, title="Real job"):
    return {"context": copy.deepcopy(context), "cmd": {"schema": "cmd.v0.addendum-r4", "kind": "command",
            "operation_id": operation or uid(), "home_id": context["home_id"], "command": "job.create",
            "job_id": job, "job_scope_revision": None, "expected_revision": 0,
            "payload": {"title": title, "scope_text": "Observed fixture scope", "capture_refs": []}}}


def deny(response, code):
    assert response["error"] == {"code": -32000, "message": code, "data": {}}
    assert "result" not in response


@pytest.fixture
def owner(tmp_path):
    root = tmp_path / "owner"
    with HomeWorkspace(root) as app:
        app.provision(["A", "B"], uid())
    return root


def fact_counts(root, home):
    path = root / ("home-" + home["home_id"]) / "ledger.sqlite"
    with sqlite3.connect(path.resolve().as_uri() + "?mode=ro", uri=True) as con:
        return {name: con.execute("SELECT COUNT(*) FROM " + name).fetchone()[0]
                for name in ("jobs", "job_events", "audit", "operations")}


def test_raw_two_home_same_job_ids_and_receipts_are_fenced(owner):
    with Core(owner) as core:
        a, b = call(core, "home.list", {})["result"]["homes"]
        ca = select(core, a)
        request = create(ca, title="A job")
        ra = call(core, "job.create", request)["result"]
        assert ra["state"] == "confirmed" and ra["result"]["aggregate_revision"] == 1
        assert ra["result"]["scope_revision"] == 1
        cb = select(core, b)
        rb = call(core, "job.create", create(cb, title="B job"))["result"]
        assert rb["result"]["job_id"] == ra["result"]["job_id"] == JOB
        deny(call(core, "job.create", request), "HOME_CONTEXT")
        foreign = call(core, "operation.get", {"context": cb, "operation_id": ra["operation_id"]})
        unknown = call(core, "operation.get", {"context": cb, "operation_id": uid()})
        deny(foreign, "HOME_CONTEXT")
        assert foreign["error"] == unknown["error"]
        assert call(core, "job.list", {"context": cb, "cursor": None, "limit": 100})["result"]["items"][0]["title"] == "B job"
        fresh = select(core, a)
        request["context"] = fresh
        assert call(core, "job.create", request)["result"] == ra
        assert fact_counts(owner, a) == fact_counts(owner, b) == {"jobs": 1, "job_events": 1, "audit": 1, "operations": 1}


def test_restart_reenvelopes_semantic_intent_and_preserves_receipt(owner):
    with Core(owner) as first:
        home = call(first, "home.list", {})["result"]["homes"][0]
        original = create(select(first, home))
        receipt = call(first, "job.create", original)["result"]
    with Core(owner) as restarted:
        fresh = select(restarted, home)
        assert fresh["session_id"] != original["context"]["session_id"]
        deny(call(restarted, "job.create", original), "HOME_CONTEXT")
        retry = dict(original, context=fresh)
        assert call(restarted, "job.create", retry)["result"] == receipt
        uppercase = copy.deepcopy(retry)
        for key in ("home_id", "store_instance_id", "session_id"):
            uppercase["context"][key] = uppercase["context"][key].upper()
        for key in ("home_id", "job_id", "operation_id"):
            uppercase["cmd"][key] = uppercase["cmd"][key].upper()
        assert call(restarted, "job.create", uppercase)["result"] == receipt
        assert call(restarted, "operation.get", {"context": fresh, "operation_id": receipt["operation_id"]})["result"] == {"receipt": receipt, "attach_attempt": None}
        changed = copy.deepcopy(retry)
        changed["cmd"]["payload"]["title"] = "Changed intent"
        deny(call(restarted, "job.create", changed), "OPERATION_ID_CONFLICT")
        changed["cmd"]["payload"]["capture_refs"] = [{"kind": "record", "id": uid()}]
        deny(call(restarted, "job.create", changed), "OPERATION_ID_CONFLICT")
        assert fact_counts(owner, home)["operations"] == 1


def test_business_rejection_is_durable_failed_receipt_and_replays(owner):
    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        ctx = select(core, home)
        call(core, "job.create", create(ctx))
        second = create(ctx, title="Duplicate job with new operation")
        receipt = call(core, "job.create", second)["result"]
        assert receipt["state"] == "failed" and receipt["result"] is None
        assert receipt["error"] == {"code": "STALE_JOB", "body": {}}
        assert call(core, "job.create", second)["result"] == receipt
        assert call(core, "operation.get", {"context": ctx, "operation_id": receipt["operation_id"]})["result"]["receipt"] == receipt
        assert fact_counts(owner, home) == {"jobs": 1, "job_events": 1, "audit": 2, "operations": 2}


def test_command_home_mismatch_and_bad_structure_create_no_receipts(owner):
    with Core(owner) as core:
        a, b = core.workspace.list_homes()
        ctx = select(core, a)
        request = create(ctx)
        request["cmd"]["home_id"] = b["home_id"]
        deny(call(core, "job.create", request), "HOME_CONTEXT")
        malformed = create(ctx)
        malformed["cmd"]["payload"]["extra"] = "not allowed"
        assert call(core, "job.create", malformed)["error"] == {"code": -32602, "message": "Invalid params"}
        assert fact_counts(owner, a) == fact_counts(owner, b) == {"jobs": 0, "job_events": 0, "audit": 0, "operations": 0}


@pytest.mark.parametrize("frame", [b'{"id":1,"id":2}\n', b'{"value":NaN}\n', b'{"value":Infinity}\n',
                                   b'\xff\n', b'{}', b'{}\n{}\n', b'[]\n'])
def test_bad_frames_never_reach_persistence(owner, frame):
    with Core(owner) as core:
        response = json.loads(core.raw_frame(frame))
        assert response["error"]["code"] in {-32700, -32600}
        assert response["id"] is None
        for home in core.workspace.list_homes():
            assert fact_counts(owner, home)["operations"] == 0


def test_frame_size_boundary_and_notifications(owner):
    with Core(owner) as core:
        request = {"jsonrpc": "2.0", "id": uid(), "method": "home.list", "params": {}}
        raw = json.dumps(request).encode()
        maximum = raw + b" " * (MAX_FRAME - len(raw) - 1) + b"\n"
        assert "result" in json.loads(core.raw_frame(maximum))
        assert json.loads(core.raw_frame(b" " + maximum))["error"]["code"] == -32700
        del request["id"]
        assert json.loads(core.raw_frame((json.dumps(request) + "\n").encode()))["error"]["code"] == -32600


def test_same_home_reselection_invalidates_prior_generation(owner):
    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        old, new = select(core, home), select(core, home)
        assert new["session_generation"] == old["session_generation"] + 1
        deny(call(core, "job.create", create(old)), "HOME_CONTEXT")
        assert call(core, "job.create", create(new))["result"]["state"] == "confirmed"


def test_failed_switch_reopens_previous_with_fresh_generation(owner):
    with Core(owner) as core:
        a, b = core.workspace.list_homes()
        old = select(core, a)
        with core.workspace.open_store(b["home_id"], b["store_instance_id"]):
            denied = call(core, "session.select_home", {key: b[key] for key in ("home_id", "store_instance_id")})
            deny(denied, "HOME_WRITER_EXISTS")
        assert core.context["home_id"] == a["home_id"]
        assert core.context["session_generation"] > old["session_generation"]
        deny(call(core, "job.create", create(old)), "HOME_CONTEXT")
        fresh = select(core, a)
        assert call(core, "job.create", create(fresh))["result"]["state"] == "confirmed"


def test_job_pagination_high_water_and_generation_fence(owner, monkeypatch):
    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        ctx = select(core, home)
        for title in ["one", "two", "three"]:
            call(core, "job.create", create(ctx, job=uid(), title=title))
        first = call(core, "job.list", {"context": ctx, "cursor": None, "limit": 1})["result"]
        assert [job["title"] for job in first["items"]] == ["one"]
        call(core, "job.create", create(ctx, job=uid(), title="after high-water"))
        rest = call(core, "job.list", {"context": ctx, "cursor": first["next_cursor"], "limit": 100})["result"]
        assert [job["title"] for job in rest["items"]] == ["two", "three"]
        assert rest["next_cursor"] is None
        next_context = select(core, home)
        deny(call(core, "job.list", {"context": next_context, "cursor": first["next_cursor"], "limit": 1}), "HOME_CONTEXT")
        fresh_page = call(core, "job.list", {"context": next_context, "cursor": None, "limit": 1})["result"]
        monkeypatch.setattr("packages.application.session.time.monotonic", lambda: float("inf"))
        deny(call(core, "job.list", {"context": next_context, "cursor": fresh_page["next_cursor"], "limit": 1}), "HOME_CONTEXT")


def test_parallel_same_intent_has_one_fact_audit_and_receipt(owner):
    with Core(owner) as core, ThreadPoolExecutor(max_workers=4) as callers:
        home = core.workspace.list_homes()[0]
        request = create(select(core, home))
        replies = list(callers.map(lambda _: call(core, "job.create", request)["result"], range(8)))
        assert all(reply == replies[0] for reply in replies)
        assert fact_counts(owner, home) == {"jobs": 1, "job_events": 1, "audit": 1, "operations": 1}


def test_command_commit_failure_rolls_back_all_facts_and_receipt(owner, monkeypatch):
    original_connect = sqlite3.connect

    class FailOnce(sqlite3.Connection):
        failed = False

        def commit(self):
            if not self.failed:
                self.failed = True
                raise sqlite3.OperationalError("injected commit failure with private path")
            return super().commit()

    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        with monkeypatch.context() as patch:
            patch.setattr(sqlite3, "connect", lambda *a, **kw: original_connect(*a, factory=FailOnce, **kw))
            ctx = select(core, home)
        request = create(ctx)
        assert call(core, "job.create", request)["error"] == {"code": -32603, "message": "Internal error"}
        assert fact_counts(owner, home) == {"jobs": 0, "job_events": 0, "audit": 0, "operations": 0}
        deny(call(core, "operation.get", {"context": ctx, "operation_id": request["cmd"]["operation_id"]}), "HOME_CONTEXT")
        assert call(core, "job.create", request)["result"]["state"] == "confirmed"


def test_lost_command_commit_ack_is_reconciled_without_duplicate(owner, monkeypatch):
    original_connect = sqlite3.connect

    class LoseOnce(sqlite3.Connection):
        lost = False

        def commit(self):
            super().commit()
            if not self.lost:
                self.lost = True
                raise sqlite3.OperationalError("injected lost acknowledgement")

    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        with monkeypatch.context() as patch:
            patch.setattr(sqlite3, "connect", lambda *a, **kw: original_connect(*a, factory=LoseOnce, **kw))
            ctx = select(core, home)
        request = create(ctx)
        assert call(core, "job.create", request)["error"]["code"] == -32603
        receipt = call(core, "operation.get", {"context": ctx, "operation_id": request["cmd"]["operation_id"]})["result"]["receipt"]
        assert receipt["state"] == "confirmed"
        assert call(core, "job.create", request)["result"] == receipt
        assert fact_counts(owner, home) == {"jobs": 1, "job_events": 1, "audit": 1, "operations": 1}


def test_registry_and_packaged_schemas_match_preserved_authority(owner):
    resource = files("apps.edge").joinpath("resources/schemas")
    for name in ["contract.json", "methods.json"]:
        assert resource.joinpath(name).read_bytes() == (APP / "contract/schemas" / name).read_bytes()
    with Core(owner) as core:
        assert len(core.methods) == 20
        assert call(core, "not.a.method", {})["error"]["code"] == -32601
        home = core.workspace.list_homes()[0]
        ctx = select(core, home)
        params = {"context": ctx, "job_id": JOB, "asset_id": uid()}
        # Known unfinished method fails honestly; it is not a fabricated success.
        assert call(core, "serial.recall", params)["error"]["code"] == -32603


def test_application_checks_context_without_transport_authority(owner):
    from packages.domain.errors import DomainError
    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        ctx = select(core, home)
        wrong = create(ctx)
        wrong["context"]["home_id"] = uid()
        with pytest.raises(DomainError) as error:
            core.application.dispatch("job.create", wrong)
        assert error.value.code == "HOME_CONTEXT"
        assert fact_counts(owner, home)["operations"] == 0


def test_inactive_recovery_guard_precedes_old_receipt_replay(owner):
    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        original = create(select(core, home))
        old_receipt = call(core, "job.create", original)["result"]
    # A labeled recovery fixture uses a real Backup API copy. This is not evidence
    # of the still-unimplemented restore/activation operation.
    recovery_id = uid()
    directory = owner / "recovery" / recovery_id
    directory.mkdir(parents=True)
    source = owner / ("home-" + home["home_id"]) / "ledger.sqlite"
    with sqlite3.connect(source.resolve().as_uri() + "?mode=ro", uri=True) as src, sqlite3.connect(directory / "ledger.sqlite") as target:
        src.backup(target)
        target.execute("UPDATE store_meta SET store_instance_id=?,active=0,recovery=1", (recovery_id,))
    with sqlite3.connect(owner / "private-home-index") as index:
        index.execute("INSERT INTO homes VALUES(?,?,?,?,?,?)",
                      (home["home_id"], recovery_id, "Recovery fixture", "recovery/" + recovery_id, 0, 1))
    before = (directory / "ledger.sqlite").read_bytes()
    with Core(owner) as core:
        descriptor = next(h for h in core.workspace.list_homes() if h["store_instance_id"] == recovery_id)
        ctx = select(core, descriptor)
        assert call(core, "operation.get", {"context": ctx, "operation_id": old_receipt["operation_id"]})["result"]["receipt"] == old_receipt
        retry = dict(original, context=ctx)
        deny(call(core, "job.create", retry), "RECOVERY_INACTIVE")
        deny(call(core, "job.create", create(ctx, job=uid())), "RECOVERY_INACTIVE")
    assert (directory / "ledger.sqlite").read_bytes() == before


def test_killed_command_before_commit_leaves_no_partial_facts(owner):
    with HomeWorkspace(owner) as workspace:
        home = workspace.list_homes()[0]
    request = create({"home_id": home["home_id"]}, operation=uid())
    script = """import os,sqlite3,sys,json
from apps.edge.rpc import Core
real_connect=sqlite3.connect
class KillBeforeCommit(sqlite3.Connection):
    def commit(self): os._exit(82)
sqlite3.connect=lambda *a,**kw:real_connect(*a,factory=KillBeforeCommit,**kw)
request=json.loads(sys.argv[2])
with Core(sys.argv[1]) as core:
    home=core.workspace.list_homes()[0]
    context=core.application.dispatch('session.select_home',{'home_id':home['home_id'],'store_instance_id':home['store_instance_id']})
    request['context']=context
    frame={'jsonrpc':'2.0','id':sys.argv[3],'method':'job.create','params':request}
    core.raw_frame((json.dumps(frame)+'\\n').encode())
"""
    result = subprocess.run([sys.executable, "-c", script, str(owner), json.dumps(request), uid()],
                            env=dict(os.environ, PYTHONPATH=str(APP)), timeout=15)
    assert result.returncode == 82
    assert fact_counts(owner, home) == {"jobs": 0, "job_events": 0, "audit": 0, "operations": 0}
    with Core(owner) as core:
        request["context"] = select(core, home)
        deny(call(core, "operation.get", {"context": request["context"], "operation_id": request["cmd"]["operation_id"]}), "HOME_CONTEXT")
        assert call(core, "job.create", request)["result"]["state"] == "confirmed"


def test_decimal_integer_and_sibling_command_fields_are_rejected(owner):
    with Core(owner) as core:
        home = core.workspace.list_homes()[0]
        params = create(select(core, home))
        params["cmd"]["expected_revision"] = 0.0
        assert call(core, "job.create", params)["error"]["code"] == -32602
        params["cmd"]["expected_revision"] = 0
        params["cmd"]["command"] = "job.update"
        assert call(core, "job.create", params)["error"]["code"] == -32602
        assert fact_counts(owner, home)["operations"] == 0
