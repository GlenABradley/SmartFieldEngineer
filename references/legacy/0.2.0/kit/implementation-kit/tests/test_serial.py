import json
from pathlib import Path
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from fieldoffice import Office

class SerialTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.o=Office(self.root/'live')
        for j in ('A','B'):self.o.save_job({'id':j,'scope':'Scope','client':'Client'})
    def tearDown(self):self.o.db.close();self.tmp.cleanup()
    def observe(self,raw='  Ab-001  ',job='A',asset='SW1',**extra):
        d={'raw':raw,'method':'manual_label_read','source':'physical label',
           'captured_by':'owner','observed_at':'2026-09-18T10:00:00-04:00'}
        if job:d.update(job_id=job,asset_id=asset)
        d.update(extra)
        return self.o.observe_serial(d)['observation_id']
    def bind(self,oid,revision=0):return self.o.verify_bind(oid,revision,'owner','checked label','initial or corrected')
    def test_unknown_and_unassigned_voice(self):
        self.assertIsNone(self.o.recall_serial('A','SW1')['serial'])
        with self.assertRaises(ValueError):self.bind(self.observe(None))
        oid=self.observe(job=None,method='voice_transcript',source='manually entered spoken note')
        with self.assertRaises(ValueError):self.bind(oid)
        self.o.assign_observation(oid,'A','SW1')
        self.assertEqual(self.o.recall_serial('A','SW1')['status'],'unresolved')
        with self.assertRaises(sqlite3.IntegrityError):self.o.assign_observation(oid,'B','SW1')
        self.bind(oid);self.assertEqual(self.o.recall_serial('A','SW1')['serial'],'Ab-001')
    def test_correction_stale_writer_history_dispute(self):
        first=self.bind(self.observe());second=self.bind(self.observe('Ab-002'),1)
        other=Office(self.root/'live')
        try:
            oid=self.observe('Ab-003')
            with self.assertRaises(ValueError):other.verify_bind(oid,1,'owner','label','correction')
            self.assertEqual(self.o.recall_serial('A','SW1',1)['bind']['bind_id'],first['bind_id'])
            self.assertEqual(second['supersedes_bind_id'],first['bind_id'])
            self.o.dispute_bind('A','SW1',2,'conflicting label')
            self.assertEqual(self.o.recall_serial('A','SW1')['status'],'unresolved')
            self.assertEqual(self.o.recall_serial('A','SW1',1)['serial'],'Ab-001')
            self.bind(oid,2);self.assertEqual(self.o.recall_serial('A','SW1')['serial'],'Ab-003')
            self.assertEqual(self.o.verify()['sqlite'],'ok')
        finally:other.db.close()
    def test_wrong_job_and_damaged_evidence(self):
        f=self.root/'label';f.write_text('training label')
        eid=self.o.attach('B',f,'SW1','label')
        with self.assertRaises(ValueError):self.observe(evidence_id=eid)
        eid=self.o.attach('A',f,'SW1','label');oid=self.observe(evidence_id=eid,method='photo_transcription')
        h=self.o.db.execute('SELECT hash FROM evidence WHERE id=?',(eid,)).fetchone()[0]
        (self.o.blobs/h).write_text('damaged')
        with self.assertRaises(ValueError):self.bind(oid)
    def test_unknown_model_label_and_job_link(self):
        self.bind(self.observe());self.assertIsNone(self.o.recall_serial('A','SW1')['bind']['model'])
        self.assertEqual(self.o.recall_serial('B','SW1')['status'],'unresolved')
        self.bind(self.observe('Panel West',asset='PANEL1',identity_kind='asset_label'))
        self.assertEqual(self.o.recall_serial('A','PANEL1')['reason'],'asset_label_is_not_a_serial')
        self.bind(self.observe(asset='REPLACEMENT'))
        self.assertEqual(self.o.recall_serial('A','REPLACEMENT')['bind']['asset_id'],'REPLACEMENT')
    def test_snapshot_immutability_and_backup(self):
        self.bind(self.observe('<Ab-001>'))
        d={'business':'Business','recipient':'Client','terms':'Review','tax_amount':'0',
           'lines':[{'description':'Labor','quantity':1,'unit_price':1}],'asset_serial_refs':['SW1']}
        did=self.o.document('A','work_order',d);out=self.o.root/'exports'/(did+'.html');text=out.read_text()
        self.assertIn('&lt;Ab-001&gt;',text)
        self.bind(self.observe('CORRECTED'),1);self.o.render_document(did);self.assertEqual(text,out.read_text())
        with self.assertRaises(sqlite3.IntegrityError):self.o.db.execute("UPDATE asset_bindings SET data='{}'")
        self.o.db.rollback();self.o.backup(self.root/'backup');other=Office(self.root/'backup')
        try:
            self.assertEqual(other.recall_serial('A','SW1')['serial'],'CORRECTED')
            self.assertEqual(other.ledger_id,self.o.ledger_id)
        finally:other.db.close()
    def test_cli_lifecycle(self):
        script=Path(__file__).resolve().parents[1]/'fieldoffice.py'
        def run(*args):
            r=subprocess.run([sys.executable,str(script),'--home',str(self.o.root),*args],capture_output=True,text=True)
            self.assertEqual(r.returncode,0,r.stderr);return json.loads(r.stdout)
        f=self.root/'capture.json';f.write_text(json.dumps({'raw':'VOICE-1','method':'voice_transcript',
            'source':'manually entered note','captured_by':'owner','observed_at':'2026-09-18T10:00:00-04:00'}))
        oid=run('observe-serial',str(f))['observation_id'];run('assign-observation',oid,'A','SW1')
        run('verify-bind',oid,'0','owner','physical label','initial')
        self.assertEqual(run('recall-serial','A','SW1')['serial'],'VOICE-1')
        self.assertEqual(run('recall-serial','B','SW1')['status'],'unresolved')
        run('dispute-bind','A','SW1','1','review');self.assertEqual(run('recall-serial','A','SW1')['status'],'unresolved')

if __name__=='__main__':unittest.main()
