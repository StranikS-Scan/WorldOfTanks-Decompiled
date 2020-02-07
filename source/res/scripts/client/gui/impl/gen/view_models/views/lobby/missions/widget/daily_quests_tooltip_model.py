# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/missions/widget/daily_quests_tooltip_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class DailyQuestsTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=8, commands=0):
        super(DailyQuestsTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIcon(self):
        return self._getString(0)

    def setIcon(self, value):
        self._setString(0, value)

    def getIsCompleted(self):
        return self._getBool(1)

    def setIsCompleted(self, value):
        self._setBool(1, value)

    def getCurrentProgress(self):
        return self._getNumber(2)

    def setCurrentProgress(self, value):
        self._setNumber(2, value)

    def getTotalProgress(self):
        return self._getNumber(3)

    def setTotalProgress(self, value):
        self._setNumber(3, value)

    def getDescription(self):
        return self._getString(4)

    def setDescription(self, value):
        self._setString(4, value)

    def getReward1(self):
        return self._getResource(5)

    def setReward1(self, value):
        self._setResource(5, value)

    def getReward2(self):
        return self._getResource(6)

    def setReward2(self, value):
        self._setResource(6, value)

    def getReward3(self):
        return self._getResource(7)

    def setReward3(self, value):
        self._setResource(7, value)

    def _initialize(self):
        super(DailyQuestsTooltipModel, self)._initialize()
        self._addStringProperty('icon', '')
        self._addBoolProperty('isCompleted', False)
        self._addNumberProperty('currentProgress', 0)
        self._addNumberProperty('totalProgress', 0)
        self._addStringProperty('description', '')
        self._addResourceProperty('reward1', R.invalid())
        self._addResourceProperty('reward2', R.invalid())
        self._addResourceProperty('reward3', R.invalid())
