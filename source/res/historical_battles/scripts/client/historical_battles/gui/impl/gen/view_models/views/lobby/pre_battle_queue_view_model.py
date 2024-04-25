# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/pre_battle_queue_view_model.py
from enum import Enum
from frameworks.wulf import Array
from historical_battles.gui.impl.gen.view_models.views.common.selectable_view_model import SelectableViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel

class FrontmanRole(Enum):
    ENGINEER = 'engineer'
    AVIATION = 'aviation'
    ARTILLERY = 'artillery'


class PreBattleQueueViewModel(SelectableViewModel):
    __slots__ = ('onExitBattle',)

    def __init__(self, properties=6, commands=3):
        super(PreBattleQueueViewModel, self).__init__(properties=properties, commands=commands)

    def getTimePassed(self):
        return self._getString(0)

    def setTimePassed(self, value):
        self._setString(0, value)

    def getSelectedVehicleName(self):
        return self._getString(1)

    def setSelectedVehicleName(self, value):
        self._setString(1, value)

    def getSelectedFrontmanRole(self):
        return FrontmanRole(self._getString(2))

    def setSelectedFrontmanRole(self, value):
        self._setString(2, value.value)

    def getOrders(self):
        return self._getArray(3)

    def setOrders(self, value):
        self._setArray(3, value)

    @staticmethod
    def getOrdersType():
        return OrderModel

    def getSelectedOrderId(self):
        return self._getString(4)

    def setSelectedOrderId(self, value):
        self._setString(4, value)

    def getIsQuitButtonDisabled(self):
        return self._getBool(5)

    def setIsQuitButtonDisabled(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(PreBattleQueueViewModel, self)._initialize()
        self._addStringProperty('timePassed', '')
        self._addStringProperty('selectedVehicleName', '')
        self._addStringProperty('selectedFrontmanRole')
        self._addArrayProperty('orders', Array())
        self._addStringProperty('selectedOrderId', '')
        self._addBoolProperty('isQuitButtonDisabled', False)
        self.onExitBattle = self._addCommand('onExitBattle')
