# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/crew/personal_case/tankman_skill_model.py
from enum import Enum
from frameworks.wulf import ViewModel

class AnimationType(Enum):
    NONE = 'none'
    UNLOCKED = 'unlocked'
    SELECTED = 'selected'


class TankmanSkillModel(ViewModel):
    __slots__ = ()

    def __init__(self, properties=12, commands=0):
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

    def getIsDisabled(self):
        return self._getBool(6)

    def setIsDisabled(self, value):
        self._setBool(6, value)

    def getIsIrrelevant(self):
        return self._getBool(7)

    def setIsIrrelevant(self, value):
        self._setBool(7, value)

    def getIsLocked(self):
        return self._getBool(8)

    def setIsLocked(self, value):
        self._setBool(8, value)

    def getWithDirective(self):
        return self._getBool(9)

    def setWithDirective(self, value):
        self._setBool(9, value)

    def getIsFullDirective(self):
        return self._getBool(10)

    def setIsFullDirective(self, value):
        self._setBool(10, value)

    def getAnimationType(self):
        return AnimationType(self._getString(11))

    def setAnimationType(self, value):
        self._setString(11, value.value)

    def _initialize(self):
        super(TankmanSkillModel, self)._initialize()
        self._addStringProperty('skillId', '')
        self._addStringProperty('skillUserName', '')
        self._addStringProperty('skillIcon', '')
        self._addNumberProperty('skillProgress', 0)
        self._addBoolProperty('isInProgress', False)
        self._addBoolProperty('isZero', False)
        self._addBoolProperty('isDisabled', False)
        self._addBoolProperty('isIrrelevant', False)
        self._addBoolProperty('isLocked', False)
        self._addBoolProperty('withDirective', False)
        self._addBoolProperty('isFullDirective', False)
        self._addStringProperty('animationType', AnimationType.NONE.value)
