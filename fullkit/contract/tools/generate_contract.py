"""Generate the effective, locally resolved draft-2020-12 contract; no application code."""
from pathlib import Path
import json, copy
ROOT=Path(__file__).resolve().parents[1]
D={}
def obj(p,optional=()):return {'type':'object','properties':p,'required':[k for k in p if k not in optional],'additionalProperties':False}
def ref(n):return {'$ref':'#/$defs/'+n}
def arr(s,minimum=0,maximum=None,unique=False):
 d={'type':'array','items':s,'minItems':minimum}
 if maximum is not None:d['maxItems']=maximum
 if unique:d['uniqueItems']=True
 return d
def enum(*s):return {'enum':list(s)}
def const(s):return {'const':s}
def nullable(s):return {'anyOf':[s,{'type':'null'}]}
def integer(minimum=0):return {'type':'integer','minimum':minimum}
S={'type':'string','minLength':1,'pattern':r'\S'}
TEXT={'type':'string'}
U={'type':'string','format':'uuid'}
T={'type':'string','format':'date-time','pattern':r'(Z|[+-][0-9]{2}:[0-9]{2})$'}
SHA={'type':'string','pattern':'^[0-9a-f]{64}$'}
N={'type':'null'};B={'type':'boolean'};I=integer();P=integer(1);NU=nullable(U)
D['source_reference']=obj(dict(kind=enum('operator_attestation','document','external_record'),reference=S,observed_at=T,claimed_source=S))
D['context']=obj(dict(home_id=U,store_instance_id=U,session_id=U,session_generation=P))
D['capture_ref']={'oneOf':[obj({'kind':const(k),'id':U}) for k in ['record','evidence']]}
CR=arr(ref('capture_ref'),unique=True);IDS=arr(U,unique=True)
D['read_handle']=obj(dict(token=U,expires_at=T,home_id=U,store_instance_id=U,session_id=U,session_generation=P,media_type=S,sha256=SHA))
D['job_create']=obj(dict(title=S,scope_text=S,capture_refs=CR))
common=dict(interruption_id=NU,capture_refs=CR,reason=S,provenance=const('sourced_manual'),source_reference=nullable(ref('source_reference')))
D['scope']=obj(dict(update_kind=const('scope'),scope_text=S,**common),('interruption_id','source_reference'))
tracks={'field':['planned','ready','in_progress','blocked','completed'],'delivery':['not_prepared','prepared','delivery_recorded','accepted','disputed'],'billing':['not_prepared','prepared','issued_recorded','partially_settled_recorded','settled_recorded','disputed'],'returns':['none','pending','closed'],'exception':['none','open','held','resolved']}
D['track_event']={'oneOf':[]}
for track,states in tracks.items():
 p=obj(dict(update_kind=const('track_event'),track=const(track),track_state=enum(*states),evidence_ids=IDS,**common),('interruption_id','source_reference'))
 # C1: proposed correction represents owner decision by explicit sourced event itself, no new field.
 D['track_'+track]=p;D['track_event']['oneOf'].append(ref('track_'+track))
