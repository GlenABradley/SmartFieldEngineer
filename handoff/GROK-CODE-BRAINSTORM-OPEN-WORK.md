# Code brainstorm — remaining Slice 1 work

18 September 2026 · Grok · feed to Sol after credit reset · not a spec rewrite

Effective law: Spec 1.00 + H1–H5 + Addendum 1.00.2 (C1/C2 adopted, unimplemented).  
Code HEAD: `3c85b53`. Do not add RPC methods. Do not skip F1/F3 before transport.

This is how to write the code, not another product argument.

---

## 0. Order of commits (do not merge these)

| Commit | Name | Done when |
|---|---|---|
| S04.1 | Fix F1 + F3 + F4 | New tests green; 41 old foundation tests still green |
| S05 | Child + journal + testing driver | `test_two_home` collects; fails on serial, not ImportError |
| S06 | Serial vertical slice | two-Home seed/recall/pin assertions start passing or fail only on evidence/docs |
| S07 | Evidence two-phase | attach stage/publish + photo observe |
| S08 | Documents + interruption + office records | pin, hold, time/cost/stock/envelope |
| S09 | Backup API + inactive restore + 0.2.0 import | §18 demo minus Qt polish |
| S10 | Qt Today/Job/Capture shell | ugly-but-real screens on the real transport |

Grok Build later works the same list. Harmony = this order.

---

## S04.1 — three small fixes (write these first)

### F1. Failed select must reopen previous with its flags

Bug: `session.py` `_select` except-path calls `open_store(prev_home, prev_store)` writable.

```python
# packages/application/session.py  — keep flags beside context

self.context = {..., "session_generation": self.generation}
self._context_flags = {
    "readonly": descriptor["recovery"] or not descriptor["active"],
}

# on failure:
self.store = self.workspace.open_store(
    previous["home_id"],
    previous["store_instance_id"],
    readonly=self._previous_flags["readonly"],
)
```

Also stash `_previous_flags` before clearing. If previous was recovery, reopen readonly.

Test: labeled Backup API recovery fixture already in store tests → `select(A)`, `select(R)`, hold B lock, `select(B)` → `HOME_WRITER_EXISTS`, `core.context` still R, `job.list` on R works, `job.create` on R is `RECOVERY_INACTIVE`.

Keep existing “fresh generation on failed switch” test. Do not silently change that policy.

### F3. One queue in the process that owns SQLite

Today: Core executor → Application executor → Store executor. Close-from-worker deadlocks.

S04.1 minimum (before QProcess):

- Delete `Core._executor`. `raw_frame` calls `_frame` on the caller thread **or** one process-wide queue owned by Application.
- `StoreSession` keeps its one thread (connection affinity). That is the only nested pool allowed.
- `Core.close()`: set `_closed`, do not `submit` onto the same pool that is inside `_frame`. From outside: wait for in-flight frame, then `application.close()`.

```python
# apps/edge/rpc.py
def raw_frame(self, frame):
    if self._closed:
        raise StoreError("Core is closed")
    return self._frame(frame)   # child process is already single-threaded

def close(self):
    if self._closed:
        return
    self._closed = True
    self.application.close()
```

If tests use threads against one Core, serialize inside `Application.dispatch` only (keep that one executor). Do not add a fourth.

### F4. Create contract in `execute_command`

```python
if cmd["command"] == "job.create":
    if cmd["expected_revision"] != 0 or cmd["job_scope_revision"] is not None:
        raise NotImplementedError  # or durable SCHEMA — pick one and test
    if cmd["payload"]["capture_refs"]:
        raise NotImplementedError
```

Add a test that calls `store.submit_command` with `expected_revision=1` and does not create a job.

---

## S05 — transport (the planned block, sharpened)

### Process shape

```
Qt UI thread ──signals──► Transport (Qt thread)
                              │ QProcess
                              ▼
                    python -m apps.edge --owner-root R
                              │
                    stdin  newline JSON-RPC
                    stdout newline JSON-RPC
                    stderr diagnostics only
                              │
                    Core._frame → Application.dispatch → StoreSession thread
```

Child command:

```
python -m apps.edge serve --owner-root <abs> --transport qprocess
python -m apps.edge provision --owner-root <abs> --labels A,B --operation <uuid>
```

