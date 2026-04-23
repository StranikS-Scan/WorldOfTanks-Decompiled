# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/optional_devices_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.wrappers.user_list_model import ListModel
from historical_battles.gui.impl.gen.view_models.views.common.coin_exchange_widget_model import CoinExchangeWidgetModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.optional_device_item_view_model import OptionalDeviceItemViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.wallet_view_model import WalletViewModel

class OptionalDevicesViewModel(ViewModel):
    __slots__ = ('onClose', 'onBack')

    def __init__(self, properties=4, commands=2):
        super(OptionalDevicesViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def coinWidget(self):
        return self._getViewModel(0)

    @staticmethod
    def getCoinWidgetType():
        return CoinExchangeWidgetModel

    @property
    def items(self):
        return self._getViewModel(1)

    @staticmethod
    def getItemsType():
        return OptionalDeviceItemViewModel

    @property
    def wallet(self):
        return self._getViewModel(2)

    @staticmethod
    def getWalletType():
        return WalletViewModel

    def getPurchasesLeft(self):
        return self._getNumber(3)

    def setPurchasesLeft(self, value):
        self._setNumber(3, value)

    def _initialize(self):
        super(OptionalDevicesViewModel, self)._initialize()
        self._addViewModelProperty('coinWidget', CoinExchangeWidgetModel())
        self._addViewModelProperty('items', ListModel())
        self._addViewModelProperty('wallet', WalletViewModel())
        self._addNumberProperty('purchasesLeft', 0)
        self.onClose = self._addCommand('onClose')
        self.onBack = self._addCommand('onBack')
