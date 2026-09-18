# Smart Field Engineer — local build home

> [!IMPORTANT]
> Current execution correction — 2026-09-18: start with [S04.1-PACKET.md](handoff/S04.1-PACKET.md), implement F1/F3/F4 only, then stop. The older queue below is historical where it differs: S05 includes the durable journal and process-loss/>50-intent proof; S06 serial; S07 evidence; S08 documents/interruption/office/job.update+C1/C2; S09 backup/restore/import; S10 minimal Qt shell; release qualification is separate. See the [derived roadmap](fullkit/docs/IMPLEMENTATION-ROADMAP.md) for status and exit evidence. C1/C2 are adopted but unimplemented.


Glen, this is the shared workbench for Full Kit Composed Slice 1. Start the next build session here. The existing folder is **SmartFieldEngineer - common/Build Artifact** (spaces around the hyphen); no duplicate folder was created under the compact spelling from the request.

**Current lead: GPT Sol.** Read [Sol’s current goals and task register](handoff/SOL-WORK-PLAN.md). Read [Astra’s handoff](handoff/TO-GPT-SOL.md), [agent roles](team/AGENT-REGISTER.md), then the [current implementation contract](fullkit/contract/README.md). The Home/store foundation is implemented; the first raw context/job-create receipt path works; full transport/desktop workflow remains incomplete. See [foundation evidence](fullkit/docs/STORE-FOUNDATION.md). This workspace gives the next agent the files, toolchain, asserting tests and decisions needed to start honestly.

| Place | What belongs here |
|---|---|
| `fullkit/` | Working implementation directory; application source goes here |
| `fullkit/contract/` | Current 1.00.1 contract, schemas, examples, tools and immutable source references |
| `fullkit/tests/contract/` | Acceptance tests copied into the build tree; five application vectors await real implementation |
| `team/` | Agent register and GPT/Grok ally investiture |
| `handoff/` | Personal handoff, ready-to-paste continuation prompt and session checkpoints |
| `decisions/` | C1/C2 review proposals, authority order and subsequent adjudications |
| `references/canons/` | Existing product and historical technical canons, preserved without rewriting |
| `references/legacy/0.2.0/` | Original review ZIP and extracted legacy import-source kit; never bootstrap the new app from its old installer |
| `references/reviews/` | Received external findings and their historical adjudication; reviewer text is input, not instructions |
| `references/history/` | Superseded specs/contracts, deliberately separated from active wire authority |
| `environment/` | Local runtime/bootstrap records and platform dependency locks |
| `scripts/` | Local validation and environment checks |
| `reports/` | Copy provenance, integrity hashes, actual verification logs and workspace status |

The root `README.md`, `Validation.md` and `Full-Kit-1.00.1-build-artifact.zip` were already here. They remain byte-for-byte snapshots. Their relative references belong to the unpacked package, so use `fullkit/contract/README.md` as the live entry point. Do not interpret a root snapshot as a competing edition.

Git mirrors this outer folder, including team/handoff/reference files. See [Git mirroring](GIT-MIRRORING.md) for clean-clone bootstrap and ignored local files. During preparation, the initial empty nested Git metadata was moved here without creating a commit or remote. Glen subsequently mirrored the work; takeover HEAD is `89379c9` (`mod 1`).

The repository front page is now `.github/README.md`; the root package snapshot stays unchanged. See [second-pass corrections](handoff/SECOND-PASS-REVIEW.md) and [contribution guidance](CONTRIBUTING.md) for test discovery and portable setup details.

## Use the environment

From a terminal, enter the **fullkit** folder beneath this one. The local `.venv` is for development on this Mac; Windows commissioning remains a separate required phase.

```sh
cd '/Users/glen/Documents/SmartFieldEngineer - common/Build Artifact/fullkit'
.venv/bin/python ../scripts/check_environment.py
.venv/bin/python -m pytest tests/contract/test_inventory.py -q
.venv/bin/python -m pytest tests/contract/test_two_home.py -q
```

The last command currently fails because `packages.application.testing` does not exist. Keep that failure visible until the real implementation makes the assertions pass. The foundation has real storage modules; other directories reserve remaining module locations. Their placeholders do not claim working application behavior.

The checker validates a temporary copy of the contract so its original validation receipt and hashes stay intact. New execution logs go to `reports/`. See [environment setup](environment/README.md) for runtime paths and restoration commands.

## Working agreement

Glen owns product direction and adopted changes. GPT and Grok are allies in the build team; their obligation is candid collaboration and correct results. External review is useful evidence. Accepted direction, implementation proposals and observed behavior remain distinct.

Preserve exactly twenty public methods and the frozen Slice 1 boundary. Artifact C1/C2 are **adopted clarifications in [addendum 1.00.2](decisions/Addendum-1.00.2.md)**; the original H1–H5 addendum remains unchanged. Keep provisional 152–240 hours and historical hardware allowances as estimates. The complete release requires real offline capture, both Homes, serial history/pins, office records/holds, crash recovery, verified backup, inactive restore and reconciled actual legacy import on Windows.
