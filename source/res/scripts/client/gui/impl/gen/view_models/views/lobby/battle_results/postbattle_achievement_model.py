# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_results/postbattle_achievement_model.py
from frameworks.wulf import ViewModel

class PostbattleAchievementModel(ViewModel):
    __slots__ = ()
    ACHIEVEMENT_LEFT_BLOCK = 'left'
    ACHIEVEMENT_RIGHT_BLOCK = 'right'
    MARK_OF_MASTERY = 'markOfMastery'
    MARK_ON_GUN = 'marksOnGun'

    def __init__(self, properties=6, commands=0):
        super(PostbattleAchievementModel, self).__init__(properties=properties, commands=commands)

    def getName(self):
        return self._getString(0)

    def setName(self, value):
        self._setString(0, value)

    def getGroupID(self):
        return self._getString(1)

    def setGroupID(self, value):
        self._setString(1, value)

    def getIsEpic(self):
        return self._getBool(2)

    def setIsEpic(self, value):
        self._setBool(2, value)

    def getIconName(self):
        return self._getString(3)

    def setIconName(self, value):
        self._setString(3, value)

    def getTooltipId(self):
        return self._getString(4)

    def setTooltipId(self, value):
        self._setString(4, value)

    def getTooltipArgs(self):
        return self._getString(5)

    def setTooltipArgs(self, value):
        self._setString(5, value)

    def _initialize(self):
        super(PostbattleAchievementModel, self)._initialize()
        self._addStringProperty('name', '')
        self._addStringProperty('groupID', '')
        self._addBoolProperty('isEpic', False)
        self._addStringProperty('iconName', '')
        self._addStringProperty('tooltipId', '')
        self._addStringProperty('tooltipArgs', '')