D['job_update']={'oneOf':[ref('scope'),ref('track_event')]}
rcommon=dict(reason=S,source_reference=ref('source_reference'))
D['record_note']=obj(dict(entry_kind=const('note'),text=S,**rcommon),('source_reference',))
D['record_time']=obj(dict(entry_kind=const('time'),minutes=P,started_at=nullable(T),ended_at=nullable(T),activity=S,**rcommon),('source_reference',))
D['record_time']['allOf']=[{'oneOf':[{'properties':{'started_at':N,'ended_at':N}},{'properties':{'started_at':T,'ended_at':T}}]}]
D['record_cost']=obj(dict(entry_kind=const('cost'),amount_cents=I,currency=const('USD'),category=S,**rcommon),('source_reference',))
D['record_item_upsert']=obj(dict(entry_kind=const('item_upsert'),item_id=U,sku=S,display_name=S,unit_name=S,reason=S))
D['record_stock_move']=obj(dict(entry_kind=const('stock_move'),item_id=U,quantity={'type':'integer','not':const(0)},direction=enum('receive','consume','adjust'),location=S,unit_cost_cents=nullable(I),currency=const('USD'),**rcommon),('source_reference','unit_cost_cents'))
D['record_stock_move']['allOf']=[{'if':{'properties':{'direction':enum('receive','consume')}},'then':{'properties':{'quantity':P}}},{'if':{'properties':{'direction':const('receive')}},'then':{'required':['unit_cost_cents']}}]
D['record_payload']={'oneOf':[ref('record_'+k) for k in ['note','time','cost','item_upsert','stock_move']]}
D['observation_payload']=obj(dict(identity_kind=enum('serial','asset_label'),raw=nullable(S),normalization=const('trim_only.v0'),method=enum('manual_label_read','photo_transcription','barcode_scan','device_inventory_output','voice_transcript'),claimed_observer=S,observed_at=T,source_reference=ref('source_reference'),evidence_ids=IDS,manufacturer=nullable(S),model=nullable(S)))
D['observation_payload']['allOf']=[{'if':{'properties':{'method':const('photo_transcription')}},'then':{'properties':{'evidence_ids':arr(U,1,unique=True)}}}]
D['assignment_payload']=obj(dict(observation_id=U,asset_id=U))
D['verification']=obj(dict(claimed_verifier=S,verified_at=T,source_reference=ref('source_reference')))
D['verify_payload']=obj(dict(observation_id=U,asset_id=U,verification=ref('verification'),reason=S))
D['dispute_payload']=obj(dict(bind_id=U,asset_id=U,reason=S))
D['document_payload']=obj(dict(type=enum('work_order','job_summary','closeout'),title=S,body_text=TEXT,asset_ids=IDS))
D['interruption_payload']=obj(dict(trigger=enum('scope_change','tool_missing','unsafe_site','mentor_unavailable','other'),step_name=nullable(S),last_verified_state=S,exposed=S,service_impact=S,reversible=enum('yes','no','unknown'),irreversible=enum('yes','no','unknown'),stabilization=S,stabilization_done=B,evidence_ids=IDS,source_reference=nullable(ref('source_reference')),hold=S,responsible=S,state=enum('detected','stabilizing','secured_on_hold','stabilization_failed')))
D['interruption_payload']['allOf']=[{'if':{'properties':{'state':const('secured_on_hold')}},'then':{'properties':{'stabilization_done':const(True)},'anyOf':[{'properties':{'evidence_ids':arr(U,1,unique=True)}},{'properties':{'source_reference':ref('source_reference')}}]}}]
D['components']=obj({k:I for k in ['preparation','travel','work','contingency','documentation','replenishment','aftercare','supervision']})
D['envelope_payload']=obj(dict(envelope_id=U,starts_at=T,ends_at=T,site_timezone=S,state=enum('soft','hard'),resources=arr(S,1,16,True),components_minutes=ref('components')))
D['evidence_metadata']=obj(dict(original_name={'type':'string','minLength':1,'pattern':r'^[^/\\\u0000]+$'},media_type=S,classification=enum('internal','customer'),declared_length={'type':'integer','minimum':1,'maximum':52428800},declared_sha256=SHA))
for phase in ['stage','publish']:
 p=dict(phase=const(phase),attempt=P,metadata=ref('evidence_metadata'))
 if phase=='publish':p['token']=U
 D['attach_'+phase]=obj(p)
