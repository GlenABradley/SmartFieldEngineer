"""Disposable Qt/QProcess and SQLite toolkit probes, not Full Kit application tests."""
import json,sqlite3,sys,tempfile
from pathlib import Path
from importlib.metadata import version
from PySide6.QtCore import QProcess,qVersion
from PySide6.QtWidgets import QApplication
app=QApplication([])
p=QProcess();p.start(sys.executable,['-c','print("qprocess-toolchain-ok")'])
assert p.waitForStarted(10000) and p.waitForFinished(10000)
assert p.exitCode()==0 and bytes(p.readAllStandardOutput()).strip()==b'qprocess-toolchain-ok'
with tempfile.TemporaryDirectory() as td:
 src=sqlite3.connect(Path(td)/'source.sqlite');src.execute('PRAGMA journal_mode=WAL');src.execute('PRAGMA wal_autocheckpoint=0');src.execute('CREATE TABLE probe(value INTEGER)');src.execute('INSERT INTO probe VALUES(17)');src.commit()
 assert (Path(td)/'source.sqlite-wal').stat().st_size>0
 target=sqlite3.connect(Path(td)/'snapshot.sqlite');src.backup(target);target.close()
 with sqlite3.connect(Path(td)/'snapshot.sqlite') as check:
  assert check.execute('PRAGMA integrity_check').fetchone()[0]=='ok'
  assert check.execute('SELECT value FROM probe').fetchone()[0]==17
 src.close()
print(json.dumps({'python':sys.version.split()[0],'qt':qVersion(),'pyside6':version('PySide6'),'jsonschema':version('jsonschema'),'pytest':version('pytest'),'sqlite':sqlite3.sqlite_version,'qt_offscreen_qprocess_probe':'passed','sqlite_backup_api_probe':'passed','fullkit_application_test':False,'windows_qualification':False},indent=2))
