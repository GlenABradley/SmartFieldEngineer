"""Target commissioning probe. Reports observations; does not certify Windows or encrypt disks."""
import json,platform,sqlite3,sys
r={'python':platform.python_version(),'platform':platform.platform(),'architecture':platform.machine(),'sqlite':sqlite3.sqlite_version,'sqlite_source_id':sqlite3.connect(':memory:').execute('SELECT sqlite_source_id()').fetchone()[0],'encrypted_volume':'unknown','qualification':'not performed'}
errors=[]
if sys.version_info[:3]!=(3,13,15):errors.append('Selected CPython baseline is 3.13.15; document/review any substitution')
v=sqlite3.sqlite_version_info
if not (v==(3,51,3) or v>=(3,53,0)):errors.append('SQLite runtime outside selected patched branches; review exact source/build')
try:
 import PySide6
 from PySide6.QtCore import qVersion
 r['pyside']=PySide6.__version__;r['qt']=qVersion()
 if PySide6.__version__!='6.11.2':errors.append('PySide6 baseline mismatch')
except ImportError:errors.append('PySide6 is not installed')
if platform.system()!='Windows':errors.append('Not a Windows commissioning host')
r['checks_requiring_windows_execution']=['ACL inheritance and explicit grants','exclusive lock handle identity','junction/subst aliases','readiness observation','offline Qt rendering','WAL backup/inactive restore','clean install/reinstall']
r['errors']=errors
print(json.dumps(r,indent=2));sys.exit(bool(errors))
