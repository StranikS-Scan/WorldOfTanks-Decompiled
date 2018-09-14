# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_imports2.py
"""Fix incompatible imports and module references that must be fixed after
fix_imports."""
from . import fix_imports
MAPPING = {'whichdb': 'dbm',
 'anydbm': 'dbm'}

class FixImports2(fix_imports.FixImports):
    run_order = 7
    mapping = MAPPING
