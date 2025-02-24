# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: gui_lootboxes/scripts/client/gui_lootboxes/gui/impl/gen/view_models/views/lobby/gui_lootboxes/tooltips/lootbox_tooltip_extended_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.complex_lootbox_slot_model import ComplexLootboxSlotModel
from gui_lootboxes.gui.impl.gen.view_models.views.lobby.gui_lootboxes.tooltips.vehicle_special_slot_model import VehicleSpecialSlotModel

class LootboxTooltipExtendedModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=5, commands=0):
        super(LootboxTooltipExtendedModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleSpecialSlot(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleSpecialSlotType():
        return VehicleSpecialSlotModel

    def getLootboxName(self):
        return self._getString(1)

    def setLootboxName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getRotationsToGuaranteedVehicle(self):
        return self._getNumber(3)

    def setRotationsToGuaranteedVehicle(self, value):
        self._setNumber(3, value)

    def getSlots(self):
        return self._getArray(4)

    def setSlots(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSlotsType():
        return ComplexLootboxSlotModel

    def _initialize(self):
        super(LootboxTooltipExtendedModel, self)._initialize()
        self._addViewModelProperty('vehicleSpecialSlot', VehicleSpecialSlotModel())
        self._addStringProperty('lootboxName', '')
        self._addStringProperty('description', '')
        self._addNumberProperty('rotationsToGuaranteedVehicle', 0)
        self._addArrayProperty('slots', Array())
