# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/ranked_battles/ranked_models.py
import operator
from collections import namedtuple
from operator import attrgetter
from gui.Scaleform.genConsts.RANKEDBATTLES_ALIASES import RANKEDBATTLES_ALIASES
from gui.Scaleform.locale.RANKED_BATTLES import RANKED_BATTLES
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.ranked_battles.constants import RANK_TYPES
from gui.shared.money import Currency
from helpers import i18n
from helpers import time_utils
from shared_utils import CONST_CONTAINER, collapseIntervals, findFirst, first
from season_common import CycleStatus, GameSeason

class RANK_STATE(CONST_CONTAINER):
    UNDEFINED = 2
    NOT_ACQUIRED = 2
    ACQUIRED = 4
    LOST = 8
    MAXIMUM = 16
    UNBURNABLE = 32
    CURRENT = 64
    NEW_FOR_PLAYER = 128
    LAST_SEEN_BY_PLAYER = 256


class RANK_STATUS(CONST_CONTAINER):
    NOT_ACHIEVED = 'not_achieved'
    ACHIEVED = 'achieved'
    LOST = 'lost'


class RANK_CHANGE_STATES(object):
    RANK_EARNED = 'rankEarned'
    RANK_LOST = 'rankLost'
    STEP_EARNED = 'stepEarned'
    STEPS_EARNED = 'stepsEarned'
    STEP_LOST = 'stepLost'
    NOTHING_CHANGED = 'nothingChanged'
    RANK_POINT = 'rankPoint'


class RankedCycle(namedtuple('RankedCycle', 'ID, status, startDate, endDate, ordinalNumber, points')):

    def __cmp__(self, other):
        return cmp(self.ID, other.ID)


class RankedSeason(GameSeason):

    def __init__(self, seasonInfo, seasonData, stats=None, points=0):
        super(RankedSeason, self).__init__(seasonInfo, seasonData)
        self.__stats = stats or {}
        self.__currCyclePoints = points

    def getPoints(self):
        dossierData = self.__stats.get((self.getSeasonID(), 0))
        if dossierData:
            _, _, _, points, _ = dossierData
        else:
            points = sum(map(attrgetter('points'), self.getAllCycles().values()))
        return points

    def _buildCycle(self, idx, status, start, end, number):
        points = 0
        if status == CycleStatus.PAST:
            cycleStats = self.__stats.get((self.getSeasonID(), idx))
            if cycleStats is not None:
                _, _, _, points, _ = cycleStats
        elif status == CycleStatus.CURRENT:
            points = self.__currCyclePoints
        return RankedCycle(idx, status, start, end, number, points)


class RankStep(object):

    def __init__(self, stepID, stepState):
        super(RankStep, self).__init__()
        self._stepID = stepID
        self._state = stepState

    def getID(self):
        return self._stepID

    def canBeLost(self):
        return self._state & RANK_STATE.UNBURNABLE == 0

    def isAcquired(self):
        return self._state & RANK_STATE.ACQUIRED > 0

    def isLost(self):
        return self._state & RANK_STATE.LOST > 0

    def isNewForPlayer(self):
        return self._state & RANK_STATE.NEW_FOR_PLAYER > 0

    def isLastSeenByPlayer(self):
        return self._state & RANK_STATE.LAST_SEEN_BY_PLAYER > 0

    def isCurrent(self):
        return self._state & RANK_STATE.CURRENT > 0

    def isMax(self):
        return self._state & RANK_STATE.MAXIMUM > 0


class RankProgress(object):

    def __init__(self, steps):
        super(RankProgress, self).__init__()
        self._steps = steps

    def __eq__(self, other):
        if len(self.getSteps()) != len(other.getSteps()):
            return False
        return False if len(self.getAcquiredSteps()) != len(other.getAcquiredSteps()) else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def getSteps(self):
        return self._steps

    def getAcquiredSteps(self):
        return filter(operator.methodcaller('isAcquired'), self._steps)


