# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/postbattle/achievement_model.py
from frameworks.wulf import ViewModel

class AchievementModel(ViewModel):
    __slots__ = ()
    ACHIEVEMENT_TOOLTIP = 'achievementTooltip'
    ACHIEVEMENT_LEFT_BLOCK = 'left'
    ACHIEVEMENT_RIGHT_BLOCK = 'right'
    MARKS_ON_GUN = 'marksOnGun'

    def __init__(self, properties=6, commands=0):
        super(AchievementModel, self).__init__(properties=properties, commands=commands)

    def getAchievementID(self):
        return self._getNumber(0)

    def setAchievementID(self, value):
        self._setNumber(0, value)

    def getName(self):
        return self._getString(1)

    def setName(self, value):
        self._setString(1, value)

    def getIsPersonal(self):
        return self._getBool(2)

    def setIsPersonal(self, value):
        self._setBool(2, value)

    def getGroupID(self):
        return self._getString(3)

    def setGroupID(self, value):
        self._setString(3, value)

    def getIsEpic(self):
        return self._getBool(4)

    def setIsEpic(self, value):
        self._setBool(4, value)

    def getIconName(self):
        return self._getString(5)

    def setIconName(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(AchievementModel, self)._initialize()
        self._addNumberProperty('achievementID', 0)
        self._addStringProperty('name', '')
        self._addBoolProperty('isPersonal', False)
        self._addStringProperty('groupID', '')
        self._addBoolProperty('isEpic', False)
        self._addStringProperty('iconName', '')
