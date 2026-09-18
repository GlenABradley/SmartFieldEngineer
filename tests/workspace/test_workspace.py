"""Tests of the workbench itself; never substitutes for application acceptance."""
import ast,hashlib,importlib.util,json,re,shutil,subprocess,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[2]
def load(name):
    spec=importlib.util.spec_from_file_location('workspace_'+name,ROOT/'scripts'/f'{name}.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module);return module
check=load('check_environment');bootstrap=load('bootstrap')

@pytest.mark.parametrize('missing',['packages','packages.application','packages.application.testing'])
def test_absent_application_driver_is_reported_not_implemented(tmp_path,missing):
    output=f"ModuleNotFoundError: No module named '{missing}'"
    assert check.application_state(tmp_path,2,output)=='integration driver absent; visible import failure'

def test_partial_implementation_error_is_not_mislabeled(tmp_path):
    d=tmp_path/'packages/application';d.mkdir(parents=True);(d/'testing.py').write_text('')
    assert check.application_state(tmp_path,2,"ModuleNotFoundError: No module named 'packages'")=='implementation tests failing; inspect log'

@pytest.mark.parametrize('exit_code,message',[(2,"ModuleNotFoundError: No module named 'packages.domain.identity'"),(2,'SyntaxError: broken file'),(124,'timed out'),(1,'assertion failed')])
def test_other_failures_are_not_expected_absence(tmp_path,exit_code,message):
    assert check.application_state(tmp_path,exit_code,message)=='implementation tests failing; inspect log'

def test_only_zero_exit_means_tests_passed(tmp_path):
    assert check.application_state(tmp_path,0,'')=='tests passed'

def test_platform_locks_are_explicit():
    assert bootstrap.select_lock('Darwin','arm64').is_file()
    assert bootstrap.select_lock('Windows','AMD64').is_file()
    with pytest.raises(SystemExit,match='No verified wheel lock'):bootstrap.select_lock('Linux','x86_64')

def test_venv_cannot_silently_point_to_another_checkout(tmp_path):
    target=tmp_path/'fullkit/.venv';runtime=tmp_path/'environment/runtimes'
    good={'version':'3.13.15','prefix':str(target),'base_prefix':str(runtime/'cpython')}
    bootstrap.validate_existing_venv(good,target,runtime)
    for field,value in [('version','3.12.0'),('prefix',str(tmp_path/'another-venv')),('base_prefix','/other/checkout/python')]:
        with pytest.raises(ValueError):bootstrap.validate_existing_venv(dict(good,**{field:value}),target,runtime)

def test_new_navigation_links_resolve():
    for relative in ['.github/README.md','START-HERE.md']:
        source=ROOT/relative
        for destination in re.findall(r'\]\(([^)]+)\)',source.read_text()):
            if '://' in destination or destination.startswith('#'):continue
            target=(source.parent/destination.split('#')[0]).resolve()
            assert target.is_relative_to(ROOT),destination
            assert target.exists(),f'{relative}: {destination}'

def test_reviewed_contract_bytes_are_intact():
    p=subprocess.run([sys.executable,str(ROOT/'scripts/verify_baseline.py')],capture_output=True,text=True)
    assert p.returncode==0,p.stdout+p.stderr
    assert json.loads(p.stdout)['mismatches']==[]

def test_baseline_checker_detects_substantive_tampering(tmp_path):
    (tmp_path/'scripts').mkdir();contract=tmp_path/'fullkit/contract';contract.mkdir(parents=True)
    shutil.copy2(ROOT/'scripts/verify_baseline.py',tmp_path/'scripts/verify_baseline.py')
    expected=b'original reviewed bytes'
    (contract/'sample.json').write_bytes(expected)
    (contract/'Manifest.json').write_text(json.dumps({'files':{'sample.json':{'sha256':hashlib.sha256(expected).hexdigest()},'.DS_Store':{'sha256':'0'*64}}}))
    command=[sys.executable,str(tmp_path/'scripts/verify_baseline.py')]
    assert subprocess.run(command,capture_output=True).returncode==0
    (contract/'sample.json').write_bytes(b'changed')
    result=subprocess.run(command,capture_output=True,text=True)
    assert result.returncode==1
    assert json.loads(result.stdout)['mismatches']==['sample.json']

def test_acceptance_assertions_match_preserved_contract():
    # The working copies have a reviewed portable path locator; domain assertions stay identical.
    for name in ['test_inventory.py','test_two_home.py']:
        baseline=ast.parse((ROOT/'fullkit/contract/tests'/name).read_text())
        working=ast.parse((ROOT/'fullkit/tests/contract'/name).read_text())
        assertions=lambda tree:[ast.dump(n,include_attributes=False) for n in ast.walk(tree) if isinstance(n,ast.Assert)]
        tests=lambda tree:sorted(n.name for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name.startswith('test_'))
        assert assertions(working)==assertions(baseline), 'Assertion changes need explicit contract review.'
        assert tests(working)==tests(baseline)
