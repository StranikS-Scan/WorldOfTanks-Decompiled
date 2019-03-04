# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/loot_box_view/loot_vehicle_compensation_renderer_model.py
from gui.impl.gen.view_models.views.loot_box_view.loot_compensation_renderer_model import LootCompensationRendererModel

class LootVehicleCompensationRendererModel(LootCompensationRendererModel):
    __slots__ = ()

    def getVehicleName(self):
        return self._getString(21)

    def setVehicleName(self, value):
        self._setString(21, value)

    def getVehicleType(self):
        return self._getString(22)

    def setVehicleType(self, value):
        self._setString(22, value)

    def getVehicleLvl(self):
        return self._getString(23)

    def setVehicleLvl(self, value):
        self._setString(23, value)

    def getIsElite(self):
        return self._getBool(24)

    def setIsElite(self, value):
        self._setBool(24, value)

    def _initialize(self):
        super(LootVehicleCompensationRendererModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('vehicleLvl', '')
        self._addBoolProperty('isElite', True)
