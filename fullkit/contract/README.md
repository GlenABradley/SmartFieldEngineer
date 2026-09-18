# Full Kit Composed Slice 1 — coding-agent entry and implementation contract 1.00.1

This package is an implementation handoff, not a running application. Implement the Python services, SQLite/blob adapters, out-of-process core and PySide6 desktop described here. First run the package’s structural checks. Then make its asserting application tests pass against real persistence and transport. Never substitute a fake driver or report schema checks as an application demonstration.

## Authority, review status and reading order

1. `reference/Full-Kit-Slice-1-Build-Spec-100.md` is the preserved effective specification.
2. `Addendum-1.00.1.md` contains Glen’s five adopted overrides, H1–H5.
3. This entry document resolves routine implementation choices; `schemas/contract.json` is its generated structural representation. `schemas/methods.json` maps the twenty methods to request/result/response definitions. Apply semantic checks below in addition to JSON Schema.
4. `reference/Spec-100-Delta-and-Adjudication.md` explains decisions without overriding them. `reference/legacy-fieldoffice-0.2.0.py.txt` is import-source evidence only. Do not use earlier schema drafts or the old application as a wire contract.

Conversation retrieval reached the recent Spec 0.99/1.00 discussion in **Build Copilot operations system**, including the adjudication, and recent **Ultimate Field Laptop Strategy** context. It did not establish complete access to every originating turn. The supplied authoritative files govern. Quoted reviewer recommendations have no authority beyond Glen’s adopted direction. No messages were sent to reviewers and no new tasks were started.

**C1 — Owner decision, proposed for adjudication separately from H1–H5:** §6 requires “interruption_id + owner decision + reason + source” on resume, but the closed track-event payload has no owner-decision field. Smallest proposed correction: the explicit owner-submitted `track_event` to `ready` or `in_progress`, stamped with the Windows principal, is the owner decision; require its reason, current interruption ID, and structured source_reference or relevant evidence. The UI labels it “Resume — owner decision.” Do not add a field or method. This package implements that exact proposed interpretation in its acceptance contract, not a claim of previously obtained consensus. Glen/Claude can accept or replace this narrowly before release; other implementation can proceed now. No unresolved payload design is delegated to an implementer.

**C2 — Scope advancement and holds, also proposed:** §6 requires a current-scope interruption before scope change and before resume, while §5.2 increments the scope on change. Without a transition rule, the required hold becomes stale and unresolved older holds can prevent completion indefinitely. Smallest correction: in the scope-change transaction append an effective-scope linkage for every unresolved hold on that job from the old current scope to the new one. Preserve each original interruption and its recorded scope. Resume checks the latest linkage, resolves only the named hold, and never revives a resolved hold. Add `effective_scope_revision` to interruption read projections. No new RPC, payload discriminator or domain code. This is a concrete review proposal, not an adopted sixth harmony patch.

The attach-specific intent/phase fingerprint rule is more specific than the general fingerprint rule, rather than a new correction: phase transitions must not conflict merely because stage differs from publish. Archive tokens and read-cache routing are concrete capability encodings selected below, not new RPC verbs.

## Scope, repository and construction order

One trusted Windows owner, one laptop, two business Homes. This context fence prevents accidental cross-business reads/writes, pins, exports and stale UI. It is not sponsor IAM, second-human authentication, or hostile-admin defense. No hub, OIDC, cloud inference, telephony, connectors, OCR/ASR, platform writes, guided installation, robots, payment automation or hidden adapters. Voice-transcript identity input means already supplied text; it does not enable ASR. “Phone-ready” needs later qualification.

Create a new `fullkit/` implementation repository beside this package; never modify `reference/`, the reviewed sandbox originals, synced `sources/`, or 0.2.0. Copy this package into `fullkit/contract/` and tests into `fullkit/tests/contract/`. Repository boundaries:

| Directory | Responsibility and prohibited dependency |
|---|---|
| packages/domain | Pure validation, identity, office and interruption rules; no Qt, SQL, filesystem or network |
| packages/application | Context authorization, execute_command, reads, maintenance, writer queue, transactions, receipts; inject adapters |
| adapters/sqlite | Migrations, repositories, Backup API snapshot; only application owns writable connections |
| adapters/fs_blobs | Home-local staging, publication, read cache, retention, inventory |
| apps/edge | Core entry, JSON frame codec, dispatch, Windows principal and OS lock |
| apps/desktop | PySide6 views, QProcess client, semantic intent journal and read-handle consumer; no SQL writes |
| migrations/local | Forward-only numbered SQL, schema version and migration receipt through maintenance |
| tests | Real integration, fault injection, Windows qualification; production code has no success stubs |
| docs | This contract and implementation Validation.md |

Order: schemas/specimens → two-Home test → store identity/lock/context/command/receipt → transport spike → evidence/serial/pins → office/interruption → backup/import → desktop → clean Windows commissioning. Qt must not mask a failing raw RPC boundary. Two-day transport spike compares identical tests; production remains QProcess unless the specification is explicitly revised. Skeletons do not satisfy completion.

## Dependencies and commands

