# Hybrid AI Architecture Decision

Revision 1.1  September 18 2026

This decision updates the AI architecture and cost assumptions in Implementation Canon 1.0, especially Sections 3, 8 and 20. The product uses local AI plus cloud assistance when useful. Cloud service is a normal part of the intended commercial product. Local capability provides resilience, low-cost routine work and continued field operation without connectivity.

## Routing policy

Keep the job ledger, scheduling arithmetic, inventory, document versioning and approval rules deterministic. A model may recommend an action; the same business rules apply regardless of whether the model runs locally or remotely.

Use local processing for offline briefings, reference lookup, simple extraction and drafting when the selected model meets the task's quality and latency requirements. Send difficult troubleshooting, large document comparisons, image interpretation and multi-step planning directly to an appropriate cloud model when connectivity and standing data permissions allow it. Do not waste time requiring a failed local attempt first. Let Glen explicitly select cloud reasoning at any time within those permissions.

Route by task type, required capability, input size, measured model performance, network availability and remaining spending allowance. Do not use a model's self-reported confidence as the sole escalation signal. Display the processing location and model on the result, with the reason for escalation available on demand.

## Standing data permission

During customer onboarding, configure approved providers and which job information may be processed there. Normal work under that policy requires no repeated cloud-approval prompt. Customer-specific restrictions override the business default. Exclude credentials and irrelevant records. Photos, configuration extracts and packet payloads need explicit category rules because their sensitivity differs from ordinary job notes.

OpenAI's API data controls distinguish model-training use, abuse-monitoring retention and stored application state. Eligible retention controls and endpoint behavior require verification; cloud permission does not mean zero retention. Use the provider's current controls and the customer's agreed terms. Source: https://developers.openai.com/api/docs/guides/your-data

## Hardware consequence

Retain the low-cost Toughbook plan. Do not buy a GPU laptop merely to force every reasoning task offline. The 32 GB memory allowance remains useful for field applications, captures and local inference. The local model should be selected for a useful offline subset, while the cloud supplies compute-intensive assistance. Hardware budgets remain USD 2,320 core and USD 3,505 expanded, before contingency.

---PAGE---

## Cloud gateway implementation specification

For the commercial product, put provider credentials behind a small authenticated cloud gateway. Each technician authenticates to the business account; the laptop receives no shared master provider key. The gateway selects an approved model, enforces customer policy and a per-business spending ledger, limits request size and concurrency, and records request IDs, usage and outcomes. For an owner-only prototype, a user-owned key in an operating-system credential store is an alternative deployment choice.

Estimate cost before dispatch from the selected model's current input, output and tool rates. Reserve that amount atomically against the business allowance, constrain maximum output and tool use, then reconcile actual usage. Retain unresolved cost reservations after ambiguous timeouts until reconciled. A dashboard alert alone is not the application's spending control. Do not silently change to a more expensive model.

Choose a normal cloud tier and a stronger reasoning tier through task evaluations. Keep exact model identifiers, supported modalities and pricing in a versioned deployment configuration. This decision does not invent an API identifier or assert access to a model merely because it appears in a desktop model picker. Pricing source: https://developers.openai.com/api/docs/pricing

## Failure behavior and field continuity

When the network or provider fails, retain the job data and continue deterministic functions. Offer local assistance where it can meet the task, clearly identify reduced capability, and preserve unsatisfied requirements. Recheck job version and data permission before resubmitting an old cloud request. Never replay a business action because an inference request was retried. Hosted call transfer must keep working independently of AI reasoning and the laptop.

## Cost revision

Start with a USD 25 monthly cloud-inference allowance per active technician, with an owner-configurable USD 50 ceiling. These are proposed spending controls, not provider price quotations or guaranteed usage forecasts. Measure a representative month before setting commercial pricing. At the USD 25 allocation, the original USD 60 to 135 operating range becomes USD 85 to 160 per month. At the USD 50 ceiling it becomes USD 110 to 185. Hosted gateway costs require a separate deployment estimate and are not included in those revised ranges.

Keep continuous voice-agent costs separate from occasional reasoning. The original telephone allowance covers the limited routing prototype, not an unrestricted conversational receptionist. Track cloud cost per completed job and per technician, plus latency and correction rate, to decide whether the stronger model improves the economics.

## Delivery status and acceptance

This revision changes the product design. The supplied local-assist.py remains a working local-only adapter; no cloud connector or gateway has been installed, credentialed or tested. No API spending occurred for this revision. The README and distribution package include this decision so the intended hybrid architecture is not confused with the current code's narrower capability.

Before enabling cloud execution, verify account access, a securely provisioned credential, customer policy enforcement, concurrent budget limits, service failure behavior, job-version checks and representative diagnostic quality. Test that cloud outputs cannot bypass Approval Apertures and that an unavailable provider does not stop evidence capture or job records. The local and cloud paths must identify their actual execution state without simulated success.
