# Second pass before Glen’s next mirror

Scope: complete the local repository’s navigation, setup and validation. No application implementation, new public method, external message or remote push. Existing reviewed files remain preserved.

## Corrections made

1. **GitHub entry point.** The repository homepage was displaying the preserved package README, whose package-relative paths do not describe the outer repository. Added `.github/README.md` with working repository-relative navigation and honest current status. GitHub gives this location precedence, so the original root snapshot can remain untouched. Source: [GitHub README location rules](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).
2. **Test collection boundary.** Added root pytest.ini so a normal repository test run targets workspace/application tests, not archived legacy tests or duplicate tests inside the preserved artifact. Default application acceptance still fails visibly until implemented; no tests were marked skipped/xfail.
3. **Misclassified missing imports.** The environment checker previously accepted any missing `packages...` import as an absent implementation. It now recognizes only the exact absent-driver case and checks whether the driver already exists. An internal import failure, syntax error, assertion failure or timeout is reported as a failure.
4. **Importable checker and timeout reporting.** The checker now has a main guard and reusable classification function. Timed-out checks produce a recorded exit 124 and log rather than terminating without an explanation.
5. **Relocated virtual environment detection.** Bootstrap now checks both version and runtime/prefix ownership before reusing an existing venv. A same-version venv pointing to another checkout must be explicitly recreated rather than silently reused.
6. **Workspace regression tests and contribution guidance.** Added real tests for failure classification, platform lock selection, venv identity, navigation, tamper detection and acceptance-test parity; added CONTRIBUTING.md with current test/build boundaries and no invented project license.
7. **Acceptance-test paths.** The first root-level run exposed another issue: the copied inventory/import tests located the contract relative to the caller’s working directory. The working copies now locate it through their own parent directories. Preserved packaged tests remain unchanged; their test names and every domain assertion are checked for parity with the working copies.

## Validation and limits

Current machine-readable results are generated into `reports/Environment-Validation.json` and `reports/Second-Pass-Validation.json`; these remain local generated evidence. The original artifact’s validation receipts are unchanged. A fresh temporary checkout/bootstrap on this Mac is a setup test, not Windows qualification or a running application demonstration.

Verified results: **15 workspace tests and 8 inventory tests passed**. Schema validation passed 479 positive and 503 negative specimens across 212 definitions and exactly 20 public methods. All 42 substantive baseline entries matched their original hashes; the original manifest’s Finder metadata remains explicitly excluded. Original root snapshots were unchanged.

A fresh temporary Git checkout installed its own pinned Python 3.13.15 runtime and dependencies and completed the environment checker successfully on this Mac. The real Git index was preserved. Default root test collection found the intended 23 tooling/inventory cases and the expected missing application-driver error; archived tests were not collected. Fresh-install logs were retained locally and the disposable installation was removed.

The new workspace tests are tests of tooling, not mocks of Full Kit. The five application integration vectors remain dependent on the missing real application interface. C1/C2 remain pending proposals; no owner decision was inferred from this review.

No automatic CI workflow or deployment was added. Windows clean-install behavior, ACL/lock aliases, encryption observation and real hardware tests remain required. Actual customer legacy data are still absent. Glen chooses project licensing; this preparation does not grant a new license.
