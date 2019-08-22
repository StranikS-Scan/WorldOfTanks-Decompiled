# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/battle_royale_summary_results_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class BattleRoyaleSummaryResultsViewModel(ViewModel):
    __slots__ = ('onShowHangarBtnClick', 'onTabBarAnimComplete')

    def getIsMovingTextEnabled(self):
        return self._getBool(0)

    def setIsMovingTextEnabled(self, value):
        self._setBool(0, value)

    def getInSquad(self):
        return self._getBool(1)

    def setInSquad(self, value):
        self._setBool(1, value)

    def getIsWinner(self):
        return self._getBool(2)

    def setIsWinner(self, value):
        self._setBool(2, value)

    def getIsBattleFinished(self):
        return self._getBool(3)

    def setIsBattleFinished(self, value):
        self._setBool(3, value)

    def getRewardsList(self):
        return self._getArray(4)

    def setRewardsList(self, value):
        self._setArray(4, value)

    def getNamesList(self):
        return self._getArray(5)

    def setNamesList(self, value):
        self._setArray(5, value)

    def getStatsList(self):
        return self._getArray(6)

    def setStatsList(self, value):
        self._setArray(6, value)

    def getChevronsDiff(self):
        return self._getNumber(7)

    def setChevronsDiff(self, value):
        self._setNumber(7, value)

    def getChevronsDiffTrigger(self):
        return self._getBool(8)

    def setChevronsDiffTrigger(self, value):
        self._setBool(8, value)

    def getIsBattleState(self):
        return self._getBool(9)

    def setIsBattleState(self, value):
        self._setBool(9, value)

    def getIsAnimCanceled(self):
        return self._getBool(10)

    def setIsAnimCanceled(self, value):
        self._setBool(10, value)

    def getIsAnimInProgress(self):
        return self._getBool(11)

    def setIsAnimInProgress(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(BattleRoyaleSummaryResultsViewModel, self)._initialize()
        self._addBoolProperty('isMovingTextEnabled', False)
        self._addBoolProperty('inSquad', False)
        self._addBoolProperty('isWinner', False)
        self._addBoolProperty('isBattleFinished', True)
        self._addArrayProperty('rewardsList', Array())
        self._addArrayProperty('namesList', Array())
        self._addArrayProperty('statsList', Array())
        self._addNumberProperty('chevronsDiff', 0)
        self._addBoolProperty('chevronsDiffTrigger', False)
        self._addBoolProperty('isBattleState', False)
        self._addBoolProperty('isAnimCanceled', False)
        self._addBoolProperty('isAnimInProgress', True)
        self.onShowHangarBtnClick = self._addCommand('onShowHangarBtnClick')
        self.onTabBarAnimComplete = self._addCommand('onTabBarAnimComplete')
