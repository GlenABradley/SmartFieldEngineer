# Serial-once workflow — executable local increment 0.2.0

The commands below operate on one trusted local operator's ledger. They do not enforce user roles or Business Home isolation. Back up existing data before upgrading; opening the ledger adds identity tables and a persistent ledger namespace without replacing existing job tables.

## Capture input

`observe-serial` reads JSON. Required fields are `raw` (nonempty text or null), `method`, `source`, `captured_by`, and offset-aware `observed_at`. Optional fields are `job_id` and `asset_id` (both or neither), `manufacturer`, `model`, `identity_kind` (`serial` or `asset_label`), and `evidence_id`.

Supported methods are `manual_label_read`, `voice_transcript`, `photo_transcription`, `barcode_scan`, and `device_inventory_output`. These describe the provenance of supplied text; no command automatically records audio, transcribes, scans, or runs device discovery. Unknown manufacturer/model values are null. Unknown identity is null, not the literal string “unknown.” A panel label is `asset_label`, not a fabricated serial.

Evidence IDs must be real imported evidence belonging to the assigned job. File digest is checked at capture and verification. An unassigned spoken note can be stored without an evidence ID and explicitly assigned later. Its verifier must then provide the source of the actual identity check. An absent file is not a photograph. An operator statement is not machine-certified evidence.

Use the supplied `examples/serial-voice.json` only for training; it is deliberately DEMO. The real program returns generated observation and bind IDs.

## Working Windows training sequence

Run from the kit folder with Python 3.12 installed:

```powershell
$serialDemoHome = Join-Path $env:TEMP ('FieldOfficeSerial-' + [guid]::NewGuid().ToString('N'))
py -3.12 fieldoffice.py --home $serialDemoHome init
py -3.12 fieldoffice.py --home $serialDemoHome job examples/job.json
$serialCapture = py -3.12 fieldoffice.py --home $serialDemoHome observe-serial examples/serial-voice.json | ConvertFrom-Json
py -3.12 fieldoffice.py --home $serialDemoHome observations
py -3.12 fieldoffice.py --home $serialDemoHome assign-observation $serialCapture.observation_id DEMO-001 SW1
py -3.12 fieldoffice.py --home $serialDemoHome recall-serial DEMO-001 SW1
py -3.12 fieldoffice.py --home $serialDemoHome verify-bind $serialCapture.observation_id 0 DEMO-owner 'DEMO physical-label review' 'Initial DEMO bind'
py -3.12 fieldoffice.py --home $serialDemoHome recall-serial DEMO-001 SW1
py -3.12 fieldoffice.py --home $serialDemoHome document DEMO-001 work_order examples/serial-document.json
py -3.12 fieldoffice.py --home $serialDemoHome dispute-bind DEMO-001 SW1 1 'DEMO conflicting identity'
py -3.12 fieldoffice.py --home $serialDemoHome recall-serial DEMO-001 SW1
py -3.12 fieldoffice.py --home $serialDemoHome recall-serial DEMO-001 SW1 --revision 1
py -3.12 fieldoffice.py --home $serialDemoHome verify
```

The first current recall is unresolved until verification. The dispute makes current recall unresolved again. Explicit historical recall still returns revision 1 and reports the disputed current state. Unresolved recall is a successful query with `status: unresolved` and `serial: null`, not an invented value. Unknown jobs are errors.

The simple desktop command form exposes these operations, too; historical recall and job-filtered observations remain CLI options. The Tk window and this PowerShell training sequence were not exercised on Windows; the corresponding CLI lifecycle was tested via Python subprocesses on macOS.

## Correct and reuse

Create a new observation for the same asset with corrected identity and explicit source. Assign it to the job if needed. Run `verify-bind` with the last current revision and a correction reason. Revision 2 points to revision 1; a stale expected revision is rejected, even if another program instance made the competing revision. An observation can only be assigned once and verified once. If assigned incorrectly, preserve it and create a new correctly assigned observation.

A replacement device gets a new asset ID. The operator can record the replacement relationship as a sourced job fact; no automatic replacement-graph feature is claimed. Reusing an asset on another job requires a new explicitly assigned and verified observation for that job before recall there. This prevents accidental recall from an unrelated job but does not implement access control between people. A similar serial never automatically merges assets.

`document` accepts an optional `asset_serial_refs` list of asset IDs. It resolves current verified serials for the document's job and stores only asset ID, bind ID, revision and serial in an immutable prepared-document snapshot. Disputed or unresolved references block preparation. Caller-supplied `asset_identity_snapshots` are rejected. Older prepared documents keep their original snapshot. Issuance, sending and accounting remain external/manual boundaries.

## Implemented data representation

| Object | Stored facts | Mutability |
|---|---|---|
| `office_meta` | Persistent random `ledger_id` | Created once; backup preserves it; not a Business Home credential |
| `serial_observations` | ID, original capture JSON, creation time | Append-only, database update/delete triggers reject writes |
| `serial_assignments` | Observation ID, job ID, asset ID | One assignment per observation through the application |
| `asset_bindings` | Bind ID, asset, revision, observation ID, full verified bind JSON | Append-only with update/delete guards; unique asset/revision and observation |
| `asset_heads` | Asset ID, latest revision, active/disputed state | Transactional expected-revision control |
| `asset_jobs` | Explicit verified asset/job associations | Added only during verification |
| `documents` | Prepared payload including optional identity snapshots | Existing immutable preparation path; no automatic issuance |

A bind carries `ledger_id`, `bind_id`, `asset_id`, `revision`, `source_job_id`, `observation_id`, `identity_kind`, `raw`, trim-only `normalized`, nullable `manufacturer`/`model`, original observation, verification actor/time/source, predecessor bind ID and change reason. Current dispute belongs to the head, not a rewrite of the verified historical bind. The 1.3 Home-scoped JSON Schema is a future design artifact, not the schema of this local increment.

Audit verification checks stored observation, assignment and bind payloads against their audit events, checks head revision consistency, and retains the existing blob integrity checks. These detect damage; a privileged administrator can rewrite a local database and its hash chain. Do not market these checks as tamper-proof storage.

## Remaining work

Automatic voice/OCR intake, authenticated roles, shared Homes, secure mobile upload, assignment grants, a released guided-installation engine, automatic asset discovery, issuer supersession tracking and live instrument adapters are not implemented here. The ledger stores the operator's verifier identity as text; it does not authenticate that person or independently prove the label is correct.
