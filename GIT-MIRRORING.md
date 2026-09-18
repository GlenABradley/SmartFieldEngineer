# Git mirroring and clean-clone setup

**Mirror the entire `Build Artifact` folder.** Its `.git/` now lives here, so the team register, handoff, decisions, setup scripts, references and `fullkit/` travel together. The previous nested repository had no tracked files, commits or remotes; its empty metadata was moved up intact. There is no submodule or nested Git repository.

No commit, remote, push or publication was created by this preparation. Choose the remote and its visibility yourself when promoting the folder. Git stores the build materials; it does not install another agent or transfer access to an account.

## Included

- Current contracts, generated schema/specimen baseline and asserting tests.
- Implementation directory structure and build configuration.
- Team/ally charter, personal Sol handoff and authority register.
- Reviewed canons, legacy source kit, review inputs and archived historical contracts.
- Exact macOS ARM64 and Windows x64 dependency locks, and a hashed bootstrap-tool lock.
- Original copy provenance. Absolute paths in historical receipts are provenance from Glen’s machine, not configuration requirements for a clone.

The materials are small enough for ordinary Git; no Git LFS dependency is needed. Binary document/ZIP snapshots are intentional, and are preserved rather than unpacked/repacked on every build.

## Excluded but retained locally

Managed Python distributions, bootstrap/development virtual environments, dependency cache, host runtime/install receipts, generated verification reports, build outputs, editor/OS files and operational SQLite databases. Local secrets/configuration and private-data/owner-root directories are ignored. Ignore rules are convenience, not a secret detector; review any future staged data before publishing it.

`.gitattributes` standardizes new source text as LF while preserving reviewed contract/reference snapshots byte-for-byte. Existing package manifests remain unchanged. Their accidental `.DS_Store` entry is explicitly excluded by `scripts/verify_baseline.py`: Finder state is not a portable source artifact. All substantive manifest entries are still checked. The original ZIP remains intact, including its exact original metadata.

## Clean clone

Clone into any local folder, then use an existing Python **3.10+** solely to bootstrap:

```sh
python3 scripts/bootstrap.py --plan
python3 scripts/bootstrap.py
```

On Windows, use `py -3 scripts/bootstrap.py` with a Python 3.10+ installation. The script installs CPython 3.13.15 inside `environment/runtimes/`, creates `fullkit/.venv`, installs the matching platform lock with hashes, and runs local checks. It does not edit system Python or global shell settings. Currently verified locks support Apple Silicon macOS and Windows x64. Other platforms need a separately reviewed wheel lock.

Everyday checks, from the root:

```sh
fullkit/.venv/bin/python scripts/check_environment.py
```

Windows equivalent:

```powershell
fullkit\.venv\Scripts\python.exe scripts\check_environment.py
```

A clone starts without `reports/Environment-Validation.json`; the checker creates it. Environment readiness is separate from application completion. The application test currently exposes the missing implementation, and Windows commissioning is still required.

For implementation commands, work inside `fullkit/`; for Git operations, use this outer root (Git will also discover it from subdirectories). Do not initialize another `.git/` inside fullkit. The local preparation report is `reports/Git-Mirroring-Validation.json`; it is regenerated evidence and intentionally untracked.
