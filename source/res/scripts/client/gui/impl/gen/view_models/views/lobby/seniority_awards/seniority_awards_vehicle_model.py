# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/seniority_awards/seniority_awards_vehicle_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class SeniorityAwardsVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
        super(SeniorityAwardsVehicleModel, self).__init__(properties=properties, commands=commands)

    def getDescription(self):
        return self._getString(10)

    def setDescription(self, value):
        self._setString(10, value)

    def getVehicleId(self):
        return self._getString(11)

    def setVehicleId(self, value):
        self._setString(11, value)

    def _initialize(self):
        super(SeniorityAwardsVehicleModel, self)._initialize()
        self._addStringProperty('description', '')
        self._addStringProperty('vehicleId', '')
