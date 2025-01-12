# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/battle/commendations/player_model.py
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class PlayerModel(UserNameModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(PlayerModel, self).__init__(properties=properties, commands=commands)

    def getVehicleName(self):
        return self._getString(10)

    def setVehicleName(self, value):
        self._setString(10, value)

    def getVehicleType(self):
        return self._getString(11)

    def setVehicleType(self, value):
        self._setString(11, value)

    def getVehicleLevel(self):
        return self._getNumber(12)

    def setVehicleLevel(self, value):
        self._setNumber(12, value)

    def getDamage(self):
        return self._getNumber(13)

    def setDamage(self, value):
        self._setNumber(13, value)

    def getKills(self):
        return self._getNumber(14)

    def setKills(self, value):
        self._setNumber(14, value)

    def getXp(self):
        return self._getNumber(15)

    def setXp(self, value):
        self._setNumber(15, value)

    def getIsReported(self):
        return self._getBool(16)

    def setIsReported(self, value):
        self._setBool(16, value)

    def getIsCommended(self):
        return self._getBool(17)

    def setIsCommended(self, value):
        self._setBool(17, value)

    def _initialize(self):
        super(PlayerModel, self)._initialize()
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', '')
        self._addNumberProperty('vehicleLevel', 1)
        self._addNumberProperty('damage', 0)
        self._addNumberProperty('kills', 0)
        self._addNumberProperty('xp', 0)
        self._addBoolProperty('isReported', False)
        self._addBoolProperty('isCommended', False)
