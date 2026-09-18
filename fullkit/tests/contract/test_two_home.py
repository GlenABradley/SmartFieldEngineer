"""Release-contract integration, intentionally fails collection until real app exists.
Implement packages.application.testing.launch per README; never supply a fake driver.
"""
import copy,json,uuid
from pathlib import Path
import pytest
from packages.application.testing import launch

JOB='22222222-2222-4222-8222-222222222222'
ASSET='33333333-3333-4333-8333-333333333333'
AT='2026-09-18T12:00:00-04:00'
SOURCE={'kind':'operator_attestation','reference':'Disposable integration observation','observed_at':AT,'claimed_source':'test owner (claimed)'}
def uid():return str(uuid.uuid4())

def call(app,method,params):
 request={'jsonrpc':'2.0','id':uid(),'method':method,'params':params}
 # Goes through actual JSON frame parser and application dispatch, not a convenience mock.
 response=json.loads(app.raw_frame((json.dumps(request)+'\n').encode('utf-8')))
 assert response['jsonrpc']=='2.0' and response['id']==request['id']
 return response

def ok(app,method,params):
 response=call(app,method,params)
 assert 'error' not in response,response
 return response['result']

def deny(response,code):
 if 'error' in response:
  assert response['error']=={'code':-32000,'message':code,'data':{}}
  assert 'result' not in response
 else:
  # Accepted, authorized commands persist rule rejection as a failed receipt.
  assert code not in {'HOME_CONTEXT','RECOVERY_INACTIVE','OPERATION_ID_CONFLICT'}
  receipt=response['result']
  if 'receipt' in receipt:receipt=receipt['receipt']
  assert receipt['state']=='failed' and receipt['result'] is None
  assert receipt['error']=={'code':code,'body':{}}

def select(app,h):return ok(app,'session.select_home',{'home_id':h['home_id'],'store_instance_id':h['store_instance_id']})

def command(ctx,name,payload,job=JOB,scope=1,expected=None,operation=None):
 return {'context':copy.deepcopy(ctx),'cmd':{'schema':'cmd.v0.addendum-r4','kind':'command','operation_id':operation or uid(),'home_id':ctx['home_id'],'command':name,'job_id':job,'job_scope_revision':scope,'expected_revision':expected,'payload':payload}}

def confirmed(app,ctx,name,payload,**kw):
 params=command(ctx,name,payload,**kw);r=ok(app,name,params)
 assert r['state']=='confirmed',r
 assert r['home_id']==ctx['home_id'] and r['store_instance_id']==ctx['store_instance_id']
 return r

def seed(app,ctx,serial):
 created=confirmed(app,ctx,'job.create',{'title':'Same-ID job','scope_text':'Disposable scope','capture_refs':[]},scope=None,expected=0)
 assert created['result']['aggregate_revision']==1 and created['result']['scope_revision']==1
 observed=confirmed(app,ctx,'serial.observe',{'identity_kind':'serial','raw':' '+serial+' ','normalization':'trim_only.v0','method':'manual_label_read','claimed_observer':'test owner','observed_at':AT,'source_reference':SOURCE,'evidence_ids':[],'manufacturer':None,'model':None})
 oid=observed['result']['observation_id']
 assigned=confirmed(app,ctx,'serial.assign',{'observation_id':oid,'asset_id':ASSET},expected=0)
 assert assigned['result']['revision']==1
 verified=confirmed(app,ctx,'serial.verify',{'observation_id':oid,'asset_id':ASSET,'verification':{'claimed_verifier':'test owner','verified_at':AT,'source_reference':SOURCE},'reason':'Direct label comparison'},expected=0)
 assert verified['result']['normalized']==serial and verified['result']['revision']==1
 return verified

def recall(app,ctx):return ok(app,'serial.recall',{'context':ctx,'job_id':JOB,'asset_id':ASSET})
def projection(app,ctx,view,job=JOB):return ok(app,'job.get',{'context':ctx,'job_id':job,'view':view,'cursor':None,'limit':100})

@pytest.fixture(params=['qprocess','in_process_dev'])
def app(tmp_path,request):
 with launch(owner_root=tmp_path,transport=request.param) as running:
  provision=running.maintenance(['provision','--label','Home A','--label','Home B'])
  assert provision['status']=='confirmed'
  yield running

