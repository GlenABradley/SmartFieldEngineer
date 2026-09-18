"""Offline validation. No URL resolver: every schema reference is in a closed local registry."""
from pathlib import Path
import json,sys,platform,sqlite3,importlib.metadata
from jsonschema import Draft202012Validator,FormatChecker
from referencing import Registry,Resource
R=Path(__file__).resolve().parents[1]
files=list((R/'schemas').glob('*.json'));schemas=[]
for p in files:
 s=json.loads(p.read_text())
 if '$schema' in s:
  Draft202012Validator.check_schema(s);schemas.append(s)
def deny_remote(uri):raise RuntimeError('Nonlocal schema reference: '+uri)
registry=Registry(retrieve=deny_remote).with_resources((s['$id'],Resource.from_contents(s)) for s in schemas)
contract=next(s for s in schemas if '$defs' in s)
checker=FormatChecker()
assert checker.conforms('11111111-1111-4111-8111-111111111111','uuid')
assert not checker.conforms('bad','uuid')
assert not checker.conforms('2026-01-01T12:00:00','date-time')
def validator(n):return Draft202012Validator({'$ref':contract['$id']+'#/$defs/'+n},registry=registry,format_checker=checker)
corpus=json.loads((R/'examples/specimens.json').read_text());errors=[]
for x in corpus['positive']:
 es=list(validator(x['definition']).iter_errors(x['value']))
 if es:errors.append(x['name']+': '+es[0].message)
for x in corpus['negative']:
 if validator(x['definition']).is_valid(x['value']):errors.append('Rejection accepted: '+x['name'])
methods=json.loads((R/'schemas/methods.json').read_text());assert len(methods)==20
covered={x['definition'] for x in corpus['positive']};assert set(contract['$defs'])<=covered
for m in methods:
 assert 'request_'+m in covered and 'response_'+m in covered
# All refs resolve without network, even those not traversed by first-branch witnesses.
def walk(x):
 if isinstance(x,dict):
  if '$ref' in x:registry.resolver(contract['$id']).lookup(x['$ref'])
  for y in x.values():walk(y)
 elif isinstance(x,list):
  for y in x:walk(y)
walk(contract)
result={'status':'passed' if not errors else 'failed','schema_files':len(schemas),'definitions':len(contract['$defs']),'public_methods':len(methods),'positive':len(corpus['positive']),'negative':len(corpus['negative']),'format_checks':['uuid','offset-aware date-time'],'resolution':'local only','python':platform.python_version(),'sqlite':sqlite3.sqlite_version,'jsonschema':importlib.metadata.version('jsonschema'),'errors':errors}
(R/'validation-schema.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));sys.exit(bool(errors))
