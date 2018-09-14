# Python 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/lib2to3/fixes/fix_isinstance.py
"""Fixer that cleans up a tuple argument to isinstance after the tokens
in it were fixed.  This is mainly used to remove double occurrences of
tokens as a leftover of the long -> int / unicode -> str conversion.

eg.  isinstance(x, (int, long)) -> isinstance(x, (int, int))
       -> isinstance(x, int)
"""
from .. import fixer_base
from ..fixer_util import token

class FixIsinstance(fixer_base.BaseFix):
    BM_compatible = True
    PATTERN = "\n    power<\n        'isinstance'\n        trailer< '(' arglist< any ',' atom< '('\n            args=testlist_gexp< any+ >\n        ')' > > ')' >\n    >\n    "
    run_order = 6

    def transform(self, node, results):
        names_inserted = set()
        testlist = results['args']
        args = testlist.children
        new_args = []
        iterator = enumerate(args)
        for idx, arg in iterator:
            if arg.type == token.NAME and arg.value in names_inserted:
                if idx < len(args) - 1 and args[idx + 1].type == token.COMMA:
                    iterator.next()
                    continue
            else:
                new_args.append(arg)
                if arg.type == token.NAME:
                    names_inserted.add(arg.value)

        if new_args and new_args[-1].type == token.COMMA:
            del new_args[-1]
        if len(new_args) == 1:
            atom = testlist.parent
            new_args[0].prefix = atom.prefix
            atom.replace(new_args[0])
        else:
            args[:] = new_args
            node.changed()
