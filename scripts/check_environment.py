"""Check local tooling separately from absent, passing or broken application tests."""
from pathlib import Path
import hashlib,json,os,platform,re,shutil,sqlite3,subprocess,sys,tempfile
from datetime import datetime,timezone
ROOT=Path(__file__).resolve().parents[1]

def application_state(repo,exit_code,output):
    if exit_code==0:
        return 'tests passed'
    # Only absence of the real application test driver is an expected setup condition.
    # A driver that exists but has a broken internal import must fail the checker.
    driver_present=any((repo/p).exists() for p in (
        'packages/application/testing.py','packages/application/testing/__init__.py'))
    missing_driver=bool(re.search(
        r"ModuleNotFoundError: No module named ['\"](?:packages|packages\.application|packages\.application\.testing)['\"]",
        output))
    if exit_code==2 and missing_driver and not driver_present:
        return 'not implemented; visible import failure'
    return 'implementation tests failing; inspect log'

def main():
    repo=ROOT/'fullkit';report=ROOT/'reports';report.mkdir(exist_ok=True)
    results={}
    def run(name,args,cwd=repo,extra_env=None):
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        if extra_env:env.update(extra_env)
        try:
            p=subprocess.run(args,cwd=cwd,env=env,text=True,stdout=subprocess.PIPE,
                             stderr=subprocess.STDOUT,timeout=180)
        except subprocess.TimeoutExpired as exc:
            output=exc.stdout or ''
            if isinstance(output,bytes):output=output.decode('utf-8',errors='replace')
            p=subprocess.CompletedProcess(args,124,output+'\nCHECK TIMED OUT after 180 seconds\n')
        (report/(name+'.log')).write_text(p.stdout)
        results[name]={'exit_code':p.returncode,'log':name+'.log'}
        return p
    run('artifact-integrity',[sys.executable,str(ROOT/'scripts/verify_baseline.py')])
    with tempfile.TemporaryDirectory(prefix='fullkit-contract-check-') as td:
        copy=Path(td)/'contract'
        shutil.copytree(repo/'contract',copy,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
        run('schema-validation',[sys.executable,str(copy/'tools/validate_contract.py')])
        if (copy/'validation-schema.json').exists():
            shutil.copy2(copy/'validation-schema.json',report/'schema-validation.json')
    run('workspace-tests',[sys.executable,'-m','pytest',str(ROOT/'tests/workspace'),'-q','-p','no:cacheprovider'])
    run('inventory-tests',[sys.executable,'-m','pytest','tests/contract/test_inventory.py','-q','-p','no:cacheprovider'])
    integration=run('application-integration',[sys.executable,'-m','pytest','tests/contract/test_two_home.py','-q','-p','no:cacheprovider'])
    run('local-toolchain',[sys.executable,str(ROOT/'scripts/probe_toolchain.py')],extra_env={'QT_QPA_PLATFORM':'offscreen'})
    source=json.loads((report/'Source-Copy-Register.json').read_text());changed=[]
    for name,h in source['existing_root_files_preserved'].items():
        p=ROOT/name
        if not p.is_file() or hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(name)
    required=['artifact-integrity','schema-validation','workspace-tests','inventory-tests','local-toolchain']
    local_ok=all(results[n]['exit_code']==0 for n in required) and not changed
    status=application_state(repo,integration.returncode,integration.stdout)
    summary={'checked_at':datetime.now(timezone.utc).isoformat(),'workspace':str(ROOT),
             'python':platform.python_version(),'executable':sys.executable,'platform':platform.platform(),
             'sqlite':sqlite3.sqlite_version,'local_environment_ready':local_ok,'checks':results,
             'preexisting_files_changed':changed,'application_status':status,
             'application_release_qualified':False,'windows_qualified':False,
             'pending_contract_proposals':['artifact 1.00.1 C1','artifact 1.00.1 C2']}
    (report/'Environment-Validation.json').write_text(json.dumps(summary,indent=2)+'\n')
    print(json.dumps(summary,indent=2))
    return 0 if local_ok and status in {'not implemented; visible import failure','tests passed'} else 1
if __name__=='__main__':sys.exit(main())
