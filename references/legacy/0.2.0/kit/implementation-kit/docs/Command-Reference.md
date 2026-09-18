# Practical command reference

Run these from the kit folder on Windows. Substitute real IDs returned by previous commands. Keep training data separate. All operations are local except the optional local-model request, which targets loopback only.

```powershell
# Select an encrypted, non-synchronized production data folder after setup.
$env:FIELD_OFFICE_HOME="$env:USERPROFILE\FieldOfficeData"
py -3.12 fieldoffice.py init
py -3.12 fieldoffice.py --help
py -3.12 desktop.py

# Make your own job JSON from examples/job.json, then import it once.
py -3.12 fieldoffice.py job my-job.json
py -3.12 fieldoffice.py list
py -3.12 fieldoffice.py show JOB-ID
py -3.12 fieldoffice.py record JOB-ID requirement my-requirement.json

# Inbound travel belongs to this destination job. Review time does not release a hold.
py -3.12 fieldoffice.py reserve JOB-ID 2030-01-07T08:00:00-05:00 2030-01-06T18:00:00-05:00 --work 180 --travel 45 --closeout 30 --recovery 90 --state soft
# Repeat with --state hard only after actual acceptance is recorded.
py -3.12 fieldoffice.py release JOB-ID "Cancellation confirmed by buyer; remaining return separately tracked"

# Sourced records and protected original evidence.
py -3.12 fieldoffice.py record JOB-ID test measurement.json
py -3.12 fieldoffice.py attach JOB-ID .\test-result.pdf "Panel A port 7" "Post-repair test" customer
py -3.12 fieldoffice.py satisfy JOB-ID REQUIREMENT-ID EVIDENCE-ID "Reviewed target, setup and acceptance criteria"
py -3.12 fieldoffice.py track JOB-ID field complete "Technician departure review"
py -3.12 fieldoffice.py track JOB-ID returns pending "Buyer return instruction"

# Whole stock units and USD amounts. Returns and fractional quantities need manual accounting.
py -3.12 fieldoffice.py receive PATCH-CAT6 bag 10 4.25
py -3.12 fieldoffice.py consume JOB-ID PATCH-CAT6 bag 2
py -3.12 fieldoffice.py record JOB-ID cost my-cost.json
py -3.12 fieldoffice.py record JOB-ID time my-time.json
py -3.12 fieldoffice.py economics JOB-ID

# Immutable prepared snapshots; not issued or delivered documents.
py -3.12 fieldoffice.py document JOB-ID estimate my-estimate.json
py -3.12 fieldoffice.py document JOB-ID purchase_order my-po.json
py -3.12 fieldoffice.py document JOB-ID invoice my-invoice.json
py -3.12 fieldoffice.py report JOB-ID internal-report.html
py -3.12 fieldoffice.py export JOB-ID customer-closeout-v1.zip

# Review actual action JSON and the exact attached file hashes before approval.
py -3.12 fieldoffice.py propose JOB-ID my-action.json 2030-01-07T18:00:00-05:00
py -3.12 fieldoffice.py action ACTION-ID
py -3.12 fieldoffice.py approve ACTION-ID EXACT-HASH-RETURNED-BY-ACTION
# Perform the action manually in the official application, then record actual evidence.
py -3.12 fieldoffice.py outcome ACTION-ID confirmed "Provider transaction ID and retained receipt filename"
# If ambiguous, use uncertain. Inspect provider state before any retry.

# Back up with other writers closed; destination must be new and outside the live folder.
py -3.12 fieldoffice.py verify
py -3.12 fieldoffice.py backup E:\EncryptedBackups\FieldOffice-2030-01-07
# Restore drill: point to backup copy, never overwrite your only live copy.
py -3.12 fieldoffice.py --home E:\EncryptedBackups\FieldOffice-2030-01-07 verify

# Optional PDF tool. Installation uses a dedicated environment.
py -3.12 -m venv .venv-pdf
.\.venv-pdf\Scripts\python.exe -m pip install pypdf==6.10.0
.\.venv-pdf\Scripts\python.exe pdf-pages.py extract filled-form.pdf 4 signature-page.pdf
.\.venv-pdf\Scripts\python.exe pdf-pages.py replace filled-form.pdf 4 signed-form-v1.pdf --signed-page scanned-signed-page.pdf

# Optional local AI after official Ollama installation and model download.
ollama pull qwen2.5:7b-instruct-q4_K_M
py -3.12 local-assist.py --home "$env:FIELD_OFFICE_HOME" --job JOB-ID --question "What evidence is missing before departure?" --reference .\approved-checklist.txt --output advisory-draft-v1.txt
```

The source files provide the concrete SQLite schema and all command implementations. The desktop form exposes the same operations, with conservative default timing for reservations. It is intentionally a proof-of-concept interface.

Example measurement.json:

```json
{
  "source": "Technician instrument observation",
  "target": "Panel A port 7 to room 102 jack B",
  "instrument": "Exact make model serial and firmware",
  "method": "Actual method performed",
  "setup": "Actual reference and cable adapters",
  "captured_at": "2030-01-07T10:15:00-05:00",
  "result": "Enter actual observation",
  "units": "Enter applicable units",
  "acceptance_criteria": "Buyer specification reference",
  "classification": "diagnostic",
  "interpretation": "Technician-reviewed interpretation"
}
```

This is an input example, not a measurement. Replace every illustrative field. The generic record store retains these fields but does not itself determine whether the measurement establishes acceptance.

## Identity commands (application 0.2.0)

See `revision-1.4/Serial-Workflow.md` for complete inputs, a training sequence, limitations and data representation.

- `observe-serial JSON`: store a proposed serial/label observation, optionally unassigned.
- `assign-observation ID JOB ASSET`: link a previously unassigned observation once.
- `observations [--job JOB]`: list original observations and their current assignments.
- `verify-bind OBSERVATION EXPECTED_REVISION VERIFIER SOURCE REASON`: create an immutable verified revision; use 0 for a new asset.
- `recall-serial JOB ASSET [--revision N]`: return a verified serial or an explicit unresolved result.
- `dispute-bind JOB ASSET EXPECTED_REVISION REASON`: block current recall until a newly verified revision resolves the identity.

Prepared documents accept `asset_serial_refs`, a list of asset IDs resolved into pinned verified serial snapshots. All commands remain local single-operator operations.
