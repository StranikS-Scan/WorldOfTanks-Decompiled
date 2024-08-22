# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/common/crew_skill_model.py
from frameworks.wulf import ViewModel

class CrewSkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(CrewSkillModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getCustomName(self):
        return self._getString(1)

    def setCustomName(self, value):
        self._setString(1, value)

    def getIcon(self):
        return self._getString(2)

    def setIcon(self, value):
        self._setString(2, value)

    def getHasInstruction(self):
        return self._getBool(3)

    def setHasInstruction(self, value):
        self._setBool(3, value)

    def getIsIrrelevant(self):
        return self._getBool(4)

    def setIsIrrelevant(self, value):
        self._setBool(4, value)

    def getLevel(self):
        return self._getReal(5)

    def setLevel(self, value):
        self._setReal(5, value)

    def _initialize(self):
        super(CrewSkillModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('customName', '')
        self._addStringProperty('icon', '')
        self._addBoolProperty('hasInstruction', False)
        self._addBoolProperty('isIrrelevant', False)
        self._addRealProperty('level', 0.0)
