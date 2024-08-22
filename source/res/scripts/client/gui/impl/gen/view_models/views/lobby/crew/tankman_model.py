# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/tankman_model.py
from enum import Enum
from gui.impl.gen import R
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_list_model import CrewSkillListModel

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

    def __init__(self, properties=22, commands=0):
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

    @property
    def skills(self):
        return self._getViewModel(2)

    @staticmethod
    def getSkillsType():
        return CrewSkillListModel

    def getTankmanID(self):
        return self._getNumber(3)

    def setTankmanID(self, value):
        self._setNumber(3, value)

    def getRecruitID(self):
        return self._getString(4)

    def setRecruitID(self, value):
        self._setString(4, value)

    def getIconName(self):
        return self._getString(5)

    def setIconName(self, value):
        self._setString(5, value)

    def getNation(self):
        return self._getString(6)

    def setNation(self, value):
        self._setString(6, value)

    def getRole(self):
        return TankmanRole(self._getString(7))

    def setRole(self, value):
        self._setString(7, value.value)

    def getTankmanKind(self):
        return TankmanKind(self._getString(8))

    def setTankmanKind(self, value):
        self._setString(8, value.value)

    def getCardState(self):
        return TankmanCardState(self._getString(9))

    def setCardState(self, value):
        self._setString(9, value.value)

    def getLocation(self):
        return TankmanLocation(self._getString(10))

    def setLocation(self, value):
        self._setString(10, value.value)

    def getFullUserName(self):
        return self._getString(11)

    def setFullUserName(self, value):
        self._setString(11, value)

    def getHasRolePenalty(self):
        return self._getBool(12)

    def setHasRolePenalty(self, value):
        self._setBool(12, value)

    def getIsInSkin(self):
        return self._getBool(13)

    def setIsInSkin(self, value):
        self._setBool(13, value)

    def getLastSkillLevel(self):
        return self._getNumber(14)

    def setLastSkillLevel(self, value):
        self._setNumber(14, value)

    def getRecruitGlowImage(self):
        return self._getResource(15)

    def setRecruitGlowImage(self, value):
        self._setResource(15, value)

    def getIsMainActionDisabled(self):
        return self._getBool(16)

    def setIsMainActionDisabled(self, value):
        self._setBool(16, value)

    def getTimeToDismiss(self):
        return self._getNumber(17)

    def setTimeToDismiss(self, value):
        self._setNumber(17, value)

    def getHasVoiceover(self):
        return self._getBool(18)

    def setHasVoiceover(self, value):
        self._setBool(18, value)

    def getHasPostProgression(self):
        return self._getBool(19)

    def setHasPostProgression(self, value):
        self._setBool(19, value)

    def getDisableIcon(self):
        return self._getResource(20)

    def setDisableIcon(self, value):
        self._setResource(20, value)

    def getDisableReason(self):
        return self._getResource(21)

    def setDisableReason(self, value):
        self._setResource(21, value)

    def _initialize(self):
        super(TankmanModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('tankmanVehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('skills', CrewSkillListModel())
        self._addNumberProperty('tankmanID', 0)
        self._addStringProperty('recruitID', '')
        self._addStringProperty('iconName', '')
        self._addStringProperty('nation', '')
        self._addStringProperty('role', TankmanRole.ANY.value)
        self._addStringProperty('tankmanKind')
        self._addStringProperty('cardState', TankmanCardState.DEFAULT.value)
        self._addStringProperty('location', TankmanLocation.INBARRACKS.value)
        self._addStringProperty('fullUserName', '')
        self._addBoolProperty('hasRolePenalty', False)
        self._addBoolProperty('isInSkin', False)
        self._addNumberProperty('lastSkillLevel', 0)
        self._addResourceProperty('recruitGlowImage', R.invalid())
        self._addBoolProperty('isMainActionDisabled', False)
        self._addNumberProperty('timeToDismiss', 0)
        self._addBoolProperty('hasVoiceover', False)
        self._addBoolProperty('hasPostProgression', False)
        self._addResourceProperty('disableIcon', R.invalid())
        self._addResourceProperty('disableReason', R.invalid())
