# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tankman_model.py
from enum import Enum
from frameworks.wulf import Array
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_tankman_skill_model import CrewWidgetTankmanSkillModel

class TankmanRole(Enum):
    ANY = 'any'
    COMMANDER = 'commander'
    RADIOMAN = 'radioman'
    DRIVER = 'driver'
    GUNNER = 'gunner'
    LOADER = 'loader'


class TankmanLocation(Enum):
    INBARRACKS = 'in_barracks'
    INTANK = 'in_tank'
    DISMISSED = 'dismissed'


class TankmanKind(Enum):
    TANKMAN = 'tankman'
    RECRUIT = 'recruit'
    DISMISSED = 'dismissed'


class TankmanCardState(Enum):
    DEFAULT = 'default'
    SELECTED = 'selected'
    DISABLED = 'disabled'


class TankmanInfo(Enum):
    ISLOCKCREW = 'isLockCrew'
    TANKMANHASROLE = 'tankmanHasRole'


class TankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(TankmanModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    @property
    def tankmanVehicleInfo(self):
        return self._getViewModel(1)

    @staticmethod
    def getTankmanVehicleInfoType():
        return VehicleInfoModel

    def getTankmanID(self):
        return self._getNumber(2)

    def setTankmanID(self, value):
        self._setNumber(2, value)

    def getRecruitID(self):
        return self._getString(3)

    def setRecruitID(self, value):
        self._setString(3, value)

    def getIconName(self):
        return self._getString(4)

    def setIconName(self, value):
        self._setString(4, value)

    def getNation(self):
        return self._getString(5)

    def setNation(self, value):
        self._setString(5, value)

    def getRole(self):
        return TankmanRole(self._getString(6))

    def setRole(self, value):
        self._setString(6, value.value)

    def getTankmanKind(self):
        return TankmanKind(self._getString(7))

    def setTankmanKind(self, value):
        self._setString(7, value.value)

    def getCardState(self):
        return TankmanCardState(self._getString(8))

    def setCardState(self, value):
        self._setString(8, value.value)

    def getLocation(self):
        return TankmanLocation(self._getString(9))

    def setLocation(self, value):
        self._setString(9, value.value)

    def getFullUserName(self):
        return self._getString(10)

    def setFullUserName(self, value):
        self._setString(10, value)

    def getSpecializationLevel(self):
        return self._getNumber(11)

    def setSpecializationLevel(self, value):
        self._setNumber(11, value)

    def getHasRolePenalty(self):
        return self._getBool(12)

    def setHasRolePenalty(self, value):
        self._setBool(12, value)

    def getHasSpecializationLevelPenalty(self):
        return self._getBool(13)

    def setHasSpecializationLevelPenalty(self, value):
        self._setBool(13, value)

    def getIsInSkin(self):
        return self._getBool(14)

    def setIsInSkin(self, value):
        self._setBool(14, value)

    def getSkills(self):
        return self._getArray(15)

    def setSkills(self, value):
        self._setArray(15, value)

    @staticmethod
    def getSkillsType():
        return CrewWidgetTankmanSkillModel

    def getLastSkillLevel(self):
        return self._getNumber(16)

    def setLastSkillLevel(self, value):
        self._setNumber(16, value)

    def getRecruitGlowImage(self):
        return self._getResource(17)

    def setRecruitGlowImage(self, value):
        self._setResource(17, value)

    def getIsMainActionDisabled(self):
        return self._getBool(18)

    def setIsMainActionDisabled(self, value):
        self._setBool(18, value)

    def getTimeToDismiss(self):
        return self._getNumber(19)

    def setTimeToDismiss(self, value):
        self._setNumber(19, value)

    def getHasVoiceover(self):
        return self._getBool(20)

    def setHasVoiceover(self, value):
        self._setBool(20, value)

    def getDisableIcon(self):
        return self._getResource(21)

    def setDisableIcon(self, value):
        self._setResource(21, value)

    def getDisableReason(self):
        return self._getResource(22)

    def setDisableReason(self, value):
        self._setResource(22, value)

    def _initialize(self):
        super(TankmanModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('tankmanVehicleInfo', VehicleInfoModel())
        self._addNumberProperty('tankmanID', 0)
        self._addStringProperty('recruitID', '')
        self._addStringProperty('iconName', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('role', TankmanRole.ANY.value)
        self._addStringProperty('tankmanKind')
        self._addStringProperty('cardState')
        self._addStringProperty('location', TankmanLocation.INBARRACKS.value)
        self._addStringProperty('fullUserName', '')
        self._addNumberProperty('specializationLevel', 0)
        self._addBoolProperty('hasRolePenalty', False)
        self._addBoolProperty('hasSpecializationLevelPenalty', False)
        self._addBoolProperty('isInSkin', False)
        self._addArrayProperty('skills', Array())
        self._addNumberProperty('lastSkillLevel', 0)
        self._addResourceProperty('recruitGlowImage', R.invalid())
        self._addBoolProperty('isMainActionDisabled', False)
        self._addNumberProperty('timeToDismiss', 0)
        self._addBoolProperty('hasVoiceover', False)
        self._addResourceProperty('disableIcon', R.invalid())
        self._addResourceProperty('disableReason', R.invalid())
