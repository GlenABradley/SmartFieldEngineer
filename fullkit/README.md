# Full Kit Composed — implementation repository

The implementation starts here. Read `../AGENTS.md`, `../START-HERE.md` and `contract/README.md`.

This implementation directory now contains a real Home/store foundation: provisioning, exclusive writer ownership and transactional migrations. See [foundation status and evidence](docs/STORE-FOUNDATION.md). The first raw context/job-create receipt path is implemented; complete transport/desktop behavior and the integration driver remain unfinished; the supplied acceptance tests remain visibly failing. No success-returning stubs were introduced.

Local environment: `.venv/bin/python` on this Mac. Run `../scripts/check_environment.py` with it to check the toolchain and contract without changing the baseline artifact. See `../reports/Environment-Validation.json` for actual results.

The Windows target remains a separately qualified production environment. Git metadata lives one directory above, alongside the handoff and team files. Glen manages the GitHub mirror; setup and local checks do not push or send reviewer messages.
