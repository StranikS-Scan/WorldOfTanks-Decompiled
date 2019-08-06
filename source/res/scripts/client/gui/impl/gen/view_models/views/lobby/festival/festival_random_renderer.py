# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_random_renderer.py
from frameworks.wulf import ViewModel

class FestivalRandomRenderer(ViewModel):
    __slots__ = ()

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getCost(self):
        return self._getNumber(1)

    def setCost(self, value):
        self._setNumber(1, value)

    def getReceivedCount(self):
        return self._getNumber(2)

    def setReceivedCount(self, value):
        self._setNumber(2, value)

    def getTotalCount(self):
        return self._getNumber(3)

    def setTotalCount(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(FestivalRandomRenderer, self)._initialize()
        self._addStringProperty('name', '')
        self._addNumberProperty('cost', 0)
        self._addNumberProperty('receivedCount', 0)
        self._addNumberProperty('totalCount', 0)
