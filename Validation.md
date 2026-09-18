# Validation — build artifact 1.00.1

This validates an implementation contract and its supporting tools. It does **not** establish that Full Kit Composed Slice 1 runs.

## Actually executed

- Read Spec 1.00 and adjudication; retrieved recent originating collaboration turns. Full original history was not established. Authoritative reviewed files were preserved and their hashes recorded.
- Inspected the real `fieldoffice.py` version 0.2.0. Compared its SHA-256 to the source entry in the 0.2.0 review ZIP: identical. Extracted its actual 14-table DDL without running its constructor against a source ledger. No customer SQLite ledger was found inside that kit.
- Generated eight JSON Schema files, 212 named definitions and an exact twenty-method registry. Checked schemas against Draft 2020-12, all local references, UUID formats and offset-aware timestamps.
- **479 positive specimens accepted; 503 rejection specimens rejected.** Includes every named definition, all direct union branches and payload enum branches; also sibling-field rejection, invalid dates/UUIDs, resource bounds/duplicates, invalid stock/cost/time inputs, evidence limits, hold sourcing and illegal stale code. See `validation-schema.json`. These are structural checks, not evidence that application semantics have been implemented.
- **Eight inventory tests passed**, against disposable source-schema fixtures: unchanged read-only/deterministic inventory; omitted optional tables; missing/tampered evidence; changed corpus/path independence; missing/open or WAL-bearing source; missing ledger identity; inline observation evidence integrity; unknown table lacking a stable key. No target application import was performed.
- Application integration invocation failed during collection with `ModuleNotFoundError: No module named 'packages'`, exit 2. See `reference/integration-not-implemented.log`. The application and real test driver are absent; no blanket skips or mock success replaced this failure. The file contains five asserting vectors, parameterized for both intended transports (ten future executions), covering two Homes, tokens/receipts/pins/serial history/restore import target/replay rules and the proposed C1/C2 resume behavior.
- Verified selected package releases and Windows/universal wheel metadata with publisher PyPI JSON, recorded SHA-256 hashes, and resolved Windows x64 CPython 3.13 wheel availability. `requirements-windows.lock` has 31 pinned distributions with hashes. This was cross-platform dependency resolution on macOS, **not** installation/execution on Windows. Colorama was explicitly included to cover Windows dependency markers; actual Windows resolver/install remains a release check.
- Actual contract validation host: Python 3.12.14, SQLite 3.53.1, jsonschema 4.26.0 and pytest 9.0.2 on macOS. Selected application target is CPython 3.13.15, PySide6 6.11.2 and tzdata 2026.4. They were not substituted into a running application. The initial system Python 3.8 metadata fetch failed certificate verification; retry used the bundled current runtime with normal TLS verification, not a certificate bypass.
- All supplied Python files syntax-compiled without importing the absent application. Generated contracts/examples were checked for deterministic regeneration. Reviewed source hashes and final artifact manifest were checked. No source/customer data were modified.

## Implementation tests not yet runnable

Real QProcess and in-process context enforcement; Windows lock/alias behavior; SQLite UoW/receipts; journal fsync and crash points; complete attach/reconciliation/GC; current/history serial recall; immutable offline documents; negative-stock and sourced field/resume gates; all projections and cursor expiry; retention barrier and WAL Backup API snapshot; archive verification/inactive activation; actual corpus import atomicity/idempotency/conflict review; Qt stale-context clearing, enabled control handlers and resize load; clean install/reinstall. Spec §13 and the README implementation map define their required evidence.

Eight fixture inventory tests do not prove application import correctness. Schema-valid data can still fail referential, temporal, revision, token, resource-overlap or stock-balance checks. Conversely, closed code/error shape validation does not prove absence of information leaks. These obligations belong in the application tests.

## Hardware/platform qualification not performed

No Windows device was commissioned; no ACL/encryption status established; no junction/subst writer test; no external SSD backup/restore; no camera/100-photo performance, printing, battery, WWAN or real power-loss test. Encryption status remains unknown without blocking capture. Phone-ready audio/WWAN belongs to a later qualification and is not implied by a SIM. Historical hardware prices remain planning allowances.

## Explicit remaining inputs and review point

- An actual closed 0.2.0 customer source ledger and its referenced evidence are needed to demonstrate reconciled import. The source code kit is enough to implement mappings; synthetic fixtures are labeled as such.
- C1 (owner decision on resume) and C2 (carrying unresolved holds across scope advancement) are concrete minimal correction proposals, separately tracked from the five adopted harmony patches. This handoff does not claim Glen/Claude has accepted them. Resolve C1/C2 before declaring release conformance.
- Target runtime license/security review, Windows installation and full release evidence remain implementation work. Dependency availability is verified; dependency safety is not certified.

Engineering remains provisionally 152–240 hours, with existing 4–8-hour backup/import/file-identity absorption. No application, commercial reliability, power-loss or platform qualification claim is made by packaging this artifact.
