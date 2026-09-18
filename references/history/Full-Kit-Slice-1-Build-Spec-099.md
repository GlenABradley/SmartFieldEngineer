# Full Kit Composed
## Slice 1 Build Specification — 0.99

**Status:** frozen for code generation and Claude adversarial review  
**Date:** 18 September 2026  
**Authors:** GPT Sol + Grok, under Glen Bradley  
**Application code:** none in this document  
**Historical input:** Field Office 0.2.0 remains unchanged and is an import source only  

This is the single effective text. Earlier rounds are archive. A generator must not consult R1–R4 for wire format.

---

### 0. How to read this

| Word | Meaning here |
|---|---|
| Home | Business ownership boundary. Survives backup and restore. |
| store instance | One on-disk ledger+blob tree for a Home. A Home may have one working instance and any number of inactive recovery instances. |
| Floor / horizon / halo | Product scope labels. Nothing in this file is floor software. |
| Confirmed | Local durable result. Never means emailed, paid, booked, or physically safe. |
| Claimed | Operator-supplied text. Not authentication. |
| Slice 1 | Local office on one Windows profile. No hub, no voice, no connectors. |

If two sentences appear to conflict, the **fail-closed** sentence wins.

---

### 1. What we are building

A field engineer’s laptop office that still works when the SIM is in a drawer: capture, bind identity, record time/cost/stock, protect a local envelope, prepare a document, hold interrupted work, crash-recover a command, back up, restore inactive, import 0.2.0.

The composed product is larger: calls, shared authority, packs, guided work, settlement. That product is not Slice 1. Do not implement it behind a Slice 1 button.

Three buyers, one engine later. Slice 1 has one trusted Windows owner and two provisioned Homes. That is context isolation, not multi-user security and not defense against a hostile local administrator.

Phone-ready (WWAN + live business audio while Workshop is open) is a later slice. Slice 1 must not display call, secretary, or marketplace controls.

---

### 2. Non-negotiable laws

1. One command boundary. GUI, helper, and any future model cannot write the ledger.
2. Capture in an unlocked authorized session is not blocked by radio, hub, or identity-provider absence.
3. Capture is not permission to change a live network.
4. Serial is observed, assigned, verified. Recall uses the bind. Unresolved returns no serial.
5. Prepared is not issued. Sourced-manual settlement is not a processor receipt.
6. Scope change during active field work requires a current interruption on that job.
7. Identity work and raw capture may continue during scope drift.
8. No last-write-wins on commitments, binds, money, or reservations.
9. No second writer on a store. Restore never lands on a live directory.
10. No HTTP in templates, readiness, or document render.
11. No robot token, OCR button, ASR button, or dummy adapter in the shipped tree.

---

### 3. Layout and lock

```text
owner-root/
  private-home-index          # labels, instance ids, recovery flags — no dossier
  home-A/
    home.lock                 # OS exclusive handle, held for writer life
    ledger.sqlite
    blobs/sha256/<digest>
    staging/<token>/original
    read-cache/<token>/
    client-intents/
  backups/home-A/             # provisioned sibling; convenience only
  recovery/<store_instance>/  # same home_id, new store_instance_id, inactive
  home-B/                     # peer tree, no shared blob root
```

- `home.list` returns labels, ids, active/recovery status. **Never paths.**
- Open store: acquire OS exclusive lock on `home.lock`, then SQLite. PID text in the file is diagnostic only. Never delete a lock because a PID looks dead.
- Canonicalize paths so `C:\Data\HomeA` and a junction to it are one store.
- Second core: `HOME_WRITER_EXISTS`, no dossier body.
- One desktop, one child core. Second launch on a locked store fails.
- Home switch: finish in-flight commit/publish, persist intents, drop unused tokens, release lock, acquire the other. Failure → previous context or none. Never half-selected.
- SQLite: patched runtime (do not infer from Python), WAL, `synchronous=FULL`, foreign keys, one writer queue.
- Encrypt the volume before real customer data. Uncommissioned → readiness `encrypted_volume: unknown|no`, not “safe.”

Maintenance (`--maintenance` provision / import / activate) uses the same binary and lock. No second script on a live DB.

---

### 4. Transport

Default: QProcess, JSON-RPC 2.0, UTF-8, newline frames, stdout protocol, stderr diagnostics, 1 MiB frame. Files move by staging tokens.

