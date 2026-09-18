# Business in a Box: product definition

Revision 1.2 · September 18, 2026 · Owner direction: Glen

## Buyer and promise

The primary buyer is a top-shelf independent field engineer: someone whose technical judgment earns money, but whose time disappears into calls, scheduling, paperwork, procurement, documentation, and collections. The product is a portable field office with local AI, cloud AI, practical instruments, and one continuous job record.

**Buy the bag. Bring your judgment. Let the office run around you.**

The product ambition is to run everything around the Allen wrenches: find and qualify work, prepare the engineer, organize the visit, capture proof, handle the administrative follow-through, and track the job through settled payment. The engineer chooses the work they enjoy and delegates the rest within standing authority. This is a target product promise, not a statement that today's prototype already performs these functions.

The secondary operating mode lets the owner hand the kit to a less-experienced field technician. The system guides that technician through a qualified, job-specific installation, from preinstall photographs to tested handover and the business processes that follow. It does not assume every possible installation can be completed by an unqualified person.

## Two operating modes, one business

**Expert mode:** Quiet by default. Show the next useful action, exceptions, commitments, and decisions worth the owner's attention. Capture notes by voice or photograph; turn them into structured records and drafts. The owner can skip explanations, take direct control, and choose which tasks remain personal. Do not make an expert follow a beginner's wizard.

**Guided technician mode:** Present one actionable step at a time: what to do, where to do it, which part or tool is needed, what success looks like, and what evidence to capture. Bind the procedure to the actual site, device model, approved design, and technician permissions. Carry forward the same job record used by the owner. Commercial, banking, and customer-administration privileges remain with the authorized business role.

An expert can assign a job and review exceptions without exposing the entire business. The technician receives only the site information, scoped credentials, and actions needed for that assignment. Escalation transfers the relevant photographs, measurements, completed steps, and precise question to the owner.

## Full lifecycle and completion evidence

| Stage | Product responsibility | Evidence required to advance |
|---|---|---|
| Opportunity | Capture inbound requests and permitted lead sources; identify customer, site, problem, budget, timing, and fit | Traceable request and qualification record; missing facts visible |
| Scope and quote | Prepare scope, exclusions, labor, parts, travel, schedule, and terms | Accepted scope and commercial authorization; promises within owner policy |
| Preinstall survey | Request and organize photographs of rack, power, cabling, labels, access, equipment, and work area | Required views linked to site and asset; unreadable or missing views explicitly unresolved |
| Engineering | Produce bill of materials, device-specific procedure, dependencies, test plan, and rollback | Reviewed design; compatibility checks; approved change window and recovery route |
| Procurement and dispatch | Check stock, source missing parts, reserve tools, schedule access and travel | Parts and instruments accounted for; appointment and access confirmed |
| Arrival | Confirm site, contact, assets, existing service, and work authorization | Arrival baseline, photos, serials, initial measurements, and site authorization |
| Installation | Walk through mounting, patching, labeling, and approved configuration | Step-specific physical evidence and configuration records; exceptions resolved |
| Verification | Run applicable connectivity, throughput, configuration, power, copper, fiber, or RF checks | Raw readings and declared pass criteria; instrument limits recorded; failures remain open |
| Handover | Assemble as-built records, asset inventory, configuration backup, test results, and customer instructions | Customer-facing closeout package, delivery record, and acceptance or documented dispute |
| Billing | Match approved scope and changes to labor, materials, expenses, and terms | Reconciled invoice with correct customer and approved amounts; delivery confirmation |
| Collection | Follow receivables, send authorized reminders, reconcile receipts and fees | Payment-provider or bank evidence of settlement; partial payments, disputes, and reversals retained |
| Aftercare | Track warranty, callbacks, maintenance opportunities, and actual job profitability | Linked service history and cost reconciliation; obligations assigned |

“Final paycheck” means payment reconciled against the job, not simply an invoice marked sent or a model declaring success. Customer response and settlement are external events; automation can pursue them but cannot guarantee them.

## How guided installation must work

1. Select a released playbook matched to equipment, firmware, site design, and work type. Free-form model text is advice until accepted into an authorized procedure.
2. Check prerequisites: identity, assignment, access, equipment, tools, qualifications, service dependencies, and recovery options.
3. Capture a before-state. Link each picture and reading to a specific asset and step. Preserve originals and record capture/import provenance; do not claim an imported photo proves current site conditions.
4. Give a concrete action with a diagram or reference photo where useful, expected outcome, and verification method.
5. Verify using the strongest available evidence. A photograph can support label or placement review; it cannot establish cable certification, torque, electrical safety, or end-to-end performance. Ask for a measurement or qualified human check where necessary.
6. Resolve discrepancies explicitly. If hardware, wiring, firmware, or site conditions differ, pause the affected step, preserve service where possible, and escalate with context. Do not improvise destructive configuration changes.
7. Authorize any business or device action through deterministic policy: permitted actor, job, action, scope, spending limit, and current approval. Track duplicate requests and results so retries cannot issue duplicate purchases, invoices, or payments.
8. Record after-state, test outputs, deviations, and handover. Completion depends on the acceptance checklist, not on every screen having been tapped.

