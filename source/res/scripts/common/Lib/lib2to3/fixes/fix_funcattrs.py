# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_funcattrs.py
"""Fix function attribute names (f.func_x -> f.__x__)."""
from .. import fixer_base
from ..fixer_util import Name

class FixFuncattrs(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "\n    power< any+ trailer< '.' attr=('func_closure' | 'func_doc' | 'func_globals'\n                                  | 'func_name' | 'func_defaults' | 'func_code'\n                                  | 'func_dict') > any* >\n    "

    def transform(self, node, results):
        attr = results['attr'][0]
        attr.replace(Name(u'__%s__' % attr.value[5:], prefix=attr.prefix))
