# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/disjoint_set.py
from __future__ import absolute_import
import logging
import typing
from future.utils import viewvalues
if typing.TYPE_CHECKING:
    from typing import Any, Iterable
_logger = logging.getLogger(__name__)

class DisjointSet(object):

    def __init__(self):
        super(DisjointSet, self).__init__()
        self._root = {}
        self._set = {}

    def __contains__(self, item):
        return item in self._root

    def __len__(self):
        return len(self._root)

    @property
    def subsets(self):
        return iter(viewvalues(self._set))

    @property
    def nsubsets(self):
        return len(self._set)

    @classmethod
    def fromIterables(cls, iterables):
        res = cls()
        for iterable in iterables:
            try:
                root = next((i for i in iterable))
            except StopIteration:
                continue

            for element in iterable:
                res.add(element)
                root = res.union(root, element)

        return res

    def add(self, element):
        if element in self._root:
            _logger.warning('trying to add already existing element to disjoint set %s', element)
            return
        self._root[element] = element
        self._set[element] = {element}

    def clear(self):
        self._root.clear()
        self._set.clear()

    def getRoot(self, element):
        return self._root.get(element)

    def getSubset(self, element):
        root = self.getRoot(element)
        return self._set[root] if root is not None else None

    def inSameSubset(self, elementA, elementB):
        return elementA in self._root and self.getRoot(elementA) == self.getRoot(elementB)

    def union(self, elementA, elementB):
        rootA = self.getRoot(elementA)
        if rootA is None:
            return
        else:
            rootB = self.getRoot(elementB)
            if rootB is None:
                return
            if rootA == rootB:
                return rootA
            if len(self._set[rootA]) < len(self._set[rootB]):
                rootA, rootB = rootB, rootA
            setB = self._set.pop(rootB)
            for element in setB:
                self._root[element] = rootA

            self._set[rootA].update(setB)
            return rootA
