# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/dbhash.py
# Compiled at: 2010-05-25 20:46:16
"""Provide a (g)dbm-compatible interface to bsddb.hashopen."""
import sys
if sys.py3kwarning:
    import warnings
    warnings.warnpy3k('in 3.x, dbhash has been removed', DeprecationWarning, 2)
try:
    import bsddb
except ImportError:
    del sys.modules[__name__]
    raise

__all__ = ['error', 'open']
error = bsddb.error

def open(file, flag='r', mode=438):
    return bsddb.hashopen(file, flag, mode)
