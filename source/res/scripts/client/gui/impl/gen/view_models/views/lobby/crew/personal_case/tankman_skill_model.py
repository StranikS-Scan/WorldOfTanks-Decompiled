# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/tankman_skill_model.py
from frameworks.wulf import ViewModel

class TankmanSkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=6, commands=0):
        super(TankmanSkillModel, self).__init__(properties=properties, commands=commands)

    def getSkillId(self):
        return self._getString(0)

    def setSkillId(self, value):
        self._setString(0, value)

    def getSkillUserName(self):
        return self._getString(1)

    def setSkillUserName(self, value):
        self._setString(1, value)

    def getSkillIcon(self):
        return self._getString(2)

    def setSkillIcon(self, value):
        self._setString(2, value)

    def getSkillProgress(self):
        return self._getNumber(3)

    def setSkillProgress(self, value):
        self._setNumber(3, value)

    def getIsInProgress(self):
        return self._getBool(4)

    def setIsInProgress(self, value):
        self._setBool(4, value)

    def getIsZero(self):
        return self._getBool(5)

    def setIsZero(self, value):
        self._setBool(5, value)

    def _initialize(self):
        super(TankmanSkillModel, self)._initialize()
        self._addStringProperty('skillId', '')
        self._addStringProperty('skillUserName', '')
        self._addStringProperty('skillIcon', '')
        self._addNumberProperty('skillProgress', 0)
        self._addBoolProperty('isInProgress', False)
        self._addBoolProperty('isZero', False)
