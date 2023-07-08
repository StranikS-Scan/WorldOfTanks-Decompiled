# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_confirm_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel

class BattlePassBuyConfirmViewModel(ViewModel):
    __slots__ = ('onCloseClick', 'onBuyClick', 'onShowRewardsClick')

    def __init__(self, properties=5, commands=3):
        super(BattlePassBuyConfirmViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def compoundPrice(self):
        return self._getViewModel(0)

    @staticmethod
    def getCompoundPriceType():
        return UserCompoundPriceModel

    def getPrice(self):
        return self._getNumber(1)

    def setPrice(self, value):
        self._setNumber(1, value)

    def getChapterID(self):
        return self._getNumber(2)

    def setChapterID(self, value):
        self._setNumber(2, value)

    def getIsActive(self):
        return self._getBool(3)

    def setIsActive(self, value):
        self._setBool(3, value)

    def getCompoundPriceDefaultID(self):
        return self._getString(4)

    def setCompoundPriceDefaultID(self, value):
        self._setString(4, value)

    def _initialize(self):
        super(BattlePassBuyConfirmViewModel, self)._initialize()
        self._addViewModelProperty('compoundPrice', UserCompoundPriceModel())
        self._addNumberProperty('price', 0)
        self._addNumberProperty('chapterID', 0)
        self._addBoolProperty('isActive', False)
        self._addStringProperty('compoundPriceDefaultID', '')
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onShowRewardsClick = self._addCommand('onShowRewardsClick')