Two-day spike may select in-process single-writer queue. **Application methods and receipts stay identical.**

Every scoped call carries:

```text
home_id, store_instance_id, session_id, session_generation
```

Core issues `session_id` at start and increments `session_generation` on select. Mismatch → `HOME_CONTEXT` with empty body. Do not search other stores to decide if an id exists. Unknown operation and foreign operation return the same inaccessible error.

Exceptions without prior select: `home.list`, `session.select_home`.

---

### 5. Twenty methods

No twenty-first method. Reads that were missing are views and handles, not new verbs.

| # | Method | Request | Result |
|---|---|---|---|
| 1 | home.list | `{}` | Homes/instances, labels, active/recovery. No paths. |
| 2 | session.select_home | `home_id`, `store_instance_id` | Issued context. Recovery selectable **read-only**. |
| 3 | job.create | cmd envelope + title, scope_text, capture_refs | New job, aggregate 1, scope 1 |
| 4 | job.list | cursor, limit 1–100 | Summaries + next_cursor |
| 5 | job.get | job_id UUID or null; view; cursor; limit 1–100 | See §5.1 |
| 6 | job.update | cmd + scope \| track_event | Receipt |
| 7 | record.add | cmd + entry_kind payload | Receipt |
| 8 | evidence.attach | cmd + stage \| publish | Receipt + stage or evidence |
| 9 | serial.observe | cmd + identity payload | Observation id |
| 10 | serial.assign | cmd + observation_id, asset_id | Assignment rev 1 |
| 11 | serial.verify | cmd + observation, asset, verification, reason | Bind |
| 12 | serial.recall | job_id, asset_id, revision optional | verified \| unresolved |
| 13 | serial.dispute | cmd + bind_id, asset_id, reason | Head disputed |
| 14 | document.prepare | cmd + type, title, body_text, asset_ids | Prepared artifact |
| 15 | interruption.record | cmd + interruption payload | Interruption id |
| 16 | reservation.put | cmd + envelope payload | Reservation |
| 17 | operation.get | operation_id | Receipt + attach-attempt if any |
| 18 | backup.create | cmd + destination_token or null | Archive receipt |
| 19 | backup.restore | cmd + archive/destination, mode=inactive | recovery_copy_id, source_home_id |
| 20 | system.status | active_job_id or null | Runtime, readiness, last 50 ops |

Unknown properties: schema error.

#### 5.1 job.get views

`view` is exactly one of: `summary` | `records` | `observations` | `evidence` | `documents` | `interruptions` | `reservations`.

- `job_id` null: inbox only — records, observations, evidence not yet allocated. Other views error `INBOX_VIEW`.
- `summary` does not inline blobs or document HTML.
- Collection views paginate at most 100. No recursive include. No `*` view.
- Evidence rows: `evidence_id`, `original_name`, `media_type`, `sha256`, `classification`, optional `read_handle` (120 s, this session).
- Document rows: `document_id`, `type`, `prepared_at`, `job_scope_revision`, `digest`, optional `read_handle`.
- Read handle opens only the core-published read-cache file. Expires on generation bump or Home switch. Foreign artifact → `HOME_CONTEXT`.

#### 5.2 Mutating envelope (`cmd.v0.addendum-r4`)

```
schema, kind=command, operation_id, home_id, command,
job_id, job_scope_revision, expected_revision, payload
```

`home_id` must match session Home. No `actor`. Core stamps Windows owner. Claimed verifier/observer stay text.

| Command | expected_revision | Scope |
|---|---|---|
| job.create | 0, job absent | null; result job=1 scope=1 |
| job.update scope | job aggregate | submitted = current; both increment; field `in_progress`/`blocked` needs live interruption |
| job.update track_event | job aggregate | submitted = current; aggregate increments; scope unchanged |
| serial.observe | null | inbox null; job-tagged may be stale; store submitted + current |
| serial.assign | 0 if none | current scope required |
| serial.verify | bind head, 0 if none | drift allowed; record both scopes |
| serial.dispute | bind rev + head state | drift allowed |
| evidence.attach | null | drift allowed |
| record.add | null | inbox null or recorded stale/current |
| document.prepare | job aggregate | current scope required; unresolved pin blocks; job rev **not** incremented |
| interruption.record | null | records current; does not authorize work |
| reservation.put | reservation rev, 0 if new | scope null |
| backup.create / restore | null | job/scope null |

