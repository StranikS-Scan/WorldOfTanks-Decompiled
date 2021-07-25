# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/common/buy_vehicle_window_model.py
from frameworks.wulf import Array
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel
from gui.impl.gen.view_models.windows.selector_dialog_model import SelectorDialogModel

class BuyVehicleWindowModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=15, commands=3):
        super(BuyVehicleWindowModel, self).__init__(properties=properties, commands=commands)

    @property
    def selector(self):
        return self._getViewModel(11)

    @property
    def vehicle(self):
        return self._getViewModel(12)

    def getPrices(self):
        return self._getArray(13)

    def setPrices(self, value):
        self._setArray(13, value)

    def getFooterText(self):
        return self._getResource(14)

    def setFooterText(self, value):
        self._setResource(14, value)

    def _initialize(self):
        super(BuyVehicleWindowModel, self)._initialize()
        self._addViewModelProperty('selector', SelectorDialogModel())
        self._addViewModelProperty('vehicle', VehicleModel())
        self._addArrayProperty('prices', Array())
        self._addResourceProperty('footerText', R.invalid())
