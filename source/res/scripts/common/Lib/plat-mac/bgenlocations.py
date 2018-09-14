# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/plat-mac/bgenlocations.py
import os
from warnings import warnpy3k
warnpy3k('In 3.x, the bgenlocations module is removed.', stacklevel=2)
Error = 'bgenlocations.Error'
BGENDIR = '/Users/jack/src/python/Tools/bgen/bgen'
INCLUDEDIR = '/Users/jack/src/Universal/Interfaces/CIncludes'
TOOLBOXDIR = '/Users/jack/src/python/Lib/plat-mac/Carbon'
CREATOR = 'CWIE'
try:
    from bgenlocationscustomize import *
except ImportError:
    pass

if not os.path.exists(BGENDIR):
    raise Error, 'Please fix bgenlocations.py, BGENDIR does not exist: %s' % BGENDIR
if not os.path.exists(INCLUDEDIR):
    raise Error, 'Please fix bgenlocations.py, INCLUDEDIR does not exist: %s' % INCLUDEDIR
if not os.path.exists(TOOLBOXDIR):
    raise Error, 'Please fix bgenlocations.py, TOOLBOXDIR does not exist: %s' % TOOLBOXDIR
if BGENDIR[-1] != os.sep:
    BGENDIR = BGENDIR + os.sep
if INCLUDEDIR[-1] != os.sep:
    INCLUDEDIR = INCLUDEDIR + os.sep
if TOOLBOXDIR[-1] != os.sep:
    TOOLBOXDIR = TOOLBOXDIR + os.sep
