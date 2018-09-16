# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/unittest/__main__.py
import sys
if sys.argv[0].endswith('__main__.py'):
    sys.argv[0] = 'python -m unittest'
__unittest = True
from .main import main, TestProgram, USAGE_AS_MAIN
TestProgram.USAGE = USAGE_AS_MAIN
main(module=None)
