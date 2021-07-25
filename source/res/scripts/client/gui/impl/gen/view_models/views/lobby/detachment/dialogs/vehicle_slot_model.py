# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/dialogs/vehicle_slot_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class VehicleSlotModel(VehicleModel):
    __slots__ = ()
    SLOT_TOOLTIP = 'slotTooltip'

    def __init__(self, properties=11, commands=0):
        super(VehicleSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(8)

    def getIsSelected(self):
        return self._getBool(9)

    def setIsSelected(self, value):
        self._setBool(9, value)

    def getState(self):
        return self._getString(10)

    def setState(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(VehicleSlotModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('state', '')
