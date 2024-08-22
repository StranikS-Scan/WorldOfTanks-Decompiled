# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_widget_tankman_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_skill_list_model import CrewSkillListModel

class CrewWidgetTankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=20, commands=0):
        super(CrewWidgetTankmanModel, self).__init__(properties=properties, commands=commands)

    @property
    def skills(self):
        return self._getViewModel(0)

    @staticmethod
    def getSkillsType():
        return CrewSkillListModel

    @property
    def possibleSkills(self):
        return self._getViewModel(1)

    @staticmethod
    def getPossibleSkillsType():
        return CrewSkillListModel

    def getTankmanID(self):
        return self._getNumber(2)

    def setTankmanID(self, value):
        self._setNumber(2, value)

    def getFullName(self):
        return self._getString(3)

    def setFullName(self, value):
        self._setString(3, value)

    def getIcon(self):
        return self._getString(4)

    def setIcon(self, value):
        self._setString(4, value)

    def getRoles(self):
        return self._getArray(5)

    def setRoles(self, value):
        self._setArray(5, value)

    @staticmethod
    def getRolesType():
        return unicode

    def getNewSkillsAmount(self):
        return self._getNumber(6)

    def setNewSkillsAmount(self, value):
        self._setNumber(6, value)

    def getPossibleSkillsAmount(self):
        return self._getNumber(7)

    def setPossibleSkillsAmount(self, value):
        self._setNumber(7, value)

    def getLastPossibleSkillLevel(self):
        return self._getReal(8)

    def setLastPossibleSkillLevel(self, value):
        self._setReal(8, value)

    def getHasPossibleProgress(self):
        return self._getBool(9)

    def setHasPossibleProgress(self, value):
        self._setBool(9, value)

    def getLastSkillLevel(self):
        return self._getReal(10)

    def setLastSkillLevel(self, value):
        self._setReal(10, value)

    def getLastSkillLevelFull(self):
        return self._getReal(11)

    def setLastSkillLevelFull(self, value):
        self._setReal(11, value)

    def getIsLessMastered(self):
        return self._getBool(12)

    def setIsLessMastered(self, value):
        self._setBool(12, value)

    def getIsInSkin(self):
        return self._getBool(13)

    def setIsInSkin(self, value):
        self._setBool(13, value)

    def getIsFemale(self):
        return self._getBool(14)

    def setIsFemale(self, value):
        self._setBool(14, value)

    def getHasWarning(self):
        return self._getBool(15)

    def setHasWarning(self, value):
        self._setBool(15, value)

    def getIsInteractive(self):
        return self._getBool(16)

    def setIsInteractive(self, value):
        self._setBool(16, value)

    def getHasPostProgression(self):
        return self._getBool(17)

    def setHasPostProgression(self, value):
        self._setBool(17, value)

    def getSkillsEfficiency(self):
        return self._getReal(18)

    def setSkillsEfficiency(self, value):
        self._setReal(18, value)

    def getPossibleSkillsEfficiency(self):
        return self._getReal(19)

    def setPossibleSkillsEfficiency(self, value):
        self._setReal(19, value)

    def _initialize(self):
        super(CrewWidgetTankmanModel, self)._initialize()
        self._addViewModelProperty('skills', CrewSkillListModel())
        self._addViewModelProperty('possibleSkills', CrewSkillListModel())
        self._addNumberProperty('tankmanID', 0)
        self._addStringProperty('fullName', '')
        self._addStringProperty('icon', '')
        self._addArrayProperty('roles', Array())
        self._addNumberProperty('newSkillsAmount', 0)
        self._addNumberProperty('possibleSkillsAmount', 0)
        self._addRealProperty('lastPossibleSkillLevel', -1)
        self._addBoolProperty('hasPossibleProgress', False)
        self._addRealProperty('lastSkillLevel', 0.0)
        self._addRealProperty('lastSkillLevelFull', 0.0)
        self._addBoolProperty('isLessMastered', False)
        self._addBoolProperty('isInSkin', False)
        self._addBoolProperty('isFemale', False)
        self._addBoolProperty('hasWarning', False)
        self._addBoolProperty('isInteractive', False)
        self._addBoolProperty('hasPostProgression', False)
        self._addRealProperty('skillsEfficiency', 0.0)
        self._addRealProperty('possibleSkillsEfficiency', -1)