class Rank(object):
    _ICON_SIZES = {'tiny': '24x24',
     'small': '58x80',
     'medium': '80x110',
     'big': '114x160',
     'huge': '190x260',
     'final': '216x300'}
    _awardsOrder = ['oneof',
     Currency.CRYSTAL,
     Currency.GOLD,
     'premium',
     Currency.CREDITS,
     'items']

    def __init__(self, rankID, rankState, points, progress=None, quest=None, finalQuest=None, isMaxAccRank=False):
        super(Rank, self).__init__()
        self._rankID = rankID
        self._state = rankState
        self._progress = progress
        self._quest = quest
        self._type = RANK_TYPES.ACCOUNT
        self.__points = points
        self.__finalQuest = finalQuest
        self.__isMaxAccRank = isMaxAccRank

    def __eq__(self, other):
        if self.getID() != other.getID():
            return False
        return False if self.getProgress() != other.getProgress() else True

    def __ne__(self, other):
        return not self.__eq__(other)

    def getType(self):
        return self._type

    def getID(self):
        return self._rankID

    def getUserName(self):
        return i18n.makeString(str(self._rankID))

    def getIcon(self, size):
        return RES_ICONS.getRankIcon(self._ICON_SIZES.get(size, ''), self._rankID)

    def getCycleFinalQuest(self):
        return self.__finalQuest

    def canBeLost(self):
        return self._state & RANK_STATE.UNBURNABLE == 0

    def isAcquired(self):
        return self._state & RANK_STATE.ACQUIRED > 0

    def isLost(self):
        return self._state & RANK_STATE.LOST > 0

    def isNewForPlayer(self):
        return self._state & RANK_STATE.NEW_FOR_PLAYER > 0

    def isLastSeenByPlayer(self):
        return self._state & RANK_STATE.LAST_SEEN_BY_PLAYER > 0

    def isCurrent(self):
        return self._state & RANK_STATE.CURRENT > 0

    def isMax(self):
        return self._state & RANK_STATE.MAXIMUM > 0

    def isRewardClaimed(self):
        return self._quest is None or self._quest.isCompleted()

    def hasProgress(self):
        return self._progress is not None and len(self._progress.getAcquiredSteps()) > 0

    def getProgress(self):
        return self._progress

    def getStatus(self):
        if self.isAcquired():
            return RANK_STATUS.ACHIEVED
        return RANK_STATUS.LOST if self.isLost() else RANK_STATUS.NOT_ACHIEVED

    def getQuest(self):
        return self._quest

    def getStepsCountToAchieve(self):
        return len(self.getProgress().getSteps())

    def getPoints(self):
        return self.__points

    def getAwardsVOs(self, forCycleFinish=False, iconSize='small'):
        quest = self.__finalQuest if forCycleFinish else self._quest
        awards = []
        if quest is not None:
            bonuses = {b.getName():b for b in quest.getBonuses()}
            for bonusName in self._awardsOrder:
                bonus = bonuses.pop(bonusName, None)
                if bonus:
                    awards.extend(bonus.getRankedAwardVOs(iconSize))

            for bonus in bonuses.values():
                awards.extend(bonus.getRankedAwardVOs(iconSize))

        return awards

    def getBoxIcon(self, size='450x400', boxType='wooden', isOpened=True):
        return RES_ICONS.getRankedBoxIcon(size, boxType, '_opened' if isOpened else '', self._rankID)

    def getIsMaxAccRank(self):
        return self.__isMaxAccRank


