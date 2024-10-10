# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_post_progression_buy_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class ArmoryYardPostProgressionBuyViewModel(ViewModel):
    __slots__ = ('onBuy', 'onCancel', 'onBack')
    ARG_TOKENS = 'tokens'
    ARG_CURRENCY_TYPE = 'currencyType'

    def __init__(self, properties=8, commands=3):
        super(ArmoryYardPostProgressionBuyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    @property
    def crystalPrice(self):
        return self._getViewModel(1)

    @staticmethod
    def getCrystalPriceType():
        return PriceModel

    def getTokensCount(self):
        return self._getNumber(2)

    def setTokensCount(self, value):
        self._setNumber(2, value)

    def getPayedTokensLimit(self):
        return self._getNumber(3)

    def setPayedTokensLimit(self, value):
        self._setNumber(3, value)

    def getIsWalletAvailable(self):
        return self._getBool(4)

    def setIsWalletAvailable(self, value):
        self._setBool(4, value)

    def getIsBlurEnabled(self):
        return self._getBool(5)

    def setIsBlurEnabled(self, value):
        self._setBool(5, value)

    def getUserGold(self):
        return self._getNumber(6)

    def setUserGold(self, value):
        self._setNumber(6, value)

    def getUserCrystal(self):
        return self._getNumber(7)

    def setUserCrystal(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(ArmoryYardPostProgressionBuyViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addViewModelProperty('crystalPrice', PriceModel())
        self._addNumberProperty('tokensCount', 0)
        self._addNumberProperty('payedTokensLimit', 0)
        self._addBoolProperty('isWalletAvailable', True)
        self._addBoolProperty('isBlurEnabled', False)
        self._addNumberProperty('userGold', 0)
        self._addNumberProperty('userCrystal', 0)
        self.onBuy = self._addCommand('onBuy')
        self.onCancel = self._addCommand('onCancel')
        self.onBack = self._addCommand('onBack')
