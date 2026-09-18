# Full Kit Composed — adopted clarification addendum 1.00.2

Adopted by Glen Bradley on 2026-09-18 in the existing build task. Exact instruction: “i agree. adopt C1/C2. i approve.” This resolves the artifact 1.00.1 C1/C2 proposals recommended in Sol’s work plan. Historical reviewer findings with the same labels are unrelated.

Effective contract: preserved Spec 1.00 + adopted H1–H5 in Addendum-1.00.1 + this adopted clarification overlay. The original 1.00.1 package, schemas, specimens, tests, manifest and release ZIP remain preserved; their pending-proposal annotations describe their original publication status, not current authority.

## C1 — sourced owner decision on resume

The explicit owner-submitted job.update track_event to ready or in_progress is the owner decision when resuming interrupted work. Core independently stamps the local principal. Require the current applicable interruption ID, reason and a valid structured source reference or relevant Home/job evidence. The desktop labels the action “Resume — owner decision.” Append a resolution event; never erase the interruption. No new RPC or payload field.

Distinguish an initial entry into a field track from resuming a held job. This clarification does not require a nonexistent interruption for every first start and does not waive resume gates for interrupted work.

## C2 — unresolved holds across scope advance

In the same scope-change transaction, append an effective-scope linkage for every unresolved hold on that job from the old current scope to the new scope. Preserve each original interruption and recorded scope. Read projections expose effective_scope_revision. Resume validates against the latest linkage, resolves only its explicitly named hold, and never revives a resolved hold. Remaining unresolved holds continue to block completion.

No new RPC, payload discriminator or domain code. Failed transactions leave neither a partial scope advance nor partial linkages. Verify multiple holds, stale/resolved holds and transaction failure against real persistence.

## Implementation and release status

The five original integration vectors remain the acceptance foundation. Their final C1/C2 vector now covers adopted behavior, even though its preserved name/comment says “proposed.” Do not rewrite the historical baseline to conceal that distinction. Exactly twenty public methods, existing architecture/scope and provisional 152–240-hour estimate remain unchanged.

Adoption resolves the semantic decision; it does not establish application implementation, test success or Windows qualification.
