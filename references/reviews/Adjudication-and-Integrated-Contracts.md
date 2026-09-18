# Independent review round 1 — adjudication and integration

September 18, 2026. Received: Gemini, DeepSeek, Perplexity and Claude; all four independent reviews are now adjudicated. Authority remains Glen's direction and the existing canon hierarchy. Application version remains 0.2.0; no software functionality is added by these design integrations. Both base canons remain intact. This is an adjudicated review record, not another regenerated canon.

## Findings and decisions

| ID | Reviewer | Finding | Decision and evidence | Integration / activation |
|---|---|---|---|---|
| G1 | Gemini | SQLite lacks WAL/power-loss protection; add FULL and precommit sidecar roots | Correct and adapt. `Office.__init__` already sets WAL; inspected runtime reports synchronous=2 (FULL). DELETE journaling is not inherently corrupting. No measured <5 ms promise. A separate precommit sidecar is not an atomic transaction with SQLite and can disagree after interruption | Preserve WAL; make synchronization policy explicit and verify it in a future hardening release; qualify database runtime, blobs, documents, backup and actual storage separately; process-crash experiment passed with stated limits |
| G2 | Gemini | Unbounded asynchronous router; 4K tokens and 3-second fallback | Reject as existing defect; adapt as future resilience contract. There is no cloud router. `local-assist.py` bounds references/context, sets model context/output limits and a 300-second HTTP timeout, and has no tool execution or cloud fallback | Before routed inference: per-task model budgets, bounded deadlines, cancellation, nonblocking UI, route/circuit state, visible unavailable status; no universal 4K/3-second or cached-guidance promise |
| G3 | Gemini | Approval replay across sites; add timestamp nonce and signing | Attack not demonstrated; adapt domain-binding requirement. Actions already have unique random IDs and job/scope/expiry/state fields. Hash currently covers exact payload only, so identical payloads can have identical hashes; approval hashes are not signed portable credentials | Before execution adapters, versioned digest binds ledger/Home as applicable, action ID, job, scope revision, expiry, exact payload, policy and relevant asset/pack revisions; preserve old receipts and reapprove changed authority rather than pretending timestamps authenticate actors |
| G4 | Gemini | Free-text verifier needs TPM/secure enclave keys | Accept attribution gap already disclosed; defer prescribed implementation. Hardware keys do not establish individual identity, correct observations, account roles or safe recovery by themselves | Claimed actor, authenticated principal and authority basis stay distinct; authenticated individual action and Home authorization before delegation/shared use; choose keystore/signing only with revocation, recovery and offline threat model |
| D1 | DeepSeek | Authenticated authority missing; signed authority event layer | Accept boundary, adapt means. Single trusted operator remains legitimate; signatures are not a substitute for session identity/authorization or independent record anchoring | Explicit unauthenticated local trust now; authenticated principal and scoped policy checks before second-operator action; signed audit/anchoring where the selected threat model warrants it |
| D2 | DeepSeek | Backup restores can fork offline job reality | Accept and refine. Prototype has no sync, so no existing last-write-wins merge is demonstrated; the future failure is real | Separate business authority, ledger lineage, installation/device instance and recovery generation; recovered copy remains inactive for external execution until designated writer; no silent merge of commitments, approvals or identity |
| D3 | DeepSeek | Guided procedure lifecycle and stop-work authority | Accept; extends existing pack qualification rather than replaces it | One qualified task/platform procedure with author/reviewer/version, source binding, applicability, revalidation triggers, stop conditions and explicit technician stop authority; before guided sale |
| D4 | DeepSeek | Confidentiality, secrets, retention and cloud containment absent from brief | Accept brief gap; correct corpus claim. Implementation Canon 21 already requires OS encryption and credential-manager storage; Hybrid 1.1 excludes credentials and minimizes cloud data | Before customer data: verified disk/backup protection and secret references; before cloud: data-classification/permission checks, minimization and egress record; privacy-aware retention/recording policy, not indiscriminate permanent logs |
| D5 | DeepSeek | Missing model-risk evaluation harness | Accept implementation gap; evaluation scenarios already specified in Implementation Canon 20 but not run against a model | Task-risk tiers; deterministic authority/measurement outcome gates; versioned representative evals and regression; finite-suite results cannot establish universally zero unsafe outputs |
| P1 | Perplexity | Explicit job-state transition authority | Accept and adapt. Core already stores independent tracks and audit events; `track` validates vocabulary and field blockers but not a full authority/evidence transition contract | Enrich existing transition events, not a second ledger or single linear done flag; contract-specific acceptance/invoicing conditions; before transitions trigger outside actions |
| P2 | Perplexity | Claim-specific evidence sufficiency | Accept as major gem. Organized/hash-checked files alone do not prove a particular outcome; existing instrument contract supplies part of the needed provenance | Job-specific claim checks link scope/asset/config/criterion, evidence, instrument/procedure, freshness and reviewer; manual checks now, automation after representative trials |
| P3 | Perplexity | Claimed actor versus authenticated principal versus authority assertion | Accept distinction; qualify “non-repudiable.” No key arrangement eliminates disputes or proves an observation is correct | Extend the existing attribution model; label free-text names as claimed; authenticate/authorize/revoke before shared use; avoid absolute non-repudiation marketing |
| P4 | Perplexity | Suggest/prepare/queue/execute/reconcile delegation ladder | Accept and refine. Preparing a draft alone does not demonstrate a working connector; reconcile may verify by authoritative provider status/receipt rather than an unrelated channel | Capability rung and actual operation state are separate; one low-risk external workflow through real execution and reconciliation, with ambiguity/duplicate tests; standing authority preserved |
| P5 | Perplexity | Bounded reversible capability release; correct escalation counts | Accept. Preserve existing Apprenticeship Graduation vocabulary instead of introducing a competing term | Graduation revision holds exact task/platform limits, evidence, supervision, commercial band and validity; appropriate stop/escalate is positive outcome; mentor time part of job envelope |

