# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/impl/gen/view_models/views/lobby/pre_battle_queue_view_model.py
from frameworks.wulf import Array
from historical_battles.gui.impl.gen.view_models.views.common.selectable_view_model import SelectableViewModel
from historical_battles.gui.impl.gen.view_models.views.lobby.order_model import OrderModel

class PreBattleQueueViewModel(SelectableViewModel):
    __slots__ = ('onExitBattle',)

    def __init__(self, properties=4, commands=3):
        super(PreBattleQueueViewModel, self).__init__(properties=properties, commands=commands)

    def getTimePassed(self):
        return self._getString(0)

    def setTimePassed(self, value):
        self._setString(0, value)

    def getDivisionName(self):
        return self._getString(1)

    def setDivisionName(self, value):
        self._setString(1, value)

    def getOrders(self):
        return self._getArray(2)

    def setOrders(self, value):
        self._setArray(2, value)

    @staticmethod
    def getOrdersType():
        return OrderModel

    def getIsQuitButtonDisabled(self):
        return self._getBool(3)

    def setIsQuitButtonDisabled(self, value):
        self._setBool(3, value)

    def _initialize(self):
        super(PreBattleQueueViewModel, self)._initialize()
        self._addStringProperty('timePassed', '')
        self._addStringProperty('divisionName', '')
        self._addArrayProperty('orders', Array())
        self._addBoolProperty('isQuitButtonDisabled', False)
        self.onExitBattle = self._addCommand('onExitBattle')
