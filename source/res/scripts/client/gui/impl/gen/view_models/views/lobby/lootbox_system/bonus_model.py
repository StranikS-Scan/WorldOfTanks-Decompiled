# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/lootbox_system/bonus_model.py
from enum import Enum
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.lootbox_system.compensation_model import CompensationModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class BonusRarity(Enum):
    COMMON = 'common'
    RARE = 'rare'
    EPIC = 'epic'


class BonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=25, commands=0):
        super(BonusModel, self).__init__(properties=properties, commands=commands)

    @property
    def compensation(self):
        return self._getViewModel(9)

    @staticmethod
    def getCompensationType():
        return CompensationModel

    def getName(self):
        return self._getString(10)

    def setName(self, value):
        self._setString(10, value)

    def getId(self):
        return self._getNumber(11)

    def setId(self, value):
        self._setNumber(11, value)

    def getStyleID(self):
        return self._getNumber(12)

    def setStyleID(self, value):
        self._setNumber(12, value)

    def getCount(self):
        return self._getNumber(13)

    def setCount(self, value):
        self._setNumber(13, value)

    def getOverlayType(self):
        return self._getString(14)

    def setOverlayType(self, value):
        self._setString(14, value)

    def getDescription(self):
        return self._getString(15)

    def setDescription(self, value):
        self._setString(15, value)

    def getType(self):
        return VehicleType(self._getString(16))

    def setType(self, value):
        self._setString(16, value.value)

    def getLevel(self):
        return self._getNumber(17)

    def setLevel(self, value):
        self._setNumber(17, value)

    def getIsElite(self):
        return self._getBool(18)

    def setIsElite(self, value):
        self._setBool(18, value)

    def getIsRent(self):
        return self._getBool(19)

    def setIsRent(self, value):
        self._setBool(19, value)

    def getIsInHangar(self):
        return self._getBool(20)

    def setIsInHangar(self, value):
        self._setBool(20, value)

    def getRarity(self):
        return BonusRarity(self._getString(21))

    def setRarity(self, value):
        self._setString(21, value.value)

    def getSpecialAwardName(self):
        return self._getString(22)

    def setSpecialAwardName(self, value):
        self._setString(22, value)

    def getVehicleShortName(self):
        return self._getString(23)

    def setVehicleShortName(self, value):
        self._setString(23, value)

    def getVehicle3DStyleName(self):
        return self._getString(24)

    def setVehicle3DStyleName(self, value):
        self._setString(24, value)

    def _initialize(self):
        super(BonusModel, self)._initialize()
        self._addViewModelProperty('compensation', CompensationModel())
        self._addStringProperty('name', '')
        self._addNumberProperty('id', 0)
        self._addNumberProperty('styleID', 0)
        self._addNumberProperty('count', 0)
        self._addStringProperty('overlayType', '')
        self._addStringProperty('description', '')
        self._addStringProperty('type')
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isElite', False)
        self._addBoolProperty('isRent', False)
        self._addBoolProperty('isInHangar', False)
        self._addStringProperty('rarity')
        self._addStringProperty('specialAwardName', '')
        self._addStringProperty('vehicleShortName', '')
        self._addStringProperty('vehicle3DStyleName', '')
