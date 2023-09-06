# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/vehicle_bonus_model.py
from gui.impl.gen.view_models.views.lobby.battle_pass.reward_item_model import RewardItemModel

class VehicleBonusModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(VehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(15)

    def setIsElite(self, value):
        self._setBool(15, value)

    def getVehicleName(self):
        return self._getString(16)

    def setVehicleName(self, value):
        self._setString(16, value)

    def getVehicleType(self):
        return self._getString(17)

    def setVehicleType(self, value):
        self._setString(17, value)

    def getVehicleLvl(self):
        return self._getNumber(18)

    def setVehicleLvl(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(VehicleBonusModel, self)._initialize()
        self._addBoolProperty('isElite', True)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLvl', 0)
