# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_completed_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattlePassCompletedTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=4, commands=0):
        super(BattlePassCompletedTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getLevel(self):
        return self._getNumber(0)

    def setLevel(self, value):
        self._setNumber(0, value)

    def getIsBattlePassPurchased(self):
        return self._getBool(1)

    def setIsBattlePassPurchased(self, value):
        self._setBool(1, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(2)

    def setNotChosenRewardCount(self, value):
        self._setNumber(2, value)

    def getIsStyleChosen(self):
        return self._getBool(3)

    def setIsStyleChosen(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BattlePassCompletedTooltipViewModel, self)._initialize()
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isBattlePassPurchased', False)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addBoolProperty('isStyleChosen', False)
