# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/dialogs/sub_views/exchange_coins_side_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from historical_battles.gui.impl.gen.view_models.views.dialogs.sub_views.exchange_coin_data_model import ExchangeCoinDataModel

class Side(Enum):
    LEFT = 'left'
    RIGHT = 'right'


class ExchangeCoinsSideModel(ViewModel):
    __slots__ = ('onDropdownItemClicked',)

    def __init__(self, properties=3, commands=1):
        super(ExchangeCoinsSideModel, self).__init__(properties=properties, commands=commands)

    def getCoinName(self):
        return self._getString(0)

    def setCoinName(self, value):
        self._setString(0, value)

    def getSide(self):
        return Side(self._getString(1))

    def setSide(self, value):
        self._setString(1, value.value)

    def getDropdownList(self):
        return self._getArray(2)

    def setDropdownList(self, value):
        self._setArray(2, value)

    @staticmethod
    def getDropdownListType():
        return ExchangeCoinDataModel

    def _initialize(self):
        super(ExchangeCoinsSideModel, self)._initialize()
        self._addStringProperty('coinName', '')
        self._addStringProperty('side')
        self._addArrayProperty('dropdownList', Array())
        self.onDropdownItemClicked = self._addCommand('onDropdownItemClicked')