D['attach_payload']={'oneOf':[ref('attach_stage'),ref('attach_publish')]}
D['backup_payload']=obj(dict(destination_token=NU))
D['restore_payload']=obj(dict(archive_token=U,destination_token=NU,mode=const('inactive')))
commands={'job.create':'job_create','job.update':'job_update','record.add':'record_payload','evidence.attach':'attach_payload','serial.observe':'observation_payload','serial.assign':'assignment_payload','serial.verify':'verify_payload','serial.dispute':'dispute_payload','document.prepare':'document_payload','interruption.record':'interruption_payload','envelope.put':'envelope_payload','backup.create':'backup_payload','backup.restore':'restore_payload'}
for cmd,pay in commands.items():
 er=N if cmd in ['record.add','evidence.attach','serial.observe','interruption.record','backup.create','backup.restore'] else I
 if cmd in ['job.create','serial.assign']:er=const(0)
 if cmd in ['job.update','document.prepare','serial.dispute']:er=P
 jid=N if cmd.startswith('backup.') else U if cmd in ['job.create','job.update','serial.assign','serial.verify','serial.dispute','document.prepare','interruption.record'] else NU
 scope=N if cmd in ['job.create','envelope.put','backup.create','backup.restore'] else P if jid==U else nullable(P)
 D['cmd_'+cmd]=obj(dict(schema=const('cmd.v0.addendum-r4'),kind=const('command'),operation_id=U,home_id=U,command=const(cmd),job_id=jid,job_scope_revision=scope,expected_revision=er,payload=ref(pay)))
 if cmd in ['record.add','evidence.attach','serial.observe']:
  D['cmd_'+cmd]['allOf']=[{'if':{'properties':{'job_id':N}},'then':{'properties':{'job_scope_revision':N}},'else':{'properties':{'job_scope_revision':P}}}]
D['command']={'oneOf':[ref('cmd_'+c) for c in commands]}
# Facts and projections. Core provenance is a Windows SID, never operator-supplied identity.
fact=dict(home_id=U,created_at=T,local_principal=S,submitted_scope_revision=nullable(P),current_scope_revision=nullable(P))
D['observation']=obj(dict(observation_id=U,job_id=NU,payload=ref('observation_payload'),**fact))
D['assignment']=obj(dict(observation_id=U,asset_id=U,job_id=U,revision=const(1),**fact))
D['bind']=obj(dict(bind_id=U,asset_id=U,job_id=U,observation_id=U,revision=P,identity_kind=enum('serial','asset_label'),raw=S,normalized=S,normalization=const('trim_only.v0'),verification=ref('verification'),reason=S,supersedes_bind_id=NU,**fact))
D['dispute']=obj(dict(dispute_id=U,bind_id=U,asset_id=U,job_id=U,revision=P,reason=S,**fact))
D['identity_fact']={'oneOf':[ref(x) for x in ['observation','assignment','bind','dispute']]}
D['evidence']=obj(dict(evidence_id=U,job_id=NU,original_name=S,media_type=S,sha256=SHA,byte_length={'type':'integer','minimum':1,'maximum':52428800},classification=enum('internal','customer'),read_handle=ref('read_handle')),('read_handle',))
D['pin']=obj(dict(asset_id=U,bind_id=U,revision=P,serial=S))
D['document']=obj(dict(document_id=U,job_id=U,type=enum('work_order','job_summary','closeout'),prepared_at=T,job_scope_revision=P,digest=SHA,pins=arr(ref('pin')),read_handle=ref('read_handle')),('read_handle',))
D['job_summary']=obj(dict(job_id=U,title=S,scope_text=S,aggregate_revision=P,scope_revision=P,tracks=obj({k:enum(*v) for k,v in tracks.items()})))
D['record']=obj(dict(record_id=U,job_id=NU,payload=ref('record_payload'),**fact))
D['interruption']=obj(dict(interruption_id=U,job_id=U,payload=ref('interruption_payload'),effective_scope_revision=P,resolved_at=nullable(T),resolution_operation_id=NU,**fact))
D['envelope']=obj(dict(job_id=NU,revision=P,payload=ref('envelope_payload')))
D['stage_result']=obj(dict(attempt=P,token=U,expires_at=T,staging_path=S))
D['archive']=obj(dict(archive_token=U,manifest_sha256=SHA,verified_at=T))
D['recovery']=obj(dict(recovery_copy_id=U,source_home_id=U,active=const(False)))
D['recall']={'oneOf':[obj(dict(status=const('verified'),serial=S,bind=ref('bind'),historical=B,current_state=enum('active','disputed'))),obj(dict(status=const('unresolved'),serial=N,job_id=U,asset_id=U))]}
D['home_instance']=obj(dict(home_id=U,store_instance_id=U,label=S,active=B,recovery=B))
codes=['HOME_CONTEXT','HOME_WRITER_EXISTS','RECOVERY_INACTIVE','OPERATION_ID_CONFLICT','STALE_JOB','STALE_BIND','STALE_ASSIGNMENT','STALE_RESERVATION','FIELD_TRACK_ACTIVE','INTERRUPTION_FOREIGN','INTERRUPTION_STALE','SERIAL_UNRESOLVED','ITEM_UNKNOWN','CAPTURE_ALREADY_ALLOCATED','OBSERVATION_ALREADY_ASSIGNED','OBSERVATION_ALREADY_VERIFIED','STAGE_EXPIRED','INBOX_VIEW','SCHEMA']
D['domain_failure']=obj(dict(code=enum(*codes),body=obj({})))
D['attach_attempt']=obj(dict(attempt=P,phase=enum('stage','publish'),phase_fingerprint=SHA,state=enum('staged','consumed','expired','published','failed'),result=nullable({'oneOf':[ref('stage_result'),ref('evidence')]}),error=nullable(ref('domain_failure'))))
results={'job.create':ref('job_summary'),'job.update':ref('job_summary'),'record.add':ref('record'),'evidence.attach':{'oneOf':[ref('stage_result'),ref('evidence')]},'serial.observe':ref('observation'),'serial.assign':ref('assignment'),'serial.verify':ref('bind'),'serial.dispute':ref('dispute'),'document.prepare':ref('document'),'interruption.record':ref('interruption'),'envelope.put':ref('envelope'),'backup.create':ref('archive'),'backup.restore':ref('recovery')}
receiptbase=dict(schema=const('receipt.v0.addendum-r4'),kind=const('receipt'),operation_id=U,home_id=U,store_instance_id=U,fingerprint=SHA,updated_at=T)
D['receipt']={'oneOf':[]}
for c,r in results.items():
 for state in ['queued','executing','confirmed','failed','unknown']:
  # stage remains executing, never confirms evidence prematurely.
  rr=r if state=='confirmed' else N
  if c=='evidence.attach':rr=ref('evidence') if state=='confirmed' else nullable(ref('stage_result')) if state=='executing' else N
  n='receipt_'+c+'_'+state
  D[n]=obj(dict(**receiptbase,command=const(c),state=const(state),result=rr,error=ref('domain_failure') if state=='failed' else N))
  D['receipt']['oneOf'].append(ref(n))
