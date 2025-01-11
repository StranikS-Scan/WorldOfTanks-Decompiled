# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/gui/impl/gen/view_models/views/battle/grinch_player_model.py
from enum import Enum
from gui.impl.gen.view_models.common.user_name_model import UserNameModel

class VehicleTypeEnum(Enum):
    LIGHTTANK = 'lightTank'
    MEDIUMTANK = 'mediumTank'
    HEAVYTANK = 'heavyTank'


class PlatoonEnum(Enum):
    NONE = ''
    PLATOON1 = 'platoon1'
    PLATOON2 = 'platoon2'
    PLATOON3 = 'platoon3'
    PLATOON4 = 'platoon4'
    PLATOON5 = 'platoon5'
    PLATOON6 = 'platoon6'
    PLATOON7 = 'platoon7'


class GrinchPlayerModel(UserNameModel):
    __slots__ = ()

    def __init__(self, properties=19, commands=0):
        super(GrinchPlayerModel, self).__init__(properties=properties, commands=commands)

    def getScore(self):
        return self._getNumber(10)

    def setScore(self, value):
        self._setNumber(10, value)

    def getVehicleName(self):
        return self._getString(11)

    def setVehicleName(self, value):
        self._setString(11, value)

    def getVehicleType(self):
        return VehicleTypeEnum(self._getString(12))

    def setVehicleType(self, value):
        self._setString(12, value.value)

    def getCarryingItems(self):
        return self._getNumber(13)

    def setCarryingItems(self, value):
        self._setNumber(13, value)

    def getPlatoon(self):
        return PlatoonEnum(self._getString(14))

    def setPlatoon(self, value):
        self._setString(14, value.value)

    def getIsCurrentPlayer(self):
        return self._getBool(15)

    def setIsCurrentPlayer(self, value):
        self._setBool(15, value)

    def getIsDead(self):
        return self._getBool(16)

    def setIsDead(self, value):
        self._setBool(16, value)

    def getIsCurrentPlatoon(self):
        return self._getBool(17)

    def setIsCurrentPlatoon(self, value):
        self._setBool(17, value)

    def getKills(self):
        return self._getNumber(18)

    def setKills(self, value):
        self._setNumber(18, value)

    def _initialize(self):
        super(GrinchPlayerModel, self)._initialize()
        self._addNumberProperty('score', 0)
        self._addStringProperty('vehicleName', '')
        self._addStringProperty('vehicleType', VehicleTypeEnum.LIGHTTANK.value)
        self._addNumberProperty('carryingItems', 0)
        self._addStringProperty('platoon')
        self._addBoolProperty('isCurrentPlayer', False)
        self._addBoolProperty('isDead', False)
        self._addBoolProperty('isCurrentPlatoon', False)
        self._addNumberProperty('kills', 0)
