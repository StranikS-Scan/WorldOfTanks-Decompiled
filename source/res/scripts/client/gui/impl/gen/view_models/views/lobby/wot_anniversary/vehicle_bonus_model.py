# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/wot_anniversary/vehicle_bonus_model.py
from gui.impl.gen.view_models.common.missions.bonuses.bonus_model import BonusModel

class VehicleBonusModel(BonusModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(VehicleBonusModel, self).__init__(properties=properties, commands=commands)

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
        return self._getNumber(10)

    def setVehicleLvl(self, value):
        self._setNumber(10, value)

    def _initialize(self):
        super(VehicleBonusModel, self)._initialize()
        self._addBoolProperty('isElite', True)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLvl', 0)
