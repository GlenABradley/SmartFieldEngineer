<p align="center">
  <img src="assets/readme-hero.svg" alt="Smart Field Engineer — offline-first field operations" width="100%">
</p>

<p align="center">
  <img alt="Status: foundation in development" src="https://img.shields.io/badge/status-foundation_in_development-F59E0B">
  <img alt="Contract version 1.00.2" src="https://img.shields.io/badge/contract-1.00.2-36C5F0">
  <img alt="Python 3.13" src="https://img.shields.io/badge/Python-3.13-3776AB?logo=python&amp;logoColor=white">
  <img alt="Target platform: Windows 11" src="https://img.shields.io/badge/target-Windows_11-0078D4?logo=windows11&amp;logoColor=white">
</p>

Smart Field Engineer is an offline-first desktop operations system for a trusted independent field engineer. It is designed to keep two business Homes isolated while managing jobs, evidence, serial identity, office records, scheduling holds, durable command receipts, backups, and legacy imports on one local Windows laptop.

> [!IMPORTANT]
> This repository is a pre-release implementation workbench, not an installable application. The storage and first command boundary are real; most product workflows and the desktop UI are not implemented yet.

## What exists today

- A reviewed 20-method JSON-RPC contract with 479 accepted and 503 rejected schema specimens.
- Real provisioning for two independent Homes, each with its own SQLite ledger and blob roots.
- Handle-owned writer exclusion, forward-only migrations, WAL/FULL/FK database configuration, and Home/store identity checks.
- Strict bounded JSON framing, selected-context authorization, and context generation invalidation.
- Atomic `job.create` facts, audit entries, durable receipts, idempotent replay, conflict detection, and bounded job pagination.
- Real foundation and command-boundary tests, plus preserved contract, provenance, decision, and legacy-import source material.

**S04.1 is implemented, reviewed, and merged**: failed-switch recovery preserves read-only state, only the Core executor was removed, and invalid internal create revisions leave no rows. The [proposed S05 block](../handoff/NEXT-CODE-BLOCK.md) adds the real child/QProcess transport, test driver, and durable journal with process-loss and more-than-50-intent proof. It remains unimplemented; its later execution starts on a fresh branch from current main. See the [implementation roadmap](../fullkit/docs/IMPLEMENTATION-ROADMAP.md) for the complete sequence and exit criteria.

## Architecture

```mermaid
flowchart TD
    UI["PySide6 desktop — planned"] -->|QProcess + JSON-RPC — planned| EDGE["Edge core — codec implemented"]
    EDGE --> APP["Application — context and job-create boundary"]
    APP --> DOMAIN["Domain rules — mostly pending"]
    APP --> STORE[("Selected Home SQLite — foundation implemented")]
    APP --> BLOBS[("Selected Home blobs — directories only")]
    STORE -. separate store .- PEER[("Peer Home SQLite")]
```

Production is intentionally local and out-of-process: the desktop will own no writable SQL connection, and all ledger mutations will cross the same serialized command boundary.

## Authority and implementation status

Glen’s current instructions → Spec 1.00 + H1–H5 + adopted Addendum 1.00.2 → routine contract/schema detail. See the [authority register](../decisions/AUTHORITY.md). The roadmap reports status; it cannot adopt decisions, expand scope, or resequence work. C1/C2 are adopted and scheduled for S08, but remain unimplemented. Preserved package references calling them proposals are historical.

Scope-limited authority is the project’s **“Fourth Amendment”** principle: a review or documentation assignment confers authority within that assignment. It does not authorize changing contracts, milestone boundaries, or product scope. Useful reviewer input stays identifiable as input until adopted.

Current S04.1 evidence: Sol observed **44 application + 15 workspace + 8 inventory = 67 passing cases on Linux/Python 3.12.14**, plus 479 positive/503 negative schema specimens. Grok reviewed the actual a94e3a7 diff and passed it; he did not independently rerun tests. Earlier 41-case/macOS results remain historical. PySide6 is absent on the verification host, so the environment checker remains red; these results do not establish the supported Python 3.13/Qt toolchain or a finished application. The supplied two-Home integration suite still fails collection because the real test driver is absent; Windows execution remains unqualified.

## Start here

| If you want to… | Read… |
|---|---|
| Understand the workbench | [START-HERE.md](../START-HERE.md) |
| See current implementation status | [Implementation roadmap](../fullkit/docs/IMPLEMENTATION-ROADMAP.md) |
| Work on the code | [CONTRIBUTING.md](../CONTRIBUTING.md) |
| Review community expectations | [Code of conduct](../CODE_OF_CONDUCT.md) |
| Read the governing contract | [Authority and adopted overlay](../decisions/AUTHORITY.md), then [preserved contract entry](../fullkit/contract/README.md) |
| Trace adopted decisions | [Authority register](../decisions/AUTHORITY.md) |
| Review foundation evidence | [Store foundation](../fullkit/docs/STORE-FOUNDATION.md) |
| Restore the toolchain | [Environment guide](../environment/README.md) |
| Report a vulnerability | [Security policy](../SECURITY.md) |
| Ask for help | [Support guide](../SUPPORT.md) |

## Development setup

The reproducible bootstrap currently supports Apple Silicon macOS and Windows x64. A reviewed Linux dependency lock does not yet exist.

```sh
python3 scripts/bootstrap.py --plan
python3 scripts/bootstrap.py
```

The bootstrap installs the pinned Python 3.13.15 runtime and project dependencies inside the checkout. It does not alter the system Python. See [Git mirroring and clean-clone setup](../GIT-MIRRORING.md) before running or publishing the project.

## Product boundary

Slice 1 is intentionally narrow: one trusted Windows owner, one laptop, two isolated Homes, local capture, and offline operation. It does not include cloud sync, telephony, OCR/ASR, connectors, payment automation, autonomous agents, or a plugin platform.

The effective contract is version 1.00.2. Windows locking, ACLs, encryption observation, offline rendering, clean installation, and power-loss behavior remain release qualification—not inferred capabilities.

## Repository status

This source is available for review and development, but the owner has not selected a project distribution license. Do not infer redistribution rights from dependency licenses or repository visibility. No stable release has been published.