## Claude — five further decisions

| ID | Finding | Decision and evidence | Integration / activation |
|---|---|---|---|
| C1 | Approval invalidation has no defined mid-task behavior | Accept as a substantive operating gap. Scope revision invalidates prepared/approved actions in code; it does not establish a physically safe interruption, automatically notify a working technician or hold the whole field workflow | Add an interrupted-work record and safe-boundary/hold procedure; manual baseline immediately, automatic interruption handling before guided/device execution |
| C2 | Standing authority has no explicit offline path | Accept the specific policy gap; correct claim that offline behavior is wholly absent. Implementation 21 permits evidence/drafts, warns about stale remote state, and says prototype has no replay queue | Define allowed local work versus pending remote proposals, authority freshness and reconnect checks; shared offline authority/queue remains unimplemented |
| C3 | Voice consent not addressed | Adapt. Implementation 18 already requires location-specific consent review before live use and the voicemail code announces recording; a dedicated consent-state/participant gate is not implemented | Legal-reviewed recording/transcription/participation policy and captured consent evidence before activation; no claim an announcement or checkbox universally establishes legal compliance; Voice Bridge remains horizon |
| C4 | Replacement assets lack lineage | Accept dedicated structure; correct absence claim. Serial workflow already permits a sourced job fact for replacement relation | Append a temporal old/new relationship event with job, location/role, time, reason and evidence; explicit bidirectional lookup later, no automatic graph or warranty transfer claimed |
| C5 | SQLite concurrency not flagged for sponsor | Accept a measured decision gate; qualify inevitability. Local single-writer and future central authority are already specified; a sponsor workload/capacity decision is not quantified | Qualify service/database topology before shared deployment; benchmark realistic transaction and recovery workload, do not infer seat-count bottleneck or migrate now |

