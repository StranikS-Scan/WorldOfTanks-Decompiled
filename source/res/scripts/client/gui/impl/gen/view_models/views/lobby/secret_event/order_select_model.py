# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/order_select_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_exchange_model import OrderExchangeModel
from gui.impl.gen.view_models.views.lobby.secret_event.pack_card_model import PackCardModel

class OrderSelectModel(ViewModel):
    __slots__ = ('onBuyPack', 'onClose')

    def __init__(self, properties=8, commands=2):
        super(OrderSelectModel, self).__init__(properties=properties, commands=commands)

    @property
    def packItems(self):
        return self._getViewModel(0)

    @property
    def exchangePack(self):
        return self._getViewModel(1)

    def getGeneralID(self):
        return self._getNumber(2)

    def setGeneralID(self, value):
        self._setNumber(2, value)

    def getCredits(self):
        return self._getNumber(3)

    def setCredits(self, value):
        self._setNumber(3, value)

    def getGolds(self):
        return self._getNumber(4)

    def setGolds(self, value):
        self._setNumber(4, value)

    def getCrystals(self):
        return self._getNumber(5)

    def setCrystals(self, value):
        self._setNumber(5, value)

    def getFreexp(self):
        return self._getNumber(6)

    def setFreexp(self, value):
        self._setNumber(6, value)

    def getIsExchange(self):
        return self._getBool(7)

    def setIsExchange(self, value):
        self._setBool(7, value)

    def _initialize(self):
        super(OrderSelectModel, self)._initialize()
        self._addViewModelProperty('packItems', UserListModel())
        self._addViewModelProperty('exchangePack', OrderExchangeModel())
        self._addNumberProperty('generalID', 0)
        self._addNumberProperty('credits', 0)
        self._addNumberProperty('golds', 0)
        self._addNumberProperty('crystals', 0)
        self._addNumberProperty('freexp', 0)
        self._addBoolProperty('isExchange', False)
        self.onBuyPack = self._addCommand('onBuyPack')
        self.onClose = self._addCommand('onClose')
