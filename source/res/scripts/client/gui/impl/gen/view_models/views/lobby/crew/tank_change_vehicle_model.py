# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tank_change_vehicle_model.py
from gui.impl.gen.view_models.views.lobby.common.vehicle_model import VehicleModel

class TankChangeVehicleModel(VehicleModel):
    __slots__ = ()

    def __init__(self, properties=13, commands=0):
        super(TankChangeVehicleModel, self).__init__(properties=properties, commands=commands)

    def getIsInInventory(self):
        return self._getBool(9)

    def setIsInInventory(self, value):
        self._setBool(9, value)

    def getIsElite(self):
        return self._getBool(10)

    def setIsElite(self, value):
        self._setBool(10, value)

    def getIsSelected(self):
        return self._getBool(11)

    def setIsSelected(self, value):
        self._setBool(11, value)

    def getIsTrainingAvailable(self):
        return self._getBool(12)

    def setIsTrainingAvailable(self, value):
        self._setBool(12, value)

    def _initialize(self):
        super(TankChangeVehicleModel, self)._initialize()
        self._addBoolProperty('isInInventory', False)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isTrainingAvailable', False)
