"""Check the actual local workbench, without treating missing app code as a pass."""
from pathlib import Path
import hashlib,json,os,platform,shutil,sqlite3,subprocess,sys,tempfile
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1];REPO=ROOT/'fullkit';REPORT=ROOT/'reports'
REPORT.mkdir(exist_ok=True)
results={}
def run(name,args,cwd=REPO,extra_env=None):
 env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
 if extra_env:env.update(extra_env)
 p=subprocess.run(args,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,timeout=180)
 (REPORT/(name+'.log')).write_text(p.stdout)
 results[name]={'exit_code':p.returncode,'log':name+'.log'}
 return p
run('artifact-integrity',[sys.executable,str(ROOT/'scripts/verify_baseline.py')])
with tempfile.TemporaryDirectory(prefix='fullkit-contract-check-') as td:
 copy=Path(td)/'contract';shutil.copytree(REPO/'contract',copy,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
 run('schema-validation',[sys.executable,str(copy/'tools/validate_contract.py')])
 if (copy/'validation-schema.json').exists():shutil.copy2(copy/'validation-schema.json',REPORT/'schema-validation.json')
run('inventory-tests',[sys.executable,'-m','pytest','tests/contract/test_inventory.py','-q','-p','no:cacheprovider'])
integration=run('application-integration',[sys.executable,'-m','pytest','tests/contract/test_two_home.py','-q','-p','no:cacheprovider'])
run('local-toolchain',[sys.executable,str(ROOT/'scripts/probe_toolchain.py')],extra_env={'QT_QPA_PLATFORM':'offscreen'})
# Preserve every copied source and all preexisting files; repository acceptance tests may later evolve.
source=json.loads((REPORT/'Source-Copy-Register.json').read_text());changed=[]
for name,h in source['existing_root_files_preserved'].items():
 if hashlib.sha256((ROOT/name).read_bytes()).hexdigest()!=h:changed.append(name)
required=['artifact-integrity','schema-validation','inventory-tests','local-toolchain']
local_ok=all(results[n]['exit_code']==0 for n in required) and not changed
missing=integration.returncode==2 and "No module named 'packages" in integration.stdout
summary={'checked_at':datetime.now(timezone.utc).isoformat(),'workspace':str(ROOT),'python':platform.python_version(),'executable':sys.executable,'platform':platform.platform(),'sqlite':sqlite3.sqlite_version,'local_environment_ready':local_ok,'checks':results,'preexisting_files_changed':changed,'application_status':'not implemented; visible import failure' if missing else 'tests passed' if integration.returncode==0 else 'implementation tests failing; inspect log','application_release_qualified':False,'windows_qualified':False,'pending_contract_proposals':['artifact 1.00.1 C1','artifact 1.00.1 C2']}
(REPORT/'Environment-Validation.json').write_text(json.dumps(summary,indent=2)+'\n')
print(json.dumps(summary,indent=2))
# Success means toolchain/contract are ready, not that application tests passed.
sys.exit(0 if local_ok and (missing or integration.returncode==0) else 1)
