# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/frameworks/state_machine/node.py
import weakref
from .exceptions import NodeError

class Node(object):
    __counter = 0
    __slots__ = ('__weakref__', '__id', '__parent', '__children')

    def __init__(self):
        super(Node, self).__init__()
        self.__id = self.__genID()
        self.__parent = lambda : None
        self.__children = []

    def __repr__(self):
        return '{}(id={})'.format(self.__class__.__name__, self.__id)

    def clear(self):
        self.__parent = lambda : None
        while self.__children:
            children = self.__children.pop()
            children.clear()

    def getNodeID(self):
        return self.__id

    def getParent(self):
        return self.__parent()

    def getChildren(self, filter_=None):
        return filter(filter_, self.__children)

    def getChildByIndex(self, index):
        return self.__children[index] if 0 <= index < len(self.__children) else None

    def addChild(self, child):
        self._addChild(child)

    def removeChild(self, child):
        self._removeChild(child)

    def visitInOrder(self, filter_=None):
        yield self
        for child in self.getChildren(filter_=filter_):
            for item in child.visitInOrder(filter_=filter_):
                yield item

    def _addChild(self, child):
        if child is None:
            raise NodeError('Child is not defined')
        if not isinstance(child, Node):
            raise NodeError('Child must extend Node class')
        if child.getParent() is not None:
            raise NodeError('Parent is already added')
        child.__parent = weakref.ref(self)
        if child not in self.__children:
            self.__children.append(child)
        return

    def _removeChild(self, child):
        if child is None:
            raise NodeError('Child is not defined')
        if not isinstance(child, Node):
            raise NodeError('Child must extend Node class')
        if child in self.__children:
            self.__children.remove(child)
            child.clear()
        return

    @classmethod
    def __genID(cls):
        cls.__counter += 1
        return cls.__counter


class NodesVisitor(object):
    __slots__ = ()

    @classmethod
    def getAncestors(cls, node, upper=None):
        if not isinstance(node, Node):
            raise NodeError('Invalid argument "node" = {}'.format(node))
        if upper is not None and not isinstance(upper, Node):
            raise NodeError('Invalid argument "upper" = {}'.format(upper))
        result = []
        found = node.getParent()
        while found != upper and found is not None:
            result.append(found)
            found = found.getParent()

        return result

    @classmethod
    def isDescendantOf(cls, node, ancestor):
        if not isinstance(node, Node):
            raise NodeError('Invalid argument "node" = {}'.format(node))
        if not isinstance(ancestor, Node):
            raise NodeError('Invalid argument "ancestor" = {}'.format(ancestor))
        found = node.getParent()
        while found is not None:
            if found == ancestor:
                return True
            found = found.getParent()

        return False

    @classmethod
    def getDescendantIndex(cls, node, ancestor, filter_=None):
        children = ancestor.getChildren(filter_=filter_)
        for index, child in enumerate(children):
            if child == node or cls.isDescendantOf(node, child):
                return index

    @classmethod
    def getLCA(cls, nodes, upper=None):
        if not nodes:
            return None
        else:
            ancestors = cls.getAncestors(nodes[0], upper=upper)
            others = nodes[1:]
            others.reverse()
            while ancestors:
                ancestor = ancestors.pop(0)
                found = False
                for state in others:
                    if cls.isDescendantOf(state, ancestor):
                        found = True

                if found:
                    return ancestor

            return None
