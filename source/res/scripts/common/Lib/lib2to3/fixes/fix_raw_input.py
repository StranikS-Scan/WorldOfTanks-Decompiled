# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_raw_input.py
"""Fixer that changes raw_input(...) into input(...)."""
from .. import fixer_base
from ..fixer_util import Name

class FixRawInput(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "\n              power< name='raw_input' trailer< '(' [any] ')' > any* >\n              "

    def transform(self, node, results):
        name = results['name']
        name.replace(Name(u'input', prefix=name.prefix))
