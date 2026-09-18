"""Verify exact versions against publisher metadata; record wheel hashes, never install GUI here."""
import json,urllib.request
from pathlib import Path
root=Path(__file__).resolve().parents[1]
pins={'jsonschema':'4.26.0','PySide6':'6.11.2','pytest':'9.0.2','build':'1.4.0','tzdata':'2026.4','colorama':'0.4.6','setuptools':'84.0.0'}
results={}
for name,version in pins.items():
 url=f'https://pypi.org/pypi/{name}/{version}/json'
 with urllib.request.urlopen(url) as r:d=json.load(r)
 assert d['info']['version']==version
 wheels=[{'filename':f['filename'],'sha256':f['digests']['sha256'],'url':f['url'],'yanked':f['yanked']} for f in d['urls'] if f['packagetype']=='bdist_wheel' and ('win_amd64' in f['filename'] or 'none-any' in f['filename'])]
 assert wheels and not any(f['yanked'] for f in wheels)
 results[name]={'version':version,'metadata_url':url,'requires_python':d['info']['requires_python'],'license':d['info'].get('license_expression') or d['info'].get('license'),'requires_dist':d['info'].get('requires_dist'),'windows_or_universal_wheels':wheels}
(root/'reference/dependency-verification.json').write_text(json.dumps(results,indent=2)+'\n')
(root/'requirements-validation.txt').write_text('jsonschema[format]==4.26.0\npytest==9.0.2\ncolorama==0.4.6\n')
(root/'requirements-application.txt').write_text('PySide6==6.11.2\njsonschema[format]==4.26.0\ntzdata==2026.4\n')
(root/'requirements-build.txt').write_text('build==1.4.0\nsetuptools==84.0.0\n')
print(json.dumps({k:v['version'] for k,v in results.items()}))
