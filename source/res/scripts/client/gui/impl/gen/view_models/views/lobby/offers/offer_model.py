# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/offers/offer_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.offers.gift_model import GiftModel

class OfferModel(ViewModel):
    __slots__ = ('onBack', 'onLearnMore')

    def __init__(self, properties=13, commands=2):
        super(OfferModel, self).__init__(properties=properties, commands=commands)

    @property
    def gifts(self):
        return self._getViewModel(0)

    @staticmethod
    def getGiftsType():
        return GiftModel

    def getId(self):
        return self._getNumber(1)

    def setId(self, value):
        self._setNumber(1, value)

    def getName(self):
        return self._getString(2)

    def setName(self, value):
        self._setString(2, value)

    def getDescription(self):
        return self._getString(3)

    def setDescription(self, value):
        self._setString(3, value)

    def getLearnMore(self):
        return self._getString(4)

    def setLearnMore(self, value):
        self._setString(4, value)

    def getTokens(self):
        return self._getNumber(5)

    def setTokens(self, value):
        self._setNumber(5, value)

    def getTokensIcon(self):
        return self._getString(6)

    def setTokensIcon(self, value):
        self._setString(6, value)

    def getClicksCount(self):
        return self._getNumber(7)

    def setClicksCount(self, value):
        self._setNumber(7, value)

    def getSignImageLarge(self):
        return self._getString(8)

    def setSignImageLarge(self, value):
        self._setString(8, value)

    def getSignImageSmall(self):
        return self._getString(9)

    def setSignImageSmall(self, value):
        self._setString(9, value)

    def getExpiration(self):
        return self._getNumber(10)

    def setExpiration(self, value):
        self._setNumber(10, value)

    def getBackground(self):
        return self._getString(11)

    def setBackground(self, value):
        self._setString(11, value)

    def getShowPrice(self):
        return self._getBool(12)

    def setShowPrice(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(OfferModel, self)._initialize()
        self._addViewModelProperty('gifts', ListModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('learnMore', '')
        self._addNumberProperty('tokens', 0)
        self._addStringProperty('tokensIcon', '')
        self._addNumberProperty('clicksCount', 0)
        self._addStringProperty('signImageLarge', '')
        self._addStringProperty('signImageSmall', '')
        self._addNumberProperty('expiration', 0)
        self._addStringProperty('background', '')
        self._addBoolProperty('showPrice', False)
        self.onBack = self._addCommand('onBack')
        self.onLearnMore = self._addCommand('onLearnMore')