Maintenance: desktop kills/stops serve, runs provision as a separate process (or a `maintenance` method later — do not add RPC #21). After provision, start serve again. Old session_id is dead. That matches NEXT-CODE-BLOCK.

### Framing (child stdin)

State machine, no unbounded buffer:

```
buf = bytearray()
MAX = 1_048_576
while True:
    chunk = os.read(0, 4096)
    if not chunk:
        flush_and_exit()
    buf += chunk
    if len(buf) > MAX + 1:
        # emit one parse error with id null, then drop until next \n
        drop_until_newline_or_reset()
        continue
    while b"\n" in buf:
        line, buf = buf.split(b"\n", 1)
        write_stdout(core.raw_frame(line + b"\n"))
```

Coalesced two requests in one read: loop handles it. Fragmented request: wait. Frame without newline that exceeds MAX: parse error, resync on next newline. Never decode before newline.

stderr: `logging` to stderr, no paths from Home roots, no SQL, no serials.

### Qt client

Do not use `QProcess.waitForReadyRead` on the GUI thread in production code. Tests may spin `QEventLoop` with a timeout.

```python
class CoreProcess(QObject):
    responded = Signal(str, dict)   # request_id, message
    failed = Signal(str, str)       # request_id, reason
    child_died = Signal(int)

    def send(self, request: dict, context_snapshot: dict):
        rid = request["id"]
        self._pending[rid] = context_snapshot
        self._proc.write(json.dumps(request).encode() + b"\n")

    def _on_ready(self):
        self._buf += bytes(self._proc.readAllStandardOutput())
        # same newline split as child
        # if pending[rid].generation != current: discard (stale callback)
```

Stale: captured `session_generation` at send time ≠ current generation → drop response, do not apply to UI.

Restart: new process, `home.list`, `session.select_home` original working store (never recovery), then `operation.get` for open intents.

### Intent journal

Path: `{home}/client-intents/{operation_id}.json` then `fsync` file and directory (POSIX). Windows: flush + `FlushFileBuffers` later qualification.

```json
{
  "operation_id": "...",
  "home_id": "...",
  "store_instance_id": "...",
  "fingerprint": "...",
  "semantic_request": { "method": "job.create", "params": { } },
  "state": "pending"
}
```

Rules:

1. Write+fsync *then* `send`. If write fails, do not send.
2. On response confirmed/failed: rewrite state `acked` or delete.
3. On restart: for each pending file whose store is the **working** instance of that Home, `session.select_home` that store, `operation.get`.
   - receipt exists → ack, do not resend
   - `HOME_CONTEXT` (unknown) → resend **same** UUID and payload
   - store is recovery → leave file, do not send
4. Keep all pending files. Do not use `system.status` last-50 as the journal.

>50 intents test: write 60 pending files after 60 confirmed creates with lost responses; restart; 60 receipts, 60 jobs.

### `packages.application.testing`

Source only. `pyproject` package-dir exclude.

```python
@contextmanager
def launch(owner_root, transport="qprocess"):
    if transport == "in_process_dev":
        with Core(owner_root) as core:
            yield Driver(core)
    elif transport == "qprocess":
        proc = start_module_child(owner_root)
        yield Driver(proc)
```

`Driver.raw_frame` must send bytes through the same codec path.  
`Driver.maintenance(["provision", ...])` runs the serve-stop + provision entry.

Wheel test: `python -c "import packages.application.testing"` fails against installed wheel.

### S05 tests (minimum)

- fragment / coalesced / oversized / EOF
- child kill mid-command; restart; one job
- journal write failure → no send
- stale generation callback dropped
- in_process vs qprocess receipt equality for create/list/get/deny
- unmodified `tests/contract/test_two_home.py` collects, fails on `serial.observe` (or whatever first missing method)

---

## S06 — serial slice (after S05 is honest)

Implement four commands + recall query. Same transaction style as `job.create`.

Tables (migration `003_identity.sql`):

```
observations(observation_id PK, raw, normalized, kind, evidence_json, source_json, at, principal)
assignments(observation_id PK, job_id, asset_id, revision)
assets(asset_id PK, created_seq)
binds(bind_id PK, observation_id, job_id, asset_id, revision, predecessor,
      normalized, verification_json, at, principal)
disputes(dispute_id PK, bind_id, asset_id, job_id, bind_revision, reason, at, principal)
asset_head(home implicit, asset_id PK, bind_id, revision, disputed INT)
```

Head key is per store (one Home per ledger), so `asset_id` PK is enough **inside one store**. Same asset UUID in Home B is a different ledger. That is the two-Home trick.

Flow:

1. `serial.observe` — append observation. `expected_revision` null. Photo requires evidence_ids that exist — **if evidence not built yet**, only allow `typed` / `imported_text` with empty evidence in S06, and let two-Home photo path fail until S07. Better: S06 typed only; test_two_home uses typed first if we must; **do not change the supplied test**. The supplied test observes with `evidence_ids: []` and `method: manual_label_read`. That is typed. Photo-without-evidence reject later.

Look at seed() in test_two_home: evidence_ids []. So S06 typed observe works.

2. `serial.assign` — expected 0, once, creates asset row if needed.
3. `serial.verify` — expected bind head 0→1. Observation not reused.
4. `serial.recall` — query. Undisputed head + assignment on this job → serial string. Else unresolved `{serial: null, status: "unresolved"}`.
5. `serial.dispute` — mark head disputed, bind row immutable.

Fingerprint: reuse `commands.fingerprint`. Replay before branch.

`document.prepare` is **not** S06 unless the two-Home test requires pin. It does (`document.prepare` + read_handle). So either:

- S06 ends with recall only, two-Home still fails at document.prepare, or
- S06 includes a stub document.prepare that pins current bind and writes a local HTML file + digest + read_handle.

Prefer tiny document.prepare in S06 so the two-Home happy path can reach restore and then fail there. Restore is S09. Sequence of failures in the unmodified test is progress.

Minimal `document.prepare`:

- require current verified bind for each asset_id
- write `read-cache/<token>/doc.html` escaped body, no network
- pin `{bind_id, revision, serial}`
- read_handle 120s, session-bound

`app.open_read_handle` in the test driver: core copies blob to a temp readable file or returns bytes + sha256. Implement real consumer, no fake digest.

---

## S07 — evidence two-phase

Migration `004_evidence.sql`: `evidence(evidence_id, job_id null, blob_key, sha256, length, ...)`, `attach_attempts(...)`.

`evidence.attach` phases as spec 1.00. Same operation_id. Token in `staging/<token>/original`. Publish: hash, move to `blobs/sha256/<digest>`, metadata in same TX as receipt.

Foreign Home token → `HOME_CONTEXT`, **do not consume B’s token**.

Then photo observe: require those evidence ids.

---

## S08 — office + interruption + envelope

`record.add` discriminated payload. Integer cents, USD, item_upsert + stock_move.

`job.update` scope/track. C2: in the scope TX, copy linkage `effective_scope_revision = new_scope` for every unresolved hold. Resume = C1 track_event to ready/in_progress with interruption_id + source.

`interruption.record` with structured `source_reference`. `secured_on_hold` = stabilization_done and (evidence_ids or source_reference). No `SOURCED:` prefix.

`envelope.put` + `job.get` view `envelopes` including Home-level (`job_id` null).

`job.get` views one enum. Implement the views the two-Home test calls.

---

## S09 — backup / restore / import

`backup.create`: pause writer queue, `sqlite3.Connection.backup()` into a new file in `backups/home-<id>/`, copy referenced blobs from snapshot inventory, manifest, receipt.

`backup.restore`: new directory `recovery/<store_instance_id>`, same `home_id`, insert index row active=0 recovery=1. Never write into live home-*.

Import: read-only 0.2.0 snapshot, `legacy-source-manifest.v1` digest, `IMPORT_ALREADY_APPLIED` on same digest.

Do not implement activation cutover beyond maintenance flag flip with writer stopped.

---

## S10 — Qt shell

Screens: Today, Job, Capture, Exceptions. Every enabled button = one of the 20 methods. Home switch combo. No call/marketplace widgets.

Reuse S05 Transport. Intent journal already exists.

Ugly is allowed. Do not start a design system.

---

## Shared implementation recipes (copy these)

### Transaction template (already good in commands.py)

```
BEGIN IMMEDIATE
prior = SELECT operations
if prior: rollback; return prior receipt if fingerprint match else CONFLICT
... mutate ...
INSERT audit, facts, operations
COMMIT
except: ROLLBACK; raise
```

Lost commit-ack: commit succeeded, exception after → next replay or `operation.get` finds the row. Keep that test.

### Context check order

1. codec schema
2. session context equality (normalized UUID strings)
3. store identity / recovery flag
4. fingerprint replay
5. branch business rules

Never skip to 5 from a helper that opens SQLite directly.

### Error mapping

```
DomainError.code → RPC -32000 message=code data={}
ProtocolError → json-rpc numeric
StoreError / NotImplementedError / Exception → -32603 Internal error
```

Expand `DomainError` allowlist when you first return `STALE_BIND` etc. as RPC denials rather than failed receipts. Failed receipts stay for accepted-but-rejected business (duplicate job). Authorization denials stay DomainError with empty body.

### UUID normalize once

`str(uuid.UUID(x))` at session boundary. Fingerprints see canonical lowercase. Tests already send uppercase on replay.

---

## What not to invent when credits return

- Method 21
- `STALE_ENVELOPE`
- In-process as the installer default
- Hub, voice, Ollama button
- Fake `packages.application.testing` that returns fixtures
- Implementing C1/C2 inside S05
- Changing `test_two_home.py` to make it pass early

---

## Grok Build later

When Build opens, point it at this file + Spec 1.00 + 1.00.1 + 1.00.2 + `fullkit/docs/STORE-FOUNDATION.md`. First prompt: “Implement S04.1 only.” Second: “Implement S05 as specified in this brainstorm and NEXT-CODE-BLOCK.md.” Do not let Build start at Qt.
)
