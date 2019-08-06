# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/festival/festival_rewards_renderer.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class FestivalRewardsRenderer(ViewModel):
    __slots__ = ()

    def getProgressLevel(self):
        return self._getString(0)

    def setProgressLevel(self, value):
        self._setString(0, value)

    def getIsAchieved(self):
        return self._getBool(1)

    def setIsAchieved(self, value):
        self._setBool(1, value)

    def getReachValue(self):
        return self._getNumber(2)

    def setReachValue(self, value):
        self._setNumber(2, value)

    def getItems(self):
        return self._getArray(3)

    def setItems(self, value):
        self._setArray(3, value)

    def _initialize(self):
        super(FestivalRewardsRenderer, self)._initialize()
        self._addStringProperty('progressLevel', '')
        self._addBoolProperty('isAchieved', False)
        self._addNumberProperty('reachValue', 0)
        self._addArrayProperty('items', Array())
