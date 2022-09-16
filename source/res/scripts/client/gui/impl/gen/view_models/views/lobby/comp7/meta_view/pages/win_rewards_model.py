# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/comp7/meta_view/pages/win_rewards_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.comp7.comp7_bonus_model import Comp7BonusModel

class WinRewardsModel(ViewModel):
    __slots__ = ('onSetActiveProgressPoint', 'onAnimationStart', 'onAnimationEnd')

    def __init__(self, properties=7, commands=3):
        super(WinRewardsModel, self).__init__(properties=properties, commands=commands)

    def getIsCurrentValueLimitExceeded(self):
        return self._getBool(0)

    def setIsCurrentValueLimitExceeded(self, value):
        self._setBool(0, value)

    def getCurrentValue(self):
        return self._getNumber(1)

    def setCurrentValue(self, value):
        self._setNumber(1, value)

    def getPreviousValue(self):
        return self._getNumber(2)

    def setPreviousValue(self, value):
        self._setNumber(2, value)

    def getActiveProgressPoint(self):
        return self._getNumber(3)

    def setActiveProgressPoint(self, value):
        self._setNumber(3, value)

    def getNextProgressPoint(self):
        return self._getNumber(4)

    def setNextProgressPoint(self, value):
        self._setNumber(4, value)

    def getProgressPoints(self):
        return self._getArray(5)

    def setProgressPoints(self, value):
        self._setArray(5, value)

    @staticmethod
    def getProgressPointsType():
        return int

    def getRewards(self):
        return self._getArray(6)

    def setRewards(self, value):
        self._setArray(6, value)

    @staticmethod
    def getRewardsType():
        return Comp7BonusModel

    def _initialize(self):
        super(WinRewardsModel, self)._initialize()
        self._addBoolProperty('isCurrentValueLimitExceeded', False)
        self._addNumberProperty('currentValue', 0)
        self._addNumberProperty('previousValue', 0)
        self._addNumberProperty('activeProgressPoint', 0)
        self._addNumberProperty('nextProgressPoint', 0)
        self._addArrayProperty('progressPoints', Array())
        self._addArrayProperty('rewards', Array())
        self.onSetActiveProgressPoint = self._addCommand('onSetActiveProgressPoint')
        self.onAnimationStart = self._addCommand('onAnimationStart')
        self.onAnimationEnd = self._addCommand('onAnimationEnd')
