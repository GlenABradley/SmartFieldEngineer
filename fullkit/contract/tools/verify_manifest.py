"""Offline artifact integrity check. Self-referential manifest hash lives in the archive sidecar."""
from pathlib import Path
import hashlib,json,sys
r=Path(__file__).resolve().parents[1];m=json.loads((r/'Manifest.json').read_text());errors=[]
for name,expected in m['files'].items():
 p=r/name
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=expected['sha256']:errors.append(name)
print(json.dumps({'files_checked':len(m['files']),'mismatches':errors},indent=2));sys.exit(bool(errors))