## Status corrections in the received reviews

Gemini's status matrix misclassifies the protected reservation calculator as development: it is implemented and covered by the original envelope test. Windows installation scripts exist but are unvalidated on Windows; they are not absent. A local Job Dossier is implemented, while customer delivery is manual. An Aruba CX template exists; an ArubaOS-Switch pack is not supplied. There is no cloud router or tenant-isolation enforcement to describe as merely performance-unvalidated; those are unimplemented.

Voice Bridge remains horizon, with live qualification and presence gates. Moving it to halo would change Glen's intended voice operating capability without justification. Fusion splicing/robots/custom carrier remain halo. Current Job Reality is a revisable sourced projection; historical events are retained, but the current projection must not be frozen as Gemini's “immutable” wording suggests.

Only application processes or isolated lab copies should be used for initial crash experiments. Do not make an actual customer job or Glen's working laptop the first destructive power-loss trial. A process exit does not simulate a disk losing power, partial sector writes or broken fsync. “100% recovery,” “zero data loss” and “under 90 seconds” are proposed or unsupported claims, not established field facts.

## Integrated operational contracts

### 1. Claim checks inside the Job Dossier

Start as a sourced manual record, not an automated certification service. Minimum fields:

- Claim ID/text; Home when implemented; job/scope revision; target asset bind, run/endpoints or configuration revision.
- Approved criterion and applicable customer terms; required evidence classes and freshness requirements.
- Supplied evidence IDs/digests with explicit gaps, conflicts, unknowns and provenance.
- Applicable instrument bind, capability, settings/profile, units, setup, calibration/verification status and raw results.
- Claimed reviewer; authenticated principal when available; authority basis; check time.
- Review result: sufficient, insufficient, conflicting, manual-review-required, or not-applicable with an explicit reason.

Evidence adequacy is claim-specific. A serial observation can support identity; it cannot establish a cable test. “Sufficient” means the approved criterion has been reviewed against the named evidence, not that AI confidence exceeded a number. Applicability exceptions require their own authority. A new scope, asset, procedure or relevant configuration can invalidate a current claim evaluation without deleting history.

### 2. Transition authority over separate tracks

Retain operational, delivery/acceptance, billing/payment, returns and exception dimensions. A milestone summary is derived from these dimensions, not an alternative global state machine.

Transition record: operation/event ID; job and expected scope/track revision; from/to state; claimed actor/authenticated principal; policy/delegation/approval basis; claim/evidence references; event and observation times; preconditions; effect on next obligations; correction/supersession reference when needed.

Before advancing a consequential state, recheck authority, scope, required claims and authoritative external receipts. Prepared documents display claims/status; they do not establish delivery, acceptance or payment. Invoice eligibility follows the actual approved contract: deposits and milestone invoices can precede field completion, so do not impose universal customer-acceptance-before-invoice logic. Partial payments, fees, disputes, reversals and refunds remain distinguishable.

### 3. Delegation: rung, operation state and measured attention

Rungs describe supported capability: suggest, prepare, queue, execute, reconcile. State describes one attempted operation: prepared, queued, executing, confirmed, failed, unknown, reversed or manual-reconciliation-required. “Queued” is not “sent,” and connector availability is not result confirmation.

An execution candidate carries action/job/scope/policy context, exact payload digest, account/entitlement, unique operation ID, target idempotency key when supported, duplicate-risk marker otherwise, expiry, relevant preconditions, attempts and provider receipts. Timeout after possible acceptance remains unknown. Query authoritative status or reconcile manually; do not replay blindly. Duplicate webhook/event receipts are deduplicated and associated with the correct attempt.

Measure owner review time, exception/reconciliation time, repetitive entry, failed attempts, duplicate rate and confirmed external outcomes. A connector that creates more supervision than it removes has not proven useful delegation. Start with one nonbinding routine customer update under standing authority, after real channel permissions and data handling are established; do not combine booking, purchasing and invoice issuance into the first test.

