# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/compiler/syntax.py
from compiler import ast, walk

def check(tree, multi=None):
    v = SyntaxErrorChecker(multi)
    walk(tree, v)
    return v.errors


class SyntaxErrorChecker:

    def __init__(self, multi=None):
        self.multi = multi
        self.errors = 0

    def error(self, node, msg):
        self.errors = self.errors + 1
        if self.multi is not None:
            print '%s:%s: %s' % (node.filename, node.lineno, msg)
        else:
            raise SyntaxError, '%s (%s:%s)' % (msg, node.filename, node.lineno)
        return

    def visitAssign(self, node):
        pass
