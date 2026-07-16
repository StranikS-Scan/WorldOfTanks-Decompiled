# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/WWISE.py
from __future__ import absolute_import, print_function
enabled = True
try:
    from _WWISE import *
    import _WWISE
except ImportError:
    print('WARNING: WWISE support is not enabled.')
    enabled = False