### 4. Actor attribution and confidentiality

Source/provenance, human verification, authenticated actor and permission are independent facts. A claimed name is not an authenticated principal. Authentication is not authorization; neither makes an observation true. Do not relabel inherited free-text records as authenticated during migration.

Single-operator mode continues under explicit local trust. Before another person acts through the application, enforce appropriate accounts, scoped assignment/authority and revocation; shared/sponsor use additionally requires Home isolation across all data, retrieval, keys, costs, exports and background actions. Do not assume TPM, Keychain and Secure Enclave have interchangeable key or recovery semantics.

Keep secrets in an approved OS/provider store and place references in job records. Protect real data and backups with verified OS/encrypted storage; the current application does not encrypt its own database. Define retention and deletion across database, evidence, backup, recording and provider copies. Record cloud egress permissions and minimum required data, route/model/version/policy and result references; retain raw prompts/audio only when necessary and permitted. “Log everything forever” conflicts with confidentiality and minimization.

### 5. Procedure and graduation lifecycle

Retain Platform Pack and Field Mission Harness names. A released procedure binds exact applicability, sources, author/reviewer, version, prerequisites, allowed actions, evidence requirements, rollback/recovery, stop conditions, review date and revocation/revalidation triggers. Firmware drift, missing tools, topology mismatch or absent mentor invalidate relevant execution eligibility.

Technicians may stop and escalate without manufacturing completion. Correct escalation is a positive observed outcome, not automatic graduation and not a guarantee the interrupted job is billable. Owner-approved graduation changes scoped capability, eligible commercial band and reserved supervision together, with effective/review dates and suspension reasons. No predictive competence score is needed for the first guided release.

### 6. Restoration lineage and one authority for commitments

A ledger namespace is neither a Home nor a live-writer credential. Backups preserve historical lineage. A future installation/device identity distinguishes running copies, while a recovery generation and writer designation establish which copy may execute outside actions. A same-machine restore still needs writer/queued-action review even if the device identity is unchanged.

Until sync exists, designate one active working ledger and keep restored copies inactive/for review until controlled cutover. Stop the prior writer before using the replacement for business action. Future reconnect must expose conflicting scope/identity/events; commitments and approvals never use last-write-wins. Replayed queued actions must recheck current authority and remote outcome, not rely on restored “pending” state.

## Durability evidence and runtime gate

The reviewed application already requests WAL. Inspection on this environment reports SQLite 3.53.1 and synchronous=2 (FULL). An isolated child-process recovery experiment preserved a committed sourced record and rolled back a second uncommitted record plus audit insert; SQLite integrity and application audit checks passed. This establishes one process-termination case, not power-loss qualification.

SQLite's [synchronization documentation](https://www.sqlite.org/pragma.html#pragma_synchronous) describes FULL; its [atomic-commit discussion](https://www.sqlite.org/atomiccommit.html) explains storage assumptions and simulated crash testing. A separate sidecar written before commit creates an additional reconciliation problem, not automatic durability. Independent audit anchoring is a different tamper-detection requirement.

