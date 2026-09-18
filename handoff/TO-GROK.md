# Sol → Grok: code review handoff

## 2026-09-18 — first code assessment, commit 3c85b53

Grok, Glen asks for your eyes on the code Sol wrote and your assessment before the next generation block. The workshop has moved from contract-only to a real store/first-command foundation. Please attack the code and collaboratively identify the smallest fixes; do not treat this handoff as approval to broaden Slice 1.

Review target: **3c85b53**, feat: add Home/store and command receipt foundation, based on 89379c9. Local tree was clean when this review started. Remote HEAD was still 89379c9 when checked; an exact git-archive ZIP of 3c85b53 is provided for review. No local runtimes, untracked logs, credentials or customer Homes are included. Glen still controls mirroring; no push was attempted.

Glen explicitly adopted artifact C1/C2: “i agree. adopt C1/C2. i approve.” Effective authority is Spec 1.00 + H1–H5 + decisions/Addendum-1.00.2.md. Original package proposal labels are historical; adoption does not claim those resume/scope implementations exist yet.

### What now works

Two real Home stores/private index; handle-owned writer lifetime; packaged forward-only SQL migrations; SQLite WAL/FULL/FK; application-owned selected context/generation; strict frame parsing and exact twenty-method registry; job.create with empty capture_refs; job.list high-water keyset paging; operation.get; durable confirmed/failed receipts, exact replay and intent conflicts. Facts/job event/principal audit/terminal receipt share a transaction. Unfinished valid routes fail Internal error, not synthetic success.

Read code in this order:

1. fullkit/apps/edge/rpc.py — frame/shape/error boundary.
2. fullkit/packages/application/session.py — context-first dispatch, switching, generations/cursors.
3. fullkit/packages/application/commands.py — canonical fingerprint, replay and transaction.
4. fullkit/packages/application/store.py and fullkit/adapters/sqlite/store.py — lifetime/migrations/connection ownership.
5. fullkit/packages/application/homes.py — index/provision atomicity and ambiguous acknowledgement.
6. fullkit/apps/edge/writer_lock.py and principal.py — actual platform adapter code, Windows unexecuted.
7. fullkit/migrations/local/001_store.sql and 002_commands.sql.
8. fullkit/tests/application/ plus tests/workspace/, preserved contract and working supplied integration vectors.

### Evidence and honest limits

Sol executed 41 application foundation + 15 workspace + 8 inventory cases: **64 passed** on this Mac. Schema checks: 479 positive / 503 negative, 212 definitions, exactly 20 methods. Preserved 42 substantive baseline entries/root snapshots matched. An isolated installed development wheel exercised actual provision/select/create/list/receipt/replay outside the source tree. See fullkit/docs/STORE-FOUNDATION.md for committed results; detailed generated logs remain local and are not in the ZIP.

These are Sol’s observed results, not tests you have independently run. Please state your own host/runtime and distinguish your executions from static review.

No QProcess core binary/client, integration driver, serial lifecycle, evidence/documents, office/holds, actual backup/restore/import or Qt shell yet. Supplied integration file still fails on missing packages.application.testing. The recovery guard test uses a labeled Backup API fixture, not implemented restore. Windows handle/principal code is present but not executed; aliases/ACLs/encryption observations and hardware/power loss remain pending. POSIX lock is development only. Runtime/security/license gates and full recovery-directory immutability remain release obligations.

### Specific review pressure points

- Can malformed UUID/request IDs or parser/serialization edge cases produce an invalid response or escape the closed error boundary?
- Does authorization remain sufficient at application/storage entry points, including code paths that do not arrive through the codec? Are internal trusted adapters/principal injection distinguished from caller authority?
- Are fingerprint normalization/replay ordering and inactive guard correct, including cross-command operation reuse and failed receipts?
- Can migration/commit/rollback acknowledgement failures leak a lock, fabricate success or leave a registered store deleted? What happens if cleanup/rollback itself fails?
- Can a Home switch lose track of the prior writer or leave a stale generation/cursor usable? The former recovery context reopening case deserves attention.
- Do root/file/sidecar aliases, fixed NTFS restrictions and retained Windows handles behave as intended? Separate real defects from missing Windows qualification.
- Are read-only recovery side effects and crash-orphan handling narrow enough for the eventual frozen acceptance tests? Flag the exact unmet requirement rather than relabeling the fixture as restore.
- Are four nested single-thread executors a necessary ownership seam or needless overhead/deadlock risk when QProcess/Qt enter? Inspect shutdown/error ordering.

### Requested return

Give a short overall assessment, then concrete findings with severity, file/line, trigger, expected vs observed behavior and smallest correction/test. Mark required corrections before transport work separately from later release work. Describe what you actually inspected/executed and what remained inaccessible. Assess the proposed next block in NEXT-CODE-BLOCK.md and suggest bounded changes. A verdict may be “proceed after fixes”; do not manufacture consensus or certify Windows.

Review receipt will be appended below after your response. No assessment is attributed to you before it arrives.
