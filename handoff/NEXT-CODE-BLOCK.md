# Proposed next generation block — real process transport and test driver

Originally proposed after foundation 3c85b53; reconciled 2026-09-18 after Grok-reviewed S04.1 a94e3a7 merged in fca57c1. This remains the existing S05 plan, not generated code or passing evidence. F1/F3/F4 are complete. Glen authorized merging and documentation reconciliation now; execution is deferred to a later instruction on a fresh branch from then-current main, not either repair branch. Spec 1.00 + H1–H5 + Addendum 1.00.2 govern. Preserve the completed S04.1 packet and the historical handoffs.

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

1. Confirm the starting main contains reviewed S04.1 and record the actual host/toolchain baseline. Preserve its fixes, the 20-method registry and immutable artifact tests. Do not repeat a general foundation-improvement pass; report a concrete blocking defect if one is discovered.
2. Add the installed-module child and its bounded stream codec first; exercise real standard input/output and clean EOF/termination. Arbitrarily fragmented input must never require unbounded buffering. Protocol and diagnostics remain separate.
3. Implement QProcess as an asynchronous Qt object on its owning Qt thread. Use signals and bounded event-loop waits in the test harness; do not call blocking future.result() on the desktop UI thread. Reuse the existing codec/application inside the child, where serialized persistence is appropriate.
4. Add write-before-send journal publication/flush and same-intent operation.get reconciliation. On restart obtain a fresh session context for the original Home/store; never rebind an intent to a recovered store. A positively authorized unknown receipt permits identical-operation resend, not presumed failure. Test more than 50 open intents without relying on recent-operation lists.
5. Add the test-only driver package and identical positive/negative parity cases. Maintenance releases the current core writer, invokes the real maintenance binary, then reconnects with fresh context; retained old context is never silently valid. Exclude the testing package from wheel discovery and verify the production wheel contains required schemas/migrations but no test driver/fault hooks.
6. Run the supplied two-Home file unmodified. Record its new actual failure locations: it should fail on missing serial/evidence/etc behavior, not ImportError. The checker must report integration failure honestly once the driver exists; tooling readiness remains separate from application conformance. Do not redefine a failing suite as environment acceptance.

## Completion evidence

Both transports show the same durable first-command results and Home denials; real QProcess child PID/lifecycle is observed; malformed/fragmented/oversized frames and stderr noise do not corrupt responses; lost-response lookup/restart causes one mutation; journal publication failure sends no command; stale contexts/callbacks and inactive recovery intents cannot mutate; shutdown/maintenance leave no competing writer; an isolated installed wheel runs the real child entry. Test logs/next failed acceptance assertions and platform are recorded locally and summarized in SESSION-LOG.md.

The full serial vertical slice is the following block (S06), using the same transaction/receipt boundary. Windows alias/ACL/hardware qualification remains a real later gate. No cloud, voice, connector, payment or additional public method enters this work. Estimate remains provisional 152–240 hours; report concrete new complexity rather than hiding it.


## Reviewable S05 acceptance matrix

These expand the existing completion evidence; they are planned checks, not results or extra product scope.

| Boundary | Exercise | Required observation |
|---|---|---|
| Installed child | Launch the installed module, observe PID, close stdin and terminate/restart | Real process owns Core; no source-tree-only dependency; lifecycle releases the writer |
| Stream framing | Fragment/coalesce requests; oversized terminated/unterminated input; EOF; malformed UTF-8 | Bounded buffering and correct resynchronization; diagnostics cannot contaminate stdout frames |
| Qt transport | Use signals/event loop, concurrent pending request IDs, error/exit callbacks | Correlated responses on the owning Qt thread; no blocking GUI waits; no stale-context delivery |
| Intent publication | Fail durable journal publication before send | No command reaches the child and no business mutation occurs |
| Process loss | Inject before send, before commit, after commit/before response, before acknowledgement | Restart resolves the original operation; committed work is not duplicated; unresolved state is retained |
| Receipt authorization | Reacquire original Home/working store; test foreign/stale context and recovery instance | HOME_CONTEXT alone is never retry permission; only positively authorized unknown receipts allow identical semantic resend |
| Pending history | Reconcile more than 50 pending intents, including lost responses to committed commands | Individual operation lookup resolves all; no reliance on recent-status truncation |
| Maintenance | Stop/release serve writer, invoke real maintenance, reconnect | No competing writer; fresh context; original sessions cannot mutate |
| Transport parity | Same positive and denial cases through QProcess and in-process development driver | Equivalent semantic receipts/denials with real persistence; compare generated IDs/times only where contractually meaningful |
| Packaging | Inspect/install wheel outside source checkout | Schemas/migrations and real child included; testing driver and fault hooks absent |
| Supplied integration | Run original two-Home vectors unchanged | Collection succeeds; absent domain capabilities fail honestly; exact next failure locations are recorded |

## Handoff and stop line

At the later generation trigger, branch from current main and record its exact SHA. Reuse the hardened Core/Application/StoreSession/HomeWorkspace ownership; the GUI gains no SQL writer. C1/C2 remain adopted but belong to S08. No serial/evidence/document implementation, backup/import, additional RPC, screens or success stubs enter S05.

The full environment needs supported Python/Qt dependencies before real QProcess evidence can be claimed. The prior Linux 3.12.14 S04.1 run lacked PySide6; it cannot be repurposed as S05 transport evidence. Keep integration/toolchain failures visible and record the actual versions and commands.

Stop after the bounded S05 implementation and its reviewable evidence. Grok reviews the actual new diff through Glen before S06. The larger S06–S10 order and provisional 152–240-hour estimate remain unchanged. No S05 code was generated in the merge/documentation session.
