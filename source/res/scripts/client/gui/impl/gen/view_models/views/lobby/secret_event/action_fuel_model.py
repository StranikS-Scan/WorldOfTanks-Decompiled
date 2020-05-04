# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/action_fuel_model.py
from gui.impl.gen.view_models.views.lobby.secret_event.action_menu_model import ActionMenuModel
from gui.impl.gen.view_models.views.lobby.secret_event.price_model import PriceModel

class ActionFuelModel(ActionMenuModel):
    __slots__ = ('onBuyFuel',)

    def __init__(self, properties=7, commands=4):
        super(ActionFuelModel, self).__init__(properties=properties, commands=commands)

    @property
    def fuelPrice(self):
        return self._getViewModel(4)

    def getFuelCount(self):
        return self._getNumber(5)

    def setFuelCount(self, value):
        self._setNumber(5, value)

    def getTimer(self):
        return self._getNumber(6)

    def setTimer(self, value):
        self._setNumber(6, value)

    def _initialize(self):
        super(ActionFuelModel, self)._initialize()
        self._addViewModelProperty('fuelPrice', PriceModel())
        self._addNumberProperty('fuelCount', 0)
        self._addNumberProperty('timer', 0)
        self.onBuyFuel = self._addCommand('onBuyFuel')