A real additional runtime gate emerged from primary-source verification: SQLite documents a rare WAL-reset race involving overlapping writers/checkpoints and fixes in 3.51.3 or later, plus stated backports. Our inspected runtime is newer; the target Windows runtime must be checked, not inferred from the Python version. See the [official WAL documentation](https://www.sqlite.org/wal.html), section 11. This is not grounds to claim this runtime is corrupt or to run unbounded parallel-writer experiments on a customer's ledger.

NIST's [digital identity revision page](https://pages.nist.gov/800-63-4/) dates final Revision 4 to July 2025; the review's August supersession phrasing should not replace the primary source. Identity guidance is useful discipline, not an invented certification mandate for this product.

## Claude integrations: interruptions, offline authority and temporal lineage

### 7. Mid-task interruption: secure, record, hold, reauthorize

Invalidate authority for affected normal work when a material change is discovered; do not equate that with an unsafe immediate physical halt. Procedures identify safe boundaries and any narrow stabilization actions permitted by standing policy. The model cannot create an emergency exemption or authorize completing the changed scope.

An interrupted-work record names job and old/new scope revisions, interrupted step, trigger and observation time, last verified state, exposed equipment/cabling/access, customer service impact, irreversible changes, reversible changes and risks, permitted stabilization action and its authority, actual stabilization result/evidence, hold conditions, responsible person and requested decision. Unknowns remain explicit.

Use interruption state as an additional exception dimension: interruption detected, stabilizing, secured/on hold, or stabilization failed/escalated. It does not erase field, acceptance, billing or return tracks. Each attempted stabilization retains its result; secured/on hold is an evidenced state, not an assumption that a command succeeded.

Advance only to the approved safe boundary, secure the site using the permitted procedure, record what is open and what remains, and hold affected work. Do not automatically roll back an irreversible or hazardous condition. Resume requires a revised plan, current site verification and renewed authority for the changed work. Unaffected work continues only if its authority and dependencies truly remain valid.

Today the operator records this as sourced facts/tasks/requirements, sets the field track blocked where appropriate, and performs the qualified physical response. The application does not automatically detect remote scope changes, enforce stabilization choices or generate an interrupted-work object. A new pending requirement can keep the existing field-completion gate from being passed, but there is no universal enforced hold state yet.

### 8. Offline authority: permission is not remote confirmation

| Activity | Offline behavior | Required boundary |
|---|---|---|
| Capture notes/evidence/identity and prepare documents | May proceed on the local ledger | Correct local job context and data protection; provenance retained; no delivery/acceptance claim |
| Already-authorized local physical/configuration work | Permitted only where the selected procedure and explicit standing policy allow offline work | Applicable cached scope/authority within validity and freshness limits, qualifications/tools, local readiness and recovery; missing online check or mentor blocks affected work |
| Safe stabilization after interruption | Only the narrow approved safe-boundary response | Current physical facts, named policy/authority and evidence; no extension of normal job scope |
| New shared booking, platform acceptance, purchase, remote message or payment operation | Do not claim remote execution while offline | Store a proposal/task; prototype requires manual reconnect reconciliation and has no automatic replay queue |
| An external operation whose response was lost | Preserve unknown outcome | Reconcile authoritative provider state before retry or marking confirmation |
| Model assistance | Local advice only where available/qualified; cloud unavailable stays unavailable | No new authority from advice; no promise of instant cached guidance or a tested offline model |

Future offline delegated authority needs a verifiable bounded grant with issuer, actor/Home/job, scope/policy revision, allowed actions, expiry, maximum offline age, permitted offline exposure and necessary prerequisites. It must explicitly state which checks may be cached and which require connectivity. Revocation cannot be learned instantly by a disconnected device; short validity and restricted action classes bound that exposure rather than claim immediate global enforcement. Protected caches and trustworthy expiry handling require implementation and tests.

On reconnect, compare current scope, policy, assignment, reservation and outside outcome before promoting any proposal. Preserve work already performed as observations; do not retroactively relabel it as approved or suppress conflicts. Current 0.2.0 does not implement signed offline grants, shared policy revocation or a replay queue.

### 9. Voice: permission and participation state before activation

Recording/transcription, provider speech processing, retained summaries and live listen-along/hot join require distinct declared handling. The consent design identifies participants, purposes, reviewed disclosure/policy, response/evidence and time, applicable retention and permitted modes. Unknown/declined consent blocks the affected mode. A new participant or changed purpose requires reevaluating the applicable permission. Consent collection cannot secretly record the conversation it is meant to authorize; use a qualified nonrecording control path where needed.

The original voicemail function announces recording but has no separate affirmative consent-state gate; the receptionist also uses provider speech recognition. Neither flow was live-qualified. Do not deploy either as a blanket compliance claim. Before live use, qualify the actual configured modes and reviewed process, including refusal, no response, joining participants and consent withdrawal, and provide a nonrecording alternative. No new voice code or legal approval is supplied in this integration.

The legal point is real but not a universal “two-party” checkbox rule. [California Penal Code 632](https://leginfo.legislature.ca.gov/faces/codes_displaySection.xhtml?sectionNum=632.&lawCode=PEN) addresses consent of all parties for covered confidential communications; [Florida 934.03(2)(d)](https://www.leg.state.fl.us/statutes/index.cfm?App_mode=Display_Statute&URL=0900-0999/0934/Sections/0934.03.html) describes prior consent of all parties for its specified consent exception. Actual multi-jurisdiction call configuration needs qualified review; these examples are not a complete nationwide legal determination.

### 10. Replacement lineage: events, not renamed identities

Keep serial correction separate from physical replacement. A minimal replacement event carries relation ID, job/scope, old asset ID/bind, new asset ID/bind, site/location/functional role, effective time, reason, claimed actor/authenticated principal when available, evidence, return disposition and warranty/service references where known. A temporary loan, permanent replacement or reinstallation is explicitly identified. Shared/Home linkage follows authority grants when implemented.

Append corrections/supersession events; do not overwrite the old asset or transfer its history to the new identity. Bidirectional lookup should answer which device replaced this one and which device it replaced, with time and location. A device reinstalled later must not produce an impossible permanent ancestry tree: temporal relation events can represent reuse. Do not infer that warranty rights transfer automatically.

For the pilot, existing `record JOB fact JSON` can retain the sourced relationship and `show` can expose it. Dedicated relationship validation, both-direction lookup and automatic document rendering are specified, not implemented. A single optional foreign-key pointer is not necessarily enough for temporary swaps, reinstallation and multiple roles over time.

### 11. Sponsor capacity: choose topology from observed load

SQLite documents one writer per database at a time and recommends considering client/server designs where substantial concurrent writers are needed; see [Appropriate Uses for SQLite](https://www.sqlite.org/whentouse.html). This establishes a constraint, not a tested failure at any particular seat count. A central authorized service can serialize some workloads successfully; sharing a live SQLite file across technician laptops or cloud-sync folders is not the proposed architecture.

Before shared deployment, establish transaction mix, peak arrival rate, acceptable lock waits/latency, workload during uploads/checkpoints/backups, queue bounds, recovery objectives and single authority for commitments. Benchmark and fault-test that workload with the chosen service and runtime. Retain a central SQLite service only if it meets measured capacity/recovery/authorization requirements; select a client/server database if requirements call for it. Migration, service operation and conflict engineering cost remain unknown, deferred and explicit.

## Next experiment and commercial effect

First run the existing identity flow on a controlled asset and target Windows configuration, including an explicit offline segment, historical document inspection and restoration to an inactive recovery copy. Inject a mock scope change during a simulated in-progress task, manually secure the mock exposed state, record the authority/stabilization/hold and verify that affected normal work is not treated as reapproved. The current software will invalidate relevant approvals but does not generate the new interruption workflow automatically. Keep process interruption in a separate disposable lab dataset. Record actual elapsed/operator time and failures without assuming a 90-second target. Check whether another reviewer can reconstruct current and historical facts without access to Glen's private business records or an oral explanation.

After this baseline, prove one real office action reduces total owner attention, including exceptions. Select and qualify an actual connector before claiming execution. Procedure/pack field trials and shared-data engineering retain their own activation gates.

No hardware additions, purchases, new monthly service or price revision is introduced here. Accepted contracts imply engineering, qualified review and later operating work whose cost is not yet estimated. Existing hardware/recurring figures remain historical planning assumptions; the $10,000 seat and pilot labor estimate retain their limitations. Do not convert the reviewers' “software only” statements into zero development cost.