def test_two_homes_raw_context_receipts_pins_and_inactive_restore(app):
 homes=ok(app,'home.list',{})['homes'];assert len(homes)==2
 assert all(set(h)=={'home_id','store_instance_id','label','active','recovery'} for h in homes)
 a,b=homes;assert a['home_id']!=b['home_id']
 ca=select(app,a);va=seed(app,ca,'A-SERIAL')
 da=confirmed(app,ca,'document.prepare',{'type':'closeout','title':'A closeout','body_text':'Literal <script> and https://invalid.example/','asset_ids':[ASSET]},expected=1)['result']
 assert da['pins'][0]['serial']=='A-SERIAL'
 assert app.open_read_handle(da['read_handle'],ca)['sha256']==da['digest']
 assert recall(app,ca)['serial']=='A-SERIAL'
 cb=select(app,b);vb=seed(app,cb,'B-SERIAL')
 assert recall(app,cb)['serial']=='B-SERIAL'
 foreign=call(app,'operation.get',{'context':cb,'operation_id':va['operation_id']})
 unknown=call(app,'operation.get',{'context':cb,'operation_id':uid()})
 deny(foreign,'HOME_CONTEXT');deny(unknown,'HOME_CONTEXT')
 assert foreign['error']==unknown['error']
 assert app.open_read_handle(da['read_handle'],cb)=={'error':{'code':'HOME_CONTEXT','body':{}}}
 deny(call(app,'serial.recall',{'context':ca,'job_id':JOB,'asset_id':ASSET}),'HOME_CONTEXT')
 crossed=command(cb,'record.add',{'entry_kind':'note','text':'must not land in B','reason':'test'})
 crossed['cmd']['home_id']=a['home_id'];deny(call(app,'record.add',crossed),'HOME_CONTEXT')
 assert projection(app,cb,'records')['data']['items']==[]
 db=confirmed(app,cb,'document.prepare',{'type':'closeout','title':'B closeout','body_text':'B','asset_ids':[ASSET]},expected=1)['result']
 assert db['pins'][0]['serial']=='B-SERIAL'
 ca2=select(app,a);assert ca2['session_generation']>cb['session_generation']
 assert recall(app,ca2)['serial']=='A-SERIAL'
 deny(call(app,'system.status',{'context':ca,'active_job_id':None}),'HOME_CONTEXT')
 # No private paths in user-facing projections.
 home_envelopes=projection(app,ca2,'envelopes',None)
 assert home_envelopes=={'view':'envelopes','job_id':None,'data':{'items':[],'next_cursor':None}}
 before=app.business_snapshot(a['home_id'],a['store_instance_id'])
 b_before=app.store_file_hashes(b['home_id'],b['store_instance_id'])
 archive=confirmed(app,ca2,'backup.create',{'destination_token':None},job=None,scope=None)['result']
 # A scoped archive capability cannot be used from B.
 cb2=select(app,b)
 foreign_restore=command(cb2,'backup.restore',{'archive_token':archive['archive_token'],'destination_token':None,'mode':'inactive'},job=None,scope=None)
 deny(call(app,'backup.restore',foreign_restore),'HOME_CONTEXT')
 ca3=select(app,a)
 # Archive capability is Home/store scoped and survives select/restart; unlike preview/stage handles.
 restored=confirmed(app,ca3,'backup.restore',{'archive_token':archive['archive_token'],'destination_token':None,'mode':'inactive'},job=None,scope=None)['result']
 assert restored['source_home_id']==a['home_id'] and restored['recovery_copy_id']!=a['store_instance_id'] and restored['active'] is False
 assert app.business_snapshot(a['home_id'],a['store_instance_id'])==before
 # B selection may checkpoint, so baseline after it is re-closed before the restore itself.
 # Strict B-byte comparison is covered below with a baseline taken immediately before a second restore.
 b_closed=app.store_file_hashes(b['home_id'],b['store_instance_id'])
 confirmed(app,ca3,'backup.restore',{'archive_token':archive['archive_token'],'destination_token':None,'mode':'inactive'},job=None,scope=None)
 assert app.store_file_hashes(b['home_id'],b['store_instance_id'])==b_closed
 recovery={'home_id':a['home_id'],'store_instance_id':restored['recovery_copy_id']}
 cr=select(app,recovery);assert recall(app,cr)['serial']=='A-SERIAL'
 deny(call(app,'record.add',command(cr,'record.add',{'entry_kind':'note','text':'forbidden','reason':'test'})),'RECOVERY_INACTIVE')
 deny(call(app,'backup.create',command(cr,'backup.create',{'destination_token':None},job=None,scope=None)),'RECOVERY_INACTIVE')
 listed=ok(app,'home.list',{})['homes']
 assert len({h['home_id'] for h in listed})==2
 assert next(h for h in listed if h['store_instance_id']==cr['store_instance_id'])['recovery'] is True
 # Immutable pin remains the original value in inactive recovery.
 docs=projection(app,cr,'documents')['data']['items']
 assert next(d for d in docs if d['document_id']==da['document_id'])['pins'][0]['serial']=='A-SERIAL'

