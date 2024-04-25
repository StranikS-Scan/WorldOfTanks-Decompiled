# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_views/shop_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.coin_exchange_widget_model import CoinExchangeWidgetModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.shop_item_view_model import ShopItemViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.showcase_view_model import ShowcaseViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.shop_views.wallet_view_model import WalletViewModel
from gui.impl.gen.view_models.ui_kit.list_model import ListModel

class ShopTabs(Enum):
    BEST = 'best'
    INSTRUCTION = 'instruction'
    RESERVES = 'reserves'
    CREWBOOK = 'crewbook'
    EQUIPMENT = 'equipment'


class ShopViewModel(ViewModel):
    __slots__ = ('onTabChange', 'onClose', 'onBack')

    def __init__(self, properties=5, commands=3):
        super(ShopViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def coinWidget(self):
        return self._getViewModel(0)

    @staticmethod
    def getCoinWidgetType():
        return CoinExchangeWidgetModel

    @property
    def showcase(self):
        return self._getViewModel(1)

    @staticmethod
    def getShowcaseType():
        return ShowcaseViewModel

    @property
    def wallet(self):
        return self._getViewModel(2)

    @staticmethod
    def getWalletType():
        return WalletViewModel

    @property
    def items(self):
        return self._getViewModel(3)

    @staticmethod
    def getItemsType():
        return ShopItemViewModel

    def getSelectedTab(self):
        return ShopTabs(self._getString(4))

    def setSelectedTab(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(ShopViewModel, self)._initialize()
        self._addViewModelProperty('coinWidget', CoinExchangeWidgetModel())
        self._addViewModelProperty('showcase', ShowcaseViewModel())
        self._addViewModelProperty('wallet', WalletViewModel())
        self._addViewModelProperty('items', ListModel())
        self._addStringProperty('selectedTab')
        self.onTabChange = self._addCommand('onTabChange')
        self.onClose = self._addCommand('onClose')
        self.onBack = self._addCommand('onBack')
