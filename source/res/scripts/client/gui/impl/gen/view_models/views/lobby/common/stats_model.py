# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/stats_model.py
from frameworks.wulf import ViewModel

class StatsModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(StatsModel, self).__init__(properties=properties, commands=commands)

    def getCredits(self):
        return self._getNumber(0)

    def setCredits(self, value):
        self._setNumber(0, value)

    def getGold(self):
        return self._getNumber(1)

    def setGold(self, value):
        self._setNumber(1, value)

    def getCrystal(self):
        return self._getNumber(2)

    def setCrystal(self, value):
        self._setNumber(2, value)

    def getFreeXP(self):
        return self._getNumber(3)

    def setFreeXP(self, value):
        self._setNumber(3, value)

    def getExchangeRate(self):
        return self._getNumber(4)

    def setExchangeRate(self, value):
        self._setNumber(4, value)

    def _initialize(self):
        super(StatsModel, self)._initialize()
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('gold', 0)
        self._addNumberProperty('crystal', 0)
        self._addNumberProperty('freeXP', 0)
        self._addNumberProperty('exchangeRate', 0)