def test_attach_context_denial_does_not_consume_authorized_token(app):
 import hashlib
 a,b=ok(app,'home.list',{})['homes'];ca=select(app,a)
 # Inbox attach permits null job/scope.
 raw=b'original evidence bytes\n';meta={'original_name':'capture.txt','media_type':'text/plain','classification':'internal','declared_length':len(raw),'declared_sha256':hashlib.sha256(raw).hexdigest()}
 op=uid();p=command(ca,'evidence.attach',{'phase':'stage','attempt':1,'metadata':meta},job=None,scope=None,operation=op)
 stage=ok(app,'evidence.attach',p);assert stage['receipt']['state']=='executing'
 slot=stage['receipt']['result'];Path(slot['staging_path']).write_bytes(raw)
 # Flush through the desktop's actual writer helper before publishing.
 app.flush_staged_file(slot['staging_path'])
 pub=command(ca,'evidence.attach',{'phase':'publish','attempt':1,'metadata':meta,'token':slot['token']},job=None,scope=None,operation=op)
 wrong=copy.deepcopy(pub);wrong['context']['home_id']=b['home_id']
 deny(call(app,'evidence.attach',wrong),'HOME_CONTEXT')
 result=ok(app,'evidence.attach',pub);assert result['receipt']['state']=='confirmed'
 eid=result['receipt']['result']['evidence_id']
 replay=ok(app,'evidence.attach',pub);assert replay==result
 rows=projection(app,ca,'evidence',None)['data']['items'];assert [r['evidence_id'] for r in rows]==[eid]
 changed=copy.deepcopy(pub);changed['cmd']['payload']['metadata']['declared_sha256']='0'*64
 deny(call(app,'evidence.attach',changed),'OPERATION_ID_CONFLICT')
 cb=select(app,b)
 deny(call(app,'evidence.attach',pub),'HOME_CONTEXT')
 assert projection(app,cb,'evidence',None)['data']['items']==[]

def test_serial_correction_dispute_and_immutable_pin(app):
 a=ok(app,'home.list',{})['homes'][0];ctx=select(app,a);v=seed(app,ctx,'A-SERIAL')
 doc=confirmed(app,ctx,'document.prepare',{'type':'work_order','title':'Pinned','body_text':'Before correction','asset_ids':[ASSET]},expected=1)['result']
 confirmed(app,ctx,'serial.dispute',{'asset_id':ASSET,'bind_id':v['result']['bind_id'],'reason':'Recheck'},expected=1)
 assert recall(app,ctx)['status']=='unresolved' and recall(app,ctx)['serial'] is None
 deny(call(app,'serial.dispute',command(ctx,'serial.dispute',{'asset_id':ASSET,'bind_id':v['result']['bind_id'],'reason':'Second conflict'},expected=1)),'STALE_BIND')
 deny(call(app,'document.prepare',command(ctx,'document.prepare',{'type':'closeout','title':'No unresolved pin','body_text':'','asset_ids':[ASSET]},expected=1)),'SERIAL_UNRESOLVED')
 o=confirmed(app,ctx,'serial.observe',{'identity_kind':'serial','raw':' A-CORRECTED ','normalization':'trim_only.v0','method':'manual_label_read','claimed_observer':'owner','observed_at':AT,'source_reference':SOURCE,'evidence_ids':[],'manufacturer':None,'model':None})['result']['observation_id']
 confirmed(app,ctx,'serial.assign',{'observation_id':o,'asset_id':ASSET},expected=0)
 corrected=confirmed(app,ctx,'serial.verify',{'observation_id':o,'asset_id':ASSET,'verification':{'claimed_verifier':'owner','verified_at':AT,'source_reference':SOURCE},'reason':'Correction'},expected=1)
 assert corrected['result']['revision']==2 and recall(app,ctx)['serial']=='A-CORRECTED'
 old=next(d for d in projection(app,ctx,'documents')['data']['items'] if d['document_id']==doc['document_id'])
 assert old['digest']==doc['digest'] and old['pins']==doc['pins']
 historical=ok(app,'serial.recall',{'context':ctx,'job_id':JOB,'asset_id':ASSET,'revision':1})
 assert historical['historical'] is True and historical['serial']=='A-SERIAL'

