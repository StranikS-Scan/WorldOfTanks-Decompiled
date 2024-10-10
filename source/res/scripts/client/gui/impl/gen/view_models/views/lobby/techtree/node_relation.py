# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/techtree/node_relation.py
from enum import IntEnum
from frameworks.wulf import ViewModel

class LineType(IntEnum):
    HORIZONTAL = 0
    VERTICAL = 1
    H_V = 2


class NodeRelation(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(NodeRelation, self).__init__(properties=properties, commands=commands)

    def getNodeInId(self):
        return self._getNumber(0)

    def setNodeInId(self, value):
        self._setNumber(0, value)

    def getNodeOutId(self):
        return self._getNumber(1)

    def setNodeOutId(self, value):
        self._setNumber(1, value)

    def getLineType(self):
        return LineType(self._getNumber(2))

    def setLineType(self, value):
        self._setNumber(2, value.value)

    def _initialize(self):
        super(NodeRelation, self)._initialize()
        self._addNumberProperty('nodeInId', 0)
        self._addNumberProperty('nodeOutId', 0)
        self._addNumberProperty('lineType')
