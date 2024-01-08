# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_models.py
import operator
import typing
from collections import namedtuple
from gui.impl import backport
from gui.impl.gen import R
from gui.periodic_battles.models import AlertData
from gui.ranked_battles.constants import RankTypes, ZERO_RANK_ID
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from season_common import GameSeason
from shared_utils import CONST_CONTAINER, first
ShieldStatus = namedtuple('ShieldStatus', 'prevHP, hp, maxHP, shieldState, newShieldState')
RankData = namedtuple('RankData', 'rank, steps')
BattleRankInfo = namedtuple('BattleRankInfo', 'level, division, isGroup')

class RankState(CONST_CONTAINER):
    UNDEFINED = 2
    NOT_ACQUIRED = 2
    ACQUIRED = 4
    LOST = 8
    CURRENT = 16
    NEW_FOR_PLAYER = 32
    BONUS = 64


class RankStatus(CONST_CONTAINER):
    NOT_ACHIEVED = 'not_achieved'
    ACHIEVED = 'achieved'
    LOST = 'lost'


class RankChangeStates(CONST_CONTAINER):
    LEAGUE_EARNED = 'leagueEarned'
    DIVISION_EARNED = 'divisionEarned'
    QUAL_EARNED = 'qualificationEarned'
    QUAL_UNBURN_EARNED = 'qualificationUnburnEarned'
    RANK_EARNED = 'rankEarned'
    RANK_UNBURN_PROTECTED = 'rankUnburnProtected'
    RANK_SHIELD_PROTECTED = 'rankShieldProtected'
    RANK_LOST = 'rankLost'
    STEP_EARNED = 'stepEarned'
    BONUS_STEP_EARNED = 'bonusStepEarned'
    STEPS_EARNED = 'stepsEarned'
    BONUS_STEPS_EARNED = 'bonusStepsEarned'
    STEP_LOST = 'stepLost'
    NOTHING_CHANGED = 'nothingChanged'


class RankedCycle(namedtuple('RankedCycle', 'ID, status, startDate, endDate, ordinalNumber announceOnly')):

    def __cmp__(self, other):
        return cmp(self.ID, other.ID)

    def getUserName(self):
        return str(self.ordinalNumber)


class RankedSeason(GameSeason):

    def __init__(self, cycleInfo, seasonData, isSpecial):
        super(RankedSeason, self).__init__(cycleInfo, seasonData)
        self.__isSpecial = isSpecial

    def _buildCycle(self, idx, status, number, rawData):
        return RankedCycle(idx, status, rawData['start'], rawData['end'], number, bool(rawData.get('announce', False)))

    @property
    def isSpecial(self):
        return self.__isSpecial

    def getUserName(self):
        if self.__isSpecial:
            seasonName = backport.text(R.strings.ranked_battles.rankedBattleMainView.specialSeason())
        else:
            seasonName = super(RankedSeason, self).getUserName()
        return seasonName


class RankStep(object):

    def __init__(self, stepID, stepState):
        super(RankStep, self).__init__()
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
        return self._state & RankState.ACQUIRED > 0

    def isBonus(self):
        return self._state & RankState.BONUS > 0

    def isCurrent(self):
        return self._state & RankState.CURRENT > 0

    def isLost(self):
        return self._state & RankState.LOST > 0

    def isNewForPlayer(self):
        return self._state & RankState.NEW_FOR_PLAYER > 0


class RankProgress(object):

    def __init__(self, steps):
        super(RankProgress, self).__init__()
        self._steps = steps

    def __eq__(self, other):
        return False if self.getSteps() != other.getSteps() else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def getSteps(self):
        return self._steps

    def getAcquiredSteps(self):
        return filter(operator.methodcaller('isAcquired'), self._steps)

    def getBonusSteps(self):
        return filter(operator.methodcaller('isBonus'), self._steps)


