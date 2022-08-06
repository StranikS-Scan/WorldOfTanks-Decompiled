# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/idlelib/idle.py
import os.path
import sys
idlelib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if idlelib_dir not in sys.path:
    sys.path.insert(0, idlelib_dir)
from idlelib.PyShell import main
main()
