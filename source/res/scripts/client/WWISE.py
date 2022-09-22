# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/WWISE.py
# Compiled at: 2002-05-16 11:38:43
enabled = True
try:
    from _WWISE import *
    import _WWISE
except ImportError:
    print 'WARNING: WWISE support is not enabled.'
    enabled = False
