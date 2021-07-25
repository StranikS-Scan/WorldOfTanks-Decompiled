# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/buy_vehicle_slot_dialog_view_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.windows.full_screen_dialog_window_model import FullScreenDialogWindowModel

class BuyVehicleSlotDialogViewModel(FullScreenDialogWindowModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=3):
        super(BuyVehicleSlotDialogViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(11)

    def _initialize(self):
        super(BuyVehicleSlotDialogViewModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
