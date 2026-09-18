import json
from pathlib import Path
import tempfile
import unittest
import zipfile
from fieldoffice import Office,cents

class OfficeTest(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory();self.root=Path(self.tmp.name)
        self.o=Office(self.root/'live')
        for jid in ['A','B']:self.o.save_job({'id':jid,'client':'Client','scope':'Scope'})
    def tearDown(self):self.o.db.close();self.tmp.cleanup()
    def test_protected_envelope(self):
        self.o.reserve('A','2030-01-01T08:00:00-05:00',120,60,30,90,'soft','2030-01-01T07:00:00-05:00')
        with self.assertRaises(ValueError):self.o.reserve('B','2030-01-01T12:30:00-05:00',60,60,30,90,'hard','2030-01-01T07:00:00-05:00')
        self.assertEqual(self.o.db.execute('SELECT count(*) FROM reservations').fetchone()[0],1)
    def test_timezone_required(self):
        with self.assertRaises(ValueError):self.o.reserve('A','2030-01-01T08:00:00',120,60,30,90,'soft','2030-01-01T07:00:00-05:00')
    def test_revision_invalidates_approval(self):
        aid=self.o.propose('A',{'action':'upload','recipient':'buyer','terms':'exact','channel':'portal'},'2099-01-01T00:00:00Z')
        self.o.approve(aid,self.o.action(aid)['hash'])
        self.o.revise('A','New scope','buyer revision')
        with self.assertRaises(ValueError):self.o.action_result(aid,'confirmed','receipt')
    def test_expiry_and_wrong_hash(self):
        with self.assertRaises(ValueError):self.o.propose('A',{'action':'a','recipient':'b','terms':'c','channel':'d'},'2000-01-01T00:00:00Z')
        aid=self.o.propose('A',{'action':'a','recipient':'b','terms':'c','channel':'d'},'2099-01-01T00:00:00Z')
        with self.assertRaises(ValueError):self.o.approve(aid,'bad')
    def test_inventory_transaction(self):
        self.o.stock('CABLE','bag',3,500);self.o.consume('A','CABLE','bag',2)
        with self.assertRaises(ValueError):self.o.consume('A','CABLE','bag',2)
        self.assertEqual(self.o.economics('A')['recorded_cost_cents'],1000)
        self.assertEqual(self.o.db.execute('SELECT qty FROM stock').fetchone()[0],1)
    def test_evidence_isolation_and_closeout(self):
        f=self.root/'photo.txt';f.write_text('training evidence')
        r=self.o.record('A','requirement',{'source':'buyer','text':'photo'})
        e=self.o.attach('B',f,'asset','photo','customer')
        with self.assertRaises(ValueError):self.o.satisfy('A',r,e,'reviewed')
        with self.assertRaises(ValueError):self.o.track('A','field','complete','operator')
        e=self.o.attach('A',f,'asset','photo','customer');self.o.satisfy('A',r,e,'reviewed')
        self.o.track('A','field','complete','operator');self.assertFalse(self.o.blockers('A'))
    def test_export_filters_private(self):
        f=self.root/'secret.txt';f.write_text('secret');self.o.attach('A',f,'internal','secret')
        dest=self.root/'out.zip';self.o.export('A',dest)
        with zipfile.ZipFile(dest) as z:self.assertEqual(len(z.namelist()),2)
    def test_hash_detects_damage(self):
        f=self.root/'file';f.write_text('data');eid=self.o.attach('A',f,'port','test')
        h=self.o.db.execute('SELECT hash FROM evidence WHERE id=?',(eid,)).fetchone()[0]
        (self.o.blobs/h).write_text('changed')
        with self.assertRaises(ValueError):self.o.verify()
    def test_backup_restores(self):
        self.o.record('A','time',{'source':'operator','minutes':60})
        self.o.backup(self.root/'backup');restored=Office(self.root/'backup')
        self.assertEqual(restored.economics('A')['recorded_minutes'],60);self.assertEqual(restored.verify()['sqlite'],'ok');restored.db.close()
    def test_documents_cents_and_html(self):
        d={'business':'Business','recipient':'<script>','terms':'Review','tax_amount':'0','lines':[{'description':'cable','quantity':'3','unit_price':'0.10'}]}
        did=self.o.document('A','invoice',d)
        self.assertEqual(self.o.economics('A')['prepared_invoice_total_cents'],30)
        self.assertIn('&lt;script&gt;',(self.o.root/'exports'/(did+'.html')).read_text())
        self.assertEqual(cents('1.005'),101)
    def test_duplicate_action_outcome(self):
        aid=self.o.propose('A',{'action':'a','recipient':'b','terms':'c','channel':'d'},'2099-01-01T00:00:00Z')
        self.o.approve(aid,self.o.action(aid)['hash']);self.o.action_result(aid,'confirmed','receipt')
        with self.assertRaises(ValueError):self.o.action_result(aid,'confirmed','again')
    def test_reopen_and_resolve(self):
        f=self.root/'result';f.write_text('actual training result')
        rid=self.o.record('A','requirement',{'text':'test','source':'buyer'})
        eid=self.o.attach('A',f,'port','test')
        self.o.satisfy('A',rid,eid,'reviewed')
        self.o.record('A','fact',{'source':'buyer rejection','reopens':rid})
        self.assertEqual(len(self.o.blockers('A')),1)
        self.o.satisfy('A',rid,eid,'reviewed again after clarification')
        self.assertEqual(len(self.o.blockers('A')),0)

if __name__=='__main__':unittest.main()