class Division(object):
    __slots__ = ('firstRank', 'lastRank', '__divisionID', '__currentRank', '__isFinal', '__rankIDs', '__isQualification')

    def __eq__(self, other):
        if self.getID() != other.getID() or self.getRanksIDs() != other.getRanksIDs():
            return False
        return False if self.isFinal() != other.isFinal() else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def __init__(self, divisionID, firstRank, lastRank, currentRank, isFinal):
        self.firstRank = firstRank
        self.lastRank = lastRank
        self.__divisionID = divisionID
        self.__currentRank = currentRank
        self.__isFinal = isFinal
        self.__rankIDs = tuple(range(self.firstRank, self.lastRank + 1))
        self.__isQualification = False

    def getID(self):
        return self.__divisionID

    def getRanksIDs(self):
        return self.__rankIDs

    def getRankUserName(self, rankID):
        return str(self.getRankUserId(rankID))

    def getRankUserId(self, rankID):
        return rankID - self.firstRank + 1 if rankID in self.getRanksIDs() else None

    def getUserID(self):
        return RANKEDBATTLES_ALIASES.DIVISIONS_ORDER[self.__divisionID] if self.__divisionID < len(RANKEDBATTLES_ALIASES.DIVISIONS_ORDER) else ''

    def getUserName(self):
        return backport.text(R.strings.ranked_battles.division.dyn(self.getUserID())())

    def isCompleted(self):
        return self.__currentRank >= self.lastRank

    def isCurrent(self):
        if self.isFinal():
            return self.firstRank - 1 <= self.__currentRank <= self.lastRank
        return self.firstRank - 1 <= self.__currentRank < self.lastRank

    def isQualification(self):
        return self.__isQualification

    def isFinal(self):
        return self.__isFinal

    def isUnlocked(self):
        return self.__currentRank >= self.firstRank - 1


class Rank(object):
    _ICON_SIZES = {'tiny': '24x24',
     'small': '58x80',
     'medium': '80x110',
     'big': '114x160',
     'huge': '190x260',
     'final': '216x300'}

    def __init__(self, rankID, rankState, progress=None, division=None, quests=None, shield=None, isUnburnable=False):
        super(Rank, self).__init__()
        self.__rankID = rankID
        self.__state = rankState
        self.__progress = progress
        self.__division = division
        self.__quests = quests
        self.__shieldStatus = shield
        self.__isUnburnable = isUnburnable
        self.__type = RankTypes.ACCOUNT

    def __eq__(self, other):
        if self.getState() != other.getState():
            return False
        if self.getID() != other.getID() or self.getProgress() != other.getProgress():
            return False
        return False if self.getShieldStatus() != other.getShieldStatus() or self.getDivision() != other.getDivision() else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def isAcquired(self):
        return self.__state & RankState.ACQUIRED > 0

    def isCurrent(self):
        return self.__state & RankState.CURRENT > 0

    def isFinal(self):
        return self.isLastInDivision() and self.__division.isFinal()

    def isFirstInDivision(self):
        return self.__rankID == self.__division.firstRank

    def isInitial(self):
        return self.__rankID == ZERO_RANK_ID

    def isInitialForNextDivision(self):
        return self.__rankID in (ZERO_RANK_ID, self.__division.lastRank) and not self.isFinal()

    def isLost(self):
        return self.__state & RankState.LOST > 0

    def isLastInDivision(self):
        return self.__rankID == self.__division.lastRank

    def isNewForPlayer(self):
        return self.__state & RankState.NEW_FOR_PLAYER > 0

    def isQualification(self):
        return self.__division.isQualification()

    def isRewardClaimed(self):
        return self.getQuest() is None or self.getQuest().isCompleted()

    def isUnburnable(self):
        return self.__isUnburnable

    def isVisualUnburnable(self):
        return self.isUnburnable()

    def getAchievedStepsCount(self):
        return len(self.getProgress().getAcquiredSteps())

    def getDivision(self):
        return self.__division

    def getDivisionUserName(self):
        return self.__division.getUserName()

    def getIcon(self, size):
        size = self._ICON_SIZES.get(size, '58x80')
        return backport.image(R.images.gui.maps.icons.rankedBattles.divisions.num(size).num(self.__division.getID())()) if self.isQualification() else backport.image(R.images.gui.maps.icons.rankedBattles.ranks.num(size).dyn('rank%s_%s' % (self.__division.getID(), self.getUserName()))())

    def getID(self):
        return self.__rankID

    def getProgress(self):
        return self.__progress

    def getQuest(self):
        return first(self.__quests)

    def getState(self):
        return self.__state

    def getShieldStatus(self):
        return self.__shieldStatus

    def getStepsCountToAchieve(self):
        return len(self.getProgress().getSteps())

    def getType(self):
        return self.__type

    def getQuests(self):
        return self.__quests

    def getUserName(self):
        return self.__division.getRankUserName(self.__rankID)


