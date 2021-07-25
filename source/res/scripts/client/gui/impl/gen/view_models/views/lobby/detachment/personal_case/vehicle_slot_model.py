# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/personal_case/vehicle_slot_model.py
from gui.impl.gen.view_models.views.lobby.detachment.common.price_model import PriceModel
from gui.impl.gen.view_models.views.lobby.detachment.common.vehicle_model import VehicleModel

class VehicleSlotModel(VehicleModel):
    __slots__ = ()
    ASSIGNED = 'assigned'
    EMPTY = 'empty'
    NOT_AVAILABLE = 'notAvailable'
    NOT_AVAILABLE_PRICE = 'notAvailablePrice'
    VEHICLE_SLOT_TOOLTIP = 'vehicleSlotTooltip'

    def __init__(self, properties=13, commands=0):
        super(VehicleSlotModel, self).__init__(properties=properties, commands=commands)

    @property
    def priceModel(self):
        return self._getViewModel(8)

    def getStatus(self):
        return self._getString(9)

    def setStatus(self, value):
        self._setString(9, value)

    def getLevelReq(self):
        return self._getNumber(10)

    def setLevelReq(self, value):
        self._setNumber(10, value)

    def getIsAnimationActive(self):
        return self._getBool(11)

    def setIsAnimationActive(self, value):
        self._setBool(11, value)

    def getIsLocked(self):
        return self._getBool(12)

    def setIsLocked(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(VehicleSlotModel, self)._initialize()
        self._addViewModelProperty('priceModel', PriceModel())
        self._addStringProperty('status', '')
        self._addNumberProperty('levelReq', 0)
        self._addBoolProperty('isAnimationActive', False)
        self._addBoolProperty('isLocked', False)
