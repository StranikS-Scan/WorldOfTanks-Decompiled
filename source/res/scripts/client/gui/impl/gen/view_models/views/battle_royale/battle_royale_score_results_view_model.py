# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle_royale/battle_royale_score_results_view_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class BattleRoyaleScoreResultsViewModel(ViewModel):
    __slots__ = ('onShowHangarBtnClick', 'onTableFadeOutComplete')

    def getIsMovingTextEnabled(self):
        return self._getBool(0)

    def setIsMovingTextEnabled(self, value):
        self._setBool(0, value)

    def getInSquad(self):
        return self._getBool(1)

    def setInSquad(self, value):
        self._setBool(1, value)

    def getIsBattleState(self):
        return self._getBool(2)

    def setIsBattleState(self, value):
        self._setBool(2, value)

    def getIsWinner(self):
        return self._getBool(3)

    def setIsWinner(self, value):
        self._setBool(3, value)

    def getTableData(self):
        return self._getArray(4)

    def setTableData(self, value):
        self._setArray(4, value)

    def getUsersData(self):
        return self._getArray(5)

    def setUsersData(self, value):
        self._setArray(5, value)

    def getNamesList(self):
        return self._getArray(6)

    def setNamesList(self, value):
        self._setArray(6, value)

    def getIsAnimCanceled(self):
        return self._getBool(7)

    def setIsAnimCanceled(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(BattleRoyaleScoreResultsViewModel, self)._initialize()
        self._addBoolProperty('isMovingTextEnabled', False)
        self._addBoolProperty('inSquad', False)
        self._addBoolProperty('isBattleState', False)
        self._addBoolProperty('isWinner', False)
        self._addArrayProperty('tableData', Array())
        self._addArrayProperty('usersData', Array())
        self._addArrayProperty('namesList', Array())
        self._addBoolProperty('isAnimCanceled', False)
        self.onShowHangarBtnClick = self._addCommand('onShowHangarBtnClick')
        self.onTableFadeOutComplete = self._addCommand('onTableFadeOutComplete')
