# Sol — current goals and task register

> [!IMPORTANT]
> Current status — 2026-09-18: S04.1 is implemented in a94e3a7, Grok-reviewed through Glen, and merged to main in fca57c1. [S05 transport/journal/test-driver plan](NEXT-CODE-BLOCK.md) is next, **not implemented or authorized for generation in this documentation session**. Start its later execution on a fresh branch from then-current main. The numbered queue below is historical where it differs: S05 includes journal/process-loss/>50-intent proof; S06 serial; S07 evidence; S08 documents/interruption/office/job.update+C1/C2; S09 backup/restore/import; S10 minimal Qt shell; release qualification is separate. C1/C2 remain adopted but unimplemented.


Updated 2026-09-18 at Glen’s request after switching this existing session from Astra to Sol. This is the current execution plan; Astra’s handoff and the reviewed contract remain preserved. No new agent task or external message was created.

## Context accepted

Glen asked for a self-contained build artifact, a durable local workshop, GPT/Grok ally roles, an intimate Sol handoff and a second Git-readiness pass. Those preparation tasks are complete. Glen now requests continuity review and updated tasks/goals. Wider product visions and science-fiction explorations remain context, not additions to Slice 1.

Local HEAD is `89379c9` (`mod 1`) after `5ab201f` (`initial commit`); the working tree was clean on takeover. Glen supplied Grok’s report that he pulled this commit and supports moving to implementation. Glen remains the ferry for external collaboration and Git mirroring. The earlier “No commit or push” log records Astra’s actions at that time; it is not a statement that Glen never published the work.

Reviewed sources: the available conversation in this task, original pasted assignment, AGENTS.md, START-HERE.md, Astra’s handoff, decision register, second-pass review, team charter, current contract entry/implementation map, adopted H1–H5 addendum, relevant Spec 1.00 payload rules, working integration interface/tests and current environment evidence. This review does not claim complete access to every originating conversation or an audit of every archived source line.

## Goals and completion evidence

| Goal | Current state | Evidence required to complete |
|---|---|---|
| G0: take over with accurate shared context | Complete | This plan, updated team status and appended session entry |
| G1: durable Home/store/context/command foundation | In progress; local store and first command slice verified | Real persistence, schema migrations, writer ownership, context-first denial and atomic fact/audit/receipt transactions tested through the frame parser |
| G2: real two-Home vertical slice | Not started | Same job/asset IDs, different serials, explicit switching and foreign/unknown receipt denial through both real transports; integration failures advance to behavior assertions |
| G3: full Slice 1 offline workflow | Not started | Evidence, serial history/pins, office records/stock/envelopes, holds, crash/intent recovery, verified backup/inactive restore and import tests pass |
| G4: Windows release qualification | Not started | Clean install/reinstall, alias locks/ACLs, observed encryption status, offline print, target hardware and complete mandatory demonstration receipts |

G2 is an intermediate milestone, not a passing-release claim. Removing ImportError alone is not completion. G3/G4 require the additional mandatory tests in Spec §13 and the implementation map, beyond the five supplied vectors. Engineering remains provisional 152–240 hours; no new scope or estimate adopted.

## Task queue

| ID | Task | State / dependency | Concrete completion |
|---|---|---|---|
| S00 | Reconcile setup and mirror history | Done | Local HEAD verified; history appended rather than rewritten |
| S01 | Recheck baseline/tooling readiness | Done | 42 substantive baseline hashes; 15 workspace + 8 inventory tests; 479 positive / 503 negative schema specimens; Qt/QProcess and SQLite probes passed |
| S02 | Review artifact 1.00.1 C1/C2 | Done; Glen adopted both 2026-09-18 | decisions/Addendum-1.00.2.md and current-contract.json record the exact approval; effective contract 1.00.2 |
| S03 | Implement store identity, migrations and writer boundary | Local foundation implemented; Windows qualification pending | Provision two real Home stores; lock before SQLite; durable metadata and migration transaction; target Windows handle identity kept explicit |
| S04 | Implement strict codec, context and command/receipt boundary | First job-create boundary implemented; remaining branches pending | Bounded UTF-8 frames, duplicate/nonfinite rejection, exact 20-method registry, context-first lookup, canonical fingerprint, atomic receipts and replay/conflict tests |
| S05 | Connect real test driver and transport spike | Next | launch/maintenance/raw_frame call real application; QProcess child/event loop and dev in-process use identical codec/dispatch; no placeholder success paths |
| S06 | Build job + serial vertical slice | After S04/S05 | Real create/observe/assign/verify/recall; same-ID Home isolation and foreign receipt denial tested; unsupported unfinished behavior fails visibly |
| S07 | Evidence attach, read handles, immutable documents and serial corrections | After S06 | Durable stage/publish/reconciliation, scoped capabilities, offline escaped artifact and unchanged pins after correction/dispute |
| S08 | Office records, stock, envelopes and interruption rules | After foundation; resume/scope portions depend on S02 | No negative usable stock; exact tags/half-open overlap; sourced gates and named-hold resolution follow adjudicated semantics |
| S09 | Intent journal and crash recovery | Start with S04, finish before durability claims | Real fsync/atomic journal; faults before send/commit/response/ack; reconcile more than 50 operations without duplicate mutation |
| S10 | Backup, inactive restore and legacy import | After relevant stores/blobs/receipts | Backup API/WAL verification, unchanged peer Home, new inactive store ID, replay/atomicity/conflict tests; real corpus demonstration awaits supplied customer ledger/evidence |
| S11 | Qt shell, packaging and Windows commissioning | After raw boundaries work | Every enabled control works; stale-context display cleared; install and mandatory release loop proven on target Windows |

The first storage implementation is complete locally; see fullkit/docs/STORE-FOUNDATION.md. The first strict codec/context/atomic job-create receipt boundary is also verified. Next is S05, then S06 serial behavior, with remaining S04 branches added through the existing boundary. Do not make the entire supplied test file appear green by stubbing unfinished methods. Commit-sized milestones should describe behavior/tooling plainly; Glen controls mirroring.

## Adopted decisions — 2026-09-18

**Artifact 1.00.1 C1:** Glen adopted the explicit sourced owner track_event as the resume decision, with independently stamped local principal and an unmistakable UI action. Preserve reason, current applicable hold and relevant source/evidence gates; do not add a method or payload field. Verify initial track entry separately from resuming a held job so implementation does not accidentally require a nonexistent hold for every first start.

**Artifact 1.00.1 C2:** Glen adopted transactional append-only effective-scope linkages for unresolved holds when scope advances. Keep original scope/interruption facts, move no resolved hold back to unresolved, and resolve only the hold explicitly named by a subsequent resume. Test multiple holds and transaction failure. This adopted semantic correction is recorded as an overlay; the reviewed spec remains preserved.

Glen explicitly approved both: “i agree. adopt C1/C2. i approve.” See decisions/Addendum-1.00.2.md. S02 is complete; resume/scope semantics are no longer blocked.

## Remaining inputs and limits

- Closed actual legacy customer ledger plus referenced evidence for the real import demonstration. The preserved 0.2.0 kit and disposable fixtures suffice to implement mappings now.
- Target Windows machine and qualification evidence. Mac toolkit results establish neither Windows writer exclusion nor release readiness.
- Project/distribution license decision and dependency notices before shipment.

Current environment result: Home/store foundation implemented and ready for local development; application integration exits 2 because packages.application.testing is missing; application release and Windows qualification remain false. Logs: reports/Environment-Validation.json and the named check logs. The earlier takeover was a review-only step; the subsequent foundation implementation is recorded in SESSION-LOG.md. No commit, push or external contact.
