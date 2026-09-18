"""Ordinary commands, called exclusively on the selected store executor."""
from datetime import datetime, timezone
import hashlib
import json
import uuid

from packages.domain.errors import DomainError


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)


def fingerprint(cmd, store_instance_id):
    semantic = {key: cmd[key] for key in ("schema", "home_id", "command", "job_id",
                                          "job_scope_revision", "expected_revision", "payload")}
    semantic["store_instance_id"] = store_instance_id
    return hashlib.sha256(canonical(semantic).encode("utf-8")).hexdigest()


def execute_command(con, identity, cmd, principal):
    if identity.recovery or not identity.active:
        raise DomainError("RECOVERY_INACTIVE")
    if cmd["home_id"] != identity.home_id:
        raise DomainError("HOME_CONTEXT")
    op, digest = str(uuid.UUID(cmd["operation_id"])), fingerprint(cmd, identity.store_instance_id)
    con.execute("BEGIN IMMEDIATE")
    try:
        prior = con.execute("SELECT * FROM operations WHERE operation_id=?", (op,)).fetchone()
        if prior:
            if prior["fingerprint"] != digest:
                raise DomainError("OPERATION_ID_CONFLICT")
            con.rollback()
            return json.loads(prior["receipt_json"])
        if cmd["command"] != "job.create" or cmd["payload"]["capture_refs"]:
            raise NotImplementedError("This command branch is not implemented")
        now, job = datetime.now(timezone.utc).isoformat(), cmd["job_id"]
        existing = con.execute("SELECT 1 FROM jobs WHERE job_id=?", (job,)).fetchone()
        summary = None
        if not existing:
            summary = {"job_id": job, "title": cmd["payload"]["title"],
                       "scope_text": cmd["payload"]["scope_text"], "aggregate_revision": 1,
                       "scope_revision": 1, "tracks": {"field": "planned", "delivery": "not_prepared",
                       "billing": "not_prepared", "returns": "none", "exception": "none"}}
        receipt = {"schema": "receipt.v0.addendum-r4", "kind": "receipt", "operation_id": op,
                   "home_id": identity.home_id, "store_instance_id": identity.store_instance_id,
                   "fingerprint": digest, "updated_at": now, "command": cmd["command"],
                   "state": "failed" if existing else "confirmed", "result": summary,
                   "error": {"code": "STALE_JOB", "body": {}} if existing else None}
        seq = con.execute("INSERT INTO audit(operation_id,command,principal,at,data_json) VALUES(?,?,?,?,?)",
                          (op, cmd["command"], principal, now, canonical({"cmd": cmd, "state": receipt["state"]}))).lastrowid
        if summary:
            con.execute("INSERT INTO jobs VALUES(?,?,?)", (job, seq, canonical(summary)))
            con.execute("INSERT INTO job_events VALUES(?,?,?)", (seq, job, canonical(cmd["payload"])))
        con.execute("INSERT INTO operations VALUES(?,?,?)", (op, digest, canonical(receipt)))
        con.commit()
        return receipt
    except BaseException:
        con.rollback()
        raise


def operation_get(con, operation_id):
    row = con.execute("SELECT receipt_json FROM operations WHERE operation_id=?", (operation_id,)).fetchone()
    if row is None:
        raise DomainError("HOME_CONTEXT")
    return {"receipt": json.loads(row["receipt_json"]), "attach_attempt": None}


def jobs_page(con, high_water, last_key, limit):
    if high_water is None:
        high_water = con.execute("SELECT COALESCE(MAX(seq),0) FROM audit").fetchone()[0]
    rows = con.execute("SELECT created_seq, job_id, summary_json FROM jobs WHERE created_seq<=? AND (created_seq,job_id)>(?,?) ORDER BY created_seq,job_id LIMIT ?",
                       (high_water, *last_key, limit + 1)).fetchall()
    page = rows[:limit]
    last = (page[-1]["created_seq"], page[-1]["job_id"]) if page else last_key
    return [json.loads(row["summary_json"]) for row in page], high_water, last, len(rows) > limit