class PostBattleRankInfo(namedtuple('PostBattleRankInfo', ('accRank', 'accStep', 'stepChanges', 'updatedStepChanges', 'prevAccRank', 'prevAccStep', 'prevMaxRank', 'prevMaxStep', 'shields', 'prevShields', 'isBonusBattle', 'stepsBonusBattles', 'efficiencyBonusBattles'))):
    __slots__ = ()

    @classmethod
    def fromDict(cls, dictWithInfo):
        accRank, accStep = dictWithInfo.get('accRank', (0, 0))
        stepChanges = dictWithInfo.get('rankChange', 0)
        updatedStepChanges = dictWithInfo.get('updatedRankChange', 0)
        prevAccRank, prevAccStep = dictWithInfo.get('prevAccRank', (0, 0))
        prevMaxRank, prevMaxStep = dictWithInfo.get('prevMaxRank', (0, 0))
        shields = dictWithInfo.get('shields', {})
        prevShields = dictWithInfo.get('prevShields', {})
        isBonusBattle = dictWithInfo.get('bonusBattleUsed', False)
        efficiencyBonusBattles = dictWithInfo.get('efficiencyBonusBattles', 0)
        stepsBonusBattles = dictWithInfo.get('stepsBonusBattles', 0)
        return cls(accRank, accStep, stepChanges, updatedStepChanges, prevAccRank, prevAccStep, prevMaxRank, prevMaxStep, shields, prevShields, isBonusBattle, stepsBonusBattles, efficiencyBonusBattles)

    @property
    def shieldHP(self):
        hp = None
        shieldState = self.shields.get(self.accRank, None)
        if shieldState is not None:
            hp, _ = shieldState
        return hp

    @property
    def shieldState(self):
        currentRankID = self.accRank
        shieldState = self.shields.get(currentRankID, None)
        state = None
        if shieldState is not None:
            lastShieldState = self.prevShields.get(currentRankID, None)
            hp, _ = shieldState
            if lastShieldState is None:
                if hp > 0:
                    state = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                else:
                    state = RANKEDBATTLES_ALIASES.SHIELD_LOSE
            else:
                lastHp, _ = lastShieldState
                if lastHp == hp:
                    if hp > 0:
                        state = RANKEDBATTLES_ALIASES.SHIELD_ENABLED
                elif lastHp > hp:
                    if hp == 0:
                        state = RANKEDBATTLES_ALIASES.SHIELD_LOSE
                    else:
                        state = RANKEDBATTLES_ALIASES.SHIELD_LOSE_STEP
                elif lastHp == 0:
                    state = RANKEDBATTLES_ALIASES.SHIELD_FULL_RENEW
                else:
                    state = RANKEDBATTLES_ALIASES.SHIELD_RENEW
        return state


class RankedDossier(namedtuple('RankedDossier', 'rank, step, vehRankCount, ladderPts, allStepsCount')):

    @staticmethod
    def defaults():
        pass


class RankedAlertData(AlertData):
    _RES_ROOT = R.strings.ranked_battles.alertMessage
    _RES_REASON_ROOT = R.strings.ranked_battles.rankedBattlesUnreachableView

    @classmethod
    def _getTooltip(cls, _):
        return TOOLTIPS_CONSTANTS.RANKED_CALENDAR_DAY_INFO
