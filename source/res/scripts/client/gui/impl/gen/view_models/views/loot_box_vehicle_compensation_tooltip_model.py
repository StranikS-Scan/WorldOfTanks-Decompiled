# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_vehicle_compensation_tooltip_model.py
from gui.impl.gen.view_models.views.loot_box_compensation_tooltip_model import LootBoxCompensationTooltipModel

class LootBoxVehicleCompensationTooltipModel(LootBoxCompensationTooltipModel):
    __slots__ = ()

    def getIsElite(self):
        return self._getBool(7)

    def setIsElite(self, value):
        self._setBool(7, value)

    def getVehicleName(self):
        return self._getString(8)

    def setVehicleName(self, value):
        self._setString(8, value)

    def getVehicleType(self):
        return self._getString(9)

    def setVehicleType(self, value):
        self._setString(9, value)

    def getVehicleLvl(self):
        return self._getString(10)

    def setVehicleLvl(self, value):
        self._setString(10, value)

    def _initialize(self):
        super(LootBoxVehicleCompensationTooltipModel, self)._initialize()
        self._addBoolProperty('isElite', True)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleLvl', '')
