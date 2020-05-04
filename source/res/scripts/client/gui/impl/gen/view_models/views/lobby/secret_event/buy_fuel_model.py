# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/secret_event/buy_fuel_model.py
from gui.impl.gen.view_models.views.lobby.secret_event.price_model import PriceModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class BuyFuelModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=2):
        super(BuyFuelModel, self).__init__(properties=properties, commands=commands)

    @property
    def fuelPrice(self):
        return self._getViewModel(10)

    def _initialize(self):
        super(BuyFuelModel, self)._initialize()
        self._addViewModelProperty('fuelPrice', PriceModel())
