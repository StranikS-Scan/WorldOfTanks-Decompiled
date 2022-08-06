# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idlever.py
import warnings as w
w.warn(__doc__, DeprecationWarning, stacklevel=2)
from sys import version
IDLE_VERSION = version[:version.index(' ')]
