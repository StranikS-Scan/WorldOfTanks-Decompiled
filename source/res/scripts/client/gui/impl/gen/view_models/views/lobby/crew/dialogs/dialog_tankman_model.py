# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/dialogs/dialog_tankman_model.py
from frameworks.wulf import Array
from frameworks.wulf import ViewModel
from gui.impl.gen.view_models.views.lobby.crew.dialogs.dialog_skill_model import DialogSkillModel

class DialogTankmanModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=9, commands=0):
        super(DialogTankmanModel, self).__init__(properties=properties, commands=commands)

    def getInvId(self):
        return self._getReal(0)

    def setInvId(self, value):
        self._setReal(0, value)

    def getIconName(self):
        return self._getString(1)

    def setIconName(self, value):
        self._setString(1, value)

    def getIsInSkin(self):
        return self._getBool(2)

    def setIsInSkin(self, value):
        self._setBool(2, value)

    def getIsFemale(self):
        return self._getBool(3)

    def setIsFemale(self, value):
        self._setBool(3, value)

    def getFullSkillsCount(self):
        return self._getNumber(4)

    def setFullSkillsCount(self, value):
        self._setNumber(4, value)

    def getIsSelected(self):
        return self._getBool(5)

    def setIsSelected(self, value):
        self._setBool(5, value)

    def getRole(self):
        return self._getString(6)

    def setRole(self, value):
        self._setString(6, value)

    def getSkillEfficiency(self):
        return self._getReal(7)

    def setSkillEfficiency(self, value):
        self._setReal(7, value)

    def getSkills(self):
        return self._getArray(8)

    def setSkills(self, value):
        self._setArray(8, value)

    @staticmethod
    def getSkillsType():
        return DialogSkillModel

    def _initialize(self):
        super(DialogTankmanModel, self)._initialize()
        self._addRealProperty('invId', 0.0)
        self._addStringProperty('iconName', '')
        self._addBoolProperty('isInSkin', False)
        self._addBoolProperty('isFemale', False)
        self._addNumberProperty('fullSkillsCount', 0)
        self._addBoolProperty('isSelected', False)
        self._addStringProperty('role', '')
        self._addRealProperty('skillEfficiency', 0.0)
        self._addArrayProperty('skills', Array())
