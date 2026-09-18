"""Read a CLOSED 0.2.0 ledger without importing its constructor or changing source.
Usage: python tools/legacy_inventory.py LEGACY_ROOT --output inventory.json
No target insertion. A WAL-bearing source must be closed/checkpointed by its owner first.
"""
import argparse,base64,hashlib,json,math,sqlite3
from pathlib import Path

def canonical(v):return json.dumps(v,sort_keys=True,separators=(',',':'),ensure_ascii=False,allow_nan=False).encode('utf-8')
def digest(v):return hashlib.sha256(v).hexdigest()
def typed(v):
 if v is None:return {'type':'null','value':None}
 if isinstance(v,bytes):return {'type':'blob','value':base64.b64encode(v).decode('ascii')}
 if isinstance(v,int):return {'type':'integer','value':str(v)}
 if isinstance(v,float):
  if not math.isfinite(v):raise ValueError('Nonfinite source real')
  return {'type':'real','value':v.hex()}
 return {'type':'text','value':v}
def inventory(root):
 root=Path(root).resolve(strict=True);db=root/'office.sqlite'
 if not db.is_file() or db.is_symlink():raise ValueError('Source database missing or indirect')
 for suffix in ['-wal','-journal']:
  p=Path(str(db)+suffix)
  if p.exists() and p.stat().st_size:raise ValueError('Close/checkpoint legacy source before immutable read-only inventory')
 before=digest(db.read_bytes())
 con=sqlite3.connect(db.as_uri()+'?mode=ro&immutable=1',uri=True)
 try:
  con.execute('PRAGMA query_only=ON')
  if con.execute('PRAGMA integrity_check').fetchall()!=[('ok',)]:raise ValueError('Source SQLite integrity failure')
  if con.execute('PRAGMA foreign_key_check').fetchall():raise ValueError('Source foreign-key failure')
  names=[r[0] for r in con.execute("SELECT name FROM sqlite_schema WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name")]
  if 'office_meta' not in names or 'jobs' not in names:raise ValueError('Missing source identity/jobs tables')
  ledger=con.execute("SELECT value FROM office_meta WHERE key='ledger_id'").fetchone()
  if not ledger or not ledger[0]:raise ValueError('Missing stable source ledger identity')
  tables=[];files=[];evidence_by_id={}
  for name in names:
   quoted='"'+name.replace('"','""')+'"'
   cols=con.execute('PRAGMA table_info('+quoted+')').fetchall()
   pk=[c[1] for c in sorted(cols,key=lambda c:c[5]) if c[5]]
   if not pk:raise ValueError('Source table without stable primary key: '+name)
   column_names=[c[1] for c in cols];rows=con.execute('SELECT * FROM '+quoted).fetchall()
   rows.sort(key=lambda r:canonical([typed(r[column_names.index(k)]) for k in pk]))
   tables.append({'name':name,'columns':[{'name':c[1],'declared_type':c[2],'pk_order':c[5]} for c in cols],'rows':[[typed(v) for v in r] for r in rows]})
   if name=='evidence':
    for row in rows:
     r=dict(zip(column_names,row));h=r['hash']
     if not isinstance(h,str) or len(h)!=64 or any(c not in '0123456789abcdef' for c in h):raise ValueError('Invalid evidence digest')
     p=root/'blobs'/h
     if (root/'blobs').is_symlink() or (root/'blobs').resolve().parent!=root:raise ValueError('Indirect source blob root')
     if not p.is_file() or p.is_symlink() or p.resolve().parent!=(root/'blobs').resolve():raise ValueError('Missing or indirect referenced evidence: '+r['id'])
     raw=p.read_bytes()
     if digest(raw)!=h:raise ValueError('Referenced evidence digest mismatch: '+r['id'])
     files.append({'evidence_id':r['id'],'sha256':h,'length':len(raw)});evidence_by_id[r['id']]=h
  # References inside identity JSON are checked even if evidence table is absent.
  if 'serial_observations' in names:
   for oid,raw in con.execute('SELECT id,data FROM serial_observations'):
    d=json.loads(raw);eid=d.get('evidence_id')
    if eid and (eid not in evidence_by_id or d.get('evidence_sha256')!=evidence_by_id[eid]):raise ValueError('Missing/inconsistent observation evidence: '+oid)
  m={'schema':'legacy-source-manifest.v1','source_application':'Field Office','source_version':'0.2.0','source_ledger_id':ledger[0],'tables':tables,'evidence':sorted(files,key=lambda r:r['evidence_id'])}
 finally:con.close()
 if before!=digest(db.read_bytes()):raise ValueError('Source changed during inventory')
 return {'source_digest':digest(canonical(m)),'manifest':m}
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('root');p.add_argument('--output',required=True);a=p.parse_args()
 result=inventory(a.root);Path(a.output).write_text(json.dumps(result,indent=2)+'\n');print(result['source_digest'])
