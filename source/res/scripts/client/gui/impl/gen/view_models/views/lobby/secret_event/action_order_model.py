# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_order_model.py
from gui.impl.gen import R
from gui.impl.wrappers.user_list_model import UserListModel
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.general_filter_item_model import GeneralFilterItemModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_exchange_model import OrderExchangeModel
from gui.impl.gen.view_models.views.lobby.secret_event.order_model import OrderModel

class ActionOrderModel(ActionMenuModel):
    __slots__ = ('onBuyPack', 'onFilterChange')

    def __init__(self, properties=12, commands=5):
        super(ActionOrderModel, self).__init__(properties=properties, commands=commands)

    @property
    def orders(self):
        return self._getViewModel(4)

    @property
    def exchangePack(self):
        return self._getViewModel(5)

    @property
    def filterItems(self):
        return self._getViewModel(6)

    def getSelectedGeneralId(self):
        return self._getNumber(7)

    def setSelectedGeneralId(self, value):
        self._setNumber(7, value)

    def getGeneralName(self):
        return self._getResource(8)

    def setGeneralName(self, value):
        self._setResource(8, value)

    def getTimer(self):
        return self._getNumber(9)

    def setTimer(self, value):
        self._setNumber(9, value)

    def getCount(self):
        return self._getNumber(10)

    def setCount(self, value):
        self._setNumber(10, value)

    def getIsQuests(self):
        return self._getBool(11)

    def setIsQuests(self, value):
        self._setBool(11, value)

    def _initialize(self):
        super(ActionOrderModel, self)._initialize()
        self._addViewModelProperty('orders', UserListModel())
        self._addViewModelProperty('exchangePack', OrderExchangeModel())
        self._addViewModelProperty('filterItems', UserListModel())
        self._addNumberProperty('selectedGeneralId', 0)
        self._addResourceProperty('generalName', R.invalid())
        self._addNumberProperty('timer', 0)
        self._addNumberProperty('count', 0)
        self._addBoolProperty('isQuests', True)
        self.onBuyPack = self._addCommand('onBuyPack')
        self.onFilterChange = self._addCommand('onFilterChange')
