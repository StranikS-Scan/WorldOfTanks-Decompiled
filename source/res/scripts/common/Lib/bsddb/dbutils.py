# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/bsddb/dbutils.py
from time import sleep as _sleep
import sys
absolute_import = sys.version_info[0] >= 3
if absolute_import:
    exec 'from . import db'
else:
    import db
_deadlock_MinSleepTime = 1.0 / 128
_deadlock_MaxSleepTime = 3.14159
_deadlock_VerboseFile = None

def DeadlockWrap(function, *_args, **_kwargs):
    sleeptime = _deadlock_MinSleepTime
    max_retries = _kwargs.get('max_retries', -1)
    if 'max_retries' in _kwargs:
        del _kwargs['max_retries']
    while True:
        try:
            return function(*_args, **_kwargs)
        except db.DBLockDeadlockError:
            if _deadlock_VerboseFile:
                _deadlock_VerboseFile.write('dbutils.DeadlockWrap: sleeping %1.3f\n' % sleeptime)
            _sleep(sleeptime)
            sleeptime *= 2
            if sleeptime > _deadlock_MaxSleepTime:
                sleeptime = _deadlock_MaxSleepTime
            max_retries -= 1
            if max_retries == -1:
                raise
