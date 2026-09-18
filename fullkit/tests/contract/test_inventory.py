"""Executed contract-tool tests on disposable fixtures, not application import proof."""
import hashlib,json,sqlite3,sys
from pathlib import Path
import pytest
ROOT=next(parent/'contract' for parent in Path(__file__).resolve().parents
          if (parent/'contract/tools/legacy_inventory.py').is_file())
sys.path.insert(0,str(ROOT/'tools'))
from legacy_inventory import inventory

def create(root,full=True):
 root.mkdir();(root/'blobs').mkdir()
 with sqlite3.connect(root/'office.sqlite') as db:
  if full:db.executescript((ROOT/'reference/legacy-ddl.sql').read_text())
  else:db.executescript('CREATE TABLE office_meta(key TEXT PRIMARY KEY,value TEXT NOT NULL); CREATE TABLE jobs(id TEXT PRIMARY KEY,data TEXT NOT NULL,version INTEGER NOT NULL);')
  db.execute('INSERT INTO office_meta VALUES(?,?)',('ledger_id','synthetic-ledger'))
  db.execute('INSERT INTO jobs VALUES(?,?,?)',('old-job',json.dumps({'client':'Fixture','scope':'Synthetic'}),1))
 return root

def hashes(root):return {str(p.relative_to(root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in root.rglob('*') if p.is_file()}

def test_source_inventory_read_only_and_deterministic(tmp_path):
 root=create(tmp_path/'legacy');before=hashes(root)
 a=inventory(root);b=inventory(root)
 assert a==b and hashes(root)==before
 assert len(a['manifest']['tables'])==14
 assert a['manifest']['source_ledger_id']=='synthetic-ledger'
 assert a['manifest']['evidence']==[]

def test_missing_optional_tables_are_omitted(tmp_path):
 r=inventory(create(tmp_path/'legacy',False))
 assert [t['name'] for t in r['manifest']['tables']]==['jobs','office_meta']
 assert all(t['rows'] for t in r['manifest']['tables'])

def test_referenced_evidence_missing_or_changed_stops(tmp_path):
 root=create(tmp_path/'legacy');raw=b'fixture';h=hashlib.sha256(raw).hexdigest()
 with sqlite3.connect(root/'office.sqlite') as db:db.execute('INSERT INTO evidence VALUES(?,?,?,?,?)',('e1','old-job',h,'fixture.bin','{}'))
 with pytest.raises(ValueError,match='Missing'):inventory(root)
 (root/'blobs'/h).write_bytes(b'wrong')
 with pytest.raises(ValueError,match='digest mismatch'):inventory(root)
 (root/'blobs'/h).write_bytes(raw)
 assert inventory(root)['manifest']['evidence']==[{'evidence_id':'e1','sha256':h,'length':len(raw)}]

def test_changed_corpus_changes_digest_paths_do_not(tmp_path):
 import shutil
 a=create(tmp_path/'a');shutil.copytree(a,tmp_path/'b')
 d=inventory(a)['source_digest'];assert inventory(tmp_path/'b')['source_digest']==d
 with sqlite3.connect(a/'office.sqlite') as db:db.execute('UPDATE jobs SET version=2')
 assert inventory(a)['source_digest']!=d

def test_bad_open_and_uncheckpointed_source_stop(tmp_path):
 root=tmp_path/'absent';root.mkdir()
 with pytest.raises(ValueError,match='missing'):inventory(root)
 root=create(tmp_path/'legacy');(root/'office.sqlite-wal').write_bytes(b'pending')
 with pytest.raises(ValueError,match='checkpoint'):inventory(root)

def test_missing_identity_stops(tmp_path):
 root=create(tmp_path/'legacy')
 with sqlite3.connect(root/'office.sqlite') as db:db.execute('DELETE FROM office_meta')
 with pytest.raises(ValueError,match='identity'):inventory(root)

def test_inline_observation_evidence_not_silently_omitted(tmp_path):
 root=create(tmp_path/'legacy')
 with sqlite3.connect(root/'office.sqlite') as db:db.execute('INSERT INTO serial_observations VALUES(?,?,?)',('o1',json.dumps({'evidence_id':'missing','evidence_sha256':'0'*64}),'2026-09-18T12:00:00Z'))
 with pytest.raises(ValueError,match='observation evidence'):inventory(root)

def test_unknown_table_without_stable_key_stops(tmp_path):
 root=create(tmp_path/'legacy')
 with sqlite3.connect(root/'office.sqlite') as db:db.execute('CREATE TABLE future_data(payload TEXT)')
 with pytest.raises(ValueError,match='stable primary key'):inventory(root)
