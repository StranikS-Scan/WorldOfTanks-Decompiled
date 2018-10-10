# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_standarderror.py
from .. import fixer_base
from ..fixer_util import Name

class FixStandarderror(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "\n              'StandardError'\n              "

    def transform(self, node, results):
        return Name(u'Exception', prefix=node.prefix)