class VehicleRank(Rank):

    def __init__(self, vehicle, accTopRankID, rankID, rankState, points, progress=None, quest=None):
        super(VehicleRank, self).__init__(rankID, rankState, points, progress, quest)
        self._type = RANK_TYPES.VEHICLE
        self.__vehicle = vehicle
        self.__accTopRankID = accTopRankID

    def getID(self):
        return self.getSerialID() + self.__accTopRankID

    def getSerialID(self):
        return self._rankID

    def getIcon(self, size):
        return RES_ICONS.getRankIcon(self._ICON_SIZES.get(size, ''), 'VehMaster')

    def getBoxIcon(self, size='450x400', boxType='wooden', isOpened=True):
        return RES_ICONS.getRankedBoxIcon(size, boxType, '_opened' if isOpened else '', self.__accTopRankID)

    def getUserName(self):
        return i18n.makeString(RANKED_BATTLES.RANKEDBATTLEVIEW_PROGRESSBLOCK_VEHICLERANK)

    def isRewardClaimed(self):
        return self.isAcquired()

    def getVehicle(self):
        return self.__vehicle

    def getIsMaxAccRank(self):
        return False


class PrimeTime(object):

    def __init__(self, peripheryID, periods=None):
        super(PrimeTime, self).__init__()
        self.__peripheryID = peripheryID
        self.__periods = periods or {}

    def hasAnyPeriods(self):
        return bool(self.__periods)

    def getAvailability(self, forTime, cycleEnd):
        periods = self.getPeriodsBetween(forTime, cycleEnd)
        if periods:
            periodsIter = iter(periods)
            currentPeriod = findFirst(lambda (pS, pE): pS <= forTime < pE, periodsIter)
            if currentPeriod is not None:
                _, currentPeriodEnd = currentPeriod
                return (True, currentPeriodEnd - forTime)
            nextPeriod = first(periods)
            if nextPeriod is not None:
                nextPeriodStart, _ = nextPeriod
                return (False, nextPeriodStart - forTime)
        return (False, 0)

    def getPeriodsBetween(self, startTime, endTime):
        periods = []
        startDateTime = time_utils.getDateTimeInUTC(startTime)
        startTimeDayStart, _ = time_utils.getDayTimeBoundsForUTC(startTime)
        weekDay = startDateTime.isoweekday()
        while startTimeDayStart <= endTime:
            if weekDay in self.__periods:
                for (startH, startM), (endH, endM) in self.__periods[weekDay]:
                    periodStartTime = startTimeDayStart + startH * time_utils.ONE_HOUR + startM * time_utils.ONE_MINUTE
                    periodEndTime = startTimeDayStart + endH * time_utils.ONE_HOUR + endM * time_utils.ONE_MINUTE
                    if startTime < periodEndTime and periodStartTime <= endTime:
                        periods.append((max(startTime, periodStartTime), min(endTime, periodEndTime)))

            if weekDay == time_utils.WEEK_END:
                weekDay = time_utils.WEEK_START
            else:
                weekDay += 1
            startTimeDayStart += time_utils.ONE_DAY

        return collapseIntervals(periods)


class PostBattleRankInfo(namedtuple('PostBattleRankInfo', ('accRank', 'accStep', 'vehRank', 'vehStep', 'stepChanges', 'prevAccRank', 'prevAccStep', 'prevVehRank', 'prevVehStep', 'shields', 'prevShields'))):
    __slots__ = ()

    @classmethod
    def fromDict(cls, dictWithInfo):
        accRank, accStep = dictWithInfo.get('accRank', (0, 0))
        vehRank, vehStep = dictWithInfo.get('vehRank', (0, 0))
        stepChanges = dictWithInfo.get('rankChange', 0)
        prevAccRank, prevAccStep = dictWithInfo.get('prevAccRank', (0, 0))
        prevVehRank, prevVehStep = dictWithInfo.get('prevVehRank', (0, 0))
        shields = dictWithInfo.get('shields', {})
        prevShields = dictWithInfo.get('prevShields', {})
        return cls(accRank, accStep, vehRank, vehStep, stepChanges, prevAccRank, prevAccStep, prevVehRank, prevVehStep, shields, prevShields)

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
