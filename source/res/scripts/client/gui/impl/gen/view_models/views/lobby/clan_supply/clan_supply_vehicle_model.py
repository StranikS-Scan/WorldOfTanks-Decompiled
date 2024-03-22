# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/clan_supply/clan_supply_vehicle_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class ClanSupplyVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=10, commands=0):
        super(ClanSupplyVehicleModel, self).__init__(properties=properties, commands=commands)

    def getFullName(self):
        return self._getString(9)

    def setFullName(self, value):
        self._setString(9, value)

    def _initialize(self):
        super(ClanSupplyVehicleModel, self)._initialize()
        self._addStringProperty('fullName', '')
