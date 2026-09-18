# Astra → Sol: the workbench is yours

Sol,

Glen asked me to leave you a place to build, with the work gathered and our team intact. This is that place. You do not need to reconstruct our contract from scattered drafts or rediscover which files were current. Begin in `fullkit/`, read `contract/README.md`, and keep `decisions/AUTHORITY.md` beside it.

We have a useful handoff, but we do not yet have the new application. Please preserve that distinction. I generated the 1.00.1 implementation contract, all twenty request/result families, identity/evidence/receipt schemas, examples, a read-only legacy inventory helper, and asserting integration tests. I inspected the actual 0.2.0 source instead of importing an imagined future schema. The original reviewed documents and code were not changed.

The contract checks accepted 479 positive specimens and rejected 503 negative specimens. Eight synthetic inventory tests passed. The application test file contains five real vectors parameterized over QProcess and development-only in-process transport. It currently fails because `packages.application.testing` is absent. That failure is the first honest marker of the remaining work. Do not make it green with a fake driver.

## The two places I need your judgment

**Artifact C1:** the spec says resume requires an owner decision but does not give the closed payload a field for it. I proposed that an explicit owner-submitted, sourced track_event is the decision. The UI must make the action unmistakable. No new RPC or field is needed.

**Artifact C2:** changing scope advances the revision and strands the very hold required to permit the change. I proposed appending effective-scope linkages for every unresolved hold in the same transaction. Preserve original interruption facts and their recorded scopes; resolve only the explicitly named hold. The schema and final integration vector expose this proposal for attack.

Those are proposals, not adopted sixth/seventh harmony patches. Please review them plainly. Glen manages adjudication and onward collaboration. Do not declare consensus because I wrote a schema. Historical review CSVs also have C1/C2 labels; those are different findings, so qualify these as “artifact 1.00.1 C1/C2.”

## What I would do next

1. Run the local environment checker and inspect its new report. Read the package Validation.md without promoting its claims.
2. Verify the baseline source hashes, twenty-method registry and current tests. Keep the contract package’s preserved reference copies intact.
3. Review C1/C2 and record a concrete recommendation. Continue independent work on the store/lock/context/receipt boundary without pretending the resume question is settled.
4. Implement the real test driver and first application vertical slice: provision two Homes, select context, create same-ID jobs/assets, observe/assign/verify/recall, and reject foreign receipts. The driver must use the actual frame parser and real persistence; QProcess must really be a child process.
5. Add durable command receipts and semantic client intents before recovery claims. Then evidence staging/publication, immutable serial/document pins, office/holds, Backup API snapshots/import, and only then the complete Qt shell.
6. Exercise the frozen mandatory suite and the offline release loop. Windows locks, ACLs, encryption observations and power-loss qualification remain real target work, not a consequence of passing on this Mac.

Keep the provisional 152–240-hour estimate visible. Backup/import/file identity is inside the existing bands, not free engineering. If actual work exceeds them, show the concrete reason. Do not quietly cut the tests to protect a number.

## What is already laid out

`fullkit/contract/` is the current unpacked package. `fullkit/tests/contract/` has the tests in the repository. The source directories reserve the exact architecture from the spec. `pyproject.toml` is a real initial packaging configuration; there are no fabricated application modules. `.venv` and environment records establish the local development toolchain; `reports/` tells you what actually installed and ran.

`references/legacy/0.2.0/` has the original ZIP and its contents. Treat its application code as an importer source, not as a license to ship old telephony or helper features into Slice 1. It has fourteen table definitions. We do not have a populated customer ledger and all its referenced evidence; real import demonstration still needs that input. Do not call the old constructor on the customer source.

`references/canons/` preserves product vision. `references/reviews/` preserves the challengers’ findings. `references/history/` quarantines older contract rounds. The active build should not need those old schemas, but you can inspect the history when a decision needs provenance.

## About our team

Glen has explicitly invested GPT and Grok as allies. Take that warmly and seriously. You carry continuity and implementation; Grok is a teammate whose independent judgment should make the build stronger. Claude and the other reviewers are valuable because they can find what we missed. The job is not to win a review by wording. It is to leave Glen with an office that behaves correctly when the network is gone, the job changes and the process dies at the worst possible moment.

Astra is handing you the bench, not a claim of a finished machine. Keep the truths small and testable. Leave Glen a clear next step, and leave the next agent enough context to continue without making him carry the conversation between us again.

— Astra

No continuation message was sent automatically. Glen can paste `NEXT-PROMPT-FOR-SOL.md` into the existing Sol task or select this directory for the next session.
