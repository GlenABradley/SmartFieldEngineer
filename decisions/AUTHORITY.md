# Authority and current decisions

Use this order, all relative to the build root:

1. Glen’s current instructions and adopted direction.
2. `fullkit/contract/reference/Full-Kit-Slice-1-Build-Spec-100.md` plus `fullkit/contract/Addendum-1.00.1.md` (H1–H5), with adopted [clarification addendum 1.00.2](Addendum-1.00.2.md) (artifact C1/C2).
3. `fullkit/contract/README.md` and generated machine schemas for routine contract detail, with original C1/C2 proposal annotations superseded by Glen’s adoption in addendum 1.00.2.
4. `fullkit/contract/reference/Spec-100-Delta-and-Adjudication.md` explains the spec; it does not supersede it.
5. Canons explain the larger product; legacy code supplies importer facts. Archived reviewer reports and old schema rounds are historical evidence, not active wire contracts.

| Decision | State | Action for Sol |
|---|---|---|
| H1 schema authority | Adopted | Generate from Spec 1.00 + addendum, not archived v0 JSON |
| H2 Home-level envelope projection | Adopted | Null job + envelopes is Home projection, not INBOX_VIEW |
| H3 resource tags/half-open conflicts | Adopted | 1–16 unique nonempty exact strings; adjacent intervals do not conflict |
| H4 stale envelope head code | Adopted | STALE_RESERVATION only |
| H5 actual import inventory | Adopted | Read-only actual tables/files, no invented missing-table rows |
| C1 owner decision on resume | Adopted 2026-09-18 | Explicit sourced owner track_event supplies the resume decision; independently stamp principal; no new field |
| C2 holds after scope advance | Adopted 2026-09-18 | Append effective-scope linkages for unresolved holds transactionally; resolve only the explicitly named hold |

The C1/C2 identifiers here refer to the **1.00.1 artifact proposals**. Historical Claude review registers also used C1/C2 for unrelated earlier findings. Always qualify by document/version to avoid merging different decisions.

No scope/estimate change was adopted in environment setup. The budget remains provisional 152–240 hours, including the previously absorbed backup/import/file-identity work. Current status is a new Home/store foundation; full RPC/desktop behavior remains unimplemented. This is not “0.2.0 upgraded.”

Glen resolved both artifact proposals on 2026-09-18: “i agree. adopt C1/C2. i approve.” Effective contract version is **1.00.2**, an overlay on the preserved 1.00.1 package. Machine-readable status is in `current-contract.json`. Do not alter the preserved release ZIP or reviewed Spec 1.00 in place. Implementation can proceed with both clarification decisions resolved.
