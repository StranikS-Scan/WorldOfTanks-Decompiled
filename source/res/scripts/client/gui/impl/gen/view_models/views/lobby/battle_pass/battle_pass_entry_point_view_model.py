# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/gen/view_models/views/lobby/battle_pass/battle_pass_entry_point_view_model.py
from enum import Enum
from frameworks.wulf import Array
from frameworks.wulf import ViewModel

class AnimationState(Enum):
    NORMAL = 'normal'
    NEW_LEVEL = 'newLevel'
    BUY_BATTLE_PASS = 'buyBattlePass'
    NOT_TAKEN_REWARDS = 'notTakenRewards'
    PROGRESSION_COMPLETED = 'progressionCompleted'
    NEW_CHAPTER = 'newChapter'
    CHANGE_PROGRESS = 'changeProgress'
    CHAPTER_NOT_CHOSEN = 'chapterNotChosen'


class BPState(Enum):
    DISABLED = 'disabled'
    SEASON_WAITING = 'seasonWaiting'
    NORMAL = 'normal'
    ATTENTION = 'attention'


class ChapterType(Enum):
    DEFAULT = 'default'
    MARATHON = 'marathon'
    RESOURCE = 'resource'


class BattlePassEntryPointViewModel(ViewModel):
    __slots__ = ('onClick',)

    def __init__(self, properties=21, commands=1):
        super(BattlePassEntryPointViewModel, self).__init__(properties=properties, commands=commands)

    def getChapterType(self):
        return ChapterType(self._getString(0))

    def setChapterType(self, value):
        self._setString(0, value.value)

    def getAvailableChapterTypes(self):
        return self._getArray(1)

    def setAvailableChapterTypes(self, value):
        self._setArray(1, value)

    def getIsResourceAvailable(self):
        return self._getBool(2)

    def setIsResourceAvailable(self, value):
        self._setBool(2, value)

    def getPrevLevel(self):
        return self._getNumber(3)

    def setPrevLevel(self, value):
        self._setNumber(3, value)

    def getLevel(self):
        return self._getNumber(4)

    def setLevel(self, value):
        self._setNumber(4, value)

    def getPrevProgression(self):
        return self._getReal(5)

    def setPrevProgression(self, value):
        self._setReal(5, value)

    def getProgression(self):
        return self._getReal(6)

    def setProgression(self, value):
        self._setReal(6, value)

    def getBattlePassState(self):
        return BPState(self._getString(7))

    def setBattlePassState(self, value):
        self._setString(7, value.value)

    def getIsSmall(self):
        return self._getBool(8)

    def setIsSmall(self, value):
        self._setBool(8, value)

    def getTooltipID(self):
        return self._getNumber(9)

    def setTooltipID(self, value):
        self._setNumber(9, value)

    def getIsFirstShow(self):
        return self._getBool(10)

    def setIsFirstShow(self, value):
        self._setBool(10, value)

    def getAnimState(self):
        return AnimationState(self._getString(11))

    def setAnimState(self, value):
        self._setString(11, value.value)

    def getAnimStateKey(self):
        return self._getNumber(12)

    def setAnimStateKey(self, value):
        self._setNumber(12, value)

    def getIsProgressionCompleted(self):
        return self._getBool(13)

    def setIsProgressionCompleted(self, value):
        self._setBool(13, value)

    def getHasBattlePass(self):
        return self._getBool(14)

    def setHasBattlePass(self, value):
        self._setBool(14, value)

    def getNotChosenRewardCount(self):
        return self._getNumber(15)

    def setNotChosenRewardCount(self, value):
        self._setNumber(15, value)

    def getPreviousChapterID(self):
        return self._getNumber(16)

    def setPreviousChapterID(self, value):
        self._setNumber(16, value)

    def getChapterID(self):
        return self._getNumber(17)

    def setChapterID(self, value):
        self._setNumber(17, value)

    def getBattleType(self):
        return self._getString(18)

    def setBattleType(self, value):
        self._setString(18, value)

    def getIsChapterChosen(self):
        return self._getBool(19)

    def setIsChapterChosen(self, value):
        self._setBool(19, value)

    def getFreePoints(self):
        return self._getNumber(20)

    def setFreePoints(self, value):
        self._setNumber(20, value)

    def _initialize(self):
        super(BattlePassEntryPointViewModel, self)._initialize()
        self._addStringProperty('chapterType')
        self._addArrayProperty('availableChapterTypes', Array())
        self._addBoolProperty('isResourceAvailable', False)
        self._addNumberProperty('prevLevel', 0)
        self._addNumberProperty('level', 0)
        self._addRealProperty('prevProgression', 0.0)
        self._addRealProperty('progression', -1)
        self._addStringProperty('battlePassState')
        self._addBoolProperty('isSmall', False)
        self._addNumberProperty('tooltipID', 0)
        self._addBoolProperty('isFirstShow', False)
        self._addStringProperty('animState')
        self._addNumberProperty('animStateKey', 0)
        self._addBoolProperty('isProgressionCompleted', False)
        self._addBoolProperty('hasBattlePass', False)
        self._addNumberProperty('notChosenRewardCount', 0)
        self._addNumberProperty('previousChapterID', 0)
        self._addNumberProperty('chapterID', 0)
        self._addStringProperty('battleType', '')
        self._addBoolProperty('isChapterChosen', False)
        self._addNumberProperty('freePoints', 0)
        self.onClick = self._addCommand('onClick')
