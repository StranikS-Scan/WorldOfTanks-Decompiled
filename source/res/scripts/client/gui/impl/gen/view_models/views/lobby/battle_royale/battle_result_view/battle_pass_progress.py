# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_royale/battle_result_view/battle_pass_progress.py
from enum import Enum
from frameworks.wulf import ViewModel

class ChapterStates(Enum):
    ACTIVE = 'active'
    PAUSED = 'paused'
    COMPLETED = 'completed'


class BattlePassProgress(ViewModel):
    __slots__ = ('onSubmitClick',)
    BP_STATE_NORMAL = 'normal'
    BP_STATE_BOUGHT = 'bought'
    BP_STATE_DISABLED = 'disabled'
    PROGRESSION_IN_PROGRESS = 'progressionInProgress'
    PROGRESSION_COMPLETED = 'progressionCompleted'

    def __init__(self, properties=12, commands=1):
        super(BattlePassProgress, self).__init__(properties=properties, commands=commands)

    def getCurrentLevel(self):
        return self._getNumber(0)

    def setCurrentLevel(self, value):
        self._setNumber(0, value)

    def getMaxPoints(self):
        return self._getNumber(1)

    def setMaxPoints(self, value):
        self._setNumber(1, value)

    def getEarnedPoints(self):
        return self._getNumber(2)

    def setEarnedPoints(self, value):
        self._setNumber(2, value)

    def getCurrentLevelPoints(self):
        return self._getNumber(3)

    def setCurrentLevelPoints(self, value):
        self._setNumber(3, value)

    def getProgressionState(self):
        return self._getString(4)

    def setProgressionState(self, value):
        self._setString(4, value)

    def getBattlePassState(self):
        return self._getString(5)

    def setBattlePassState(self, value):
        self._setString(5, value)

    def getChapterID(self):
        return self._getNumber(6)

    def setChapterID(self, value):
        self._setNumber(6, value)

    def getHasExtra(self):
        return self._getBool(7)

    def setHasExtra(self, value):
        self._setBool(7, value)

    def getHasResource(self):
        return self._getBool(8)

    def setHasResource(self, value):
        self._setBool(8, value)

    def getChapterState(self):
        return ChapterStates(self._getString(9))

    def setChapterState(self, value):
        self._setString(9, value.value)

    def getIsBattlePassPurchased(self):
        return self._getBool(10)

    def setIsBattlePassPurchased(self, value):
        self._setBool(10, value)

    def getFreePoints(self):
        return self._getNumber(11)

    def setFreePoints(self, value):
        self._setNumber(11, value)

    def _initialize(self):
        super(BattlePassProgress, self)._initialize()
        self._addNumberProperty('currentLevel', 0)
        self._addNumberProperty('maxPoints', 0)
        self._addNumberProperty('earnedPoints', 0)
        self._addNumberProperty('currentLevelPoints', 0)
        self._addStringProperty('progressionState', '')
        self._addStringProperty('battlePassState', '')
        self._addNumberProperty('chapterID', 0)
        self._addBoolProperty('hasExtra', False)
        self._addBoolProperty('hasResource', False)
        self._addStringProperty('chapterState')
        self._addBoolProperty('isBattlePassPurchased', False)
        self._addNumberProperty('freePoints', 0)
        self.onSubmitClick = self._addCommand('onSubmitClick')
