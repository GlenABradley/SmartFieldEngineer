"""Recreate ignored host runtimes/dependencies from a clone; no system changes.
Run with any Python >=3.10: python scripts/bootstrap.py
Use --plan to inspect without downloading/installing.
"""
import argparse,json,os,platform,subprocess,sys,venv
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
TARGET='3.13.15'
def executable(home,name):return home/('Scripts' if os.name=='nt' else 'bin')/(name+('.exe' if os.name=='nt' else ''))
def select_lock():
 host=platform.system();arch=platform.machine().lower()
 if host=='Darwin' and arch in {'arm64','aarch64'}:return ROOT/'environment/requirements-macos-arm64.lock'
 if host=='Windows' and arch in {'amd64','x86_64'}:return ROOT/'fullkit/contract/requirements-windows.lock'
 raise SystemExit('No verified wheel lock for this host. Resolve and review a separate platform lock; do not reuse macOS/Windows wheel hashes.')
def main():
 p=argparse.ArgumentParser();p.add_argument('--plan',action='store_true');args=p.parse_args()
 if sys.version_info<(3,10):raise SystemExit('Bootstrap requires an existing Python 3.10 or newer.')
 lock=select_lock();boot=ROOT/'environment/bootstrap';runtime=ROOT/'environment/runtimes';target=ROOT/'fullkit/.venv'
 print(json.dumps({'target_python':TARGET,'wheel_lock':str(lock.relative_to(ROOT)),'runtime_directory':str(runtime),'venv':str(target),'changes_system_python':False},indent=2))
 if args.plan:return
 env=dict(os.environ,UV_PYTHON_INSTALL_DIR=str(runtime),UV_CACHE_DIR=str(ROOT/'environment/cache'))
 def run(argv):subprocess.run([str(a) for a in argv],cwd=ROOT,env=env,check=True)
 if not executable(boot,'python').exists():venv.EnvBuilder(with_pip=True).create(boot)
 run([executable(boot,'python'),'-m','pip','install','--require-hashes','-r',ROOT/'environment/bootstrap.lock'])
 uv=executable(boot,'uv')
 run([uv,'python','install',TARGET,'--install-dir',runtime,'--no-bin'])
 interpreter=Path(subprocess.check_output([str(uv),'python','find',TARGET,'--managed-python','--no-project','--no-python-downloads'],cwd=ROOT,env=env,text=True).strip())
 if not interpreter.resolve().is_relative_to(runtime.resolve()):raise SystemExit('Managed interpreter resolved outside this workspace; stopping.')
 py=executable(target,'python')
 if py.exists():
  version=subprocess.check_output([str(py),'-c','import platform;print(platform.python_version())'],text=True).strip()
  if version!=TARGET:raise SystemExit('Existing venv has another Python version. Preserve it and explicitly recreate it before continuing.')
 else:run([uv,'venv','--seed','--python',interpreter,target])
 (ROOT/'reports').mkdir(exist_ok=True)
 run([py,'-m','pip','install','--require-hashes','-r',lock,'--report',ROOT/'environment/local-install-report.json'])
 run([py,ROOT/'scripts/check_environment.py'])
if __name__=='__main__':main()
