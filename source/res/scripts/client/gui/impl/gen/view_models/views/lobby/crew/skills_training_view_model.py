# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/skills_training_view_model.py
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.common.vehicle_info_model import VehicleInfoModel
from gui.impl.gen.view_models.views.lobby.crew.skills_list_model import SkillsListModel

class SkillsTrainingViewModel(ViewModel):
    __slots__ = ('onClose',)

    def __init__(self, properties=11, commands=1):
        super(SkillsTrainingViewModel, self).__init__(properties=properties, commands=commands)

    @property
    def vehicleInfo(self):
        return self._getViewModel(0)

    @staticmethod
    def getVehicleInfoType():
        return VehicleInfoModel

    @property
    def skillsList(self):
        return self._getViewModel(1)

    @staticmethod
    def getSkillsListType():
        return SkillsListModel

    def getIsFemale(self):
        return self._getBool(2)

    def setIsFemale(self, value):
        self._setBool(2, value)

    def getIsMajorQualification(self):
        return self._getBool(3)

    def setIsMajorQualification(self, value):
        self._setBool(3, value)

    def getRole(self):
        return self._getString(4)

    def setRole(self, value):
        self._setString(4, value)

    def getCurrentSkillsAmount(self):
        return self._getNumber(5)

    def setCurrentSkillsAmount(self, value):
        self._setNumber(5, value)

    def getTotalSkillsAmount(self):
        return self._getNumber(6)

    def setTotalSkillsAmount(self, value):
        self._setNumber(6, value)

    def getAvailableSkillsAmount(self):
        return self._getNumber(7)

    def setAvailableSkillsAmount(self, value):
        self._setNumber(7, value)

    def getAreAllSkillsLearned(self):
        return self._getBool(8)

    def setAreAllSkillsLearned(self, value):
        self._setBool(8, value)

    def getSkillsEfficiency(self):
        return self._getReal(9)

    def setSkillsEfficiency(self, value):
        self._setReal(9, value)

    def getIsAnySkillSelected(self):
        return self._getBool(10)

    def setIsAnySkillSelected(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(SkillsTrainingViewModel, self)._initialize()
        self._addViewModelProperty('vehicleInfo', VehicleInfoModel())
        self._addViewModelProperty('skillsList', SkillsListModel())
        self._addBoolProperty('isFemale', False)
        self._addBoolProperty('isMajorQualification', False)
        self._addStringProperty('role', '')
        self._addNumberProperty('currentSkillsAmount', 0)
        self._addNumberProperty('totalSkillsAmount', 0)
        self._addNumberProperty('availableSkillsAmount', 0)
        self._addBoolProperty('areAllSkillsLearned', False)
        self._addRealProperty('skillsEfficiency', 0.0)
        self._addBoolProperty('isAnySkillSelected', False)
        self.onClose = self._addCommand('onClose')
