# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_xreadlines.py
from .. import fixer_base
from ..fixer_util import Name

class FixXreadlines(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "\n    power< call=any+ trailer< '.' 'xreadlines' > trailer< '(' ')' > >\n    |\n    power< any+ trailer< '.' no_call='xreadlines' > >\n    "

    def transform(self, node, results):
        no_call = results.get('no_call')
        if no_call:
            no_call.replace(Name(u'__iter__', prefix=no_call.prefix))
        else:
            node.replace([ x.clone() for x in results['call'] ])
