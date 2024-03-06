# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_buy_confirm_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_compound_price_model import UserCompoundPriceModel

class BattlePassBuyConfirmViewModel(ViewModel):
    __slots__ = ('onCloseClick', 'onBuyClick', 'onShowRewardsClick', 'onChangePurchaseWithLevels')

    def __init__(self, properties=8, commands=4):
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

    def getPrevPrice(self):
        return self._getNumber(2)

    def setPrevPrice(self, value):
        self._setNumber(2, value)

    def getChapterID(self):
        return self._getNumber(3)

    def setChapterID(self, value):
        self._setNumber(3, value)

    def getIsActive(self):
        return self._getBool(4)

    def setIsActive(self, value):
        self._setBool(4, value)

    def getCompoundPriceDefaultID(self):
        return self._getString(5)

    def setCompoundPriceDefaultID(self, value):
        self._setString(5, value)

    def getIsPurchaseWithLevels(self):
        return self._getBool(6)

    def setIsPurchaseWithLevels(self, value):
        self._setBool(6, value)

    def getRemainingLevelsCount(self):
        return self._getNumber(7)

    def setRemainingLevelsCount(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(BattlePassBuyConfirmViewModel, self)._initialize()
        self._addViewModelProperty('compoundPrice', UserCompoundPriceModel())
        self._addNumberProperty('price', 0)
        self._addNumberProperty('prevPrice', 0)
        self._addNumberProperty('chapterID', 0)
        self._addBoolProperty('isActive', False)
        self._addStringProperty('compoundPriceDefaultID', '')
        self._addBoolProperty('isPurchaseWithLevels', False)
        self._addNumberProperty('remainingLevelsCount', 0)
        self.onCloseClick = self._addCommand('onCloseClick')
        self.onBuyClick = self._addCommand('onBuyClick')
        self.onShowRewardsClick = self._addCommand('onShowRewardsClick')
        self.onChangePurchaseWithLevels = self._addCommand('onChangePurchaseWithLevels')
