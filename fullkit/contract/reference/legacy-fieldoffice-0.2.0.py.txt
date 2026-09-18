#!/usr/bin/env python3
"""Offline, single-operator Field Office. Python 3.11+, standard library only."""
import argparse
import csv
from datetime import datetime, timedelta, timezone
from decimal import Decimal, ROUND_HALF_UP
import hashlib
import html
import json
import os
from pathlib import Path
import re
import shutil
import sqlite3
import sys
import uuid
import zipfile

VERSION = '0.2.0'
KINDS = {'fact','requirement','task','time','cost','payment','instrument','insurance',
         'material','contact','return','communication','precedent','profile','test'}
TRACKS = {'field': {'planned','onsite','working','blocked','incomplete','complete'},
          'delivery': {'not_submitted','submitted','accepted','rejected'},
          'billing': {'not_invoiced','invoiced','disputed','reconciled'},
          'returns': {'none','pending','returned'}}

def now():
    return datetime.now(timezone.utc).isoformat()

def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(',', ':'), ensure_ascii=False)

def digest(value):
    return hashlib.sha256(value).hexdigest()

def stamp(value):
    d = datetime.fromisoformat(value)
    if d.tzinfo is None:
        raise ValueError('Time must include UTC offset, for example -04:00')
    return d.astimezone(timezone.utc)

def cents(value):
    n = Decimal(str(value))
    if not n.is_finite():
        raise ValueError('Money must be finite')
    return int((n * 100).quantize(Decimal('1'), rounding=ROUND_HALF_UP))

def identifier(value):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_-]{0,63}', value):
        raise ValueError('Use 1 to 64 letters, numbers, underscores or dashes for IDs')
    return value

