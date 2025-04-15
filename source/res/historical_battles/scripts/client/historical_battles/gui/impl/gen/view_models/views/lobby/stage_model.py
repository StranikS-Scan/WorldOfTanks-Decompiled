# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/stage_model.py
from frameworks.wulf import ViewModel

class StageModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(StageModel, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getTotalLevel(self):
        return self._getNumber(1)

    def setTotalLevel(self, value):
        self._setNumber(1, value)

    def getCurrentLevelProgress(self):
        return self._getNumber(2)

    def setCurrentLevelProgress(self, value):
        self._setNumber(2, value)

    def getTotalLevelProgress(self):
        return self._getNumber(3)

    def setTotalLevelProgress(self, value):
        self._setNumber(3, value)

    def getFrontType(self):
        return self._getString(4)

    def setFrontType(self, value):
        self._setString(4, value)

    def getDate(self):
        return self._getNumber(5)

    def setDate(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(StageModel, self)._initialize()
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('totalLevel', 0)
        self._addNumberProperty('currentLevelProgress', 0)
        self._addNumberProperty('totalLevelProgress', 0)
        self._addStringProperty('frontType', '')
        self._addNumberProperty('date', 0)
