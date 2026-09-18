# Authority and current decisions

Use this order, all relative to the build root:

1. Glen’s current instructions and adopted direction.
2. `fullkit/contract/reference/Full-Kit-Slice-1-Build-Spec-100.md` plus `fullkit/contract/Addendum-1.00.1.md` (H1–H5).
3. `fullkit/contract/README.md` and generated machine schemas for routine contract detail, with its **C1/C2 review proposals explicitly pending**.
4. `fullkit/contract/reference/Spec-100-Delta-and-Adjudication.md` explains the spec; it does not supersede it.
5. Canons explain the larger product; legacy code supplies importer facts. Archived reviewer reports and old schema rounds are historical evidence, not active wire contracts.

| Decision | State | Action for Sol |
|---|---|---|
| H1 schema authority | Adopted | Generate from Spec 1.00 + addendum, not archived v0 JSON |
| H2 Home-level envelope projection | Adopted | Null job + envelopes is Home projection, not INBOX_VIEW |
| H3 resource tags/half-open conflicts | Adopted | 1–16 unique nonempty exact strings; adjacent intervals do not conflict |
| H4 stale envelope head code | Adopted | STALE_RESERVATION only |
| H5 actual import inventory | Adopted | Read-only actual tables/files, no invented missing-table rows |
| C1 owner decision on resume | Proposed, not adopted | Review whether explicit sourced owner track_event supplies the decision without adding a field |
| C2 holds after scope advance | Proposed, not adopted | Review appended effective-scope linkage for all unresolved holds; no silent implicit acceptance |

The C1/C2 identifiers here refer to the **1.00.1 artifact proposals**. Historical Claude review registers also used C1/C2 for unrelated earlier findings. Always qualify by document/version to avoid merging different decisions.

No scope/estimate change was adopted in environment setup. The budget remains provisional 152–240 hours, including the previously absorbed backup/import/file-identity work. Current application status is absent, not “0.2.0 upgraded.”

Record the exact adjudication source, date and revised contract version when either proposal is resolved. Do not alter the preserved release ZIP or reviewed Spec 1.00 in place. Independent lock/context/receipt work can begin while these narrowly scoped semantic questions remain visible.
