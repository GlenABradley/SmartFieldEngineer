"""Portable baseline check: Finder metadata is explicitly not a Git artifact."""
from pathlib import Path
import hashlib,json,sys
root=Path(__file__).resolve().parents[1]
contract=root/'fullkit/contract'
manifest=json.loads((contract/'Manifest.json').read_text())
errors=[];excluded=[];checked=0
for name,entry in manifest['files'].items():
 if Path(name).name=='.DS_Store':
  excluded.append(name);continue
 checked+=1;p=contract/name
 if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=entry['sha256']:errors.append(name)
print(json.dumps({'files_checked':checked,'mismatches':errors,'explicit_metadata_exclusions':excluded,'reason':'Original manifest retained unchanged; .DS_Store is mutable Finder state and excluded from Git.'},indent=2))
sys.exit(bool(errors))
