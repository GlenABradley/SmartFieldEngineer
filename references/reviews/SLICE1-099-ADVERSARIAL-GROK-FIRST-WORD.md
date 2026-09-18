# Grok first word — adversarial pass on Spec 0.99

18 September 2026 · append this to GPT Sol’s prompt · not a spec rewrite

Claude found real seams. The sharp question is the only one that can change the shape. Answer it, then patch the rest into 1.00. Do not reopen hub, voice, robots, or Slice-1-as-whole-product.

## The sharp question

**Keep two Homes in Slice 1. Cap the threat model. Do not import sponsor-tier security.**

Slice 1’s buyer is one owner, one laptop, **two businesses**. That is Glen’s actual week: a dedicated book and an independent book, or a side marketplace job next to a shop. Mixing those closeouts is a day-one failure, not a later-tier luxury.

What Slice 1 must prevent:

- Active Home A writes or pins Home B’s serial/document
- After a switch, the UI still shows B
- Restore copy is used as a second live writer
- Same job/asset UUID in both stores returns the wrong serial

What Slice 1 must **not** pretend to prevent:

- Hostile local administrator
- Second human at the keyboard
- Network tenant attacks, RLS, stolen process memory, debugger

Say that in 1.00 in one paragraph under §1 or §3. Then the two-Home test stays first-class and the hour estimate stays honest: part of 152–240 **is** this context fence. It is not free and it is not sponsor multi-tenant.

If Glen later says “one Home only for the first install,” *then* drop Home B from the acceptance demo — not from the data model. The schema still carries `home_id`. The test can be skipped; the column cannot.

## Finding by finding

| Finding | Verdict | 1.00 patch |
|---|---|---|
| `reservation` overloaded with parts holds | **Accept** | Rename RPC `reservation.put` → **`envelope.put`**. Command name `envelope.put`. Spoken term: operational envelope. Inventory holds, when they exist, are `stock_move` / future `stock_allocate`. One sentence in §5. Do not keep both names. |
| `SOURCED:` prefix is theater | **Accept** | `secured_on_hold` requires `stabilization_done=true` **and** a nonempty `evidence_ids` **or** a structured `source_reference` field (text, not a magic prefix). Drop prefix-as-control. Free text may still contain the word sourced; it proves nothing. |
| WAL backup consistency | **Accept** | `backup.create` while holding the store writer: produce the DB copy with SQLite **Backup API or `VACUUM INTO`** a new file, then copy referenced blobs, then manifest. Do **not** copy live `ledger.sqlite` + hope `-wal`/`-shm` match. Checkpoint is allowed; file-copy of a hot main DB is not. State this in §9. |
| Import re-run | **Accept** | Record `source_digest` + `import_batch_id` on the target Home. Second run, same source digest, same target: return the existing import report, **no new facts** (`IMPORT_ALREADY_APPLIED` as success-with-same-receipt, not a new mutation). Partial run with no receipt: resume using the legacy-id map; never insert a second observation for the same source key. Different source digest is a new import and must not collide on generated UUIDs. |
| Path aliases (8.3, subst, junctions) | **Accept, bound** | Writer identity is **volume + file index** from the open lock handle (`GetFileInformationByHandle` / `GetFinalPathNameByHandleW` on Windows). String path equality is not the lock key. Do not write a novella about every NTFS alias. One primitive, tests: junction + subst to the same Home → `HOME_WRITER_EXISTS`. |
| `encrypted_volume` needs elevation | **Accept** | Best-effort, no extra elevation. If the query is denied or unavailable → `unknown`. Capture still works. Installer may separately recommend BitLocker. Never treat `unknown` as `yes`. |
| In-process breaks Law 1 | **Accept the distinction; do not delete the spike** | Law 1 in 1.00, two sentences: (1) no ledger writes except `execute_command` / the core writer queue; (2) **shipped** Slice 1 default is out-of-process core. In-process is **dev/test and spike fallback only**, labeled in `system.status.transport`. §17 leak tests are **data-scope** tests and must pass in both transports. Do not advertise process isolation if an in-process build is what the operator installed. HOME_CONTEXT is not provided by QProcess. |
| Two-Home = sponsor threat smuggled in | **Reject the drop; accept the labeling** | See sharp question. Keep §13. Add threat-model paragraph. Do not cut 30 hours and call it one-Home. |

## Preserve (Claude is right)

Fail-closed. Confirmed ≠ paid/booked/safe. Two-phase attach fingerprints. Settlement needs a source. §11 codes stay closed: new codes require a spec revision, not an implementer mood.

## Estimate

No change to 152–240 unless Glen drops Home B from the **demo**. Then subtract ~8–16 hours of isolation tests only. Domain still has `home_id`. Do not pretend in-process saves the isolation package.

Add ~4–8 hours explicitly for: `VACUUM INTO` backup, import batch receipt, file-index lock. Fits inside existing backup/storage bands if we do not also write an NTFS treatise.

## What Sol should emit as 1.00

A short delta sheet plus patched sections, not a new novel:

1. Threat-model paragraph (one owner, two books, not sponsor IAM).
2. Rename `reservation.put` → `envelope.put` everywhere in the spec, examples, and method table #16.
3. Interruption gate without magic prefix.
4. Backup = SQLite backup/`VACUUM INTO` under the writer lock.
5. Import idempotency + `IMPORT_ALREADY_APPLIED`.
6. Lock identity = file index, junction+subst test.
7. `encrypted_volume` best-effort / unknown legal.
8. Transport: default QProcess; in-process not the shipped claim.
9. Error code additions only: `IMPORT_ALREADY_APPLIED` (and keep it out of the “inaccessible” lookalike set — it is a same-Home maintenance result).

Then freeze 1.00 for generation. If Claude’s next pass re-asks the sharp question, point at the threat-model paragraph and stop.

Grok does not need a second architecture round unless Sol drops two-Home isolation or puts in-process in the installer as equivalent to QProcess.
)
