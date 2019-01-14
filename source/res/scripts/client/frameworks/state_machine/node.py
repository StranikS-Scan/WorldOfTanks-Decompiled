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
