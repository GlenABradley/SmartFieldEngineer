# Security policy

Smart Field Engineer handles operational records and local evidence, but it is still pre-release software. Do not use the current repository build with real customer data.

## Reporting a vulnerability

When the repository exposes **Security → Report a vulnerability**, use that flow to submit a private report. If private vulnerability reporting is unavailable, contact the repository owner through a private channel listed on their GitHub profile. If no private channel is available, open a public issue that asks for one without including vulnerability details.

Do not publish a suspected vulnerability and do not include customer records, credentials, recovery material, or private filesystem paths in any report.

A useful report includes the affected revision, platform, impact, minimal reproduction using synthetic data, and any proposed mitigation. Please allow the maintainer time to reproduce and address the issue before public disclosure.

## Supported versions

No version is currently supported for production use. Security fixes apply to the active development line until the project publishes a supported release policy.

## Security boundary

The current contract assumes one trusted Windows owner. Home isolation prevents accidental cross-business reads and writes; it is not a defense against a hostile administrator or a compromised operating system. Windows ACL, encryption, installer, offline-rendering, and power-loss claims require separate target qualification.
