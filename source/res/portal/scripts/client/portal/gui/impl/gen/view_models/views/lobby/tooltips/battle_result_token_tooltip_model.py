# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/portal/gui/impl/gen/view_models/views/lobby/tooltips/battle_result_token_tooltip_model.py
from frameworks.wulf import ViewModel

class BattleResultTokenTooltipModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattleResultTokenTooltipModel, self).__init__(properties=properties, commands=commands)

    def getIsWinner(self):
        return self._getBool(0)

    def setIsWinner(self, value):
        self._setBool(0, value)

    def getBattleDifficulty(self):
        return self._getNumber(1)

    def setBattleDifficulty(self, value):
        self._setNumber(1, value)

    def getMaxBattleDifficulty(self):
        return self._getNumber(2)

    def setMaxBattleDifficulty(self, value):
        self._setNumber(2, value)

    def _initialize(self):
        super(BattleResultTokenTooltipModel, self)._initialize()
        self._addBoolProperty('isWinner', False)
        self._addNumberProperty('battleDifficulty', 0)
        self._addNumberProperty('maxBattleDifficulty', 0)
