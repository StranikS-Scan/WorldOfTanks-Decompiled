# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_confirm_view_model.py
from frameworks.wulf import ViewModel

class BattlePassBuyConfirmViewModel(ViewModel):
    __slots__ = ('onCloseClick', 'onBuyClick', 'onShowRewardsClick')

    def __init__(self, properties=5, commands=3):
        super(BattlePassBuyConfirmViewModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def getLevelsCount(self):
        return self._getNumber(1)

    def setLevelsCount(self, value):
        self._setNumber(1, value)

    def getHasBattlePass(self):
        return self._getBool(2)

    def setHasBattlePass(self, value):
        self._setBool(2, value)

    def getStartedProgression(self):
        return self._getBool(3)

    def setStartedProgression(self, value):
        self._setBool(3, value)

    def getFinishedProgression(self):
        return self._getBool(4)

    def setFinishedProgression(self, value):
        self._setBool(4, value)

    def _initialize(self):
        super(BattlePassBuyConfirmViewModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addNumberProperty('levelsCount', 0)
        self._addBoolProperty('hasBattlePass', False)
        self._addBoolProperty('startedProgression', False)
        self._addBoolProperty('finishedProgression', False)
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onShowRewardsClick = self._addCommand('onShowRewardsClick')
