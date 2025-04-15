# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/common/coin_exchange_widget_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.common.hb_coin_model import HbCoinModel

class CoinExchangeWidgetModel(ViewModel):
    __slots__ = ('onExchangeClick',)

    def __init__(self, properties=3, commands=1):
        super(CoinExchangeWidgetModel, self).__init__(properties=properties, commands=commands)

    def getEarnings(self):
        return self._getArray(0)

    def setEarnings(self, value):
        self._setArray(0, value)

    @staticmethod
    def getEarningsType():
        return HbCoinModel

    def getIsExchangeEnabled(self):
        return self._getBool(1)

    def setIsExchangeEnabled(self, value):
        self._setBool(1, value)

    def getIsHardDisabled(self):
        return self._getBool(2)

    def setIsHardDisabled(self, value):
        self._setBool(2, value)

    def _initialize(self):
        super(CoinExchangeWidgetModel, self)._initialize()
        self._addArrayProperty('earnings', Array())
        self._addBoolProperty('isExchangeEnabled', True)
        self._addBoolProperty('isHardDisabled', False)
        self.onExchangeClick = self._addCommand('onExchangeClick')
