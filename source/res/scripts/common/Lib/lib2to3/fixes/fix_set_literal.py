# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_set_literal.py
"""
Optional fixer to transform set() calls to set literals.
"""
from lib2to3 import fixer_base, pytree
from lib2to3.fixer_util import token, syms

class FixSetLiteral(fixer_base.BaseFix):
    BM_compatible = True
    explicit = True
    PATTERN = "power< 'set' trailer< '('\n                     (atom=atom< '[' (items=listmaker< any ((',' any)* [',']) >\n                                |\n                                single=any) ']' >\n                     |\n                     atom< '(' items=testlist_gexp< any ((',' any)* [',']) > ')' >\n                     )\n                     ')' > >\n              "

    def transform(self, node, results):
        single = results.get('single')
        if single:
            fake = pytree.Node(syms.listmaker, [single.clone()])
            single.replace(fake)
            items = fake
        else:
            items = results['items']
        literal = [pytree.Leaf(token.LBRACE, u'{')]
        literal.extend((n.clone() for n in items.children))
        literal.append(pytree.Leaf(token.RBRACE, u'}'))
        literal[-1].prefix = items.next_sibling.prefix
        maker = pytree.Node(syms.dictsetmaker, literal)
        maker.prefix = node.prefix
        if len(maker.children) == 4:
            n = maker.children[2]
            n.remove()
            maker.children[-1].prefix = n.prefix
        return maker
