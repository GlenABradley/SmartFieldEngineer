# Store foundation — first implementation milestone

Implemented locally on 2026-09-18 against effective contract 1.00.2. This is an application foundation, not the complete Slice 1 application. Current development wheel: 1.0.2.dev1.

## Implemented boundary

- HomeWorkspace provisions exactly two initial Homes through a named serialized maintenance execution boundary. A private SQLite index contains labels/identities/local roots and the provision intent/result; list_homes exposes only the five public descriptor fields, never paths.
- A caller-supplied operation UUID and exact labels identify provisioning. Restart/retry returns the durable prior result. Different labels under the same operation UUID yield OPERATION_ID_CONFLICT. A second fresh provisioning cannot overwrite an existing workspace.
- Each Home has its own ledger, blob root, staging, read cache, client intent directory and provisioned sibling backup directory. Jobs, job events, audit and durable operations are implemented for job.create with empty capture_refs; remaining business tables and blob/backup operations are not implemented yet.
- StoreSession acquires the writer lock before any writable SQLite connection. A single executor thread owns that connection and handle for their lifetime. Missing selected ledgers are not created. Store metadata must match the requested Home/store/flags; store/ledger aliases outside the approved root are rejected.
- Forward-only numbered SQL resources live in migrations/local, are packaged in the wheel and loaded with importlib.resources. Schema changes, identity, schema_history, internal migration receipt and user_version commit together. No executescript implicit commit. Existing migration hashes and newer schema versions are checked before applying changes.
- Connections use WAL, synchronous FULL and foreign keys. Read-only inspection uses mode=ro and query_only; it does not migrate or execute maintenance. Its original closed ledger bytes remain unchanged in tests. SQLite read-only WAL inspection may create bookkeeping sidecars; this is not a claim of byte-for-byte immutable recovery-directory inspection.

Internal home.provision/store.migrate names are maintenance identifiers, not additional public RPC methods. The first ordinary command envelope, canonical business fingerprint, fact/audit/operation receipt transaction, selected session context and 20-method registry are now implemented for the first job-create slice. Other command branches remain unfinished. Internal maintenance receipts do not masquerade as complete public RPC receipts.

## Writer platforms

Windows code uses CreateFileW with no sharing, a noninherited retained handle, file/volume identity and final paths obtained from handles. It checks the opened lock against a handle-resolved approved root and conservatively permits only fixed local NTFS volumes. Other filesystems fail until explicitly supported and qualified. This code has not been executed on Windows; junction/subst/case/8.3 aliases and ACL commissioning remain required.

macOS/Linux use an advisory flock and fstat/file-handle path identity, explicitly labeled posix_dev. Tested on this Mac only; this does not establish Windows exclusion or production filesystem support.

