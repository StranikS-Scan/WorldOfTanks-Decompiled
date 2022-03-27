# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/rts/carousel_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_supply_slot_model import CarouselSupplySlotModel
from gui.impl.gen.view_models.views.lobby.rts.carousel_vehicle_slot_model import CarouselVehicleSlotModel

class StateEnum(Enum):
    NORMAL = 'normal'
    HIDING = 'hiding'
    HIDDEN = 'hidden'


class CarouselViewModel(ViewModel):
    __slots__ = ('onVehicleSlotClicked', 'onSupplySlotClicked', 'onHidingAnimationEnded')

    def __init__(self, properties=5, commands=3):
        super(CarouselViewModel, self).__init__(properties=properties, commands=commands)

    def getVehicleSlots(self):
        return self._getArray(0)

    def setVehicleSlots(self, value):
        self._setArray(0, value)

    def getSupplySlots(self):
        return self._getArray(1)

    def setSupplySlots(self, value):
        self._setArray(1, value)

    def getSelectedVehicleSlot(self):
        return self._getNumber(2)

    def setSelectedVehicleSlot(self, value):
        self._setNumber(2, value)

    def getSelectedSupplySlot(self):
        return self._getNumber(3)

    def setSelectedSupplySlot(self, value):
        self._setNumber(3, value)

    def getState(self):
        return StateEnum(self._getString(4))

    def setState(self, value):
        self._setString(4, value.value)

    def _initialize(self):
        super(CarouselViewModel, self)._initialize()
        self._addArrayProperty('vehicleSlots', Array())
        self._addArrayProperty('supplySlots', Array())
        self._addNumberProperty('selectedVehicleSlot', -1)
        self._addNumberProperty('selectedSupplySlot', -1)
        self._addStringProperty('state')
        self.onVehicleSlotClicked = self._addCommand('onVehicleSlotClicked')
        self.onSupplySlotClicked = self._addCommand('onSupplySlotClicked')
        self.onHidingAnimationEnded = self._addCommand('onHidingAnimationEnded')
