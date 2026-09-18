# Proposed next generation block — real process transport and test driver

Proposed by Sol on 2026-09-18 after foundation commit 3c85b53. This is a plan, not generated code or a passing result. First address reproducible Grok findings affecting the current boundary; record each correction/test and preserve reviewed baselines.

## Goal and boundary

Make the supplied integration tests collect against the real application and reach honest behavior assertions through an actual QProcess child and the development in-process codec. The immediate positive milestone is existing provision/select/job-create/list/receipt/replay parity across both transports. Serial/evidence/backup/import vectors need not pass yet; missing behavior must fail rather than skip or manufacture success.

## Planned code

| Place | Responsibility |
|---|---|
| apps/edge/__main__.py | Installed-module core entry and owner maintenance provision path; real Core/application/lock, stdout protocol only |
| apps/edge framing/diagnostics | Bounded incremental stream assembly; fragments/coalesced lines; oversized-frame drain/resynchronization; sanitized stderr/private diagnostics |
| apps/desktop/transport.py | Qt-thread QProcess owner, async send/read/error/exit callbacks, request-ID correlation and captured-context stale response discard; no GUI SQL |
| apps/desktop/intents.py | Minimum durable semantic intent publication before desktop mutation, original Home/store binding and receipt reconciliation after response loss; no blind new-operation retry |
| packages/application/testing/ | Source-only context-manager driver: real binary maintenance, raw codec for both transports, deterministic lifecycle/cleanup; excluded as a package from production wheel |
| tests/application + tests/transport | Real Qt event-loop/child tests, bounded timeouts, crash/restart/parity, journal and framing failures |

Test driver launch/maintenance/raw_frame use existing application behavior. Helper methods needed by later read-handle/blob/snapshot tests must use real consumers when those features exist; they cannot return fake successful data in this block. The driver is not a new RPC/service.

## Strategy

1. Turn confirmed review defects into focused failing tests and smallest fixes before expanding transport. Keep the 20-method registry and immutable artifact tests.
2. Add the installed-module child and its bounded stream codec first; exercise real standard input/output and clean EOF/termination. Arbitrarily fragmented input must never require unbounded buffering. Protocol and diagnostics remain separate.
3. Implement QProcess as an asynchronous Qt object on its owning Qt thread. Use signals and bounded event-loop waits in the test harness; do not call blocking future.result() on the desktop UI thread. Reuse the existing codec/application inside the child, where serialized persistence is appropriate.
4. Add write-before-send journal publication/flush and same-intent operation.get reconciliation. On restart obtain a fresh session context for the original Home/store; never rebind an intent to a recovered store. A positively authorized unknown receipt permits identical-operation resend, not presumed failure. Test more than 50 open intents without relying on recent-operation lists.
5. Add the test-only driver package and identical positive/negative parity cases. Maintenance releases the current core writer, invokes the real maintenance binary, then reconnects with fresh context; retained old context is never silently valid. Exclude the testing package from wheel discovery and verify the production wheel contains required schemas/migrations but no test driver/fault hooks.
6. Run the supplied two-Home file unmodified. Record its new actual failure locations: it should fail on missing serial/evidence/etc behavior, not ImportError. The checker must report integration failure honestly once the driver exists; tooling readiness remains separate from application conformance. Do not redefine a failing suite as environment acceptance.

## Completion evidence

Both transports show the same durable first-command results and Home denials; real QProcess child PID/lifecycle is observed; malformed/fragmented/oversized frames and stderr noise do not corrupt responses; lost-response lookup/restart causes one mutation; journal publication failure sends no command; stale contexts/callbacks and inactive recovery intents cannot mutate; shutdown/maintenance leave no competing writer; an isolated installed wheel runs the real child entry. Test logs/next failed acceptance assertions and platform are recorded locally and summarized in SESSION-LOG.md.

The full serial vertical slice is the following block (S06), using the same transaction/receipt boundary. Windows alias/ACL/hardware qualification remains a real later gate. No cloud, voice, connector, payment or additional public method enters this work. Estimate remains provisional 152–240 hours; report concrete new complexity rather than hiding it.