API references: [CreateFileW](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-createfilew), [handle identity](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfileinformationbyhandle), [final path](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getfinalpathnamebyhandlew), [volume path](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumepathnamew), [volume information](https://learn.microsoft.com/en-us/windows/win32/api/fileapi/nf-fileapi-getvolumeinformationw).

## Failure and recovery truth

Store directories are built before the index transaction publishes their identities. Ordinary precommit failure rolls back registration and removes only directories created by that attempt. Abrupt process death can leave unregistered stores: subsequent provision refuses to silently adopt or delete them. An explicit orphan review/recovery tool remains to implement.

Once index commit has been attempted, failure is potentially an acknowledgement failure. Created stores are preserved, never deleted merely because the caller did not receive success. A committed receipt can be replayed; an unpublished orphan requires review. Filesystem and index are not a single atomic transaction. Mac directory flushing and SQLite FULL are exercised; Windows directory durability/power-loss qualification is pending.

Core frame parsing now runs on the caller thread. The Application executor serializes selected-context authorization; the StoreSession executor retains SQLite connection and lock affinity. HomeWorkspace retains its maintenance executor. Core and Application close admission before application cleanup is enqueued; accepted application work runs before cleanup. Desktop intent recovery and QProcess orchestration remain unfinished. No live customer root was provisioned during this work; fixtures and the installed-wheel probe used disposable directories.

## Evidence

18 real store foundation tests pass on this Mac: persistence/restart/replay; two-Home descriptor/layout separation; transactional migration failure; index publication failure; foreign identity denial; missing-ledger noncreation; independent peers/same-store exclusion; real competing process and killed-process lock release; POSIX directory aliases; approved-root enforcement; read-only inspection/write denial; foreign/unknown index targets; parallel retries; killed provisioning/orphan retention; tampered migration history; future-schema rejection; ledger symlink denial; input rejection without filesystem effects; and lost index-commit acknowledgement.

A further 23 real raw-command/application tests pass: strict parser bounds/duplicates/nonfinite numbers; schema-invalid commands; Home/context/operation isolation; same-ID jobs; restart/replay and fingerprint conflict; durable failed STALE_JOB receipt; concurrent retries; failed switch recovery/generation; high-water paginated job reads/cursor expiry; transactional commit failure; lost commit acknowledgement; killed precommit process; application checks independent of transport; inactive recovery guard before historic replay; and packaged schema parity. The recovery test uses an explicitly labeled Backup API fixture, not the unimplemented restore operation.

Together **41 application foundation tests + 15 workbench + 8 inventory = 64 passing tests**. All 479 positive/503 negative schema specimens also pass. Baseline 42 substantive hashes and supplied root snapshots remain unchanged. The existing application integration file still fails collection on absent packages.application.testing; its five vectors/domain assertions are untouched.

A development wheel was built, installed with a hash-verified locked subset of schema dependencies into a disposable fresh venv, and exercised with isolated Python from outside the source tree. It provisioned/opened two actual stores using installed migration resources and ran real select/create/list/operation receipt/replay through the codec. This verifies foundation/parser/first-command packaging only, not Qt/QProcess, installer or Windows runtime qualification. Evidence: reports/Environment-Validation.json, store-foundation-tests.log, Store-Foundation-Installed-Wheel.json and store-foundation-wheel-build.log (local generated reports).

S04.1 F1/F3/F4 is implemented; stop here for Glen-mediated diff review. S05 real integration driver/QProcess transport remains a separate block. No success stubs or acceptance skips were introduced.

## Current raw application surface

The twenty-method registry and all request schemas are packaged as byte-identical copies of preserved authority. The implemented result paths are home.list, session.select_home, job.list, operation.get and job.create (empty capture_refs). Known unfinished methods/branches yield Internal error, not synthetic success; unknown methods yield Method not found. The full mandatory suite remains incomplete.

Frame parsing validates UTF-8/newline/1-MiB bounds, rejects duplicate keys and NaN/Infinity, requires UUID request IDs and closed shapes, and rejects floating numeric payloads. Responses echo the original request ID. Session/Home authorization lives in packages.application.session and precedes receipt/job lookup; storage independently checks Home identity and inactive writes. Successful selections advance generation, including same-Home selection. Failed target acquisition reopens the prior valid context with fresh generation when possible, otherwise clears it. Current code has no stage/read capabilities yet to invalidate.

Canonical fingerprints exclude operation/request/session/generation IDs and include the original semantic fields plus selected store instance. Facts, job event, independently stamped principal audit and terminal receipt share one transaction. Accepted duplicate-job rejection is a durable failed STALE_JOB receipt. Missing/foreign operations are identical empty HOME_CONTEXT errors. Replay is checked before mutable state or unfinished branch evaluation. Inactive recovery write denial precedes replay, while historic receipts remain readable.

Job-list pagination is generation-bound keyset over creation event sequence + job UUID, with captured high-water, 120-second opaque cursors and a 100-row limit. New jobs wait for refresh. Other views remain unimplemented.

Windows principal observation uses process-token SID APIs; on Mac the principal is explicitly posix_dev:uid. Windows execution/qualification remains pending. References: [OpenProcessToken](https://learn.microsoft.com/en-us/windows/win32/api/processthreadsapi/nf-processthreadsapi-openprocesstoken), [GetTokenInformation](https://learn.microsoft.com/en-us/windows/win32/api/securitybaseapi/nf-securitybaseapi-gettokeninformation), [ConvertSidToStringSidW](https://learn.microsoft.com/en-us/windows/win32/api/sddl/nf-sddl-convertsidtostringsidw).

Owner-protected production diagnostics, complete public-method implementations, full recovery directory immutability, ordinary migration/upgrade corpus qualification, installer resources and desktop intent journal remain required before release.


## S04.1 — context recovery and execution boundary hardening

Implemented against application foundation `3c85b53` on a separate code branch based on main `c4bda07`; no CodeRabbit presentation commits are included.

- F1 snapshots `self.store.readonly` before closing the previous store and supplies it when reopening after target acquisition fails. The original target error is retained, recovery stays read-only, generation advances, and cursors remain invalidated.
- F3 removes only the Core executor. Application, StoreSession and HomeWorkspace executors remain. Core and Application set their closed flags before application shutdown/cleanup admission.
- F4 checks the internal job.create revision envelope after replay/conflict and before mutable inspection. Invalid expected/scope revisions raise StoreError with no job, event, audit or operation rows. Nonempty capture_refs remains NotImplementedError; public floating revisions remain invalid params.

Observed on Linux x86_64, Python 3.12.14, SQLite 3.53.1, pytest 9.1.1 and jsonschema 4.26.0 in a disposable test venv: baseline 41 application cases passed; three new cases initially failed at the named defects; after fixes 44 application + 15 workspace + 8 inventory cases passed. All 479 positive/503 negative specimens passed, with 212 definitions and exactly 20 methods. Baseline verifier checked 41 files with zero mismatches and two explicit Finder metadata exclusions; preserved root files were unchanged.

The extracted Backup API test fixture explicitly closes setup connections before snapshotting ledger bytes, avoiding delayed connection cleanup/checkpoint effects in its assertions. It is still a fixture, not implemented restore. Original foundation evidence above remains historical.

The existing environment checker exits 1: PySide6 is absent, so the Qt toolchain probe fails and environment readiness remains false. The unmodified two-Home suite exits 2 on missing packages.application.testing. Python 3.12/Linux checks do not establish the pinned Python 3.13 supported toolchain or Windows qualification. No wheel built; version remains 1.0.2.dev1. No S05, schema/contract, C1/C2 implementation or other application features added.