D['operation']=obj(dict(receipt=ref('receipt'),attach_attempt=nullable(ref('attach_attempt'))))
D['encryption']=obj(dict(value=enum('yes','no','unknown'),basis=enum('live_os','commissioning','unavailable'),observed_at=nullable(T),source=nullable(S)))
D['status']=obj(dict(context=ref('context'),transport=enum('qprocess','in_process_dev'),development_build=B,python_version=S,sqlite_version=S,qt_version=S,readiness=obj(dict(wwan=enum('unknown','observed_up','observed_down'),encrypted_volume=ref('encryption'),battery_percent=nullable({'type':'integer','minimum':0,'maximum':100}),on_ac=nullable(B),heavy_worker=enum('off','observed_active','unknown'))),integrity=obj(dict(checked_at=nullable(T),state=enum('unknown','ok','findings'),findings=arr(S))),operations=arr(ref('receipt'),0,50)))
D['status']['allOf']=[{'if':{'properties':{'transport':const('in_process_dev')}},'then':{'properties':{'development_build':const(True)}}}]
D['page_args']=obj(dict(cursor=nullable(S),limit={'type':'integer','minimum':1,'maximum':100}))
def page(item):return obj(dict(items=arr(item,0,100),next_cursor=nullable(S)))
D['job_page']=page(ref('job_summary'))
views={'summary':'job_summary','records':'record','observations':'identity_fact','evidence':'evidence','documents':'document','interruptions':'interruption','envelopes':'envelope'}
D['job_projection']={'oneOf':[]}
for v,item in views.items():
 D['view_'+v]=obj(dict(view=const(v),job_id=U if v in ['summary','documents','interruptions'] else NU,data=ref(item) if v=='summary' else page(ref(item))))
 D['job_projection']['oneOf'].append(ref('view_'+v))
