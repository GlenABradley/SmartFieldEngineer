# Smart Field Engineer

A local field office for an independent engineer: evidence capture, equipment identity, job records, immutable document pins, interrupted-work history, and recovery across two business Homes.

**Current state: implementation contract and development environment ready; Slice 1 application not yet implemented.** The legacy 0.2.0 code is an import source and historical reference. Windows release qualification remains ahead.

## Start here

- [Local workspace guide](../START-HERE.md)
- [Current 1.00.1 build contract](../fullkit/contract/README.md)
- [Adopted direction and pending C1/C2 proposals](../decisions/AUTHORITY.md)
- [Astra’s handoff to GPT Sol](../handoff/TO-GPT-SOL.md)
- [Agent roles and allies](../team/AGENT-REGISTER.md)
- [What was actually validated](../fullkit/contract/Validation.md)
- [Second-pass review and corrections](../handoff/SECOND-PASS-REVIEW.md)

## Recreate the environment

Clone this repository, enter its root, and run with an existing Python 3.10+:

```sh
python3 scripts/bootstrap.py --plan
python3 scripts/bootstrap.py
```

On Windows use `py -3` in place of `python3`. Current dependency locks support Apple Silicon macOS and Windows x64. Bootstrap installs its runtime and virtual environment locally; see [Git mirroring and setup](../GIT-MIRRORING.md).

Then, on macOS:

```sh
fullkit/.venv/bin/python scripts/check_environment.py
fullkit/.venv/bin/python -m pytest tests/workspace fullkit/tests/contract/test_inventory.py -q
```

On Windows the interpreter is `fullkit\.venv\Scripts\python.exe`. The application integration tests remain visibly failing until their real interface is implemented. A passing environment check does not mean a finished application.

Implementation belongs in `fullkit/`. Team, decisions, handoff and setup files live alongside it and are part of this same Git repository. Start with [contribution guidance](../CONTRIBUTING.md).

The repository-root README and Validation.md remain unmodified copies of the original artifact. This GitHub entry page supplies repository-correct navigation without rewriting those reviewed snapshots.
