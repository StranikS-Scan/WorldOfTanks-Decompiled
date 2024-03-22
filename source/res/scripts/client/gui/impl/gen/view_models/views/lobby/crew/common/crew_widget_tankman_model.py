# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_widget_tankman_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.common.crew_widget_tankman_skill_model import CrewWidgetTankmanSkillModel

class CrewWidgetTankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=18, commands=0):
        super(CrewWidgetTankmanModel, self).__init__(properties=properties, commands=commands)

    def getTankmanID(self):
        return self._getNumber(0)

    def setTankmanID(self, value):
        self._setNumber(0, value)

    def getFullName(self):
        return self._getString(1)

    def setFullName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getRoles(self):
        return self._getArray(3)

    def setRoles(self, value):
        self._setArray(3, value)

    @staticmethod
    def getRolesType():
        return unicode

    def getSkills(self):
        return self._getArray(4)

    def setSkills(self, value):
        self._setArray(4, value)

    @staticmethod
    def getSkillsType():
        return CrewWidgetTankmanSkillModel

    def getNewSkillsAmount(self):
        return self._getNumber(5)

    def setNewSkillsAmount(self, value):
        self._setNumber(5, value)

    def getPossibleSkillsAmount(self):
        return self._getNumber(6)

    def setPossibleSkillsAmount(self, value):
        self._setNumber(6, value)

    def getLastPossibleSkillLevel(self):
        return self._getReal(7)

    def setLastPossibleSkillLevel(self, value):
        self._setReal(7, value)

    def getHasPossibleProgress(self):
        return self._getBool(8)

    def setHasPossibleProgress(self, value):
        self._setBool(8, value)

    def getLastSkillLevel(self):
        return self._getReal(9)

    def setLastSkillLevel(self, value):
        self._setReal(9, value)

    def getLastSkillLevelFull(self):
        return self._getReal(10)

    def setLastSkillLevelFull(self, value):
        self._setReal(10, value)

    def getIsLessMastered(self):
        return self._getBool(11)

    def setIsLessMastered(self, value):
        self._setBool(11, value)

    def getIsInSkin(self):
        return self._getBool(12)

    def setIsInSkin(self, value):
        self._setBool(12, value)

    def getIsFemale(self):
        return self._getBool(13)

    def setIsFemale(self, value):
        self._setBool(13, value)

    def getHasWarning(self):
        return self._getBool(14)

    def setHasWarning(self, value):
        self._setBool(14, value)

    def getIsInteractive(self):
        return self._getBool(15)

    def setIsInteractive(self, value):
        self._setBool(15, value)

    def getSkillsEfficiency(self):
        return self._getReal(16)

    def setSkillsEfficiency(self, value):
        self._setReal(16, value)

    def getPossibleSkillsEfficiency(self):
        return self._getReal(17)

    def setPossibleSkillsEfficiency(self, value):
        self._setReal(17, value)

    def _initialize(self):
        super(CrewWidgetTankmanModel, self)._initialize()
        self._addNumberProperty('tankmanID', 0)
        self._addStringProperty('fullName', '')
        self._addStringProperty('icon', '')
        self._addArrayProperty('roles', Array())
        self._addArrayProperty('skills', Array())
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
        self._addRealProperty('skillsEfficiency', 0.0)
        self._addRealProperty('possibleSkillsEfficiency', -1)
