# Working on Smart Field Engineer

Read AGENTS.md, START-HERE.md, decisions/AUTHORITY.md and fullkit/contract/README.md. Glen owns adopted direction; the artifact C1/C2 clarifications are adopted in decisions/Addendum-1.00.2.md; historical package labels do not supersede that decision.

## Work locations and tests

Implement the new application under `fullkit/`. Do not modify reviewed references, root artifact snapshots or the release ZIP. Historical legacy code is preserved under references/; do not run its installer to create Slice 1.

`pytest.ini` at the repository root limits normal discovery to workspace tests and the new application’s tests. It prevents archived tests and duplicated packaged baseline tests from being collected as current application tests. No application test is skipped: the default suite will currently fail collection because the real application driver is missing.

For the checks that can pass before implementation:

```sh
fullkit/.venv/bin/python -m pytest tests/workspace fullkit/tests/contract/test_inventory.py fullkit/tests/application -q
fullkit/.venv/bin/python scripts/check_environment.py
```

Use `fullkit\.venv\Scripts\python.exe` on Windows. For full application acceptance, run `python -m pytest` with the development interpreter from the repository root, or `python -m pytest tests` from fullkit/. Do not replace absent application behavior with mocked success, xfail or blanket skips. Workspace-tool tests check real helper behavior and classification; they do not claim application correctness.

## Reviewable changes

Explain the problem, the final behavior, tests actually run and remaining qualification. Keep application changes separate from historical evidence. Contract changes need explicit decision/version provenance; a schema edit does not itself adopt a product decision. Update handoff/SESSION-LOG.md and preserve the five adopted harmony patches.

Dependencies belong in reviewed, platform-specific hash locks. A new platform needs its own resolution and validation. Preserve original notices on third-party material. No project redistribution license has been selected in this preparation; Glen owns that decision, so do not invent a license or substitute third-party license terms for project terms.

Generated reports, runtimes, virtual environments, caches, operational ledgers and private data remain local. Use disposable fixtures. Review your diff before mirroring. Do not push, publish or contact other model tasks on Glen’s behalf unless he instructs you.

There is no automatic CI/deployment workflow in this preparation. Checks are explicit local commands. Windows installation, lock aliasing, ACLs, encryption observation and power-loss behavior require their own recorded qualification.
