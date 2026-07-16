# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/challenges/bonus_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen.view_models.common.missions.bonuses.icon_bonus_model import IconBonusModel
from gui.impl.gen.view_models.views.lobby.challenges.skill_model import SkillModel

class VehicleType(Enum):
    HEAVY = 'heavyTank'
    MEDIUM = 'mediumTank'
    LIGHT = 'lightTank'
    SPG = 'SPG'
    ATSPG = 'AT-SPG'


class BonusModel(IconBonusModel):
    __slots__ = ()

    def __init__(self, properties=22, commands=0):
        super(BonusModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(9)

    def setId(self, value):
        self._setNumber(9, value)

    def getStyleID(self):
        return self._getNumber(10)

    def setStyleID(self, value):
        self._setNumber(10, value)

    def getCount(self):
        return self._getNumber(11)

    def setCount(self, value):
        self._setNumber(11, value)

    def getOverlayType(self):
        return self._getString(12)

    def setOverlayType(self, value):
        self._setString(12, value)

    def getDescription(self):
        return self._getString(13)

    def setDescription(self, value):
        self._setString(13, value)

    def getType(self):
        return VehicleType(self._getString(14))

    def setType(self, value):
        self._setString(14, value.value)

    def getLevel(self):
        return self._getNumber(15)

    def setLevel(self, value):
        self._setNumber(15, value)

    def getIsElite(self):
        return self._getBool(16)

    def setIsElite(self, value):
        self._setBool(16, value)

    def getIsRent(self):
        return self._getBool(17)

    def setIsRent(self, value):
        self._setBool(17, value)

    def getIsInHangar(self):
        return self._getBool(18)

    def setIsInHangar(self, value):
        self._setBool(18, value)

    def getVehicleShortName(self):
        return self._getString(19)

    def setVehicleShortName(self, value):
        self._setString(19, value)

    def getBonusType(self):
        return self._getString(20)

    def setBonusType(self, value):
        self._setString(20, value)

    def getSkills(self):
        return self._getArray(21)

    def setSkills(self, value):
        self._setArray(21, value)

    @staticmethod
    def getSkillsType():
        return SkillModel

    def _initialize(self):
        super(BonusModel, self)._initialize()
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
        self._addStringProperty('vehicleShortName', '')
        self._addStringProperty('bonusType', '')
        self._addArrayProperty('skills', Array())
