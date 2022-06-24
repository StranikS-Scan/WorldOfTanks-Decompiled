# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/offers/offer_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel
from gui.impl.gen.view_models.views.lobby.offers.gift_model import GiftModel

class OfferModel(ViewModel):
    __slots__ = ('onBack',)

    def __init__(self, properties=8, commands=1):
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

    def getTokens(self):
        return self._getNumber(3)

    def setTokens(self, value):
        self._setNumber(3, value)

    def getClicksCount(self):
        return self._getNumber(4)

    def setClicksCount(self, value):
        self._setNumber(4, value)

    def getExpiration(self):
        return self._getNumber(5)

    def setExpiration(self, value):
        self._setNumber(5, value)

    def getBackground(self):
        return self._getString(6)

    def setBackground(self, value):
        self._setString(6, value)

    def getKey(self):
        return self._getNumber(7)

    def setKey(self, value):
        self._setNumber(7, value)

    def _initialize(self):
        super(OfferModel, self)._initialize()
        self._addViewModelProperty('gifts', ListModel())
        self._addNumberProperty('id', 0)
        self._addStringProperty('name', '')
        self._addNumberProperty('tokens', 0)
        self._addNumberProperty('clicksCount', 0)
        self._addNumberProperty('expiration', 0)
        self._addStringProperty('background', '')
        self._addNumberProperty('key', 0)
        self.onBack = self._addCommand('onBack')
