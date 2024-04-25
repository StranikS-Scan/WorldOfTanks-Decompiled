# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/shop_view_model.py
from enum import Enum
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.coin_exchange_widget_model import CoinExchangeWidgetModel

class ShopTabs(Enum):
    BEST = 'best'
    INSTRUCTION = 'instruction'
    RESERVES = 'reserves'
    CREWBOOK = 'crewbook'
    EQUIPMENT = 'equipment'


class ShopViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=2, commands=1):
        super(ShopViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def coinWidget(self):
        return self._getViewModel(0)

    def getSelectedTab(self):
        return ShopTabs(self._getString(1))

    def setSelectedTab(self, value):
        self._setString(1, value.value)

    def _initialize(self):
        super(ShopViewModel, self)._initialize()
        self._addViewModelProperty('coinWidget', CoinExchangeWidgetModel())
        self._addStringProperty('selectedTab')
        self.onClose = self._addCommand('onClose')
