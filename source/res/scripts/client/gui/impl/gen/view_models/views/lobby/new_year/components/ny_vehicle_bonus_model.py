# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/new_year/components/ny_vehicle_bonus_model.py
from gui.impl.gen.view_models.views.lobby.new_year.components.reward_item_model import RewardItemModel

class NyVehicleBonusModel(RewardItemModel):
    __slots__ = ()

    def __init__(self, properties=21, commands=0):
        super(NyVehicleBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsElite(self):
        return self._getBool(16)

    def setIsElite(self, value):
        self._setBool(16, value)

    def getVehicleName(self):
        return self._getString(17)

    def setVehicleName(self, value):
        self._setString(17, value)

    def getVehicleType(self):
        return self._getString(18)

    def setVehicleType(self, value):
        self._setString(18, value)

    def getNation(self):
        return self._getString(19)

    def setNation(self, value):
        self._setString(19, value)

    def getVehicleLvl(self):
        return self._getNumber(20)

    def setVehicleLvl(self, value):
        self._setNumber(20, value)

    def _initialize(self):
        super(NyVehicleBonusModel, self)._initialize()
        self._addBoolProperty('isElite', True)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addStringProperty('nation', '')
        self._addNumberProperty('vehicleLvl', 0)
