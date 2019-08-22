# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_royale/royale_models.py
import operator
from collections import namedtuple
from gui.impl.gen import R
from gui.impl import backport
from gui.Scaleform.genConsts.BATTLEROYALE_ALIASES import BATTLEROYALE_ALIASES
from season_common import GameSeason
from shared_utils import CONST_CONTAINER
TitleData = namedtuple('TitleData', 'title, points')
DEFAULT_TITLE = TitleData(0, 0)

class ProgressEntityState(CONST_CONTAINER):
    UNDEFINED = 2
    NOT_ACQUIRED = 2
    ACQUIRED = 4
    LOST = 8
    CURRENT = 16
    NEW_FOR_PLAYER = 32


class BattleRoyaleCycle(namedtuple('BattleRoyaleCycle', 'ID, status, startDate, endDate, ordinalNumber')):

    def __cmp__(self, other):
        return cmp(self.ID, other.ID)


class BattleRoyaleSeason(GameSeason):

    def _buildCycle(self, idx, status, start, end, number):
        return BattleRoyaleCycle(idx, status, start, end, number)


class TitleStep(object):

    def __init__(self, stepID, stepState):
        super(TitleStep, self).__init__()
        self._stepID = stepID
        self._state = stepState

    def __eq__(self, other):
        return False if self.getID() != other.getID() or self.getState() != other.getState() else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def getID(self):
        return self._stepID

    def getState(self):
        return self._state

    def isAcquired(self):
        return self._state & ProgressEntityState.ACQUIRED > 0

    def isCurrent(self):
        return self._state & ProgressEntityState.CURRENT > 0

    def isLost(self):
        return self._state & ProgressEntityState.LOST > 0

    def isNewForPlayer(self):
        return self._state & ProgressEntityState.NEW_FOR_PLAYER > 0


class TitleProgress(object):

    def __init__(self, steps):
        super(TitleProgress, self).__init__()
        self._steps = steps

    def __eq__(self, other):
        return False if self.getSteps() != other.getSteps() else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def getSteps(self):
        return self._steps

    def getAcquiredSteps(self):
        return filter(operator.methodcaller('isAcquired'), self._steps)


class Title(object):
    __ICON_SIZES = {BATTLEROYALE_ALIASES.TITLE_TINY: '24x24',
     BATTLEROYALE_ALIASES.TITLE_SMALL: '70x70',
     BATTLEROYALE_ALIASES.TITLE_MEDIUM: '110x110',
     BATTLEROYALE_ALIASES.TITLE_BIG: '160x160',
     BATTLEROYALE_ALIASES.TITLE_HUGE: '260x260'}

    def __init__(self, titleID, titleState, progress=None, quest=None):
        super(Title, self).__init__()
        self._titleID = titleID
        self._state = titleState
        self._progress = progress
        self._quest = quest

    def __eq__(self, other):
        if self.getState() != other.getState():
            return False
        return False if self.getID() != other.getID() or self.getProgress() != other.getProgress() else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def isRewardClaimed(self):
        return self._quest is None or self._quest.isCompleted()

    def isAcquired(self):
        return self._state & ProgressEntityState.ACQUIRED > 0

    def isCurrent(self):
        return self._state & ProgressEntityState.CURRENT > 0

    def isLost(self):
        return self._state & ProgressEntityState.LOST > 0

    def isNewForPlayer(self):
        return self._state & ProgressEntityState.NEW_FOR_PLAYER > 0

    def getID(self):
        return self._titleID

    def getIcon(self, size):
        size = self.__ICON_SIZES.get(size, '70x70')
        return backport.image(R.images.gui.maps.icons.battleRoyale.titles.num(size).dyn('title{}'.format(self.getID()))())

    def getProgress(self):
        return self._progress

    def getQuest(self):
        return self._quest

    def getState(self):
        return self._state

    def getAchievedStepsCount(self):
        return len(self.getProgress().getAcquiredSteps())

    def getStepsCountToAchieve(self):
        return len(self.getProgress().getSteps())
