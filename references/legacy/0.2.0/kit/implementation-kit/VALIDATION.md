# Validation record

September 18 2026. Tested on this macOS host with bundled Python 3.12, SQLite and Node.js. Target Windows hardware was not available.

## Passed

- Twelve automated core tests: protected-envelope conflict, timezone requirement, approval invalidation after scope revision, approval expiry and wrong hash, transactional inventory shortage, job/evidence isolation and closeout blocking, private-evidence export filtering, damaged-evidence detection, backup restoration, currency arithmetic and HTML escaping, duplicate-outcome rejection, and requirement reopening/resolution.
- An independent command-line training lifecycle: initialize, import DEMO job, add requirement, reserve time, receive and consume stock, record time/cost/payment, import evidence, satisfy requirement, complete field track, prepare invoice, export report/package, approve an exact action hash, record a simulated manual outcome, verify integrity and restore backup. Prepared invoice total was USD 166.00; recorded direct costs were USD 22.50. No external submission occurred.
- PDF page extraction and replacement with pypdf 6.10.0: four-page source retained, page four extracted, one replacement page substituted, page count and geometry checked.
- Python source compilation and JavaScript syntax checks for all four telephone functions.
- Budget totals independently summed from budget.json: core 2320.00, expanded 1185.00, optional 1024.99 USD.
- Final DOCX rendered to 20 pages. All pages visually inspected; after the final text correction only page 11 changed, and that page was re-inspected.

## Not yet validated

- Windows installers, device drivers, PowerShell host diagnostics and the Tk desktop window on a Windows machine.
- Actual phone calls, Twilio hosted deployment, speech recognition quality, recording availability, fallback behavior, or carrier billing.
- A local Ollama model response, latency or diagnostic quality on the selected Toughbook.
- Any physical instrument, calibration, customer network, printer, radio, modem, battery or carrier bag.
- Field Nation or WorkMarket account entitlements or live APIs. No adapter is included or claimed.
- Concurrent-machine use, financial issuance and reconciliation, server security, multi-tenant use, disaster recovery on replacement hardware or commercial release compliance.

Passing the included tests establishes the tested local behaviors only. It does not establish complete product readiness. See the implementation canon for remaining work and acceptance gates.

## Revision 1.4 / application 0.2.0 — local identity increment

September 18, 2026. Original validation statements above are retained as historical results; all original twelve core tests were rerun and passed with the bundled Python 3.12 runtime on macOS. Six additional tests passed: unknown/unassigned voice-note intake; revision correction, stale writer rejection, historical recall and dispute; wrong-job/damaged evidence rejection; unknown model, asset-label and wrong-job recall behavior; immutable prepared-document snapshots and backup; and subprocess CLI observation-to-recall lifecycle. Total: 18 passing tests.

The default system Python is 3.8 on this host and is below the required Python 3.11 minimum; an initial run there failed three original timestamp tests. The supported Python 3.12 rerun passed. No Python-3.8 compatibility is claimed.

Identity table creation upgrades the local ledger without replacing the existing jobs. Model/manufacturer may remain unknown. The new ledger namespace is persistent across backup/restore, but is not Home authentication or user isolation. No automatic speech recognition, OCR, camera/barcode capture, mobile ingestion, role enforcement, shared tenant service, live cloud request, device modification, invoice issuance or payment reconciliation was performed. Windows/Tk/PowerShell and physical workflows remain unvalidated.