Fingerprint: schema profile + Home + store_instance + command + job + submitted scope + expected_revision + payload. Same id + same fingerprint → existing receipt. Different fingerprint → `OPERATION_ID_CONFLICT`.

Receipt: `queued` | `executing` | `confirmed` | `failed` | `unknown`. Confirmed = local durable only.

**Intent journal (mandatory):** before every mutating RPC, write `{operation_id, fingerprint, home, store}` into that Home’s `client-intents/`, fsync, then send. Persistence fail → do not send. On restart, `operation.get` each open intent. Fifty-row `system.status` list is convenience from **durable** receipts, not “this PID only,” and not a substitute for the journal.

---

### 6. Payloads

One discriminator per body. Sibling fields from another variant are schema errors.

**record.add `entry_kind`**

| Kind | Fields | Rules |
|---|---|---|
| note | text, reason, source_reference? | — |
| time | minutes>0, started_at/ended_at both set or both null, activity, reason, source_reference? | timestamps ordered; do not invent them from minutes |
| cost | amount_cents≥0, currency=`USD`, category, reason, source_reference? | not a payment |
| item_upsert | item_id, sku, display_name, unit_name, reason | sku unique per Home; no identity merge |
| stock_move | item_id, quantity≠0 int, direction receive\|consume\|adjust, location, unit_cost_cents?, currency=`USD`, reason, source_reference? | existing item; receive/consume quantity>0; adjust signed; receive needs unit cost or explicit unresolved (not zero); no negative usable stock |

**job.update `update_kind`**

- `scope`: scope_text, interruption_id?, capture_refs[], reason, provenance=`sourced_manual`, source_reference?
- `track_event`: track, track_state, interruption_id?, capture_refs[], reason, provenance=`sourced_manual`, source_reference?, evidence_ids[]

`capture_refs` allocate existing inbox records/evidence to this job once. Already on another job → `CAPTURE_ALREADY_ALLOCATED`. Do not copy amounts. Serial observations are **not** capture_refs; use `serial.assign`.

Tracks (stored values only):

```
field:     planned | ready | in_progress | blocked | completed
delivery:  not_prepared | prepared | delivery_recorded | accepted | disputed
billing:   not_prepared | prepared | issued_recorded |
           partially_settled_recorded | settled_recorded | disputed
returns:   none | pending | closed
exception: none | open | held | resolved
```

`paid` / `delivered` as names are rejected. `issued_recorded`, `settled_recorded`, `accepted`, `delivery_recorded` require `source_reference` or evidence_ids. UI must say sourced/manual.

Scope change while field is `in_progress` or `blocked`: `interruption_id` must be this job, this Home, current scope generation, state not resolved. Else `FIELD_TRACK_ACTIVE` | `INTERRUPTION_FOREIGN` | `INTERRUPTION_STALE`.

Resume to `ready` / `in_progress`: interruption_id + owner decision + reason + source. Append resolution event. Do not delete the interruption. Other open holds still block `completed`.

**interruption.record**

`trigger`: scope_change | tool_missing | unsafe_site | mentor_unavailable | other  
`state`: detected | stabilizing | secured_on_hold | stabilization_failed  
`reversible` / `irreversible`: yes | no | unknown  

`secured_on_hold` requires `stabilization_done=true` and (evidence_ids or stabilization text beginning `SOURCED:`). No exemption field.

**reservation.put**

reservation_id, starts_at, ends_at, site_timezone, state soft|hard, resources[], components_minutes {preparation, travel, work, contingency, documentation, replenishment, aftercare, supervision}. Positive interval. Hard conflicts rejected. No routing API.

**document.prepare**

type work_order | job_summary | closeout; title; body_text (escaped, not HTML/JS); asset_ids. Local templates only. Pin current authorized binds in-transaction. Output immutable HTML + offline print form. No network fetch in renderer.

---

### 7. Identity

Four facts: observation, assignment, verified bind, dispute.

- Observation `identity_kind`: `serial` | `asset_label`. Normalization `trim_only.v0`. Photo requires Home-local evidence ids. Raw preserved.
- Assignment once. Expected 0. New asset UUID created in-transaction if needed. No fuzzy serial merge.
- Bind head key: `(home_id, asset_id)`. Expected 0 → stored 1. Correction expected 1 → 2. Observation cannot verify twice.
- Dispute marks head unavailable; bind row immutable; revision number unchanged. Second dispute on same numeric rev must not silently replace the first conflict record.
- Recall current: verified association on this job + undisputed head → serial. Else unresolved, `serial: null`.
- Historical recall names revision; never used to prepare current documents.
- Replacement of hardware is a new asset. Loan/reinstall graph is out of Slice 1.

