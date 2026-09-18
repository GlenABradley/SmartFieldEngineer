# Full Kit Composed — 1.00.1 harmony addendum

Effective authority: Full-Kit-Slice-1-Build-Spec-100.md plus these five adopted rules. The adjudication explains decisions; it does not override the specification. No new RPC method, deployment service, or estimate change is introduced.

**H1 — Schema authority.** Effective machine schemas are generated from Spec 1.00 plus this 1.00.1 addendum. Archived v0/R4 JSON is not normative. The named wire family remains `cmd.v0.addendum-r4`; an artifact version is not a new method family.

**H2 — Home-level envelope reads.** `job.get` with `job_id=null` and `view=envelopes` returns the selected Home’s envelopes, paginated and without filesystem paths. This is a Home-level projection, not an inbox collection, and does not produce `INBOX_VIEW`. Job-scoped envelopes remain available through a job UUID. Other null-job views follow §5.1.

**H3 — Resources.** `resources` is an array of 1–16 unique, nonempty strings. They are owner tags, not a registry. A hard conflict is an overlap of two hard envelopes sharing any exact resource string. Intervals are half-open: `[starts_at, ends_at)`. Adjacent envelopes do not overlap.

**H4 — Stale code.** `STALE_RESERVATION` is the only legal domain code for a stale time-envelope head. Never introduce `STALE_ENVELOPE`.

**H5 — Import inventory.** The source digest covers actual source tables and referenced evidence files present in the 0.2.0 kit. Missing optional tables are omitted, never fabricated as null rows. If read-only opening and inventory fail, stop before insertion. Missing referenced evidence remains an integrity finding; this rule does not permit silently omitting required evidence.
