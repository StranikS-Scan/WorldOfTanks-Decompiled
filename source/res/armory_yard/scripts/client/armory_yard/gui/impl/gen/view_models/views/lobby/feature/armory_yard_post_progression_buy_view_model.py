# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: armory_yard/scripts/client/armory_yard/gui/impl/gen/view_models/views/lobby/feature/armory_yard_post_progression_buy_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.price_model import PriceModel

class ArmoryYardPostProgressionBuyViewModel(ViewModel):
    __slots__ = ('onBuy', 'onCancel', 'onBack')

    def __init__(self, properties=6, commands=3):
        super(ArmoryYardPostProgressionBuyViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def price(self):
        return self._getViewModel(0)

    @staticmethod
    def getPriceType():
        return PriceModel

    def getTokensCount(self):
        return self._getNumber(1)

    def setTokensCount(self, value):
        self._setNumber(1, value)

    def getPayedTokensLimit(self):
        return self._getNumber(2)

    def setPayedTokensLimit(self, value):
        self._setNumber(2, value)

    def getIsWalletAvailable(self):
        return self._getBool(3)

    def setIsWalletAvailable(self, value):
        self._setBool(3, value)

    def getIsBlurEnabled(self):
        return self._getBool(4)

    def setIsBlurEnabled(self, value):
        self._setBool(4, value)

    def getUserGold(self):
        return self._getNumber(5)

    def setUserGold(self, value):
        self._setNumber(5, value)

    def _initialize(self):
        super(ArmoryYardPostProgressionBuyViewModel, self)._initialize()
        self._addViewModelProperty('price', PriceModel())
        self._addNumberProperty('tokensCount', 0)
        self._addNumberProperty('payedTokensLimit', 0)
        self._addBoolProperty('isWalletAvailable', True)
        self._addBoolProperty('isBlurEnabled', False)
        self._addNumberProperty('userGold', 0)
        self.onBuy = self._addCommand('onBuy')
        self.onCancel = self._addCommand('onCancel')
        self.onBack = self._addCommand('onBack')
