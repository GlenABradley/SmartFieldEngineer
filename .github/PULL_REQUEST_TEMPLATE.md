## Problem and outcome

<!-- What problem does this solve, and what is observably different? -->

## Scope

<!-- Name the affected milestone, modules, contract methods, and explicit non-goals. -->

## Validation

<!-- List exact commands, observed results, platform, and any blocked qualification. -->

## Safety checklist

- [ ] I read `AGENTS.md`, `START-HERE.md`, `decisions/AUTHORITY.md`, and the applicable contract.
- [ ] I kept reviewed snapshots, `references/`, and `fullkit/contract/reference/` byte-identical.
- [ ] I did not add a public RPC method, hidden adapter, fake success path, blanket skip, or mock acceptance driver.
- [ ] All mutations in this change cross the application command/writer boundary.
- [ ] Tests use disposable fixtures and the diff contains no customer data, credentials, private paths, or generated ledgers.
- [ ] I recorded commands actually run, failures, platform limits, and remaining qualification.
- [ ] I updated `handoff/SESSION-LOG.md` when application behavior or implementation status changed.
- [ ] I reviewed the final diff and called out any contract or owner decision required.
