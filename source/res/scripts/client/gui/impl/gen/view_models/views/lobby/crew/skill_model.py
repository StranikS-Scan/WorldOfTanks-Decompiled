# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/skill_model.py
from frameworks.wulf import ViewModel

class SkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=11, commands=0):
        super(SkillModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getString(0)

    def setId(self, value):
        self._setString(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getIcon(self):
        return self._getString(3)

    def setIcon(self, value):
        self._setString(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getIsZero(self):
        return self._getBool(5)

    def setIsZero(self, value):
        self._setBool(5, value)

    def getIsIrrelevant(self):
        return self._getBool(6)

    def setIsIrrelevant(self, value):
        self._setBool(6, value)

    def getIsSelected(self):
        return self._getBool(7)

    def setIsSelected(self, value):
        self._setBool(7, value)

    def getIsLearned(self):
        return self._getBool(8)

    def setIsLearned(self, value):
        self._setBool(8, value)

    def getIsImprovedByDirective(self):
        return self._getBool(9)

    def setIsImprovedByDirective(self, value):
        self._setBool(9, value)

    def getIsDirectiveFull(self):
        return self._getBool(10)

    def setIsDirectiveFull(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(SkillModel, self)._initialize()
        self._addStringProperty('id', '')
        self._addStringProperty('name', '')
        self._addStringProperty('description', '')
        self._addStringProperty('icon', '')
        self._addNumberProperty('level', 0)
        self._addBoolProperty('isZero', False)
        self._addBoolProperty('isIrrelevant', False)
        self._addBoolProperty('isSelected', False)
        self._addBoolProperty('isLearned', False)
        self._addBoolProperty('isImprovedByDirective', False)
        self._addBoolProperty('isDirectiveFull', False)
