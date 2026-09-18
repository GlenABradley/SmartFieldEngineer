# Smart Field Engineer implementation roadmap

Updated 2026-09-18 against `main` at `c4bda075`. This is an engineering status map, not a release claim or a replacement for the governing contract.

## Executive assessment

Smart Field Engineer is a well-specified pre-release workbench with a credible persistence and command foundation. Its strongest assets are the unusually detailed offline/durability contract, strict Home isolation model, preserved decision provenance, real fault-oriented tests, and honest visible failures for missing behavior.

The project is not yet a desktop application. The current implementation covers the first narrow vertical slice: provision two Homes, open and lock their stores, select a context, create/list jobs, and retrieve/replay durable receipts through the shared frame codec. The next work should deepen this boundary before broadening into UI features.

## Product and contract boundary

Slice 1 serves one trusted Windows owner on one laptop with two isolated business Homes. It is local-first and must remain usable without a network. The contract defines exactly 20 public JSON-RPC methods:

| Reads and context | Mutations |
|---|---|
| `home.list`, `session.select_home`, `job.list`, `job.get`, `serial.recall`, `operation.get`, `system.status` | `job.create`, `job.update`, `record.add`, `evidence.attach`, `serial.observe`, `serial.assign`, `serial.verify`, `serial.dispute`, `document.prepare`, `interruption.record`, `envelope.put`, `backup.create`, `backup.restore` |

Maintenance provision/import/activation operations remain private application boundaries, not extra public RPC methods. Cloud sync, telephony, OCR/ASR, connectors, payment automation, and plugins are outside Slice 1.

## Repository anatomy

| Area | Purpose | Assessment |
|---|---|---|
| `fullkit/packages/domain/` | Pure business rules | Only shared errors exist; most domain behavior remains to build. |
| `fullkit/packages/application/` | Context, command, transaction, and query orchestration | Home provisioning, session selection, one command, receipts, and job pagination exist. |
| `fullkit/adapters/sqlite/` | SQLite connection and persistence infrastructure | Real WAL/FULL/FK setup exists; broad repositories and backup/restore do not. |
| `fullkit/adapters/fs_blobs/` | Evidence staging, publication, cache, retention | Reserved directory only. |
| `fullkit/apps/edge/` | Core codec, dispatch, principal, writer lock | Strict in-process frame handling exists; installed stdin/QProcess entry point does not. |
| `fullkit/apps/desktop/` | PySide6 UI, transport, intent journal, preview | Reserved directory only. |
| `fullkit/migrations/local/` | Forward-only local schema | Store metadata, migration receipts, audit, jobs, job events, and operations exist. |
| `fullkit/tests/application/` | Real implementation tests | 35 test functions cover the current foundation and fault boundaries. |
| `fullkit/tests/contract/` | Working copies of reviewed contract tests | Inventory/schema checks can pass; end-to-end two-Home vectors await the real driver. |
| `fullkit/contract/` | Preserved contract, schemas, specimens, and validation tools | Reviewed baseline; do not edit casually or treat it as application evidence. |
| `references/` | Canons, historical reviews, and legacy 0.2.0 import source | Valuable provenance; not active implementation code. |
| `decisions/` and `handoff/` | Adopted authority and continuation state | Detailed and current, but should not substitute for code/tests. |

## Implemented behavior

### Storage and Home isolation

- Provisions exactly two Home descriptors into a private owner index.
- Creates separate ledger, blob, staging, read-cache, intent, and backup roots.
- Persists Home/store identity and denies mismatched store selection without mutating the ledger.
- Uses one executor-owned SQLite connection per store, WAL journaling, synchronous FULL, foreign keys, and forward-only hashed migrations.
- Holds an OS-backed writer lock for the session lifetime; POSIX is development-only and Windows uses handle/file identity checks.
- Supports read-only inactive recovery inspection in the foundation, while denying mutation.

### RPC, context, and commands

- Accepts one bounded UTF-8 newline frame, rejects duplicate keys, non-finite/floating values, malformed requests, unknown methods, and oversized frames.
- Loads exactly 20 method definitions from packaged schema resources.
- Issues session/generation context and rejects stale, foreign, or malformed Home context before business lookup.
- Implements `home.list`, `session.select_home`, `job.list`, `operation.get`, and the `job.create` command path.
- Commits job facts, audit event, and terminal receipt atomically; persists semantic fingerprints for idempotent replay and operation-ID conflict detection.
- Uses high-water pagination and context-bound expiring cursors.

### Verification assets

- Contract generator/validator, preserved specimen corpus, dependency verification, legacy inventory helper, workspace integrity checks, and baseline hash verification exist.
- Current tests exercise lock exclusion, migration rollback, provision replay, Home denial equivalence, receipt replay/conflict, commit faults, lost acknowledgements, context invalidation, and pagination fences.

## Material gaps and risks

| Priority | Gap | Why it matters |
|---|---|---|
| P0 | Apply the reviewed S04.1 boundary hardening packet | Read-only context restoration, executor ownership, and direct internal revision-envelope checks must be correct before transport increases concurrency. |
| P0 | No installed core entry point or QProcess transport | The production boundary and supplied integration driver cannot run; current frame tests are in-process only. |
| P0 | No durable desktop semantic-intent journal | A process loss between send, commit, response, and acknowledgement cannot yet be reconciled from the future UI. |
| P0 | Most domain and command routes are unimplemented | Job updates, evidence, serial identity, office facts, holds, envelopes, backup, restore, and status still fail honestly. |
| P1 | Blob staging/publication/read cache absent | Evidence integrity, immutable documents, and safe preview depend on it. |
| P1 | Backup/restore/import absent | Core offline recovery and legacy migration promises are not demonstrable. |
| P1 | Desktop UI absent | There is no usable application shell, transport lifecycle, or stale-context clearing behavior. |
| P1 | Linux development is not reproducibly locked | This host cannot run the declared toolchain without a separately reviewed Linux wheel lock. |
| P1 | Windows qualification outstanding | Locks, aliases, ACLs, encryption observation, installation, printing, and power-loss behavior remain unproven. |
| P2 | No project distribution license | Repository visibility does not establish reuse or redistribution rights; the owner must select terms before a public release. |
| P2 | No CI/release automation | A premature workflow would either omit required Windows evidence or advertise incomplete checks; add it once a supported runner matrix is explicit. |