---

### 8. Evidence two-phase

Max **50 MiB** (52,428,800). Zero rejected.

Same `operation_id` for the logical attach.

**Intent fingerprint:** Home, store, job, metadata, declared length, declared digest.  
**Phase fingerprint:** phase, token, attempt.

| Step | Behavior |
|---|---|
| stage attempt N | Mint token bound to Home, store, session, generation, operation, attempt. TTL 3600 s or context change. Tokens do not survive core restart. |
| write file | Desktop writes staging path, flush, then publish. Path never in documents/readiness. |
| publish | Rehash file. Consume token on any outcome. Success → available evidence. |
| replay identical publish | Return stored attempt result. No second hash/mutate. |
| fail / expire | stage attempt N+1, same operation, new token. Failed attempts kept. |
| confirmed attach | No further attempt may create another evidence_id. |

Publish order: authorize → size → hash → type/length check → fsync → atomic same-volume move to `blobs/sha256/<digest>` → metadata+receipt transaction. Metadata fail = orphan, not available evidence.

Reconcile on startup: abandoned staging, consumed tokens, missing referenced blobs, unreferenced published files. Unreferenced published blobs: 24-hour grace, then GC. Never delete a blob still referenced by any committed row or retained backup.

---

### 9. Backup, restore, import

- `destination_token` null → provisioned `backups/<home>/` sibling. That is **not** off-machine backup. External SSD is a commissioning item.
- Bundle: consistent DB + every referenced blob + digest manifest. Exclude locks, read-cache, abandoned staging, unused secrets.
- Incomplete manifest = failure.
- Restore: new directory, new `store_instance_id`, **same `home_id`**, inactive, source untouched. Reject restore-over-live or into existing instance. Result: `recovery_copy_id`, `source_home_id`.
- Select recovery instance for read. Writes → `RECOVERY_INACTIVE`.
- Activation is owner maintenance: stop live writer, review pending ops, explicit designate. Slice 1 has no external replay queue; later slices must not fire restored `queued` rows.

Import: `--maintenance import`, source 0.2.0 read-only. Do not upgrade the source in place. Claimed names → `legacy-claimed:<text>`. Unknown fields warned, not dropped. No pending-action replay. Import report + source kit kept for rollback. Not a second live writer.

---

### 10. Status and readiness

Local files and OS APIs only.

```
wwan: unknown | observed_up | observed_down     # adapter state, not "has Internet"
encrypted_volume: yes | no | unknown
battery_percent, on_ac: observed or null
heavy_worker: off | observed_active | unknown   # default off; no model in Slice 1
```

Integrity includes `checked_at`. Do not display stale integrity as fresh. Capture still works when readiness warns. No “four-hour site” estimate.

---

### 11. Error codes Claude must not stretch

| Code | When |
|---|---|
| HOME_CONTEXT | Wrong Home, store, session, or generation. Empty body. |
| HOME_WRITER_EXISTS | Second writer. |
| RECOVERY_INACTIVE | Mutation on recovery instance. |
| OPERATION_ID_CONFLICT | Same id, different fingerprint. |
| STALE_JOB / STALE_BIND / STALE_ASSIGNMENT / STALE_RESERVATION | Head moved. |
| FIELD_TRACK_ACTIVE | Scope change without current interruption. |
| INTERRUPTION_FOREIGN / INTERRUPTION_STALE | Wrong job or already resolved/wrong scope. |
| SERIAL_UNRESOLVED | Prepare/pin without a current verified head. |
| ITEM_UNKNOWN | stock_move to missing item. |
| CAPTURE_ALREADY_ALLOCATED | Inbox ref already on a job. |
| OBSERVATION_ALREADY_ASSIGNED / VERIFIED | Replay of consumed identity fact. |
| STAGE_EXPIRED | Token dead. |
| INBOX_VIEW | job.get view illegal on inbox. |
| SCHEMA | Unknown field, bad discriminator, bad type. |

`operation.get` of a foreign or unknown id uses `HOME_CONTEXT` (or equivalent inaccessible), never “exists in A.”

---

### 12. Repository and generation order

