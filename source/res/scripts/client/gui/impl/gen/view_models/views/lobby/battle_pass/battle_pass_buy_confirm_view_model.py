# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_confirm_view_model.py
from frameworks.wulf import ViewModel

class BattlePassBuyConfirmViewModel(ViewModel):
    __slots__ = ('onCloseClick', 'onBuyClick', 'onShowRewardsClick')

    def __init__(self, properties=4, commands=3):
        super(BattlePassBuyConfirmViewModel, self).__init__(properties=properties, commands=commands)

    def getPrice(self):
        return self._getNumber(0)

    def setPrice(self, value):
        self._setNumber(0, value)

    def getChapter(self):
        return self._getNumber(1)

    def setChapter(self, value):
        self._setNumber(1, value)

    def getIsChapterStarted(self):
        return self._getBool(2)

    def setIsChapterStarted(self, value):
        self._setBool(2, value)

    def getIsChapterFinished(self):
        return self._getBool(3)

    def setIsChapterFinished(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(BattlePassBuyConfirmViewModel, self)._initialize()
        self._addNumberProperty('price', 0)
        self._addNumberProperty('chapter', 0)
        self._addBoolProperty('isChapterStarted', False)
        self._addBoolProperty('isChapterFinished', False)
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onShowRewardsClick = self._addCommand('onShowRewardsClick')