def test_import_plan_cannot_cross_home_and_same_corpus_replays(app,tmp_path):
 import sqlite3,sys
 contract=Path(__file__).resolve().parents[1]
 # In a copied implementation test directory, driver supplies contract package path by layout.
 if not (contract/'tools/legacy_inventory.py').exists():contract=Path.cwd()/'contract'
 sys.path.insert(0,str(contract/'tools'))
 from legacy_inventory import inventory
 a,b=ok(app,'home.list',{})['homes']
 legacy=tmp_path/'synthetic_legacy';legacy.mkdir()
 with sqlite3.connect(legacy/'office.sqlite') as con:
  con.executescript((contract/'reference/legacy-ddl.sql').read_text())
  con.execute('INSERT INTO office_meta VALUES(?,?)',('ledger_id','test-import-identity'))
  con.execute('INSERT INTO jobs VALUES(?,?,?)',('legacy-job',json.dumps({'client':'Fixture','scope':'Read-only source fixture'}),1))
 inv=inventory(legacy)
 plan=tmp_path/'plan.json';plan.write_text(json.dumps({'source_digest':inv['source_digest'],'target_home_id':a['home_id'],'decisions':[]}))
 def args(home):return ['import','--home',home['home_id'],'--store',home['store_instance_id'],'--source',str(legacy),'--plan',str(plan)]
 first=app.maintenance(args(a));assert first['result']=='applied'
 replay=app.maintenance(args(a));assert replay['result']=='IMPORT_ALREADY_APPLIED'
 assert first['report']==replay['report']
 assert inventory(legacy)==inv
 denied=app.maintenance(args(b));assert denied=={'error':{'code':'HOME_CONTEXT','body':{}}}
 cb=select(app,b);assert ok(app,'job.list',{'context':cb,'cursor':None,'limit':100})['items']==[]
 ca=select(app,a);rows=ok(app,'job.list',{'context':ca,'cursor':None,'limit':100})['items'];assert len(rows)==1
 recovery_archive=confirmed(app,ca,'backup.create',{'destination_token':None},job=None,scope=None)['result']
 recovery=confirmed(app,ca,'backup.restore',{'archive_token':recovery_archive['archive_token'],'destination_token':None,'mode':'inactive'},job=None,scope=None)['result']
 args_r=args({'home_id':a['home_id'],'store_instance_id':recovery['recovery_copy_id']})
 assert app.maintenance(args_r)=={'error':{'code':'RECOVERY_INACTIVE','body':{}}}

def test_proposed_c1_c2_sourced_resume_resolves_only_named_hold(app):
 """Explicit review vector for proposed C1/C2; not evidence of prior adoption."""
 a=ok(app,'home.list',{})['homes'][0];ctx=select(app,a);seed(app,ctx,'A-SERIAL')
 def track(state,expected,scope,hold=None):
  return command(ctx,'job.update',{'update_kind':'track_event','track':'field','track_state':state,'interruption_id':hold,'capture_refs':[],'reason':'Owner decision','provenance':'sourced_manual','source_reference':SOURCE,'evidence_ids':[]},scope=scope,expected=expected)
 assert ok(app,'job.update',track('in_progress',1,1))['state']=='confirmed'
 payload={'trigger':'scope_change','step_name':'inspection','last_verified_state':'fixture isolated','exposed':'none observed','service_impact':'fixture only','reversible':'yes','irreversible':'no','stabilization':'operator secured fixture','stabilization_done':True,'evidence_ids':[],'source_reference':SOURCE,'hold':'await scope review','responsible':'test owner','state':'secured_on_hold'}
 holds=[confirmed(app,ctx,'interruption.record',payload)['result']['interruption_id'] for _ in range(2)]
 change=confirmed(app,ctx,'job.update',{'update_kind':'scope','scope_text':'Revised fixture scope','interruption_id':holds[0],'capture_refs':[],'reason':'Scope review','provenance':'sourced_manual','source_reference':SOURCE},expected=2)
 assert change['result']['scope_revision']==2 and change['result']['aggregate_revision']==3
 rows=projection(app,ctx,'interruptions')['data']['items']
 assert {r['interruption_id'] for r in rows}==set(holds)
 assert all(r['current_scope_revision']==1 and r['effective_scope_revision']==2 for r in rows)
 resume=ok(app,'job.update',track('ready',3,2,holds[0]));assert resume['state']=='confirmed'
 rows=projection(app,ctx,'interruptions')['data']['items']
 assert next(r for r in rows if r['interruption_id']==holds[0])['resolved_at'] is not None
 assert next(r for r in rows if r['interruption_id']==holds[1])['resolved_at'] is None
 deny(call(app,'job.update',track('completed',4,2)),'SCHEMA')
 deny(call(app,'job.update',track('in_progress',4,2,holds[0])),'INTERRUPTION_STALE')
 assert ok(app,'job.update',track('in_progress',4,2,holds[1]))['state']=='confirmed'
 assert ok(app,'job.update',track('completed',5,2))['state']=='confirmed'
