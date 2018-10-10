# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_apply.py
from .. import pytree
from ..pgen2 import token
from .. import fixer_base
from ..fixer_util import Call, Comma, parenthesize

class FixApply(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "\n    power< 'apply'\n        trailer<\n            '('\n            arglist<\n                (not argument<NAME '=' any>) func=any ','\n                (not argument<NAME '=' any>) args=any [','\n                (not argument<NAME '=' any>) kwds=any] [',']\n            >\n            ')'\n        >\n    >\n    "

    def transform(self, node, results):
        syms = self.syms
        func = results['func']
        args = results['args']
        kwds = results.get('kwds')
        prefix = node.prefix
        func = func.clone()
        if func.type not in (token.NAME, syms.atom) and (func.type != syms.power or func.children[-2].type == token.DOUBLESTAR):
            func = parenthesize(func)
        func.prefix = ''
        args = args.clone()
        args.prefix = ''
        if kwds is not None:
            kwds = kwds.clone()
            kwds.prefix = ''
        l_newargs = [pytree.Leaf(token.STAR, u'*'), args]
        if kwds is not None:
            l_newargs.extend([Comma(), pytree.Leaf(token.DOUBLESTAR, u'**'), kwds])
            l_newargs[-2].prefix = u' '
        return Call(func, l_newargs, prefix=prefix)
