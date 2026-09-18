# Local development environment

A local CPython **3.13.15** runtime was installed under this folder with **uv 0.12.16**. The development virtual environment is `../fullkit/.venv`. No system Python or global shell configuration was replaced.

Installed application dependencies include PySide6 6.11.2, jsonschema 4.26.0 and tzdata 2026.4; tests/build include pytest 9.0.2, build 1.4.0 and setuptools 84.0.0. The actual platform-resolved packages and wheel hashes are in `requirements-macos-arm64.lock` and `local-install-report.json`; `runtime.json` and `installed.freeze.txt` record what is present. The seed pip version is recorded separately in runtime.json.

The uv bootstrap environment uses the existing bundled Python only to install/manage uv. The development environment itself points to the local downloaded 3.13.15 runtime. These environments are local to this exact folder; virtual environments should be recreated after moving the workspace, not assumed portable.

## Everyday use

From `fullkit/`:

```sh
.venv/bin/python ../scripts/check_environment.py
.venv/bin/python -m pytest tests/contract/test_inventory.py -q
.venv/bin/python -m pytest tests/contract/test_two_home.py -q
```

The preserved release manifest includes `.DS_Store`; the portable workspace checker explicitly excludes that mutable Finder metadata while checking every substantive entry. The original manifest and ZIP remain unchanged.

The checker reports environment readiness separately from application status. Its exit 0 means that the contract/toolchain checks passed and that application integration either passed or still has the explicitly recognized absent-implementation import failure. Inspect the report’s application_status; an environment-ready result is **not** release acceptance. A different integration failure makes the checker fail.

For a fresh Git clone, use `python3 scripts/bootstrap.py` from the workspace root; it locates everything relative to the clone and restores the correct platform lock. See ../GIT-MIRRORING.md.

## Recreate on this Mac

From the build root, using an available Python 3.10+ only for bootstrap:

```sh
python3 -m venv environment/bootstrap
 environment/bootstrap/bin/python -m pip install -r environment/bootstrap-requirements.txt
 environment/bootstrap/bin/uv python install 3.13.15 --install-dir environment/runtimes --no-bin
 environment/bootstrap/bin/uv venv --seed --python environment/runtimes/cpython-3.13.15-macos-aarch64-none/bin/python3.13 fullkit/.venv
 fullkit/.venv/bin/python -m pip install --require-hashes -r environment/requirements-macos-arm64.lock
 fullkit/.venv/bin/python scripts/check_environment.py
```

The exact architecture-specific runtime directory above is for this Apple Silicon Mac. Other hosts must resolve their own compatible managed interpreter and dependency wheels; do not reuse this platform lock on Windows.

For Windows x64, use `fullkit/contract/requirements-windows.lock` and the commissioning instructions in `fullkit/contract/README.md`. Inspect the actual SQLite DLL/runtime; no macOS test establishes Windows lock aliases, ACLs, encryption, printing or power-loss behavior.

## Building the application later

Once Sol has implemented actual modules and package resources, from fullkit:

```sh
.venv/bin/python -m pip install -e . --no-build-isolation
.venv/bin/python -m pytest tests -q
.venv/bin/python -m build --wheel --no-isolation
```

We deliberately did not produce an empty wheel or install the unfinished application as if it worked. The repository currently has build configuration, contracts/tests and reserved source directories. The local toolkit probe only demonstrates that Qt can start a QProcess and that this SQLite runtime exposes a working Backup API on a disposable fixture.
