from pathlib import Path
import json,copy
R=Path(__file__).resolve().parents[1];D=json.loads((R/'schemas/contract.json').read_text())['$defs']
U='11111111-1111-4111-8111-111111111111';T='2026-09-18T12:00:00-04:00'
def sample(s):
 if '$ref' in s:return sample(D[s['$ref'].split('/')[-1]])
 if 'const' in s:return s['const']
 if 'enum' in s:return s['enum'][0]
 if 'oneOf' in s:return sample(s['oneOf'][0])
 if 'anyOf' in s:return sample(s['anyOf'][0])
 ty=s.get('type')
 if ty=='object':return {k:sample(v) for k,v in s['properties'].items()}
 if ty=='array':return [sample(s['items']) for _ in range(s.get('minItems',0))]
 if ty=='null':return None
 if ty=='boolean':return False
 if ty=='integer':return max(s.get('minimum',1),1)
 if ty=='string':
  if s.get('format')=='uuid':return U
  if s.get('format')=='date-time':return T
  if s.get('pattern')=='^[0-9a-f]{64}$':return 'a'*64
  return 'sample'
 raise ValueError(s)
positives=[{'name':n,'definition':n,'value':sample(s)} for n,s in D.items()]
# Scope/job consistency constraints, not expressible by generic witness constructor.
for x in positives:
 def fix(v):
  if isinstance(v,dict):
   if v.get('transport')=='in_process_dev':v['development_build']=True
   for z in v.values():fix(z)
  elif isinstance(v,list):
   for z in v:fix(z)
 fix(x['value'])
# Exercise every top-level union branch, including all receipt states and RPC errors.
for name,schema in D.items():
 for combinator in ['oneOf','anyOf']:
  for index,branch in enumerate(schema.get(combinator,[])):
   positives.append({'name':f'{name}.{combinator}.{index}','definition':name,'value':sample(branch)})
# Every payload discriminator/enum branch gets a concrete valid witness.
for name,schema in D.items():
 if not (name.endswith('_payload') or name.startswith('record_') or name.startswith('track_')):continue
 for field,shape in schema.get('properties',{}).items():
  for value in shape.get('enum',[]):
   witness=sample(schema);witness[field]=value
   if name=='observation_payload' and witness['method']=='photo_transcription':witness['evidence_ids']=[U]
   if name=='interruption_payload' and witness['state']=='secured_on_hold':witness['stabilization_done']=True
   positives.append({'name':f'{name}.{field}.{value}','definition':name,'value':witness})
neg=[]
def bad(name,definition,value):neg.append(dict(name=name,definition=definition,value=value))
for x in positives:
 if isinstance(x['value'],dict):
  y=copy.deepcopy(x['value']);y['forbidden_extra']=True;bad(x['name']+'_unknown_property',x['definition'],y)
def mutate(name,definition,key,value):
 v=sample(D[definition]);v[key]=value;bad(name,definition,v)
mutate('uuid_format','context','home_id','not-a-uuid')
mutate('naive_timestamp','source_reference','observed_at','2026-09-18T12:00:00')
mutate('invalid_date','source_reference','observed_at','2026-02-30T12:00:00Z')
mutate('empty_resource','envelope_payload','resources',[''])
mutate('no_resources','envelope_payload','resources',[])
mutate('duplicate_resources','envelope_payload','resources',['owner','owner'])
mutate('too_many_resources','envelope_payload','resources',[str(i) for i in range(17)])
mutate('negative_cost','record_cost','amount_cents',-1)
mutate('wrong_currency','record_cost','currency','EUR')
mutate('zero_stock','record_stock_move','quantity',0)
mutate('negative_receive','record_stock_move','quantity',-1)
mutate('zero_evidence','evidence_metadata','declared_length',0)
mutate('oversize_evidence','evidence_metadata','declared_length',52428801)
mutate('stale_wrong_code','domain_failure','code','STALE_ENVELOPE')
mutate('zero_limit','page_args','limit',0)
mutate('large_limit','page_args','limit',101)
mutate('sibling_discriminator','record_note','minutes',10)
v=sample(D['interruption_payload']);v.update(state='secured_on_hold',stabilization_done=False);bad('hold_without_stabilization','interruption_payload',v)
v=sample(D['interruption_payload']);v.update(state='secured_on_hold',stabilization_done=True,source_reference=None,evidence_ids=[]);bad('hold_without_source','interruption_payload',v)
v=sample(D['observation_payload']);v.update(method='photo_transcription',evidence_ids=[]);bad('photo_without_evidence','observation_payload',v)
v=sample(D['record_time']);v['started_at']=None;bad('one_time_endpoint_null','record_time',v)
for k in ['field','delivery','billing']:
 mutate('invented_track_'+k,'track_'+k,'track_state','paid')
(R/'examples/specimens.json').write_text(json.dumps({'positive':positives,'negative':neg},indent=2)+'\n')
print(f'{len(positives)} positive definitions; {len(neg)} rejection specimens')