Start with a deliberately bounded supported service: replacement or installation of a small-business switch and access point using a preapproved design and existing suitable power/cabling. Expand the released playbook catalog only after real field trials. Other work can still be recorded and assisted, but cannot be sold as validated guided execution until qualified.

## Delegation and autonomy

Standing owner policies should cover customers, task categories, communication channels, scheduling limits, purchasing limits, pricing floors, approved vendors, change authority, and cloud data permissions. Routine permitted work should proceed without repetitive approval prompts. Ask only when a decision exceeds authority, changes a commitment, or lacks essential information.

Separate proposing an action, authorizing it, executing it, and verifying its result. Every outside service needs a real integration or an explicitly identified human handoff. An unavailable connector must produce a visible work item, never a fictitious booking, order, sent message, or payment.

Local AI supports offline guidance, search, and drafting when suitable. Cloud AI is a normal option for harder reasoning and richer inputs, subject to standing customer permissions. Interrupted connectivity must not lose evidence or repeat external actions. Do not require a discrete GPU for the initial field kit.

## What must be engineered next

| Workstream | Concrete deliverable | Release evidence |
|---|---|---|
| Job orchestration | Durable lifecycle, assigned next actions, dependencies, exception queue, resumable execution | Power/network interruptions and duplicate events produce no lost jobs or duplicate side effects |
| Expert experience | Fast voice/photo intake, concise daily brief, owner delegation controls | Measured reduction in administrative effort on real jobs |
| Guided execution | Versioned playbooks, step evidence rules, site/asset binding, owner escalation | Representative technicians complete supported jobs against expert inspection criteria |
| Business integrations | Customer communications, calendar, purchasing, accounting, invoicing, payment reconciliation | Each connector tested in sandbox and controlled live use; failures and manual fallback demonstrated |
| Cloud intelligence | Authenticated gateway, model routing, bounded spending, data policies | Customer isolation, permission enforcement, usage accounting, offline recovery validated |
| Evidence intelligence | Photo/document extraction and comparison with uncertainty and provenance | Measured error rates; deliberately missing or misleading evidence cannot silently pass critical gates |
| Instrumentation | Real interfaces or explicit manual reading capture for each supported instrument | Readings tied to the correct test and asset; accuracy and calibration limits recorded |
| Commercial operations | Provisioning, encrypted storage, role separation, backup/restore, updates, support and licenses | Recovery exercise, access-control tests, supported-device matrix, release/support procedures |

R&D remains in reliable scene interpretation, model-specific troubleshooting, novice instruction quality, confidence calibration, and broad instrument interoperability. Validate each against observed field outcomes. Never market an unvalidated inference as a certified measurement.

## Cost and current implementation boundary

Retain the lean hardware approach and the existing costed bill of materials: $2,320 core; $3,505 with extended instruments; $4,206 with the existing 20% contingency on that expanded package. These are prior planning estimates, not new supplier quotations. No additional hardware purchase is introduced by this positioning decision.

The hybrid addendum carries a proposed $25 monthly cloud-inference allowance per technician, making the prior recurring planning range $85–160/month before unquoted gateway hosting, insurance, and other excluded services. This is not the total operating cost of the full business automation product. Communications volume, payment processing, accounting/CRM subscriptions, integrations, support, and development must be costed before setting a commercial price. Track build cost, buyer operating cost, and seller support margin separately.

The delivered prototype contains local job/evidence/approval/stock/document/backup operations, a simple desktop interface, and a local advisory adapter. It does not implement autonomous business operation, a validated guided installation engine, cloud routing, live procurement, invoice delivery, or settlement reconciliation. This revision defines the commercial target and acceptance conditions; it does not change that implementation status.

## Product acceptance

The defining demonstration is one supported job carried through the full lifecycle with actual artifacts and real integration results: request, accepted scope, preinstall evidence, prepared kit, guided execution, measured tests, handover, invoice, and reconciled payment. Record owner interventions, technician errors, administrative minutes, rework, costs, and failure recovery. Repeat with expert and guided-technician users. Set numeric release thresholds before trials; publish only claims supported by those results.

Success is not the number of AI features. It is an excellent engineer reclaiming time, and an appropriately scoped technician producing work the owner can stand behind.
