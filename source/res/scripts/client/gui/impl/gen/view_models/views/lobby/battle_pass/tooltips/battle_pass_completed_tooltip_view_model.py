# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/tooltips/battle_pass_completed_tooltip_view_model.py
from frameworks.wulf import ViewModel

class BattlePassCompletedTooltipViewModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=3, commands=0):
        super(BattlePassCompletedTooltipViewModel, self).__init__(properties=properties, commands=commands)

    def getIsBattlePassPurchased(self):
        return self._getBool(0)

    def setIsBattlePassPurchased(self, value):
        self._setBool(0, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(1)

    def setNotChosenRewardCount(self, value):
        self._setNumber(1, value)

    def getIsTankmenRecieved(self):
        return self._getBool(2)

    def setIsTankmenRecieved(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(BattlePassCompletedTooltipViewModel, self)._initialize()
        self._addBoolProperty('isBattlePassPurchased', False)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addBoolProperty('isTankmenRecieved', False)
