# Network Engineer Copilot implementation kit

**Current revision 1.4 / application 0.2.0:** Start with `docs/revision-1.4/Reflection-and-Integration.md` for the integrated review and `docs/revision-1.4/Serial-Workflow.md` for the new executable identity workflow. The local ledger now captures proposed/unassigned identities, verifies and recalls serials, preserves correction revisions, blocks disputed recall, and pins prepared-document identity snapshots. Voice/photo transcriptions are supplied inputs; automatic recognition, Home isolation and roles remain outstanding. The inherited canons and overlays remain historical baselines.

**[FLOOR] Revision overlay 1.3:** Start with `docs/revision-1.3/README.md` for the five meaning patches, preserved invariants, and floor/horizon/halo scope labels; both base canons remain intact and no executable capability is added by this revision.

**Product revision 1.2:** Read `docs/Business-in-a-Box-Product-Brief.md` for the primary buyer, expert and guided-technician modes, full job-to-payment lifecycle, and commercial acceptance requirements. This is a product-definition update; it adds no executable capabilities.

**Architecture revision 1.1:** Read `docs/Hybrid-AI-Decision.md` first. Glen selected local AI plus cloud assistance when needed. This decision supersedes the local-only product-design assumption in Canon 1.0; the included executable advisor still supports local inference only. Cloud implementation and live validation remain outstanding.

This is working proof-of-concept software plus a commercial implementation specification. It is not a released commercial product. No customer networks, accounts or production machines were changed while preparing it.

Read `docs/Implementation-Canon.md` for the complete architecture, budget, installation sequence, manual equipment workflows, integration boundaries and release gates. `VALIDATION.md` records exactly what was tested.

## Start locally

Python 3.11 or newer is required; Python 3.12 on Windows is the reference deployment.

```powershell
py -3.12 fieldoffice.py --home "$env:USERPROFILE\FieldOfficeDemo" init
py -3.12 fieldoffice.py --home "$env:USERPROFILE\FieldOfficeDemo" job examples/job.json
py -3.12 fieldoffice.py --home "$env:USERPROFILE\FieldOfficeDemo" record DEMO-001 requirement examples/requirement.json
py -3.12 fieldoffice.py --home "$env:USERPROFILE\FieldOfficeDemo" reserve DEMO-001 2030-01-07T08:00:00-05:00 2030-01-06T18:00:00-05:00
py -3.12 fieldoffice.py --home "$env:USERPROFILE\FieldOfficeDemo" document DEMO-001 estimate examples/invoice.json
py -3.12 fieldoffice.py --home "$env:USERPROFILE\FieldOfficeDemo" report DEMO-001 demo-report.html
py -3.12 -m unittest discover -s tests -v
$env:FIELD_OFFICE_HOME="$env:USERPROFILE\FieldOfficeDemo"
py -3.12 desktop.py
```

Open the generated HTML in your browser and use Print / Save to PDF. Demo records deliberately say DEMO. Do not issue them to customers. The GUI is a simple operation form, not the final commercial interface. File and record identifiers printed by each operation feed later operations; do not type illustrative IDs as real IDs.

No Python package installation is required for the core. `pdf-pages.py` requires `pypdf==6.10.0`; install it into a dedicated virtual environment. `local-assist.py` requires a separately installed local Ollama runtime and downloaded model. The telephony functions require a funded Twilio account and configuration; they were not deployed.

## Operational limitations

One operator, one machine, USD, manually reviewed tax amounts, no automatic routing, no automatic platform actions, no background syncing. Back up while other program instances are closed. Local data is not encrypted by this application: use BitLocker or an encrypted volume before storing customer data. Account-wide authorization, hardened multitenancy and trusted timestamps are commercial release work.

Evidence defaults to internal. Only attachments explicitly marked customer enter closeout ZIP files. Customer exports still contain client name, scope and open requirements; inspect them before sending. Export is not delivery. Document status is prepared, and invoice totals are not accounts receivable until separately reconciled. No software command sends messages or places orders in the local core.

## File inventory

- `fieldoffice.py`: transactional local job, schedule, evidence, approval, stock, money, document, identity observation/bind/recall and backup operations.
- `desktop.py`: local desktop front end for those operations.
- `local-assist.py`: local model advisory drafts with fixed loopback endpoint and no tools.
- `install-windows.ps1`: application installation with explicit failures.
- `collect-network.ps1`: host diagnostic collection and optional authorized single-target ping.
- `pdf-pages.py`: extract or replace one PDF page while preserving originals.
- `telephony/`: runnable Twilio Functions for speech or keypad routing and voicemail.
- `tests/`: deterministic core regression tests.
- `examples/`: training inputs, never real credentials or customer records.
- `docs/`: implementation specification and budget.

The code has no placeholder success functions. Functions outside its implemented scope are documented as manual procedures or outstanding development, not hidden behind active buttons.
