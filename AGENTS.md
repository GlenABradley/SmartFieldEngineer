# Shared build-workspace instructions

Read START-HERE.md, handoff/TO-GPT-SOL.md, decisions/AUTHORITY.md, and fullkit/contract/README.md before implementing. The selected agent’s model name does not alter the contract.

- Git root is this outer Build Artifact folder. Do not create nested Git repositories or commit local runtimes/venvs/data. Read GIT-MIRRORING.md for clean-clone setup.
- This folder is the durable local build home requested by Glen. Work on the application in fullkit/. Do not build inside the ChatGPT project mirror or its read-only sources/.
- Preserve root README.md, Validation.md and the release ZIP as supplied snapshots. Preserve references/ and the reviewed reference files inside fullkit/contract/reference/. Make revisions as new files or tracked application changes; never silently rewrite reviewed history.
- Spec 1.00 + adopted H1–H5 govern. C1/C2 are explicit proposals, not adopted scope. Read the current decision register; do not infer adoption from a schema or a historical reviewer’s imperative wording.
- Exactly twenty public RPC methods. Shipped Python/PySide6/QProcess/SQLite, separate Home blob stores, one trusted owner/two Homes. No hidden cloud/voice/connector/OCR/ASR/robot/payment implementation.
- All ledger mutations, including maintenance, cross execute_command and the writer boundary. No GUI SQL writes, fake confirmations, success stubs, blanket test skips or mock acceptance drivers.
- The application integration tests must fail honestly while implementation is missing. Contract validation and a Qt smoke test do not establish a running application or Windows qualification.
- Team roles and ally investiture are in team/. They confer collaboration responsibilities, not process identity, API keys, user authentication or automatic remote access. No new autonomous agent tasks are created by these documents.
- Glen manages cross-model collaboration. Prepare local review/handoff files unless he explicitly directs sending a message or starting a task. Do not contact another model merely because it is listed in the roster.
- Keep next actions, changed files, actual tests, failures and unresolved decisions in handoff/SESSION-LOG.md. Use short, concrete updates. Record platform/runtime evidence; do not claim a Mac test proves Windows locks, ACLs or power-loss behavior.
- Current source-corpus absence: the legacy code kit is present, but no populated customer office.sqlite with referenced evidence is supplied. Do not invent customer records or silently discard missing evidence.
- Keep user data/secrets out of the repository and logs. Use disposable test fixtures. Do not initialize the old Office constructor against a source ledger.
- Do not delegate to subagents unless Glen explicitly requests delegation or a later applicable instruction does so. The roster is descriptive; it does not authorize spawning.
