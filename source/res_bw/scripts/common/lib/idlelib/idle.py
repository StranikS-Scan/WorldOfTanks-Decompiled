# Embedded file name: scripts/common/Lib/idlelib/idle.py
import os.path
import sys
idlelib_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, idlelib_dir)
import idlelib.PyShell
idlelib.PyShell.main()