```text
fullkit/
  packages/domain/
  packages/application/
  apps/edge/
  apps/desktop/
  adapters/sqlite/
  adapters/fs_blobs/
  tests/                 # two-Home vector first
  migrations/local/
  docs/                  # this spec + Validation.md
```

Order: effective JSON schemas → two-Home test (asserting) → domain/lock/receipts → blobs/serial/documents → office/interruption → backup/import → Qt. Transport spike before packaging. Skeletons are not done.

---

### 13. First test (write before UI)

Homes A and B each have job `22222222-2222-4222-8222-222222222222` and asset `33333333-3333-4333-8333-333333333333`.  
A bind `A-SERIAL`. B bind `B-SERIAL`.

1. Select A, recall `A-SERIAL`. Select B, recall `B-SERIAL`.
2. `operation.get` of A’s verify while B selected → `HOME_CONTEXT`, no A fields.
3. Cross-Home token, document handle, backup, import → fail closed.
4. Restore A → instance R, same `home_id`, new `store_instance_id`. A and B bytes unchanged.
5. Select A/R, recall `A-SERIAL`. Mutate → `RECOVERY_INACTIVE`.
6. UI must not title R as a third business.

Raw RPC, not only clicks.

Mandatory suite is §12 of the Sol merge, retained in full: context, serial lifecycle, scope/interruption, money/stock, two-phase attach, intent/crash, lock/alias, backup/import, no-network render, Qt 100-photo smoke. Fault data is disposable. Process-kill ≠ power-loss.

---

### 14. Install and honesty

Pin versions after license/security review. Installer: Windows entitlement, runtime, ACL, encryption/recovery prompt, backup sibling, lock test. Reinstall does not wipe ledgers. No secrets in the tree. Validation.md lists what actually ran.

Disabled features are absent or labeled unavailable. No success-returning stubs.

---

### 15. Out of Slice 1

Hub, OIDC, Keycloak, Postgres, sync, second human, voice console, calls, Relay, “say Glen,” marketplace, purchasing, issuance/payment automation, cloud model, ASR/OCR, pack writes, guided install, robot, fiber, custom bag, fractional stock, multi-currency, WWAN probe, template CDN, restore-over-live.

---

### 16. Money

Hardware planning (not quotes): **$2,320 / $3,505 / $4,206**.  
Slice 1 subscriptions: **$0/month** given existing Windows and local backup.  
Engineering: **152–240 h** ($11,400–36,000 at $75–150/h; +20% $13,680–43,200). Ugly-shell Qt cut: 140–220 h. Do not cut isolation, import, or recovery tests.  
$10,000 seat remains a hypothesis. Whole-composition hour range remains separate.

---

### 17. Pre-answered Claude attacks

These are specified outcomes, not hopes.

| Attack | Specified result |
|---|---|
| HOME_CONTEXT leak via error text, pagination, handle, or existence oracle | Empty body; unknown and foreign look the same; handles bound to session/generation; no paths in list/status/documents |
| job.get inbox wildcard / view soup | One view enum; inbox views limited; limit ≤100; no include=* |
| Publish twice, one operation, new bytes | Phase fingerprint + consumed token; only attempt+1 restage; confirmed attach sealed |
| Recover with no intent journal | Client must not send; if it did anyway, `operation.get` + durable receipt still one mutation — journal is required for *client* recovery, core remains idempotent |
| PID-file lock steal | OS exclusive handle only |
| Restore onto live | Reject; new instance only |
| Mutate recovery | `RECOVERY_INACTIVE` |
| Template `https://` or `file:///` | Renderer local-only; fetch is a test failure |
| `billing: settled_recorded` with no source | Reject |
| Reuse old interruption after resume | `INTERRUPTION_STALE`; new scope needs a live hold |

If an implementation passes the two-Home test and this table, Claude has to find a new hole. That is the point of 0.99.

---

### 18. Demonstration that counts as Slice 1 done

Offline, two Homes, one owner:

Provision → job → photo+typed serial → assign → verify → recall → pin document → correct/dispute → history intact → time/cost/item/stock/envelope → interruption + sourced hold → kill core → restart → intent/receipt recovered → backup → inactive restore → no live overwrite → 0.2.0 import report.

Then write Validation.md with versions, OS, what failed, and what was never claimed.

Glen’s mailbox and the named physical task for experiment C are not required to generate this slice.
)
