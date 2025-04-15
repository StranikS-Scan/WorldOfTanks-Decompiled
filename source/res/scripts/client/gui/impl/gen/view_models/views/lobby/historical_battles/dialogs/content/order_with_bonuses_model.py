# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/historical_battles/dialogs/content/order_with_bonuses_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.historical_battles.dialogs.content.bundle_bonus_view_model import BundleBonusViewModel
from gui.impl.gen.view_models.views.lobby.historical_battles.dialogs.content.order_model import OrderModel

class OrderWithBonusesModel(ViewModel):
    __slots__ = ()
    TOOLTIP_ORDER = 'TOOLTIP_ORDER'
    TOOLTIP_BONUS = 'TOOLTIP_BONUS'

    def __init__(self, properties=2, commands=0):
        super(OrderWithBonusesModel, self).__init__(properties=properties, commands=commands)

    @property
    def order(self):
        return self._getViewModel(0)

    @staticmethod
    def getOrderType():
        return OrderModel

    def getBonuses(self):
        return self._getArray(1)

    def setBonuses(self, value):
        self._setArray(1, value)

    @staticmethod
    def getBonusesType():
        return BundleBonusViewModel

    def _initialize(self):
        super(OrderWithBonusesModel, self)._initialize()
        self._addViewModelProperty('order', OrderModel())
        self._addArrayProperty('bonuses', Array())
