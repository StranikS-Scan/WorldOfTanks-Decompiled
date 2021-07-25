# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/detachment/skill_model.py
from gui.impl.gen import R
from frameworks.wulf import ViewModel

class SkillModel(ViewModel):
    __slots__ = ()
    PERKS = 'perks'
    TALENTS = 'talents'

    def __init__(self, properties=11, commands=0):
        super(SkillModel, self).__init__(properties=properties, commands=commands)

    def getId(self):
        return self._getNumber(0)

    def setId(self, value):
        self._setNumber(0, value)

    def getTitle(self):
        return self._getResource(1)

    def setTitle(self, value):
        self._setResource(1, value)

    def getDescription(self):
        return self._getString(2)

    def setDescription(self, value):
        self._setString(2, value)

    def getCourse(self):
        return self._getResource(3)

    def setCourse(self, value):
        self._setResource(3, value)

    def getIcon(self):
        return self._getString(4)

    def setIcon(self, value):
        self._setString(4, value)

    def getType(self):
        return self._getString(5)

    def setType(self, value):
        self._setString(5, value)

    def getSkillsCount(self):
        return self._getNumber(6)

    def setSkillsCount(self, value):
        self._setNumber(6, value)

    def getSkillsMaxCount(self):
        return self._getNumber(7)

    def setSkillsMaxCount(self, value):
        self._setNumber(7, value)

    def getInstructorPoints(self):
        return self._getNumber(8)

    def setInstructorPoints(self, value):
        self._setNumber(8, value)

    def getBoosterPoints(self):
        return self._getNumber(9)

    def setBoosterPoints(self, value):
        self._setNumber(9, value)

    def getIsOvercapped(self):
        return self._getBool(10)

    def setIsOvercapped(self, value):
        self._setBool(10, value)

    def _initialize(self):
        super(SkillModel, self)._initialize()
        self._addNumberProperty('id', 0)
        self._addResourceProperty('title', R.invalid())
        self._addStringProperty('description', '')
        self._addResourceProperty('course', R.invalid())
        self._addStringProperty('icon', '')
        self._addStringProperty('type', '')
        self._addNumberProperty('skillsCount', 0)
        self._addNumberProperty('skillsMaxCount', 0)
        self._addNumberProperty('instructorPoints', 0)
        self._addNumberProperty('boosterPoints', 0)
        self._addBoolProperty('isOvercapped', False)
