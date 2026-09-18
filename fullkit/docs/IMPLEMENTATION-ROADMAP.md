# Smart Field Engineer implementation roadmap

Updated 2026-09-18 against reviewed S04.1 `a94e3a7` (foundation `3c85b53`), merged to main in `fca57c1`, retaining CodeRabbit presentation `4fe4045` with corrected authority and sequence. This is an engineering status map, not a release claim or a replacement for the governing contract.

## Executive assessment

Smart Field Engineer is a well-specified pre-release workbench with a credible persistence and command foundation. Its strongest assets are the unusually detailed offline/durability contract, strict Home isolation model, preserved decision provenance, real fault-oriented tests, and honest visible failures for missing behavior.

The project is not yet a desktop application. The current implementation covers the first narrow vertical slice: provision two Homes, open and lock their stores, select a context, create/list jobs, and retrieve/replay durable receipts through the shared frame codec. S04.1 boundary hardening is complete. The next proposed work carries that boundary across a real process through S05; no second foundation pass or desktop screen build is scheduled here.

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
| `fullkit/tests/application/` | Real implementation tests | 44 application cases passed for S04.1 on Linux/Python 3.12.14; 41/macOS is historical foundation evidence. Grok reviewed the diff without rerunning tests. |
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
- Supports read-only inactive recovery inspection in the foundation, while denying mutation. F1 failed-switch restoration now preserves the snapshotted read-only flag; Backup API fixtures do not establish implemented restore or complete recovery-directory immutability.

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
| P0 | No installed core entry point or QProcess transport | The production boundary and supplied integration driver cannot run; current frame tests are in-process only. |
| P0 | No durable desktop semantic-intent journal | A process loss between send, commit, response, and acknowledgement cannot yet be reconciled from the future UI. |
| P0 | Most domain and command routes are unimplemented | Job updates, evidence, serial identity, office facts, holds, envelopes, backup, restore, and status still fail honestly. |
| P1 | Blob staging/publication/read cache absent | Evidence integrity, immutable documents, and safe preview depend on it. |
| P1 | Backup/restore/import absent | Core offline recovery and legacy migration promises are not demonstrable. |
| P1 | Desktop UI absent | There is no usable application shell, transport lifecycle, or stale-context clearing behavior. |
| P1 | Linux development is not reproducibly locked | No reviewed Linux wheel lock exists. Available host dependencies may support ad hoc checks; they do not establish the locked supported toolchain. |
| P1 | Windows qualification outstanding | Locks, aliases, ACLs, encryption observation, installation, printing, and power-loss behavior remain unproven. |
| P2 | No project distribution license | Repository visibility does not establish reuse or redistribution rights; the owner must select terms before a public release. |
| P2 | No CI/release automation | A premature workflow would either omit required Windows evidence or advertise incomplete checks; add it once a supported runner matrix is explicit. |

## Delivery sequence — frozen S04.1 → S10

This is a **derived status map**, not governing authority or permission to start a later block. Glen’s instructions and [adopted authority](../../decisions/AUTHORITY.md) govern. The [S04.1 execution packet](../../handoff/S04.1-PACKET.md) is completed and preserved; the [S05 handoff](../../handoff/NEXT-CODE-BLOCK.md) is the next proposed block; the [reviewed continuation sequence](../../handoff/GROK-CODE-BRAINSTORM-OPEN-WORK.md) supplies the subsequent milestone order. Older queue numbering and brainstorm implementation suggestions do not override the frozen packet or contract.

| Block | Scope | Required exit evidence |
|---|---|---|
| **S04.1 — complete, merged** | F1: preserve prior read-only flags on failed Home switch; F3: remove the Core executor, retain Application queue and StoreSession affinity, close admission before cleanup; F4: reject invalid internal create revision envelopes after replay/conflict and before mutation. | Observed 44 application cases passed, including F1 and two F4 regressions; schema/baseline passed. Grok passed the diff via Glen. Integration still fails collection; Windows/Qt qualification remains outstanding. |
| **S05 — next, proposed** | Real child entry, bounded streaming codec, asynchronous QProcess, source-only real test driver, durable write-before-send journal and process-loss reconciliation. | Real child PID/lifecycle; both transports agree; fragments/coalescing/oversize/EOF and stderr separation; journal failure sends nothing; pre-send/precommit/postcommit/pre-ack faults; **more than 50 pending intents** reconcile by individual receipt lookup with one mutation per intent. Unmodified integration tests collect and fail at absent behavior. |
| **S06 — pending** | Serial observe/assign/verify/recall/dispute and correction history, using the existing job-create boundary. | Same-ID two-Home isolation, revision/replay/foreign-receipt checks and immutable bind history. Evidence-dependent paths wait for S07; document pin assertions may still fail until S08. No document stub or job.update scope/track work. |
| **S07 — pending** | Evidence two-phase stage/publish, attach phase receipts, digest/size checks, orphan reconciliation, scoped read capabilities and photo observation. | Real stage/publish/fault/replay cases; foreign tokens do not consume peer state; expired/foreign read handles deny access; one evidence identity. Documents remain S08. |
| **S08 — pending** | Immutable documents/pins/offline rendering; interruption and office time/cost/notes/items/stock/envelopes; job.update scope/track with adopted C1/C2. | Pins survive correction/dispute; escaped offline artifacts; no negative stock or duplicate economics; exact resource tags and half-open conflicts; STALE_RESERVATION; sourced owner resume and transactional append-only scope linkages resolving only the named hold. Implement required read projections alongside their features. |
| **S09 — pending** | SQLite Backup API, verified archives, inactive restore/new store identity, maintenance activation and actual 0.2.0 import. | Uncheckpointed WAL survives standalone archive; peer Home unchanged; restored instance denies writes before activation; source inventory, stable IDs, full row dispositions, atomic import and exact replay. Actual customer-corpus demonstration awaits supplied ledger and referenced evidence. |
| **S10 — pending** | Minimal Qt Today/Job/Capture shell with required Inbox/Preview/Exceptions/Home workflows over S05 transport and journal. | Every enabled control works; stale callbacks and Home switches clear scoped state; real preview/print, restart and load/resize checks; no GUI SQL writes. No design-system expansion. |

S04.1 does not implement transport, journal, test driver, serial, evidence, documents, C1/C2, backup/import or Qt. C1/C2 are **adopted semantics, not implemented behavior**. F4 raises an internal error without a durable receipt; it does not invent a SCHEMA domain code. The frozen packet resolves the earlier brainstorm’s alternatives.

In S05, HOME_CONTEXT alone never authorizes a retry: first positively establish a fresh context for the original Home and working store, then reconcile that operation. Preserve the original UUID and semantic request for an authorized unknown receipt. Never rebind intents to a recovery instance or use the latest-50 status list as the journal.

### Separate release qualification gate

S10 completion is not release qualification and does not create S11a/S11b milestones. Packaging, clean Windows install/reinstall, NTFS handle aliases, ACLs, observed encryption, offline printing, mandatory Spec §13 faults and the complete offline demonstration remain a separate gate. Record actual target hardware/runtime, source and artifact hashes, failures and untested conditions. Process kill does not establish power-loss durability. No stage can claim complete conformance from contract checks or a Qt smoke test.

Engineering remains **provisional 152–240 hours**, not a measured remaining-work estimate. Backup/import/file-identity work is inside the existing bands. No schedule, budget or scope change is adopted by this roadmap.

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