queries={'home.list':obj({}),'session.select_home':obj(dict(home_id=U,store_instance_id=U)),'job.list':obj(dict(context=ref('context'),cursor=nullable(S),limit={'type':'integer','minimum':1,'maximum':100})),'job.get':obj(dict(context=ref('context'),job_id=NU,view=enum(*views),cursor=nullable(S),limit={'type':'integer','minimum':1,'maximum':100})),'serial.recall':obj(dict(context=ref('context'),job_id=U,asset_id=U,revision=P),('revision',)),'operation.get':obj(dict(context=ref('context'),operation_id=U)),'system.status':obj(dict(context=ref('context'),active_job_id=NU))}
for c in commands:queries[c]=obj(dict(context=ref('context'),cmd=ref('cmd_'+c)))
D['request']={'oneOf':[]};D['response']={'oneOf':[]}
qresults={'home.list':obj(dict(homes=arr(ref('home_instance')))),'session.select_home':ref('context'),'job.list':ref('job_page'),'job.get':ref('job_projection'),'serial.recall':ref('recall'),'operation.get':ref('operation'),'system.status':ref('status')}
for c in commands:
 specific={'oneOf':[ref('receipt_'+c+'_'+state) for state in ['queued','executing','confirmed','failed','unknown']]}
 qresults[c]=obj(dict(receipt=specific,attach_attempt=nullable(ref('attach_attempt')))) if c=='evidence.attach' else specific
for c,p in queries.items():
 D['request_'+c]=obj(dict(jsonrpc=const('2.0'),id=U,method=const(c),params=p));D['request']['oneOf'].append(ref('request_'+c))
 D['result_'+c]=qresults[c]
 # Method is paired in registry; JSON-RPC response must not add method field.
 D['response_'+c]=obj(dict(jsonrpc=const('2.0'),id=U,result=ref('result_'+c)))
D['rpc_domain_error']=obj(dict(jsonrpc=const('2.0'),id=U,error=obj(dict(code=const(-32000),message=enum(*codes),data=obj({})))))
D['rpc_protocol_error']={'oneOf':[obj(dict(jsonrpc=const('2.0'),id=NU,error=obj(dict(code=const(code),message=const(message))))) for code,message in [(-32700,'Parse error'),(-32600,'Invalid Request'),(-32601,'Method not found'),(-32602,'Invalid params'),(-32603,'Internal error')]]}
D['maintenance_report']=obj(dict(import_batch_id=U,source_digest=SHA,source_ledger_id=S,target_home_id=U,inserted=I,reused=I,warnings=arr(S),conflicts=arr(S)))
D['maintenance_result']=obj(dict(result=enum('applied','IMPORT_ALREADY_APPLIED'),report=ref('maintenance_report')))
# Response union intentionally anyOf: receipt shapes overlap across method-specific responses.
D['response']={'anyOf':[ref('response_'+c) for c in queries]+[ref('rpc_domain_error'),ref('rpc_protocol_error')]}
schema={'$schema':'https://json-schema.org/draft/2020-12/schema','$id':'https://fullkit.local/schemas/contract.json','title':'Full Kit Slice 1 1.00.1 effective structural contract; C1/C2 review proposals in README','$defs':D}
(ROOT/'schemas/contract.json').write_text(json.dumps(schema,indent=2)+'\n')
for n in ['command','receipt','identity_fact','evidence','request','response','maintenance_report']:
 (ROOT/'schemas'/f'{n}.schema.json').write_text(json.dumps({'$schema':schema['$schema'],'$id':f'https://fullkit.local/schemas/{n}.schema.json','$ref':'contract.json#/$defs/'+n},indent=2)+'\n')
(ROOT/'schemas/methods.json').write_text(json.dumps({c:{'request':'request_'+c,'result':'result_'+c,'response':'response_'+c} for c in queries},indent=2)+'\n')
print(f'Generated {len(D)} definitions and {len(queries)} methods')
