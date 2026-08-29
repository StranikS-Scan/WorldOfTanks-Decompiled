# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/client/white_tiger/gui/impl/gen/view_models/views/lobby/portals/wt_portal_bonus_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class WtPortalBonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=16, commands=0):
        super(WtPortalBonusModel, self).__init__(properties=properties, commands=commands)

    def getIsCollected(self):
        return self._getBool(8)

    def setIsCollected(self, value):
        self._setBool(8, value)

    def getIsCustom(self):
        return self._getBool(9)

    def setIsCustom(self, value):
        self._setBool(9, value)

    def getIsSpecial(self):
        return self._getBool(10)

    def setIsSpecial(self, value):
        self._setBool(10, value)

    def getName(self):
        return self._getString(11)

    def setName(self, value):
        self._setString(11, value)

    def getVehicleLvl(self):
        return self._getNumber(12)

    def setVehicleLvl(self, value):
        self._setNumber(12, value)

    def getVehicleCD(self):
        return self._getNumber(13)

    def setVehicleCD(self, value):
        self._setNumber(13, value)

    def getStyleCD(self):
        return self._getNumber(14)

    def setStyleCD(self, value):
        self._setNumber(14, value)

    def getVehicleType(self):
        return VehicleType(self._getString(15))

    def setVehicleType(self, value):
        self._setString(15, value.value)

    def _initialize(self):
        super(WtPortalBonusModel, self)._initialize()
        self._addBoolProperty('isCollected', False)
        self._addBoolProperty('isCustom', False)
        self._addBoolProperty('isSpecial', False)
        self._addStringProperty('name', '')
        self._addNumberProperty('vehicleLvl', 0)
        self._addNumberProperty('vehicleCD', 0)
        self._addNumberProperty('styleCD', 0)
        self._addStringProperty('vehicleType')