Selected application baseline: CPython **3.13.15**, regular x64 build; PySide6 **6.11.2**; jsonschema **4.26.0**; tzdata **2026.4**. Validation uses pytest **9.0.2**; wheel build uses build **1.4.0** with setuptools **84.0.0**. Publisher metadata and wheel hashes are in `reference/dependency-verification.json`; resolved platform locks are supporting files. These are verified available versions, not certification of an installed Windows runtime. Python’s version does not establish SQLite’s version. Inspect `sqlite3.sqlite_version` and `SELECT sqlite_source_id()` on the actual target, and run the backup/WAL tests. Reject known unpatched WAL-reset releases, including withdrawn 3.52.0. Qualify a maintained patched SQLite build, at least 3.51.3 on that branch or 3.53.0+ on the later branch; record the actual DLL hash. Run `python tools/runtime_check.py` to record runtime observations; non-Windows or missing/mismatched dependencies returns nonzero rather than claiming commissioning. Do not blindly replace a DLL with an ABI-incompatible build.

Sources: [Python 3.13.15](https://www.python.org/downloads/release/python-31315/), [PySide6 6.11.2](https://pypi.org/project/PySide6/6.11.2/), [jsonschema](https://pypi.org/project/jsonschema/4.26.0/), [SQLite changes](https://www.sqlite.org/changes.html). PySide6 metadata declares LGPL/GPL alternatives; retain license notices and dynamic library replaceability, and perform the distribution license review before shipping. Availability verification is not a security audit or legal approval. No paid subscription is required by this slice.

From this artifact directory, in PowerShell (macOS/Linux may substitute the corresponding venv Python path):

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\python -m pip install -r requirements-validation.txt
.\.venv\Scripts\python tools/generate_contract.py
.\.venv\Scripts\python tools/generate_examples.py
.\.venv\Scripts\python tools/validate_contract.py
.\.venv\Scripts\python -m pytest tests/test_inventory.py -q
.\.venv\Scripts\python -m pytest tests/test_two_home.py -q
```

The last command must currently fail with missing application imports. That is deliberate visibility of absent implementation, not an expected passing release test. Run it from the implementation root after installing the real application. Use the supplied resolved locks for reproducible dependency restoration; direct requirements show the deliberate top-level choices. Re-resolve on a platform/dependency change and retain the report/hashes. Do not execute network dependency resolution during the offline demo.

The implementation must expose these commands; they are targets to implement, not commands that this artifact claims already exist:

```powershell
python -m pip install -r contract/requirements-application.txt -r contract/requirements-build.txt
python -m pip install -e .
python -m apps.edge --maintenance provision --owner-root "$env:LOCALAPPDATA\FullKit\owner" --label "Home A" --label "Home B"
python -m apps.desktop --owner-root "$env:LOCALAPPDATA\FullKit\owner"
python -m apps.edge --maintenance import --owner-root "$env:LOCALAPPDATA\FullKit\owner" --home HOME_UUID --store STORE_UUID --source LEGACY_ROOT --plan reviewed-import-plan.json
python -m pytest tests -q
python -m build --wheel --no-isolation
```

Use `pyproject-template.toml` as the implementation repository’s initial pyproject.toml. Add actual package resources, not placeholder modules. A production wheel contains packages, migrations, local templates, schema resources and notices. Desktop starts exactly one QProcess core using the installed interpreter/module; stdout is protocol only. No source-tree path assumptions. Installer establishes a per-user venv/application wheel and Start menu shortcut; upgrading does not wipe owner data. No packaging server or extra service. Build and target installation commands must be exercised on clean Windows before release.

## Wire and authorization

Exactly twenty methods are in `schemas/methods.json`. Requests are JSON-RPC 2.0 objects with UUID request id, method, params. All scoped calls carry `params.context`; mutations additionally carry `params.cmd`. Method must equal cmd.command; context Home must equal cmd.home_id. Reject notifications for state-changing calls: request IDs are mandatory. UTF-8 newline frames, maximum 1,048,576 bytes including newline, reject duplicate JSON keys and NaN/Infinity, no logs on stdout. Responses echo request ID, never command operation ID by substitution.

Check frame/JSON validity, known method and structural shape, then context before looking up any business IDs, tokens, receipts or paths. Validate scoped references inside the selected store only. Never search peers for existence. Standard protocol errors use their standard numeric codes; domain denials use `error={code:-32000,message:DOMAIN_CODE,data:{}}`. Use the exact closed vocabulary in the schema. Unknown and foreign operations are indistinguishable `HOME_CONTEXT`. Internal I/O faults use -32603 with `Internal error`, no raw exception or path. Domain failed receipts have code plus empty body. Safe diagnostics go to owner-protected logs and must not enumerate foreign dossiers.

Core issues session UUID at start; successful selects increment generation even when selecting the same Home. Select recovery read-only. On switch, finish committed publication/receipt work, persist client intents, drop outstanding stage/read tokens, close old store, acquire target, then publish the new context atomically. Failure retains previous valid context with a fresh defined generation if reopened, or none; UI must clear and disable scoped actions in the latter case. Clear cached rows, previews, selection and pending callbacks before displaying new Home; discard responses whose captured context differs. In-process tests run these identical application checks.

The OS exclusive lock handle owns a writer, not a PID file. Open `home.lock` with no sharing; retain handle until close. Establish volume serial + file ID and final path from that handle, check approved local root and reject unsupported/network filesystems. Windows junction/subst/8.3/case aliases must reach the same underlying lock exclusion. Never delete the lock file or steal it based on a stale PID. Open SQLite only after locking; WAL, synchronous FULL, foreign keys on every connection. Read-only recovery uses read-only DB connection and never replays queued operations. Maintenance uses the same lock/execute_command boundary and cannot race a GUI writer.

## Command revisions, durable receipts and crash recovery

Every ordinary mutation is `execute_command(context, cmd)` on the single queue. SQL fact changes, aggregate/head changes, audit event and terminal durable receipt share a transaction. Ordinary mutation RPC handlers return after terminal commit/failure; desktop transport is asynchronous so this does not block the UI event loop. Attach stage is the documented executing-result exception. Queued/executing receipts may be committed first; neither confirms a business result. Once structurally accepted and authorized, a business-rule rejection becomes a durable failed receipt returned as the method result (wrapped in operation for attach). Context/capability denial, inactive recovery, malformed input and operation-ID conflicts return the top-level domain error; they do not replace an existing receipt. Replaying an authorized failed semantic request returns its existing failed receipt. Context errors and malformed envelopes do not write receipts to any Home. Unexpected failures never fabricate confirmed receipts.

| Command | Revision and scope behavior |
|---|---|
| job.create | Caller chooses absent job UUID; expected 0; submitted scope null; aggregate/scope both 1. Existing job with a new operation → STALE_JOB |
| job.update scope | Expected current aggregate + current submitted scope; increment both; check live interruption if field in_progress/blocked |
| job.update track_event | Expected aggregate/current scope; increment aggregate only; valid track/state pair and sourcing/resume gates |
| record.add / evidence.attach / serial.observe | Expected null. Inbox scope null; job-tagged submitted scope positive, may be stale. Preserve submitted and current scopes |
| serial.assign | Expected 0; observation previously unassigned; current job scope; assignment revision 1; create asset UUID transactionally |
| serial.verify | Expected bind head 0 or current positive; drift allowed; preserve both scopes; correction adds immutable rev+1 |
| serial.dispute | Expected positive head revision + payload bind_id must name active head. Set head disputed, append conflict, do not increment numeric revision. Second dispute → STALE_BIND |
| document.prepare | Expected current job aggregate/current scope; pin in same transaction; do not increment job aggregate |
| interruption.record | Expected null; record current job scope even if submitted stale; no work authority granted |
| envelope.put | Expected 0 or current envelope revision; scope null; job optional; stale → STALE_RESERVATION; update head increments only envelope revision |
| backup.create / restore | Expected null; job and scope null; normal inactive recovery mutation denied |

General fingerprint is SHA-256 of canonical UTF-8 JSON object containing schema, Home, store_instance_id, command, job_id, submitted scope, expected_revision and payload. Canonical encoding uses sorted keys, compact separators, ensure_ascii=False, allow_nan=False; no Unicode normalization or float rewriting. Contract payload numbers are integers. Context session/generation and request ID are excluded so a persisted semantic intent can be re-enveloped in a new session. Same operation UUID + same fingerprint returns the durable prior receipt before reevaluating mutable state; differing fingerprint → OPERATION_ID_CONFLICT. Scope/expected revision remain original on retry.

Before sending any mutation, desktop writes operation UUID, fingerprint, home, store and full semantic request to `client-intents/`, flushes/fsyncs and atomically publishes journal entry. Failure prevents sending. On restart, select original Home/store and query each open operation, including those beyond last 50. Known receipt reconciles journal. Unknown HOME_CONTEXT with positively selected matching Home/store permits same semantic request to be resubmitted under same operation UUID; it is not evidence of failure. Never redirect an intent to a restored store. UI marks unacknowledged results unknown until lookup; core never invents a durable unknown terminal result. No external actions are replayed.

Recovery copies retain historic receipts, including original store IDs and fingerprints; these are history, not authority to resend. `operation.get` may show imported historical receipts from that Home but appends no mutation. Inactive write guard precedes command replay, so even an old confirmed mutation sent as a command is denied. Activation requires explicit maintenance designation after stopping the live writer; never activate two working instances for one Home.

## Facts, payload semantics and projections

All fields are explicit in `schemas/contract.json`; unknown siblings and properties reject. Text with a nonempty requirement must contain non-whitespace; raw identity remains byte-for-byte text as supplied. UUID checking validates syntax; equality is canonical lowercase UUID text after schema validation. Time values must include offsets; compare UTC instants. Site timezone must resolve through ZoneInfo with bundled tzdata. Declared source references carry claimed source, kind, nonempty reference and offset-aware observed_at; principal is independently core-stamped Windows SID.

Observation methods accept manual label, manually supplied photo transcription, barcode text, inventory-output text and already supplied voice transcript text. No automatic extraction. Photo requires at least one existing Home-local relevant evidence ID. Assigned observations must match the job; inbox evidence can be linked only through explicit allocation. Null raw may be stored, never verified. Assignment is once; assignment/verification reference an observation in the selected Home only. Bind head key is (home_id,asset_id), observation verifies once. trim_only.v0 strips surrounding whitespace only; no case-folding, punctuation stripping or fuzzy merge. Replacement hardware gets a new asset UUID. Current recall requires job association, serial-kind bind and undisputed active head; otherwise status unresolved, serial null. Historical revision lookup may disclose an old bind only through the same authorized job association; it never authorizes a new pin.

Documents use local escaped templates and immutable HTML bytes with embedded print CSS; the offline print form is that same artifact rendered by Qt text/print support. Store serial snapshots, revision, bind IDs, job scope and digest. Later correction/dispute never rewrites a document. Disable link navigation and override resource loading to reject HTTP, file URLs and arbitrary local paths; no WebEngine/CDN needed. `body_text` is text, not executable markup.

The observations collection paginates identity facts (observation, assignment, bind, dispute) as separate immutable rows, giving the UI assignment IDs and correction/dispute history without unbounded nested arrays. Null-job observations contain only still-unassigned observations. Job-tagged identity facts retain their originating job; asset-wide head and authorized historic revisions remain available through serial.recall.

Each `job.get` returns `{view,job_id,data}`; summary data is one summary, collections data is `{items,next_cursor}`. Null job permits inbox records/observations/evidence and H2 Home envelopes only; summary/documents/interruptions → INBOX_VIEW. UUID job returns only matching rows. Empty collections are [], no existence hints. `job.list` returns summaries. No blob or HTML inline. Evidence/document rows may include read_handle; omit on integrity finding rather than publish broken bytes. Current implementation should mint handles for available originals/documents to support preview.

Pagination is keyset over monotonically assigned store-local event sequence + object UUID, ascending. First page captures a high-water sequence; opaque random cursor stores context, view, job, high-water and last key in the core. TTL 120 seconds, generation-bound, max 100 items. Reusing a foreign/stale cursor → HOME_CONTEXT. New rows after high-water wait for refresh; updates are current projections of included object IDs (not a claimed historical snapshot). summary requires cursor null; limit remains syntactically 1–100. Core expires unused cursor state.

Read handle has opaque token, Home/store/session/generation, expiry, media type and digest. Core publishes bytes to `read-cache/<token>/original`, immutable while authorized. Desktop knows selected root from private launch configuration, not from a public Home listing. Its private `open_read_handle` adapter checks context/expiry and root/file identity, opens only that token’s published file, verifies digest, and refuses arbitrary paths; this is a local file consumer, not a 21st RPC. Generation changes clear the registry/cache and close previews. Trusted-owner scope acknowledges direct local filesystem access is not hostile-user isolation. Paths are allowed only in the private stage grant needed to write bytes; never in status/list/read projections/documents.

Time: minutes positive integer; both endpoints null or both offset timestamps with ended_at > started_at. Minutes represent recorded effort and need not equal elapsed minutes; never derive missing endpoints. Cost: nonnegative cents USD; no processor/payment claim. Item: Home-unique exact sku, existing item ID updates descriptive fields; append sourced event, no identity merge. Stock: receive/consume positive quantity, adjust nonzero signed; item must exist; final usable stock at location must be nonnegative. Receive must contain unit_cost_cents: nonnegative integer, or explicit null meaning unresolved cost. Null is not zero. A consumed movement does not automatically add a separate cost record; reports must not double count movements and explicit costs. Item/stock records are Home-owned even when job-tagged; no parts reservations.

Capture_refs are typed record/evidence IDs. Allocate inbox rows once to the target job without re-inserting economics. Already this same job is a no-op within the command; another job → CAPTURE_ALREADY_ALLOCATED. Observations are never capture_refs. An operation consumes/allocates everything atomically or nothing.

Track state enums are stored exactly as listed; no paid/delivered aliases. issued_recorded, settled_recorded, accepted, delivery_recorded require source_reference or relevant evidence IDs. UI labels all such transitions sourced/manual. Scope changes during in_progress/blocked require this Home/job’s unresolved interruption at current scope. Missing → FIELD_TRACK_ACTIVE; inaccessible/wrong-job → INTERRUPTION_FOREIGN without foreign details; resolved/old-scope → INTERRUPTION_STALE. Under proposed C2, carry every unresolved hold from the prior current scope forward via separate appended linkage events in the same transaction, preserving original scope history; each can then support an explicit named resume. New interruption facts never erase prior holds.

C1 resume rule: when one or more unresolved holds exist, a field transition to ready/in_progress must name a current hold, reason and source. Append resolution event for that hold only; other holds remain open and block completed with SCHEMA. Initial ready/in_progress with no holds is an ordinary sourced track event, not a fictional resume. `secured_on_hold` requires stabilization_done true plus valid relevant evidence or structured source_reference. Operator attestation is permitted claimed assertion; it is never instrument proof or proof of physical safety. “SOURCED:” text has no special authority.

Envelopes compare start/end as instants; end > start. Components are nonnegative integer minutes, independently recorded planning components; interval duration is authoritative for overlap, no invented travel/routing estimate. Hard conflict iff another hard envelope has any exact tag in common and start < other.end AND other.start < end, excluding the head being updated. Conflict uses SCHEMA (declared-input validation); only moved revision uses STALE_RESERVATION. Soft overlaps are allowed. No resource registry or stock hold is created.

## Evidence attach state machine and recovery

One operation UUID identifies the logical attachment. Intent fingerprint contains Home/store/command/job/submitted scope/expected null and metadata (original name, media type, classification, declared_length, declared_sha256); it excludes phase/token/attempt. Phase fingerprint hashes the entire phase payload, with attempt, metadata and token included. Persist each phase result by (operation,attempt,phase). Same phase payload replays exact prior attempt result, even if its token has since expired; a replayed expired stage grant cannot publish and client must request next attempt. Different phase payload under same key → OPERATION_ID_CONFLICT. Different metadata under the operation also conflicts.

| From | Request | Durable outcome |
|---|---|---|
| Absent | stage attempt 1 | executing receipt + attempt staged; grant token/path, expires 3600s |
| Staged live N | identical stage N | prior grant, no new token |
| Staged live N | publish N with authorized token | validate and consume token; either published + confirmed evidence, or failed attempt |
| Failed/expired N | stage N+1 | new session-bound token; retain all failed attempts; logical receipt executing |
| Staged live N | stage N+1 | SCHEMA; do not bypass live attempt |
| Confirmed | identical stored phase | stored phase result; operation.get shows confirmed final receipt |
| Confirmed | new attempt or changed phase | OPERATION_ID_CONFLICT; no second evidence identity |
| Any | foreign context/token | HOME_CONTEXT; do not consume another context’s token |

Only sequential attempts, starting at 1. A core restart expires unfinished tokens; persist attempt expiration reconciliation, do not reuse paths. Pending staged receipt is executing, not a confirmation that evidence exists. Failed attempt may yield failed logical receipt but next sequential stage can resume this special multi-phase command. Generic terminal failed commands cannot change payload under same operation ID.

Publication: authorize first → verify staged file handle/root/no symlink or reparse escape → size bounds 1..52,428,800 → SHA-256 → exact declared length/digest and media validation → flush/fsync → same-volume atomic move to digest blob → SQL evidence/audit/confirmed receipt transaction. Text/plain requires valid UTF-8, JPEG/PNG/PDF require valid signatures and decoder/parser checks before preview; other media stored as application/octet-stream with no active rendering. In all cases data are evidence, never executable. If digest already exists verify existing bytes before deduplication. No cross-Home blob sharing. Validation failure consumes only an authorized token; foreign denial does not. Staging path never makes evidence available.

Metadata commit failure leaves an orphan blob; startup reconciles abandoned staging, token state, missing referenced originals and unreferenced published blobs. 24-hour grace before collecting unreferenced blobs; retain any committed or backup-held reference. Use persistent backup retention entries so process crash cannot forget protected blobs. Missing original is an integrity finding with checked_at; do not manufacture a replacement or return available evidence. Stage-byte and receipt fault tests are mandatory.

## Backup, inactive restore and importer

Backup destination null selects provisioned sibling `backups/<home>/`; it is convenience storage, not off-machine protection. Non-null destination is a capability registered by explicit maintenance commissioning against a directory handle/identity and bound to Home/store. Archive capabilities are durable Home/store-scoped IDs, unlike session stage/read tokens. They resolve only in private catalogues, never from user path interpolation. Restoring with a foreign archive token is HOME_CONTEXT. Destination null allocates a unique directory under `recovery/`; non-null capability must designate an empty, nonexisting instance destination under an approved recovery root.

Pause queue at completed transaction boundary, hold blob retention barrier, use SQLite Connection.backup to standalone DB, derive referenced blobs from completed snapshot, copy/rehash, integrity_check, foreign_key_check and reference validation, then manifest and atomic archive publication. Backup manifest records schema/version, Home/source store, snapshot digest, blob digests/lengths and archive ID; excludes staging/cache/locks/client secrets. A source receipt confirms only after verified publication. Snapshot need not include its own subsequent backup receipt. `finally` releases both barriers. No raw live-main-file copy and no checkpoint-only backup claim.

Restore verifies all manifest entries, denies traversal/absolute archive paths and symlinks, unpacks only into a new instance. Same Home, newly allocated store UUID, inactive marker. Keep source business/evidence content and old history intact; source restore audit/receipt may append. Register recovery only after full verification. A crash before registration leaves an unregistered recovery directory for maintenance cleanup, never an active writer. When switching away from B may checkpoint its WAL, take B-byte baseline only after B closes; compare exactly around the restore, not across an unrelated selection/checkpoint.

Activation: stop desktop/core, inspect pending intents and queued historical ops, explicitly choose Home + recovery store through `--maintenance activate`; acquire old/new instance locks in sorted identity order, atomically update private index so only selected store is working, retain old one inactive. Never auto-replay restored queued rows. Resume ordinary mutations only after new session select. Restore-over-live/existing is declared-input SCHEMA rejection. No normal mutating RPC on recovery, including backup/create or replay, bypasses RECOVERY_INACTIVE.

### Actual 0.2.0 mapping

Inspected source: `reference/legacy-fieldoffice-0.2.0.py.txt`, SHA-256 in provenance. Its constructor defines **14** tables; extracted SQL is `reference/legacy-ddl.sql`. Do not run that constructor on customer data. No actual populated `office.sqlite` was supplied in this artifact’s inspected kit. Customer corpus and referenced files are essential for the eventual import demonstration, not for schema/implementation work. The executable inventory helper is useful now; its tests use explicitly synthetic DDL fixtures and do not claim a real customer import.

Close legacy app. For this handoff, accept a clean closed `office.sqlite` without a nonempty WAL/journal; open URI mode=ro&immutable=1 and query_only. If sidecars contain data, stop and have the legacy owner close/checkpoint normally before taking the closed source copy; do not checkpoint or upgrade the source in the importer. This is a bounded consistent read-only snapshot route. Inventory helper hashes database before/after, checks integrity/references, reads present tables, tags SQLite value types, and hashes referenced bytes. Zero/oversize or unsupported legacy evidence is a pre-insertion migration finding requiring explicit retained-source disposition, never silently dropped.

Canonical digest is SHA-256 of `legacy-source-manifest.v1`: source application/version and ledger_id, table columns + actual rows sorted by typed primary-key encoding, referenced evidence ID/digest/length. No source path, export time or ephemeral sidecar bytes. Integer values encode decimal text, real values encode float.hex, blobs base64, text unchanged, null explicitly typed. Missing optional tables are absent, not synthesized; missing referenced evidence always fails. Unknown tables with stable keys are inventoried and retained as sourced archival records; unknown tables without stable keys stop for reviewed key plan. Required identity tables are office_meta and jobs. Every present referenced relation must reconcile before insertion.

| Actual table/columns | Target mapping (maintenance only) |
|---|---|
| office_meta(key,value) | ledger_id establishes source namespace; retain all extra metadata in batch report |
| jobs(id,data,version) | UUID5 job; data.scope → scope_text, data.client plus legacy id → title. Start target aggregate/scope at 1; retain legacy version/full JSON as archival source, never assert it equals new scope generation. No live field track imported automatically |
| records(id,job,kind,data,created) | Valid positive time → time with both endpoints null unless both explicit/valid; minutes preserved. Nonnegative USD cost with amount_cents → cost, preserve category or `legacy unspecified`. Everything else, including payment/actions semantics, → sourced note with full original JSON; never convert a payment to processor success. Each source key one fact, no duplicate economics |
| evidence(id,job,hash,name,data) | Verify blobs/<hash>; stage into target sha256 tree; classify data.visibility internal/customer; retain target/purpose/source/imported_at as sourced archival metadata, never infer capture time. Derive media type by bytes, default octet-stream. ID map references same imported evidence |
| serial_observations(id,data,created) | New observation from raw/kind/method/observed_at/manufacturer/model; evidence_id mapped. captured_by/source become `legacy-claimed:<original text>` strings. No ASR/OCR. Preserve entire source JSON/hash |
| serial_assignments(observation,job,asset) | Map observation/job/asset keys; one assignment at rev1; cross-check any duplicate inline job_id/asset_id agrees, otherwise conflict |
| asset_heads(asset,revision,state) | Reconcile complete immutable binding chain and active/disputed state. Never invent a missing bind or erase dispute |
| asset_bindings(id,asset,revision,observation,data) | Preserve revision chain, observation link, raw/normalized, supersedes and reason; verify normalization and source consistency. verification names/source remain `legacy-claimed:<original text>`; imported fact principal is importer Windows owner with source provenance, not claimed legacy verifier authentication |
| asset_jobs(asset,job) | Map authorized historical job associations only after referenced jobs/assets/binds exist |
| reservations(job,start,end,state,review) | Retain as sourced archival note by default: actual rows lack resource tags, timezone and full components. Reviewed plan may explicitly supply these per source job to create envelope with original start/end/state. Never fabricate component minutes or infer a timezone/resource owner |
| stock(sku,location,qty,unit_cents) | Opening balance only: reviewed per-sku unit_name/display_name plan creates item and one opening adjust per location; preserve unit_cents as source valuation. Do not replay historical stock movements inferred from audit. Zero opening quantity creates no movement; negative quantity is a migration conflict. Existing legacy cost records already represent consumed costs. Missing unit plan is a migration plan finding, not invented units |
| documents(id,job,kind,data,hash,created) | Verify canonical JSON digest; preserve as immutable legacy archival evidence/source record, including asset_identity_snapshots. Do not re-prepare unsupported estimate/PO/invoice/change_order into Slice 1 documents or refresh old serial pins. Existing rendered file is supplementary; original JSON is retained even if no render exists |
| actions(id,job,version,data,hash,expires,state,receipt) | Retain full inert sourced history. No active queue, adapters, approval or external replay |
| audit(seq,at,event,data,previous,hash) | Verify source hash chain by exact legacy canonical serialization; retain whole source audit as archive and report. Extract dispute provenance if present; never treat free text as verified principal |

Stable target IDs: `UUID5(UUID(target_home_id), canonical([source_ledger_id, table, typed_primary_key]))`; assets use table discriminator `legacy_asset`, key asset string. Store `(Home,ledger,table,key,source_fact_hash,target_id)` unique map. Attach full original typed source rows to immutable `legacy_sources` storage; projection is a sourced note pointing to batch/key, not lossy field dropping. Import report includes every source row disposition, warnings and counts; no source field disappears unreported. Unknown/unsupported fact has explicit archive-only disposition, never silently reclassified into operational authority.

Review plan is JSON `{source_digest,target_home_id,decisions:[{table,key,disposition,values,reason}]}` consumed by maintenance only. Allowed dispositions: `map`, `archive_only`, `conflict`; values may supply only missing operational metadata (reservation resources/timezone/components; stock item descriptions/units; ambiguous source attribution time). It cannot alter original source bytes, waive missing required evidence or force overwrite of diverged targets. Record owner stamp and plan hash in batch. No public import RPC.

For imported non-identity source references, observed_at is the importer’s actual observation of the legacy record, explicitly labeled import observation, not inferred field capture time. Legacy identity observed_at remains its original explicit value.

Stage blobs; validate all relationships, digest, plan and conflicts; then one SQL transaction writes facts, legacy maps, completed batch, report and maintenance receipt. Exact source digest + target Home returns `{result:"IMPORT_ALREADY_APPLIED",report:original_report}` and zero new facts; first success uses `{result:"applied",report:report}`. The report’s original inserted/reused counts remain unchanged, rather than fabricating a new report on replay. Changed corpus uses new batch, unchanged keys/maps reused; changed immutable keys are conflicts; changed mutable job/stock state needs reviewed plan comparing source prior hash and target head, never LWW. Default divergent mutable change stops insertion with report. Crash before commit leaves no imported facts; blobs are reconciled or reused. Source kit/report retained for rollback. Read-only/inactive target rejects before insertion. Import manifest, inventory and mapping plan remain private owner data.

## Granular implementation map

The table names functions to implement, their dependencies, acceptance contracts and observable evidence. Test names here are required implementation tests unless already present in this package; they are not claims that those tests ran.

| Function → module | Contract/dependencies | Meaningful test → observable completion |
|---|---|---|
| validate_frame/dispatch → apps.edge.rpc | request schemas, UTF-8 bound, context first | malformed/extra/duplicate keys, 20 method registry → no 21st dispatch route |
| list_homes/select_home → packages.application.context | private index, lock, receipts, generation | identical UUID two-Home tests → raw recall changes correctly; no path in list |
| authorize_context/authorize_reference → packages.application.context | selected identity only | foreign/unknown receipts indistinguishable → exact empty error body |
| acquire_writer/handle_identity → apps.edge.windows_lock | Win32 handle APIs | two core + maintenance + junction/subst → one writer, HOME_WRITER_EXISTS |
| open_store/migrate → adapters.sqlite.store | lock acquired, FULL/WAL/FK | crash migration/failed open → prior schema or complete next version |
| execute_command/lookup_receipt → packages.application.commands | canonical fingerprint, queue, SQL UoW | same/different operation intent → one mutation/conflict; receipts survive restart |
| persist_intent/reconcile_intents → apps.desktop.intents | fsync journal, semantic request | kill before send/commit/response/ack; >50 ops → same operation resumes once |
| create_job/update_scope/update_track → packages.domain.jobs + application.jobs | revision table, allocation/holds | stale aggregate/scope; active scope gate → no partial updates |
| list_jobs/get_job/project_page → packages.application.queries | scoped repos, cursor registry | every view/null view/H2/100 limit → exact bounded projections |
| add_record/upsert_item/move_stock/allocate_capture → application.office | domain validation, UoW | missing item, negative stock, allocation twice → no duplicate economics |
| observe/assign/verify/dispute/recall → domain.identity + application.identity | evidence authorization, immutable facts | 0→1→2, replay, disputed/label/wrong job → required serial/null; history retained |
| stage/publish/reconcile → application.evidence + adapters.fs_blobs | token table, root handles, UoW | 0/50MiB, mismatch, phase replay, orphan fault → one evidence ID only |
| publish_read_cache/open_read_handle → fs_blobs.read_cache + desktop.preview | generation/expiry/file identity | foreign/expired preview denied → no stale Home image or private path |
| prepare_document/render_offline → application.documents | bind snapshot transaction, escaped templates | corrected/disputed pin unchanged; network trap → same digest, zero fetch |
| record_interruption/resolve_hold → domain.interruption + application.interruption | sourced gate, current scope | unsourced hold, stale hold, two holds → named hold only resolved |
| put_envelope/find_hard_conflicts → application.envelopes | exact tags, UTC half-open, expected rev | adjacent/soft/different tag/stale → valid adjacency, STALE_RESERVATION only |
| create_backup → application.backup | lock, queue/barrier, Backup API | uncheckpointed WAL + independent open → committed rows/blob manifest present |
| restore_inactive/activate → application.recovery | verified archive, private index, writer locks | over-live rejection, B hashes, inactive tests → same Home/new store/no second live writer |
| inventory_source/plan_import/apply_import → application.import_legacy | actual DDL, helper, map/report UoW | same/changed corpus, missing file, precommit kill → no duplication/partial facts |
| status/observe_readiness → application.status + apps.edge.windows_status | OS local read-only APIs, durable receipt list | denied encryption observation/offline → unknown and capture succeeds |
| launch_core/send/receive → apps.desktop.transport | QProcess, frame codec, journal | both transports; stderr separate; restart → generation invalidation and receipt recovery |
| Today/Inbox/Preview/Exceptions/Home picker → apps.desktop.views | scoped viewmodels, handlers | 100-photo/20-command resize/core restart → every enabled control works, no stale rows |
| install/commission/build_wheel → tools + pyproject | runtime locks, ACL, backup roots | clean Windows/reinstall/offline print → working shortcut, unchanged ledgers, recorded checklist |

SQLite tables should directly represent these facts: homes/store_meta, jobs/job_events, records/items/stock_moves/stock_balances, observations/assignments/assets/binds/bind_heads/asset_jobs/disputes, evidence/attach_attempts, documents/document_pins, interruptions/resolution_events, envelopes, operations/operation_phases/audit, backups/retention, import_batches/legacy_id_map/legacy_sources. All foreign keys include Home or use separate per-Home DB plus asserted store Home; no global business-object lookup. Unique constraints mirror operation UUID, observation assignment/verification, bind revision, Home SKU, import key/digest. Read projections remain separate from writable facts; no generic plugin framework.

## Explicit integration test driver interface

Implement `packages.application.testing.launch(owner_root: Path, transport: str)` as a context manager over the real app. It provisions no fake data. Exposes:

- `maintenance(argv: list[str]) -> dict`: invoke the same maintenance application boundary (for qprocess, the real binary), after safely releasing test core writer; provision two labels returns `{status:"confirmed"}`. Import returns the maintenance_result schema, or `{error:{code:DOMAIN_CODE,body:{}}}` on domain denial. Import receives the same reviewed source/target plan as production.
- `raw_frame(frame: bytes) -> bytes`: complete one actual parser/dispatch response frame, preserving input context and command exactly. QProcess variant must really use QProcess with event loop; in-process goes through the same codec/dispatch, labeled dev only.
- `open_read_handle(handle, context) -> {sha256: str, bytes: bytes}` or `{error:{code:"HOME_CONTEXT",body:{}}}`: actual desktop consumer. No second RPC.
- `flush_staged_file(path)`: real fsync/Windows flush of the already created file, no metadata mutation.
- `business_snapshot(home_id,store_id)`: read-only canonical hashes of business fact rows/history and evidence bytes, excluding only documented command/audit/backup-catalog append effects, lock files and cache. Exclusion list is fixed/test-visible; it may not hide business changes.
- `audit_rows(home_id,store_id)`: read-only full audit rows in sequence order, including command name; tests require the entire pre-backup prefix unchanged and only backup/restore audit appends.
- `store_file_hashes(home_id,store_id)`: exact relative filename→SHA256 for every closed store file except transient lock diagnostic content. Never checkpoint or write the observed store during inspection.

The driver is test-only plumbing. No fake receipts, mocks, arbitrary fixture DB writes, blanket skips or “expected pass” flags. Fault tests can instrument real precommit/postcommit points; test hooks are absent from the production distribution. The import at test collection intentionally exposes absence of this interface today. Additional release tests from Spec §13 must be implemented, not inferred from these five vectors.

## Windows installation and commissioning

Use a supported Windows 11 x64 machine with entitlement and current servicing. Record OS build, Python/Qt/SQLite versions and hashes, installation source, disk filesystem and drive type. Run standard owner account for normal operation; encryption observation must not request elevation. Installer may request separately approved setup elevation for ACL/encryption commissioning, never for raw capture. No WAL stores on network shares or synced OneDrive folders.

Choose owner-root under local app data on a local NTFS volume. Provision two business labels and separately identifiable store UUIDs, private index, per-Home blob/staging/read-cache/intent directories and backup siblings. Apply inherited owner/SYSTEM/Administrators permissions and remove broad Users/Everyone access; inspect resulting ACLs for every root, recovery tree and external backup. Example commissioning commands after creating the root (operator must review actual account identity and ACL result):

```powershell
$ownerRoot = "$env:LOCALAPPDATA\FullKit\owner"
$ownerSid = [System.Security.Principal.WindowsIdentity]::GetCurrent().User.Value
icacls $ownerRoot /inheritance:r
icacls $ownerRoot /grant:r "*$($ownerSid):(OI)(CI)F" "*S-1-5-18:(OI)(CI)F" "*S-1-5-32-544:(OI)(CI)F"
icacls $ownerRoot
```

Inherited permission removal does not erase preexisting explicit broad grants: inspect and remove identified broad grants in a reviewed commissioning step. Do not recursively reset permissions on an arbitrary existing directory. ACLs are accidental-access controls under the trusted-owner threat model; not defense against administrators.

Commission encryption before real customer data. Obtain best-effort BitLocker/device-encryption status through OS APIs as current user. Denied/unavailable → unknown, no extra elevation and capture remains usable. Show commissioned claim source/time separately from fresh live observation. Operator confirms recovery key is saved off the laptop without pasting it into app logs. Never claim the application encrypts an unencrypted volume.

Register default sibling backup and an approved external SSD destination. Record volume/file identity, verify free space and ACLs; perform backup with network physically disconnected. Open the standalone archive database without source sidecars, verify manifest/evidence, restore to a new inactive directory and inspect both Homes. Loss of the laptop destroys sibling backups; external copy is a commissioning action, not a subscription or cloud service.

Run second-launch lock rejection, junction/subst alias tests, crash-held handle release, maintenance-versus-core collision, failed Home switch, and recovery inspection/mutation denial. Do not “fix” lock tests by deleting the lock file. Test print/preview with HTTP/file resource loading trapped; offline operation must not depend on a cached CDN. Disconnect network and execute the full release demo below. Power-loss, WWAN business audio and hardware-specific performance remain separately qualified; process kill is not a power-loss test.

Reinstall preserves owner root. Recovery procedure: stop all writers, retain original source kit/archives/intents, verify chosen archive, restore inactive, inspect, reconcile receipts, explicitly activate through maintenance. Preserve old instance inactive for rollback. Never drag a restored DB over live files.

## Release demonstration, completion and review

Demonstrate offline: provision two Homes → same-ID jobs → real photo plus typed serial → assign/verify/recall each → immutable document pins → correction/dispute/history → local time/cost/item/stock and hard envelope → scope interruption and sourced hold → resume with owner decision → kill core/restart/reconcile semantic intents and durable receipts → verified Backup API archive with uncheckpointed WAL → inactive restore, inspection and write denial → reconciled actual 0.2.0 import and same-corpus replay report. Capture screenshots/logs with disposable data and exact versions. No performance or commercial reliability claims beyond tested outcomes.

Completion requires all twenty methods and defined projections, no enabled dead controls, the asserting tests in both transports, all mandatory Spec §13 cases including fault points, clean Windows install/ACL/lock checks, zero network render/readiness dependency, and Validation.md recording failures and untested conditions. Contract-only validation does not satisfy application release. C1 and C2 must be resolved and the machine contract updated if its correction changes.

Preserve provisional **152–240 hours**; backup/import/file-identity work’s **4–8 hours is inside existing storage/backup bands**. Hardware allowances **$2,320 / $3,505 / $4,206** are historical estimates, not quotations. Slice 1 subscriptions **$0/month** assume existing Windows and local backup. No estimate change has been adopted. If actual qualification/import complexity exceeds these bands, identify concrete work and revise estimate transparently; do not cut context, import or recovery tests to fit.

For Claude review: attack the actual request/response definitions, specimens, fingerprint transitions, import mapping, C1/C2 proposals and asserting tests. Distinguish schema expressibility from application invariants. Glen manages onward collaboration; this package does not contact another model.
