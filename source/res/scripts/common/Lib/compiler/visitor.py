# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/Lib/compiler/visitor.py
from compiler import ast

class ASTVisitor:
    VERBOSE = 0

    def __init__(self):
        self.node = None
        self._cache = {}
        return

    def default(self, node, *args):
        for child in node.getChildNodes():
            self.dispatch(child, *args)

    def dispatch(self, node, *args):
        self.node = node
        klass = node.__class__
        meth = self._cache.get(klass, None)
        if meth is None:
            className = klass.__name__
            meth = getattr(self.visitor, 'visit' + className, self.default)
            self._cache[klass] = meth
        return meth(node, *args)

    def preorder(self, tree, visitor, *args):
        self.visitor = visitor
        visitor.visit = self.dispatch
        self.dispatch(tree, *args)


class ExampleASTVisitor(ASTVisitor):
    examples = {}

    def dispatch(self, node, *args):
        self.node = node
        meth = self._cache.get(node.__class__, None)
        className = node.__class__.__name__
        if meth is None:
            meth = getattr(self.visitor, 'visit' + className, 0)
            self._cache[node.__class__] = meth
        if self.VERBOSE > 1:
            print 'dispatch', className, meth and meth.__name__ or ''
        if meth:
            meth(node, *args)
        elif self.VERBOSE > 0:
            klass = node.__class__
            if klass not in self.examples:
                self.examples[klass] = klass
                print
                print self.visitor
                print klass
                for attr in dir(node):
                    if attr[0] != '_':
                        print '\t', '%-12.12s' % attr, getattr(node, attr)

                print
            return self.default(node, *args)
        return


_walker = ASTVisitor

def walk(tree, visitor, walker=None, verbose=None):
    if walker is None:
        walker = _walker()
    if verbose is not None:
        walker.VERBOSE = verbose
    walker.preorder(tree, visitor)
    return walker.visitor


def dumpNode(node):
    print node.__class__
    for attr in dir(node):
        if attr[0] != '_':
            print '\t', '%-10.10s' % attr, getattr(node, attr)
