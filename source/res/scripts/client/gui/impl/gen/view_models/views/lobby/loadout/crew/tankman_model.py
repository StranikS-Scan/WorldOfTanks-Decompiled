# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/loadout/crew/tankman_model.py
from frameworks.wulf import Array, ViewModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.bonus_skills_model import BonusSkillsModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.native_vehicle import NativeVehicle
from gui.impl.gen.view_models.views.lobby.loadout.crew.perk_model import PerkModel
from gui.impl.gen.view_models.views.lobby.loadout.crew.vehicle_bonus import VehicleBonus
from gui.impl.gen.view_models.views.lobby.loadout.crew.vehicle_bonus_detail_model import VehicleBonusDetailModel

class TankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=23, commands=0):
        super(TankmanModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleBonus(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleBonusType():
        return VehicleBonus

    @property
    def nativeVehicle(self):
        return self._getViewModel(1)

    @staticmethod
    def getNativeVehicleType():
        return NativeVehicle

    def getId(self):
        return self._getNumber(2)

    def setId(self, value):
        self._setNumber(2, value)

    def getLevel(self):
        return self._getNumber(3)

    def setLevel(self, value):
        self._setNumber(3, value)

    def getMaxLevelAchieved(self):
        return self._getBool(4)

    def setMaxLevelAchieved(self, value):
        self._setBool(4, value)

    def getCrewSkinId(self):
        return self._getString(5)

    def setCrewSkinId(self, value):
        self._setString(5, value)

    def getCustomizedSkin(self):
        return self._getBool(6)

    def setCustomizedSkin(self, value):
        self._setBool(6, value)

    def getNewPerksCount(self):
        return self._getNumber(7)

    def setNewPerksCount(self, value):
        self._setNumber(7, value)

    def getNewBonusPerksCount(self):
        return self._getNumber(8)

    def setNewBonusPerksCount(self, value):
        self._setNumber(8, value)

    def getTrainingProgress(self):
        return self._getNumber(9)

    def setTrainingProgress(self, value):
        self._setNumber(9, value)

    def getQuickTraining(self):
        return self._getBool(10)

    def setQuickTraining(self, value):
        self._setBool(10, value)

    def getPerks(self):
        return self._getArray(11)

    def setPerks(self, value):
        self._setArray(11, value)

    @staticmethod
    def getPerksType():
        return PerkModel

    def getBonusSkills(self):
        return self._getArray(12)

    def setBonusSkills(self, value):
        self._setArray(12, value)

    @staticmethod
    def getBonusSkillsType():
        return BonusSkillsModel

    def getVehicleBonusDetails(self):
        return self._getArray(13)

    def setVehicleBonusDetails(self, value):
        self._setArray(13, value)

    @staticmethod
    def getVehicleBonusDetailsType():
        return VehicleBonusDetailModel

    def getRole(self):
        return self._getString(14)

    def setRole(self, value):
        self._setString(14, value)

    def getIsInNativeTank(self):
        return self._getBool(15)

    def setIsInNativeTank(self, value):
        self._setBool(15, value)

    def getNation(self):
        return self._getString(16)

    def setNation(self, value):
        self._setString(16, value)

    def getFullName(self):
        return self._getString(17)

    def setFullName(self, value):
        self._setString(17, value)

    def getSkillsEfficiency(self):
        return self._getReal(18)

    def setSkillsEfficiency(self, value):
        self._setReal(18, value)

    def getSkillsEfficiencyXP(self):
        return self._getNumber(19)

    def setSkillsEfficiencyXP(self, value):
        self._setNumber(19, value)

    def getCurrentVehicleSkillsEfficiency(self):
        return self._getReal(20)

    def setCurrentVehicleSkillsEfficiency(self, value):
        self._setReal(20, value)

    def getTankmanSuitable(self):
        return self._getBool(21)

    def setTankmanSuitable(self, value):
        self._setBool(21, value)

    def getLockedByVehicle(self):
        return self._getBool(22)

    def setLockedByVehicle(self, value):
        self._setBool(22, value)

    def _initialize(self):
        super(TankmanModel, self)._initialize()
        self._addViewModelProperty('vehicleBonus', VehicleBonus())
        self._addViewModelProperty('nativeVehicle', NativeVehicle())
        self._addNumberProperty('id', 0)
        self._addNumberProperty('level', 0)
        self._addBoolProperty('maxLevelAchieved', False)
        self._addStringProperty('crewSkinId', '')
        self._addBoolProperty('customizedSkin', False)
        self._addNumberProperty('newPerksCount', 0)
        self._addNumberProperty('newBonusPerksCount', 0)
        self._addNumberProperty('trainingProgress', -1)
        self._addBoolProperty('quickTraining', False)
        self._addArrayProperty('perks', Array())
        self._addArrayProperty('bonusSkills', Array())
        self._addArrayProperty('vehicleBonusDetails', Array())
        self._addStringProperty('role', '')
        self._addBoolProperty('isInNativeTank', False)
        self._addStringProperty('nation', '')
        self._addStringProperty('fullName', '')
        self._addRealProperty('skillsEfficiency', 0.0)
        self._addNumberProperty('skillsEfficiencyXP', 0)
        self._addRealProperty('currentVehicleSkillsEfficiency', 0.0)
        self._addBoolProperty('tankmanSuitable', True)
        self._addBoolProperty('lockedByVehicle', False)
