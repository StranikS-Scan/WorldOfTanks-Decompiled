# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_buffer.py
from .. import fixer_base
from ..fixer_util import Name

class FixBuffer(fixer_base.BaseFix):
    BM_compatible = True
    explicit = True
    PATTERN = "\n              power< name='buffer' trailer< '(' [any] ')' > any* >\n              "

    def transform(self, node, results):
        name = results['name']
        name.replace(Name(u'memoryview', prefix=name.prefix))