## Delivery sequence

Each stage should leave unfinished routes visibly failing. Do not bypass an earlier boundary to make a later demo appear complete.

### 1. Harden the current boundary (S04.1)

Implement the accepted corrections in `handoff/S04.1-PACKET.md`: preserve read-only state when recovering a failed Home switch, remove the unnecessary codec executor layer, close dispatch races, and validate internal `job.create` revision envelopes.

Exit evidence: all current application tests plus focused recovery/revision tests pass; contract baseline hashes remain unchanged.

### 2. Add real process transport and test driver (S05)

Build `apps.edge.__main__`, bounded streaming frame assembly, sanitized stderr diagnostics, asynchronous PySide6 `QProcess` transport, the minimum write-before-send intent journal, and `packages.application.testing.launch` over the real boundaries.

Exit evidence: in-process and QProcess runs produce identical first-command results and denials; fragmented/oversized frames resynchronize; restart/replay makes one mutation; the supplied integration tests collect and fail only at the next genuinely absent capability.

### 3. Complete jobs and serial identity (S06)

Implement job update/track/scope rules and serial observe → assign → verify → recall → correct/dispute history. Preserve same-ID isolation between Homes and immutable revision chains.

Exit evidence: the two-Home serial vector passes over both real transports, including stale revisions, replay, foreign receipts, correction, dispute, and history.

### 4. Evidence and immutable documents (S07)

Add Home-local blob staging/publication, digest and size checks, attach phase receipts, orphan reconciliation, capability-scoped read cache, document rendering, and immutable serial pins.

Exit evidence: fault tests cover stage/commit/publish/reconcile boundaries; foreign or expired previews reveal no path/data; offline document bytes are deterministic and pins do not change after serial correction.

### 5. Office, scheduling, and interruption rules (S08)

Add time/cost/notes, items and stock movements, envelopes with exact tags and half-open conflicts, sourced interruptions, and the adopted C1/C2 resume/scope semantics.

Exit evidence: no negative stock, no duplicate economics, adjacency remains valid, stale envelopes return only `STALE_RESERVATION`, and resolving one hold cannot silently resolve another.

### 6. Finish intent and crash recovery (S09)

Complete semantic intent publication, startup reconciliation beyond the last 50 operations, context re-enveloping, and fault injection at before-send/before-commit/after-commit/before-ack points.

Exit evidence: every fault converges to one durable outcome and one business mutation without treating unknown receipt state as failure.

### 7. Backup, inactive restore, and legacy import (S10)

Implement barriered SQLite Backup API archives, blob manifests, verified inactive restore/new store identity, explicit activation, read-only legacy inventory, reviewed import plans, stable ID mapping, and same-corpus replay.

Exit evidence: uncheckpointed WAL data is present in archives; peer Home bytes stay unchanged; recovery is read-only; import is atomic/replay-safe and every source row has a disposition. Final customer-corpus proof remains blocked until real source data is supplied.

### 8. Build the desktop shell (S11a)

Implement the Home picker, Today, Inbox, Preview, Exceptions, and detail flows only after the raw boundaries work. Every enabled control must have a real handler; Home switches and stale responses must clear scoped state.

Exit evidence: UI tests exercise resize, large photo/command sets, core restart, failed switch, stale callbacks, offline preview/print, and zero writable SQL in the GUI process.

### 9. Package and qualify on Windows (S11b)

Build the wheel/installer, preserve owner data across reinstall, establish local NTFS roots and ACLs, inspect SQLite/runtime hashes, qualify handle aliases and recovery, observe encryption without elevation, and run the complete offline release loop on supported hardware.

Exit evidence: clean-install and reinstall receipts, full mandatory suite in both transports, standalone verified backup/restore, offline screenshots/logs with synthetic data, and a release `Validation.md` that records failures and untested conditions.

## Repository operations backlog

These are owner/admin actions that files in a checkout cannot perform:

1. Set the GitHub About description to: `Offline-first desktop operations and evidence system for independent field engineers.`
2. Add topics such as `field-service`, `offline-first`, `desktop-app`, `pyside6`, `sqlite`, `json-rpc`, `windows`, and `local-first`.
3. Upload `.github/assets/readme-hero.svg` (or a raster export) as the social preview.
4. Enable private vulnerability reporting, Dependabot alerts, secret scanning, and push protection as repository visibility/plan permits.
5. Add protected-branch rules and required checks only after the supported CI runner matrix is defined.
6. Select a project license before accepting redistribution or publishing a stable release.

## Definition of release-ready

Release-ready means all 20 methods and defined projections work through the installed QProcess core; the real asserting tests pass in both transports; there are no enabled dead controls; intent/crash recovery, backup/restore, and import are proven with real persistence; rendering has no network dependency; and a clean Windows machine passes installation, ACL, lock, offline, and recovery qualification. Contract validation or a Qt smoke test alone is never release evidence.
