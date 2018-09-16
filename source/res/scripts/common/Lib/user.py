# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/user.py
from warnings import warnpy3k
warnpy3k('the user module has been removed in Python 3.0', stacklevel=2)
del warnpy3k
import os
home = os.curdir
if 'HOME' in os.environ:
    home = os.environ['HOME']
elif os.name == 'posix':
    home = os.path.expanduser('~/')
elif os.name == 'nt':
    if 'HOMEPATH' in os.environ:
        if 'HOMEDRIVE' in os.environ:
            home = os.environ['HOMEDRIVE'] + os.environ['HOMEPATH']
        else:
            home = os.environ['HOMEPATH']
pythonrc = os.path.join(home, '.pythonrc.py')
try:
    f = open(pythonrc)
except IOError:
    pass
else:
    f.close()
    execfile(pythonrc)