class Office:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.blobs = self.root / 'blobs'
        self.blobs.mkdir(exist_ok=True)
        self.db = sqlite3.connect(self.root / 'office.sqlite', timeout=10)
        self.db.row_factory = sqlite3.Row
        self.db.execute('PRAGMA foreign_keys=ON')
        self.db.execute('PRAGMA journal_mode=WAL')
        self.db.executescript('''
        CREATE TABLE IF NOT EXISTS office_meta(key TEXT PRIMARY KEY, value TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY, data TEXT NOT NULL, version INTEGER NOT NULL);
        CREATE TABLE IF NOT EXISTS records(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), kind TEXT NOT NULL, data TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS evidence(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), hash TEXT NOT NULL, name TEXT NOT NULL, data TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS reservations(job TEXT PRIMARY KEY REFERENCES jobs(id), start TEXT NOT NULL, end TEXT NOT NULL, state TEXT NOT NULL, review TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS actions(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), version INTEGER NOT NULL, data TEXT NOT NULL, hash TEXT NOT NULL, expires TEXT NOT NULL, state TEXT NOT NULL, receipt TEXT);
        CREATE TABLE IF NOT EXISTS stock(sku TEXT NOT NULL, location TEXT NOT NULL, qty INTEGER NOT NULL, unit_cents INTEGER NOT NULL, PRIMARY KEY(sku,location));
        CREATE TABLE IF NOT EXISTS documents(id TEXT PRIMARY KEY, job TEXT REFERENCES jobs(id), kind TEXT NOT NULL, data TEXT NOT NULL, hash TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS serial_observations(id TEXT PRIMARY KEY, data TEXT NOT NULL, created TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS serial_assignments(observation TEXT PRIMARY KEY REFERENCES serial_observations(id), job TEXT NOT NULL REFERENCES jobs(id), asset TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS asset_heads(asset TEXT PRIMARY KEY, revision INTEGER NOT NULL, state TEXT NOT NULL);
        CREATE TABLE IF NOT EXISTS asset_bindings(id TEXT PRIMARY KEY, asset TEXT NOT NULL REFERENCES asset_heads(asset), revision INTEGER NOT NULL, observation TEXT UNIQUE NOT NULL REFERENCES serial_assignments(observation), data TEXT NOT NULL, UNIQUE(asset,revision));
        CREATE TABLE IF NOT EXISTS asset_jobs(asset TEXT REFERENCES asset_heads(asset), job TEXT REFERENCES jobs(id), PRIMARY KEY(asset,job));
        CREATE TRIGGER IF NOT EXISTS serial_observations_no_update BEFORE UPDATE ON serial_observations BEGIN SELECT RAISE(ABORT,'Identity observations are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS serial_observations_no_delete BEFORE DELETE ON serial_observations BEGIN SELECT RAISE(ABORT,'Identity observations are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS asset_bindings_no_update BEFORE UPDATE ON asset_bindings BEGIN SELECT RAISE(ABORT,'Identity binds are immutable'); END;
        CREATE TRIGGER IF NOT EXISTS asset_bindings_no_delete BEFORE DELETE ON asset_bindings BEGIN SELECT RAISE(ABORT,'Identity binds are immutable'); END;
        CREATE TABLE IF NOT EXISTS audit(seq INTEGER PRIMARY KEY, at TEXT NOT NULL, event TEXT NOT NULL, data TEXT NOT NULL, previous TEXT NOT NULL, hash TEXT NOT NULL);
        ''')
        with self.db:
            self.db.execute('INSERT OR IGNORE INTO office_meta VALUES(?,?)',('ledger_id',uuid.uuid4().hex))
        self.ledger_id=self.db.execute("SELECT value FROM office_meta WHERE key='ledger_id'").fetchone()[0]

    def log(self, event, data):
        prev = self.db.execute('SELECT hash FROM audit ORDER BY seq DESC LIMIT 1').fetchone()
        prev = prev[0] if prev else '0' * 64
        at, raw = now(), canonical(data)
        h = digest(canonical([at,event,raw,prev]).encode())
        self.db.execute('INSERT INTO audit(at,event,data,previous,hash) VALUES(?,?,?,?,?)', (at,event,raw,prev,h))

    def job(self, jid):
        row = self.db.execute('SELECT * FROM jobs WHERE id=?', (jid,)).fetchone()
        if not row:
            raise ValueError('Unknown job: ' + jid)
        return {**json.loads(row['data']), 'id':jid, 'version':row['version']}

    def save_job(self, data):
        jid = identifier(data['id'])
        if not data.get('scope') or not data.get('client'):
            raise ValueError('Client and scope are required')
        with self.db:
            self.db.execute('INSERT INTO jobs VALUES(?,?,1)', (jid,canonical(data)))
            self.log('job_created', data)
        return self.job(jid)

    def revise(self, jid, scope, source):
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            j = self.job(jid)
            before = dict(j)
            j['scope'], j['scope_source'] = scope, source
            self.db.execute('UPDATE jobs SET data=?,version=version+1 WHERE id=?', (canonical(j),jid))
            self.db.execute("UPDATE actions SET state='invalidated' WHERE job=? AND state IN ('prepared','approved')", (jid,))
            self.log('scope_revised', {'before':before,'scope':scope,'source':source})
        return self.job(jid)

    def record(self, jid, kind, data):
        self.job(jid)
        if kind not in KINDS:
            raise ValueError('Unsupported record kind')
        if not data.get('source'):
            raise ValueError('Record needs a source, including manual observations')
        if kind in {'cost','payment'}:
            data['amount_cents'] = cents(data.pop('amount'))
        if kind == 'time' and (not isinstance(data.get('minutes'),int) or data['minutes'] <= 0):
            raise ValueError('Time minutes must be a positive integer')
        if kind == 'requirement' and not data.get('text'):
            raise ValueError('Requirement needs text')
        rid = uuid.uuid4().hex
        with self.db:
            self.db.execute('INSERT INTO records VALUES(?,?,?,?,?)', (rid,jid,kind,canonical(data),now()))
            self.log('record_added', {'id':rid,'job':jid,'kind':kind,'data':data})
        return rid

    def records(self, jid):
        return [{'id':r['id'],'kind':r['kind'],'created':r['created'],**json.loads(r['data'])}
                for r in self.db.execute('SELECT * FROM records WHERE job=? ORDER BY rowid', (jid,))]

    def attach(self, jid, path, target, purpose, visibility='internal'):
        self.job(jid)
        if visibility not in {'internal','customer'}:
            raise ValueError('Evidence visibility must be internal or customer')
        path = Path(path)
        raw = path.read_bytes()
        h = digest(raw)
        dest = self.blobs / h
        if not dest.exists():
            dest.write_bytes(raw)
        eid = uuid.uuid4().hex
        data = {'target':target,'purpose':purpose,'visibility':visibility,'imported_at':now(),
                'source':'file import; capture time is not inferred from import time'}
        with self.db:
            self.db.execute('INSERT INTO evidence VALUES(?,?,?,?,?)', (eid,jid,h,path.name,canonical(data)))
            self.log('evidence_imported', {'id':eid,'job':jid,'hash':h,**data})
        return eid

    def observe_serial(self, data):
        """Store proposed identity, including unassigned transcripts; no speech/OCR inference."""
        data = json.loads(canonical(data))
        required = ('raw', 'method', 'source', 'captured_by', 'observed_at')
        if any(k not in data for k in required):
            raise ValueError('Observation needs raw, method, source, captured_by and observed_at')
        for k in ('source', 'captured_by'):
            if not isinstance(data[k], str) or not data[k].strip():
                raise ValueError(k + ' must be nonempty text')
        stamp(data['observed_at'])
        methods = {'manual_label_read','voice_transcript','photo_transcription',
                   'barcode_scan','device_inventory_output'}
        if data['method'] not in methods:
            raise ValueError('Unsupported identity capture method')
        kind = data.get('identity_kind', 'serial')
        if kind not in {'serial', 'asset_label'}:
            raise ValueError('Identity kind must be serial or asset_label')
        raw = data['raw']
        if raw is not None and (not isinstance(raw, str) or not raw.strip()):
            raise ValueError('Raw identity must be nonempty text or null for unknown')
        for key in ('manufacturer','model'):
            value = data.get(key)
            if value is not None and (not isinstance(value, str) or not value.strip()):
                raise ValueError(key + ' must be nonempty text or null')
            data[key] = value
        jid, asset = data.get('job_id'), data.get('asset_id')
        if bool(jid) != bool(asset):
            raise ValueError('Provide job_id and asset_id together, or neither')
        if jid:
            self.job(jid); identifier(asset)
        eid = data.get('evidence_id')
        if eid:
            e = self.db.execute('SELECT * FROM evidence WHERE id=?', (eid,)).fetchone()
            if not e or not jid or e['job'] != jid:
                raise ValueError('Evidence must belong to the assigned job')
            if digest((self.blobs/e['hash']).read_bytes()) != e['hash']:
                raise ValueError('Observation evidence integrity failure')
            data['evidence_sha256'] = e['hash']
        else:
            data['evidence_sha256'] = None
        data['identity_kind'], data['status'] = kind, 'proposed'
        # Caller cannot manufacture verification by supplying extra fields.
        allowed = {'raw','method','source','captured_by','observed_at','manufacturer','model',
                   'job_id','asset_id','evidence_id','evidence_sha256','identity_kind','status'}
        if set(data) - allowed:
            raise ValueError('Unexpected observation fields: ' + ', '.join(sorted(set(data)-allowed)))
        oid = uuid.uuid4().hex
        with self.db:
            self.db.execute('INSERT INTO serial_observations VALUES(?,?,?)',(oid,canonical(data),now()))
            if jid:
                self.db.execute('INSERT INTO serial_assignments VALUES(?,?,?)',(oid,jid,asset))
            self.log('identity_observed',{'id':oid,'data':data})
        return {'observation_id':oid,'status':'proposed','assigned':bool(jid)}

    def assign_observation(self, oid, jid, asset):
        self.job(jid); identifier(asset)
        with self.db:
            if not self.db.execute('SELECT 1 FROM serial_observations WHERE id=?',(oid,)).fetchone():
                raise ValueError('Unknown observation')
            self.db.execute('INSERT INTO serial_assignments VALUES(?,?,?)',(oid,jid,asset))
            self.log('identity_assigned',{'observation_id':oid,'job':jid,'asset':asset})
        return {'observation_id':oid,'job':jid,'asset':asset}

    def serial_observations(self, jid=None):
        if jid: self.job(jid)
        query = ('SELECT o.*,a.job,a.asset FROM serial_observations o '
                 'LEFT JOIN serial_assignments a ON a.observation=o.id')
        rows = self.db.execute(query + (' WHERE a.job=?' if jid else '') + ' ORDER BY o.rowid',
                               (jid,) if jid else ())
        return [{'id':r['id'],'created':r['created'],'observation':json.loads(r['data']),
                 'assignment':{'job':r['job'],'asset':r['asset']} if r['job'] else None}
                for r in rows]

    def verify_bind(self, oid, expected_revision, verifier, source, reason):
        if type(expected_revision) is not int or expected_revision < 0:
            raise ValueError('Expected revision must be a nonnegative integer')
        if not all(isinstance(x,str) and x.strip() for x in (verifier,source,reason)):
            raise ValueError('Verifier, verification source and revision reason are required')
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            r = self.db.execute('SELECT o.data,a.job,a.asset FROM serial_observations o '
                                'JOIN serial_assignments a ON a.observation=o.id WHERE o.id=?',(oid,)).fetchone()
            if not r:
                raise ValueError('Observation is unknown or unassigned; bind to job and asset first')
            d = json.loads(r['data'])
            if d['raw'] is None:
                raise ValueError('Unknown identity cannot be verified; capture a new observation')
            if self.db.execute('SELECT 1 FROM asset_bindings WHERE observation=?',(oid,)).fetchone():
                raise ValueError('Observation already verified; use a new observation for a correction')
            if d.get('evidence_id'):
                e = self.db.execute('SELECT * FROM evidence WHERE id=? AND job=?',
                                    (d['evidence_id'],r['job'])).fetchone()
                if not e or e['hash'] != d['evidence_sha256'] or digest((self.blobs/e['hash']).read_bytes()) != e['hash']:
                    raise ValueError('Verification evidence missing, changed or wrong job')
            h = self.db.execute('SELECT * FROM asset_heads WHERE asset=?',(r['asset'],)).fetchone()
            revision = h['revision'] if h else 0
            if revision != expected_revision:
                raise ValueError('Asset revision changed; inspect current bind before verifying')
            prev = self.db.execute('SELECT id FROM asset_bindings WHERE asset=? AND revision=?',
                                   (r['asset'],revision)).fetchone()
            bid = uuid.uuid4().hex
            bind = {'bind_id':bid,'ledger_id':self.ledger_id,'asset_id':r['asset'],
                    'revision':revision+1,'source_job_id':r['job'],'observation_id':oid,
                    'identity_kind':d['identity_kind'],'raw':d['raw'],'normalized':d['raw'].strip(),
                    'normalization_rule':'trim_surrounding_whitespace_only',
                    'manufacturer':d['manufacturer'],'model':d['model'],
                    'observation':d,'verification':{'status':'verified','verified_by':verifier,
                     'verified_at':now(),'source':source},'supersedes_bind_id':prev['id'] if prev else None,
                    'change_reason':reason}
            if h:
                self.db.execute("UPDATE asset_heads SET revision=?,state='active' WHERE asset=?",
                                (revision+1,r['asset']))
            else:
                self.db.execute("INSERT INTO asset_heads VALUES(?,?,'active')",(r['asset'],1))
            self.db.execute('INSERT INTO asset_bindings VALUES(?,?,?,?,?)',
                            (bid,r['asset'],revision+1,oid,canonical(bind)))
            self.db.execute('INSERT OR IGNORE INTO asset_jobs VALUES(?,?)',(r['asset'],r['job']))
            self.log('asset_bound',bind)
        return bind

    def recall_serial(self, jid, asset, revision=None):
        self.job(jid)
        unresolved = {'status':'unresolved','job':jid,'asset_id':asset,'serial':None}
        if not self.db.execute('SELECT 1 FROM asset_jobs WHERE asset=? AND job=?',(asset,jid)).fetchone():
            return {**unresolved,'reason':'no_verified_asset_link_for_job'}
        head = self.db.execute('SELECT * FROM asset_heads WHERE asset=?',(asset,)).fetchone()
        if revision is None and head['state'] != 'active':
            return {**unresolved,'reason':'identity_disputed','current_revision':head['revision']}
        version = head['revision'] if revision is None else revision
        r = self.db.execute('SELECT data FROM asset_bindings WHERE asset=? AND revision=?',(asset,version)).fetchone()
        if not r:
            return {**unresolved,'reason':'unknown_bind_revision'}
        bind = json.loads(r['data'])
        if bind['identity_kind'] != 'serial':
            return {**unresolved,'reason':'asset_label_is_not_a_serial','bind':bind}
        return {'status':'verified','serial':bind['normalized'],'bind':bind,
                'historical':revision is not None,'current_state':head['state']}

    def dispute_bind(self, jid, asset, expected_revision, reason):
        if not isinstance(reason,str) or not reason.strip():
            raise ValueError('Dispute reason required')
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            self.job(jid)
            if not self.db.execute('SELECT 1 FROM asset_jobs WHERE asset=? AND job=?',(asset,jid)).fetchone():
                raise ValueError('No verified asset link for this job')
            h = self.db.execute('SELECT * FROM asset_heads WHERE asset=?',(asset,)).fetchone()
            if not h or h['revision'] != expected_revision:
                raise ValueError('Asset revision changed')
            self.db.execute("UPDATE asset_heads SET state='disputed' WHERE asset=?",(asset,))
            self.log('asset_identity_disputed',{'job':jid,'asset':asset,'revision':expected_revision,'reason':reason})
        return {'asset_id':asset,'revision':expected_revision,'state':'disputed'}

    def satisfy(self, jid, rid, eid, note):
        r = self.db.execute("SELECT * FROM records WHERE id=? AND job=? AND kind='requirement'", (rid,jid)).fetchone()
        e = self.db.execute('SELECT * FROM evidence WHERE id=? AND job=?', (eid,jid)).fetchone()
        if not r or not e:
            raise ValueError('Requirement and evidence must belong to this job')
        return self.record(jid,'fact',{'source':'operator review','satisfies':rid,'evidence':eid,'note':note})

    def blockers(self, jid):
        records = self.records(jid)
        satisfied = set()
        for record in records:
            if record['kind'] == 'fact':
                if record.get('reopens'): satisfied.discard(record['reopens'])
                if record.get('satisfies'): satisfied.add(record['satisfies'])
        return [r for r in records if r['kind']=='requirement' and r['id'] not in satisfied]

    def reserve(self, jid, start, work, travel, closeout, recovery, state, review):
        self.job(jid)
        if state not in {'soft','hard'} or min(work,travel,closeout,recovery) < 0 or work == 0:
            raise ValueError('Invalid reservation')
        arrival = stamp(start)
        stamp(review)
        begin = arrival - timedelta(minutes=travel)
        end = arrival + timedelta(minutes=work+closeout+recovery)
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            rows = self.db.execute('SELECT * FROM reservations WHERE job<>?', (jid,)).fetchall()
            conflicts = [r['job'] for r in rows if begin < stamp(r['end']) and end > stamp(r['start'])]
            if conflicts:
                raise ValueError('Protected envelope conflicts with ' + ', '.join(conflicts))
            self.db.execute('INSERT OR REPLACE INTO reservations VALUES(?,?,?,?,?)',
                            (jid,begin.isoformat(),end.isoformat(),state,review))
            self.log('reservation_saved', {'job':jid,'arrival':start,'travel_in_minutes':travel,
                     'pessimistic_work_minutes':work,'closeout_minutes':closeout,'recovery_minutes':recovery,
                     'start':begin.isoformat(),'end':end.isoformat(),'state':state,'review':review})
        return {'start':begin.isoformat(),'end':end.isoformat()}

    def release(self,jid,reason):
        if not reason.strip():
            raise ValueError('Confirmed cancellation or hold resolution reason required')
        with self.db:
            self.db.execute('DELETE FROM reservations WHERE job=?',(jid,))
            self.log('reservation_released',{'job':jid,'reason':reason})

    def propose(self,jid,data,expires):
        j = self.job(jid)
        if not all(data.get(k) for k in ('action','recipient','terms','channel')):
            raise ValueError('Action, recipient, exact terms and channel required')
        if stamp(expires) <= stamp(now()):
            raise ValueError('Approval must expire in the future')
        aid = uuid.uuid4().hex
        raw=canonical(data)
        with self.db:
            self.db.execute('INSERT INTO actions VALUES(?,?,?,?,?,?,?,NULL)',
                            (aid,jid,j['version'],raw,digest(raw.encode()),expires,'prepared'))
            self.log('action_prepared',{'id':aid,'job':jid,'data':data})
        return aid

    def action(self, aid):
        r = self.db.execute('SELECT * FROM actions WHERE id=?',(aid,)).fetchone()
        if not r:
            raise ValueError('Unknown action')
        return dict(r)

    def approve(self,aid,expected_hash):
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            a=self.action(aid)
            if a['state']!='prepared' or a['hash']!=expected_hash or stamp(a['expires'])<=stamp(now()) or self.job(a['job'])['version']!=a['version']:
                raise ValueError('Action changed, expired, invalidated or hash does not match')
            self.db.execute("UPDATE actions SET state='approved' WHERE id=?",(aid,))
            self.log('action_approved',{'id':aid,'hash':expected_hash})

    def action_result(self,aid,state,receipt):
        if state not in {'confirmed','failed','uncertain','revoked'} or not receipt:
            raise ValueError('Explicit outcome and receipt or explanatory record required')
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            a=self.action(aid)
            if a['state'] not in {'approved','uncertain'}:
                raise ValueError('Action is not approved or awaiting verification')
            self.db.execute('UPDATE actions SET state=?,receipt=? WHERE id=?',(state,receipt,aid))
            self.log('manual_action_outcome',{'id':aid,'state':state,'receipt':receipt})

    def track(self,jid,track,value,source):
        if track not in TRACKS or value not in TRACKS[track]:
            raise ValueError('Unknown track or state')
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            j=self.job(jid)
            if track=='field' and value=='complete' and self.blockers(jid):
                raise ValueError('Required evidence remains unresolved')
            j.setdefault('tracks',{})[track]=value
            self.db.execute('UPDATE jobs SET data=? WHERE id=?',(canonical(j),jid))
            self.log('track_changed',{'job':jid,'track':track,'value':value,'source':source})

    def stock(self,sku,location,quantity,unit):
        identifier(sku)
        if quantity<=0 or unit<0:
            raise ValueError('Receive positive quantity and nonnegative unit cost')
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            row=self.db.execute('SELECT * FROM stock WHERE sku=? AND location=?',(sku,location)).fetchone()
            q=(row['qty'] if row else 0)+quantity
            old_value=row['qty']*row['unit_cents'] if row else 0
            weighted=int((Decimal(old_value+quantity*unit)/q).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
            self.db.execute('INSERT OR REPLACE INTO stock VALUES(?,?,?,?)',(sku,location,q,weighted))
            self.log('stock_received',{'sku':sku,'location':location,'quantity':quantity,'unit_cents':unit})

    def consume(self,jid,sku,location,quantity):
        self.job(jid)
        self.db.execute('BEGIN IMMEDIATE')
        with self.db:
            r=self.db.execute('SELECT * FROM stock WHERE sku=? AND location=?',(sku,location)).fetchone()
            if not r or quantity<=0 or r['qty']<quantity:
                raise ValueError('Insufficient stock or invalid quantity')
            self.db.execute('UPDATE stock SET qty=qty-? WHERE sku=? AND location=?',(quantity,sku,location))
            data={'sku':sku,'location':location,'quantity':quantity,'amount_cents':quantity*r['unit_cents'],'source':'stock consumption'}
            self.db.execute('INSERT INTO records VALUES(?,?,?,?,?)',(uuid.uuid4().hex,jid,'cost',canonical(data),now()))
            self.log('stock_consumed',{'job':jid,**data})

    def document(self,jid,kind,data):
        self.job(jid)
        if kind not in {'estimate','purchase_order','invoice','change_order','work_order'}:
            raise ValueError('Unsupported document type')
        if not all(data.get(k) for k in ('business','recipient','terms','lines')):
            raise ValueError('Business, recipient, terms and lines required')
        if 'asset_identity_snapshots' in data:
            raise ValueError('Identity snapshots are produced from verified binds, not supplied text')
        refs = data.pop('asset_serial_refs', [])
        if not isinstance(refs,list) or any(not isinstance(x,str) for x in refs):
            raise ValueError('asset_serial_refs must be a list of asset IDs')
        if refs:
            snapshots=[]
            for asset in refs:
                result=self.recall_serial(jid,asset)
                if result['status']!='verified':
                    raise ValueError('Asset identity unresolved: ' + asset)
                bind=result['bind']
                snapshots.append({'asset_id':asset,'bind_id':bind['bind_id'],
                                  'revision':bind['revision'],'serial':result['serial']})
            data['asset_identity_snapshots']=snapshots
        total=0
        for line in data['lines']:
            qty=Decimal(str(line['quantity']))
            if not qty.is_finite() or qty<=0:
                raise ValueError('Line quantities must be finite and positive')
            line['unit_cents']=cents(line.pop('unit_price'))
            line['total_cents']=int((qty*line['unit_cents']).quantize(Decimal('1'),rounding=ROUND_HALF_UP))
            total+=line['total_cents']
        # Tax is an explicit reviewed dollar amount, never inferred jurisdictionally.
        data['tax_cents']=cents(data.pop('tax_amount'))
        data['total_cents']=total+data['tax_cents']
        data['status']='prepared_not_sent'
        raw=canonical(data)
        did=kind+'-'+uuid.uuid4().hex[:12]
        with self.db:
            self.db.execute('INSERT INTO documents VALUES(?,?,?,?,?,?)',(did,jid,kind,raw,digest(raw.encode()),now()))
            self.log('document_prepared',{'id':did,'job':jid,'hash':digest(raw.encode())})
        self.render_document(did)
        return did

    def render_document(self,did):
        r=self.db.execute('SELECT * FROM documents WHERE id=?',(did,)).fetchone()
        d=json.loads(r['data'])
        out=self.root/'exports';out.mkdir(exist_ok=True)
        rows=''.join('<tr><td>'+html.escape(str(l['description']))+'</td><td>'+html.escape(str(l['quantity']))+'</td><td>'+format(l['unit_cents']/100,'.2f')+'</td><td>'+format(l['total_cents']/100,'.2f')+'</td></tr>' for l in d['lines'])
        content=f"<h1>{html.escape(r['kind'].replace('_',' ').title())}</h1><p>{html.escape(did)} — Prepared for review</p><p>{html.escape(d['business'])}</p><p>To {html.escape(d['recipient'])}</p><table><tr><th>Description</th><th>Qty</th><th>Unit USD</th><th>Total USD</th></tr>{rows}</table><p>Tax USD {d['tax_cents']/100:.2f}</p><p>Total USD {d['total_cents']/100:.2f}</p><p>{html.escape(d['terms'])}</p><p>Job {html.escape(r['job'])}</p>"
        if d.get('asset_identity_snapshots'):
            content+='<h2>Verified asset identities</h2><ul>'
            for identity in d['asset_identity_snapshots']:
                content+='<li>'+html.escape(identity['asset_id']+' — serial '+identity['serial']+
                    ' — bind '+identity['bind_id']+' revision '+str(identity['revision']))+'</li>'
            content+='</ul>'
        (out/(did+'.html')).write_text(page(content),encoding='utf-8')

    def economics(self,jid):
        records=self.records(jid)
        cost=sum(r.get('amount_cents',0) for r in records if r['kind']=='cost')
        paid=sum(r.get('amount_cents',0) for r in records if r['kind']=='payment')
        minutes=sum(r.get('minutes',0) for r in records if r['kind']=='time')
        invoices=[json.loads(r[0]) for r in self.db.execute("SELECT data FROM documents WHERE job=? AND kind='invoice'",(jid,))]
        return {'recorded_cost_cents':cost,'recorded_payment_cents':paid,'recorded_minutes':minutes,
                'cash_contribution_cents':paid-cost,'cash_contribution_per_hour':round((paid-cost)/100/(minutes/60),2) if minutes else None,
                'prepared_invoice_total_cents':sum(d['total_cents'] for d in invoices),
                'note':'Cash contribution excludes unrecorded costs, owner labor and tax; prepared invoices are not accounts receivable.'}

    def report(self,jid,customer=False):
        j=self.job(jid)
        content=f"<h1>Job {html.escape(jid)}</h1><p>Client {html.escape(j['client'])}</p><h2>Scope</h2><p>{html.escape(j['scope'])}</p>"
        content+='<h2>Recorded status</h2><pre>'+html.escape(json.dumps(j.get('tracks',{}),indent=2))+'</pre>'
        content+='<h2>Open requirements</h2><ul>'+''.join('<li>'+html.escape(r['text'])+'</li>' for r in self.blockers(jid))+'</ul>'
        content+='<h2>Evidence manifest</h2><ul>'
        for r in self.db.execute('SELECT * FROM evidence WHERE job=?',(jid,)):
            d=json.loads(r['data'])
            if customer and d['visibility']!='customer':continue
            content+='<li>'+html.escape(r['name']+' | '+d['target']+' | '+d['purpose']+' | SHA256 '+r['hash'])+'</li>'
        content+='</ul>'
        if not customer:
            content+='<h2>Internal records</h2><pre>'+html.escape(json.dumps(self.records(jid),indent=2))+'</pre>'
            content+='<h2>Internal economics</h2><pre>'+html.escape(json.dumps(self.economics(jid),indent=2))+'</pre>'
        return page(content)

    def export(self,jid,destination):
        self.job(jid)
        # Export is always customer-filtered, with an explicit incomplete flag.
        with zipfile.ZipFile(destination,'x',zipfile.ZIP_DEFLATED) as z:
            z.writestr('closeout.html',self.report(jid,True))
            manifest=[]
            for r in self.db.execute('SELECT * FROM evidence WHERE job=?',(jid,)):
                d=json.loads(r['data'])
                if d['visibility']!='customer':continue
                name='evidence/'+r['id']+'-'+Path(r['name']).name
                raw=(self.blobs/r['hash']).read_bytes()
                if digest(raw)!=r['hash']:raise ValueError('Evidence hash mismatch')
                z.writestr(name,raw)
                manifest.append({'path':name,'sha256':r['hash'],**d})
            z.writestr('manifest.json',canonical({'job':jid,'created':now(),'incomplete':bool(self.blockers(jid)),'evidence':manifest}))
        with self.db:self.log('customer_package_exported',{'job':jid,'sha256':digest(Path(destination).read_bytes())})

    def verify(self):
        previous='0'*64
        for r in self.db.execute('SELECT * FROM audit ORDER BY seq'):
            actual=digest(canonical([r['at'],r['event'],r['data'],previous]).encode())
            if r['previous']!=previous or r['hash']!=actual:
                raise ValueError('Audit integrity failure at '+str(r['seq']))
            previous=r['hash']
        for r in self.db.execute('SELECT hash FROM evidence'):
            if digest((self.blobs/r['hash']).read_bytes())!=r['hash']:
                raise ValueError('Evidence integrity failure')
        events = list(self.db.execute("SELECT event,data FROM audit WHERE event IN ('identity_observed','asset_bound','identity_assigned')"))
        observations = {json.loads(r['data'])['id']:json.loads(r['data'])['data']
                        for r in events if r['event']=='identity_observed'}
        binds = {json.loads(r['data'])['bind_id']:json.loads(r['data'])
                 for r in events if r['event']=='asset_bound'}
        assignments = {oid:(d['job_id'],d['asset_id']) for oid,d in observations.items() if d.get('job_id')}
        for r in events:
            if r['event']=='identity_assigned':
                d=json.loads(r['data']); assignments[d['observation_id']]=(d['job'],d['asset'])
        stored_observations={r['id']:json.loads(r['data']) for r in self.db.execute('SELECT * FROM serial_observations')}
        stored_binds={r['id']:json.loads(r['data']) for r in self.db.execute('SELECT * FROM asset_bindings')}
        stored_assignments={r['observation']:(r['job'],r['asset']) for r in self.db.execute('SELECT * FROM serial_assignments')}
        if observations!=stored_observations or binds!=stored_binds or assignments!=stored_assignments:
            raise ValueError('Identity records differ from audit history')
        for r in self.db.execute('SELECT * FROM asset_heads'):
            versions=[b['revision'] for b in binds.values() if b['asset_id']==r['asset']]
            if not versions or r['revision']!=max(versions):
                raise ValueError('Identity head revision inconsistent')
        return {'audit_head':previous,'sqlite':self.db.execute('PRAGMA integrity_check').fetchone()[0],
                'warning':'Local hashes detect damage, not malicious rewriting by an administrator. Anchor backup hashes separately.'}

    def backup(self,destination):
        dest=Path(destination).resolve()
        if dest==self.root or self.root in dest.parents:
            raise ValueError('Backup must be outside live data directory')
        dest.mkdir(parents=True,exist_ok=False)
        # Single operator must stop other writes while backup is taken.
        out=sqlite3.connect(dest/'office.sqlite')
        self.db.backup(out);out.close()
        shutil.copytree(self.blobs,dest/'blobs')
        check=Office(dest)
        result=check.verify();check.db.close()
        (dest/'backup-manifest.json').write_text(canonical(result),encoding='utf-8')
        return result

def page(body):
    return '<!doctype html><html lang="en"><meta charset="utf-8"><title>Network Engineer Copilot</title><style>body{font:16px system-ui;margin:40px;max-width:1000px;line-height:1.5}table{border-collapse:collapse;width:100%}td,th{border:1px solid #bbb;padding:8px;text-align:left}pre{white-space:pre-wrap;overflow-wrap:anywhere}@media print{body{margin:0;font-size:11pt}tr{break-inside:avoid}}</style><body>'+body+'</body></html>'

def read_json(path):
    return json.loads(Path(path).read_text(encoding='utf-8-sig'))

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--home',default=os.environ.get('FIELD_OFFICE_HOME',str(Path.home()/'FieldOfficeData')))
    sub=p.add_subparsers(dest='command',required=True)
    def cmd(name,fields):
        s=sub.add_parser(name)
        for field in fields:s.add_argument(field)
        return s
    cmd('observe-serial',['json']);cmd('assign-observation',['id','job','asset'])
    q=cmd('observations',[]);q.add_argument('--job')
    q=cmd('verify-bind',['observation','expected_revision','verifier','source','reason'])
    q=cmd('recall-serial',['job','asset']);q.add_argument('--revision',type=int)
    cmd('dispute-bind',['job','asset','expected_revision','reason'])
    cmd('init',[]);cmd('job',['json']);cmd('show',['job']);cmd('revise',['job','scope','source'])
    cmd('record',['job','kind','json']);cmd('attach',['job','file','target','purpose','visibility'])
    cmd('satisfy',['job','requirement','evidence','note']);cmd('track',['job','track','value','source'])
    r=cmd('reserve',['job','arrival','review'])
    for name,default in [('work',240),('travel',60),('closeout',30),('recovery',90)]:r.add_argument('--'+name,type=int,default=default)
    r.add_argument('--state',choices=['soft','hard'],default='soft')
    cmd('release',['job','reason']);cmd('propose',['job','json','expires']);cmd('action',['id'])
    cmd('approve',['id','hash']);cmd('outcome',['id','state','receipt'])
    cmd('receive',['sku','location','quantity','unit_price']);cmd('consume',['job','sku','location','quantity'])
    cmd('document',['job','kind','json']);cmd('economics',['job']);cmd('export',['job','zip'])
    cmd('report',['job','html']);cmd('verify',[]);cmd('backup',['destination']);cmd('list',[])
    a=p.parse_args();o=Office(a.home);c=a.command;v=None
    try:
        if c=='init':v={'home':str(o.root),'version':VERSION}
        elif c=='observe-serial':v=o.observe_serial(read_json(a.json))
        elif c=='assign-observation':v=o.assign_observation(a.id,a.job,a.asset)
        elif c=='observations':v=o.serial_observations(a.job)
        elif c=='verify-bind':v=o.verify_bind(a.observation,int(a.expected_revision),a.verifier,a.source,a.reason)
        elif c=='recall-serial':v=o.recall_serial(a.job,a.asset,a.revision)
        elif c=='dispute-bind':v=o.dispute_bind(a.job,a.asset,int(a.expected_revision),a.reason)
        elif c=='job':v=o.save_job(read_json(a.json))
        elif c=='show':v={'job':o.job(a.job),'records':o.records(a.job),'blockers':o.blockers(a.job)}
        elif c=='revise':v=o.revise(a.job,a.scope,a.source)
        elif c=='record':v=o.record(a.job,a.kind,read_json(a.json))
        elif c=='attach':v=o.attach(a.job,a.file,a.target,a.purpose,a.visibility)
        elif c=='satisfy':v=o.satisfy(a.job,a.requirement,a.evidence,a.note)
        elif c=='track':v=o.track(a.job,a.track,a.value,a.source)
        elif c=='reserve':v=o.reserve(a.job,a.arrival,a.work,a.travel,a.closeout,a.recovery,a.state,a.review)
        elif c=='release':v=o.release(a.job,a.reason)
        elif c=='propose':v=o.propose(a.job,read_json(a.json),a.expires)
        elif c=='action':v=o.action(a.id)
        elif c=='approve':v=o.approve(a.id,a.hash)
        elif c=='outcome':v=o.action_result(a.id,a.state,a.receipt)
        elif c=='receive':v=o.stock(a.sku,a.location,int(a.quantity),cents(a.unit_price))
        elif c=='consume':v=o.consume(a.job,a.sku,a.location,int(a.quantity))
        elif c=='document':v=o.document(a.job,a.kind,read_json(a.json))
        elif c=='economics':v=o.economics(a.job)
        elif c=='export':v=o.export(a.job,a.zip)
        elif c=='report':Path(a.html).write_text(o.report(a.job),encoding='utf-8');v=a.html
        elif c=='verify':v=o.verify()
        elif c=='backup':v=o.backup(a.destination)
        elif c=='list':v=[o.job(r[0]) for r in o.db.execute('SELECT id FROM jobs')]
        print(json.dumps(v if v is not None else {'ok':True},indent=2))
    except (ValueError,KeyError,sqlite3.Error,OSError) as e:
        print('ERROR: '+str(e),file=sys.stderr);return 1
    finally:o.db.close()
    return 0

if __name__=='__main__':sys.exit(main())
