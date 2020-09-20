# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_pass_common.py
import bisect
import time
import typing
import struct
from constants import MAX_VEHICLE_LEVEL, OFFER_TOKEN_PREFIX
from collections import namedtuple
from items import vehicles, parseIntCompactDescr
BATTLE_PASS_TOKEN_PREFIX = 'battle_pass:'
BATTLE_PASS_TOKEN_PASS = BATTLE_PASS_TOKEN_PREFIX + 'pass:'
BATTLE_PASS_TOKEN_VOTE = 'vote:' + BATTLE_PASS_TOKEN_PREFIX
BATTLE_PASS_TOKEN_DEFAULT_FINAL_REWARD = BATTLE_PASS_TOKEN_PREFIX + 'default_final:'
BATTLE_PASS_TOKEN_ONBOARDING_OFFER = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX + 'onboarding:'
BATTLE_PASS_TOKEN_ONBOARDING_GIFT_OFFER = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX + 'onboarding_gift:'
BATTLE_PASS_TOKEN_TROPHY_OFFER = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX + 'trophy'
BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX + 'trophy_gift'
BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX + 'new_device'
BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX + 'new_device_gift'
BATTLE_PASS_CONFIG_NAME = 'battlePass_config'
BATTLE_PASS_BADGE_ID = 90
MAX_BADGE_LEVEL = 100
ENDLESS_TIME = 4104777660L
DEFAULT_REWARD_LEVEL = 0
NON_VEH_CD = 0
BattlePassInBattleProgress = namedtuple('BattlePassInBattleProgress', ['state',
 'level',
 'pointsNew',
 'pointsTotal',
 'pointsDiff',
 'isDone',
 'pointsBattleDiff',
 'awards'])

class BattlePassRewardReason(object):
    DEFAULT = 0
    BATTLE = 1
    PURCHASE_BATTLE_PASS = 2
    PURCHASE_BATTLE_PASS_LEVELS = 3
    INVOICE = 4
    VOTE = 5
    SELECT_TROPHY_DEVICE = 6


class BattlePassState(object):
    BASE = 0
    POST = 1
    COMPLETED = 2


class BattlePassConsts(object):
    REWARD_FREE = 'free'
    REWARD_PAID = 'paid'
    REWARD_POST = 'post'
    REWARD_BOTH = 'both'
    RARE_REWARD_TAG = 'rare'
    FREE_MASK = 1
    PAID_MASK = 2
    POST_MASK = 4
    PROGRESSION_INFO = 'progressionInfo'
    PROGRESSION_INFO_PREV = 'progressionInfoPrev'
    FAKE_QUEST_ID = 'battlePassFakeQuestID'


MASK_TO_REWARD = {BattlePassConsts.FREE_MASK: BattlePassConsts.REWARD_FREE,
 BattlePassConsts.PAID_MASK: BattlePassConsts.REWARD_PAID,
 BattlePassConsts.POST_MASK: BattlePassConsts.REWARD_POST}
GIFT_TO_MAIN_TOKEN = {BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER: BATTLE_PASS_TOKEN_TROPHY_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER: BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER}

class BattlePassStatsCommon(object):
    _CNT_SEASONS_FORMAT = '<I'
    _SEASON_ID_FORMAT = '<I'
    _OTHER_STATS_FORMAT = '<3I'
    OtherStats = namedtuple('OtherStats', 'battles maxBase maxPost')
    SeasonStats = namedtuple('SeasonStats', 'seasonID vehCDs vehPoints reachedCaps otherStats')

    @staticmethod
    def _packList(inputList):
        return struct.pack('<I', len(inputList)) + struct.pack('<{}I'.format(len(inputList)), *inputList)

    @staticmethod
    def _unpackList(packed, offset):
        listLen = struct.unpack_from('<I', packed, offset)
        offset += struct.calcsize('<I')
        return (struct.unpack_from('<{}I'.format(listLen), packed, offset), offset + struct.calcsize('<{}I'.format(listLen)))

    @staticmethod
    def makeSeasonStats(seasonID, vehiclePoints, seasonStats):
        vehCDs = []
        vehPoints = []
        for vehCD, vehCDPoints in vehiclePoints.iteritems():
            vehCDs.append(vehCD)
            vehPoints.append(vehCDPoints)

        return BattlePassStatsCommon.SeasonStats(seasonID, tuple(vehCDs), tuple(vehPoints), tuple(seasonStats['reachedCaps']), BattlePassStatsCommon.OtherStats(seasonStats['battles'], seasonStats['maxBase'], seasonStats['maxPost']))

    @staticmethod
    def packSeasonStats(seasonStats):
        res = []
        res.append(struct.pack(BattlePassStatsCommon._SEASON_ID_FORMAT, seasonStats.seasonID))
        res.append(BattlePassStatsCommon._packList(seasonStats.vehCDs))
        res.append(BattlePassStatsCommon._packList(seasonStats.vehPoints))
        res.append(BattlePassStatsCommon._packList(seasonStats.reachedCaps))
        res.append(struct.pack(BattlePassStatsCommon._OTHER_STATS_FORMAT, *tuple(seasonStats.otherStats)))
        return ''.join(res)

    @staticmethod
    def unpackSeasonStats(packed, offset=0):
        seasonID = struct.unpack_from(BattlePassStatsCommon._SEASON_ID_FORMAT, packed, offset)
        offset += struct.calcsize(BattlePassStatsCommon._SEASON_ID_FORMAT)
        vehCDs, offset = BattlePassStatsCommon._unpackList(packed, offset)
        vehPoints, offset = BattlePassStatsCommon._unpackList(packed, offset)
        reachedCaps, offset = BattlePassStatsCommon._unpackList(packed, offset)
        battles, maxBase, maxPost = struct.unpack_from(BattlePassStatsCommon._OTHER_STATS_FORMAT, packed, offset)
        offset += struct.calcsize(BattlePassStatsCommon._OTHER_STATS_FORMAT)
        return (BattlePassStatsCommon.SeasonStats(seasonID, vehCDs, vehPoints, reachedCaps, BattlePassStatsCommon.OtherStats(battles, maxBase, maxPost)), offset)

    @staticmethod
    def packSeasonStatsWithPrevStats(prevPackedStats, seasonStats):
        cntPackedSeasons = struct.unpack_from(BattlePassStatsCommon._CNT_SEASONS_FORMAT, prevPackedStats)
        offset = struct.calcsize(BattlePassStatsCommon._CNT_SEASONS_FORMAT)
        return struct.pack(BattlePassStatsCommon._CNT_SEASONS_FORMAT, cntPackedSeasons + 1) + prevPackedStats[offset:] + BattlePassStatsCommon.packSeasonStats(seasonStats)

    @staticmethod
    def unpackAllSeasonStats(packedStats, curOffset=0):
        result = []
        cntSeasons = struct.unpack_from(BattlePassStatsCommon._CNT_SEASONS_FORMAT, packedStats, curOffset)
        curOffset += struct.calcsize(BattlePassStatsCommon._CNT_SEASONS_FORMAT)
        for curSeason in xrange(cntSeasons):
            curSeasonStats, curOffset = BattlePassStatsCommon.unpackSeasonStats(packedStats, curOffset)
            result.append(curSeasonStats)

        return (result, curOffset)

    @staticmethod
    def getEmptyPackedSeasonStats():
        return struct.pack(BattlePassStatsCommon._CNT_SEASONS_FORMAT, 0)

    @staticmethod
    def initialSeasonStatsData():
        return {'maxBase': 0,
         'maxPost': 0,
         'battles': 0,
         'reachedCaps': set()}


def getVehicleLevel(vehTypeCompDescr):
    _, nationID, innationID = parseIntCompactDescr(vehTypeCompDescr)
    return vehicles.g_list.getList(nationID)[innationID].level


def getBattlePassPassTokenName(season):
    return BATTLE_PASS_TOKEN_PASS + str(season)


def getSeasonFromBattlePassToken(tokenID):
    return int(tokenID.split(BATTLE_PASS_TOKEN_PASS)[-1])


def getBattlePassVoteToken(seasonID, optionID):
    return BATTLE_PASS_TOKEN_VOTE + '{}:{}'.format(seasonID, optionID)


def getBattlePassDefaultFinalRewardToken(seasonID, hadBattlePass):
    return BATTLE_PASS_TOKEN_DEFAULT_FINAL_REWARD + '{}_{}'.format(seasonID, 'paid' if hadBattlePass else 'free')


def getBattlePassOnboardingToken(seasonID):
    return BATTLE_PASS_TOKEN_ONBOARDING_OFFER + str(seasonID)


def getBattlePassOnboardingGiftToken(seasonID):
    return BATTLE_PASS_TOKEN_ONBOARDING_GIFT_OFFER + str(seasonID)


def isBattlePassPassToken(token):
    return token.startswith(BATTLE_PASS_TOKEN_PASS)


def isBattlePassVoteToken(token):
    return token.startswith(BATTLE_PASS_TOKEN_VOTE)


def extendBaseAvatarResultsForBattlePass(results):
    results.setdefault('ext', {}).setdefault('battlePass', {}).update({'basePointsDiff': 0,
     'sumPoints': 0,
     'capBonus': 0})


def getLevel(curPoints, levelPoints, prevLevel=0):
    if prevLevel >= len(levelPoints):
        return prevLevel
    if curPoints < levelPoints[prevLevel]:
        return prevLevel
    if curPoints >= levelPoints[-1]:
        return len(levelPoints)
    return prevLevel + 1 if curPoints >= levelPoints[prevLevel] and curPoints < levelPoints[prevLevel + 1] else bisect.bisect_right(levelPoints, curPoints, prevLevel)


class BattlePassConfig(object):
    REWARD_IDX = 0
    TAGS_IDX = 1
    MAX_RANKS = 15

    def __init__(self, config):
        self._config = config
        self._season = config.get('season', {})
        self._points = self._season.get('points', {})
        self._rewards = config.get('rewards', {})
        self._freeRewards = config.get('rewards', {}).get(BattlePassConsts.REWARD_FREE, {})
        self._paidRewards = config.get('rewards', {}).get(BattlePassConsts.REWARD_PAID, {})
        self._postRewards = config.get('rewards', {}).get(BattlePassConsts.REWARD_POST, {})

    @property
    def mode(self):
        return self._config.get('mode', 'disabled')

    @property
    def seasonID(self):
        return self._season.get('seasonID', 0)

    @property
    def seasonStart(self):
        return self._season.get('seasonStart', 0)

    @property
    def seasonFinish(self):
        return self._season.get('seasonFinish', 0)

    @property
    def basePoints(self):
        return self._season.get('base', [0])

    @property
    def postPoints(self):
        return self._season.get('post', [0])

    @property
    def maxBaseLevel(self):
        return len(self.basePoints)

    @property
    def maxPostLevel(self):
        return len(self.postPoints)

    @property
    def maxBasePoints(self):
        return self.basePoints[-1]

    @property
    def maxPostPoints(self):
        return self.postPoints[-1]

    @property
    def maxSoldLevelsBeforeUnlock(self):
        return self._season.get('maxSoldLevelsBeforeUnlock', 0)

    @property
    def maxLevelForNewbie(self):
        return self._season.get('maxLevelForNewbie', 0)

    @property
    def maxPointsForNewbie(self):
        return self.basePoints[self.maxLevelForNewbie - 1]

    @property
    def sellAnyLevelsUnlockTime(self):
        return self._season.get('sellAnyLevelsUnlockTime', ENDLESS_TIME)

    @property
    def finalOfferTime(self):
        return self._season.get('finalOfferTime', 0)

    @property
    def vehLevelCaps(self):
        return self._season.get('vehLevelCaps', [0] * MAX_VEHICLE_LEVEL)

    @property
    def vehCDCaps(self):
        return self._season.get('vehCDCaps', {})

    @property
    def finalReward(self):
        return self._config.get('finalReward', {})

    @property
    def seasonsHistory(self):
        return self._config.get('seasonsHistory', {})

    def getSumPointsTo(self, state, level):
        if state == BattlePassState.BASE:
            if level:
                return self.basePoints[level - 1]
            return 0
        return self.maxBasePoints + (self.postPoints[level - 1] if level else 0) if state == BattlePassState.POST else None

    def getLevelRanges(self, prevLvl, prevState, newLvl, newState):
        baseFromLvl, baseToLvl = (0, 0)
        postFromLvl, postToLvl = (0, 0)
        if prevState == BattlePassState.BASE:
            baseFromLvl = prevLvl
            if prevState == newState:
                baseToLvl = newLvl
            else:
                baseToLvl = self.maxBaseLevel
                prevState = BattlePassState.POST
                prevLvl = 0
        if prevState == BattlePassState.POST:
            postFromLvl = prevLvl
            postToLvl = newLvl if newState == BattlePassState.POST else self.maxPostLevel
        return (baseFromLvl,
         baseToLvl,
         postFromLvl,
         postToLvl)

    def iterRewardRanges(self, prevLvl, prevState, newLvl, newState, rewardMask):
        baseFromLvl, baseToLvl, postFromLvl, postToLvl = self.getLevelRanges(prevLvl, prevState, newLvl, newState)
        for fromLvl, toLvl, mask in ((baseFromLvl, baseToLvl, BattlePassConsts.FREE_MASK), (baseFromLvl, baseToLvl, BattlePassConsts.PAID_MASK), (postFromLvl, postToLvl, BattlePassConsts.POST_MASK)):
            if mask & rewardMask:
                yield (fromLvl, toLvl, mask)

    def isSellAnyUnlocked(self, curTime):
        return curTime >= self.sellAnyLevelsUnlockTime

    def isEnabled(self):
        return self.mode == 'enabled'

    def isPaused(self):
        return self.mode == 'paused'

    def isDisabled(self):
        return self.mode == 'disabled'

    def isOnboardingEnabled(self):
        return self.maxLevelForNewbie > 0

    def isBuyingAllowed(self):
        return self.isActive(int(time.time()))

    def isActive(self, curTime):
        return self.isEnabled() and self.seasonStart <= curTime < self.seasonFinish

    def isSeasonTimeOver(self, curTime):
        return int(curTime) >= self.seasonFinish

    def getSpecialVehicles(self):
        return self.finalReward.keys()

    def isSpecialVehicle(self, vehTypeCompDescr):
        return vehTypeCompDescr in self.getSpecialVehicles()

    def capacityList(self):
        return self._season.get('caps', [0] * MAX_VEHICLE_LEVEL)

    def capBonusList(self):
        return self._season.get('capBonuses', [0] * MAX_VEHICLE_LEVEL)

    def vehicleCapacity(self, vehTypeCompDescr):
        isSecret = 'secret' in vehicles.getVehicleType(vehTypeCompDescr).tags
        return 0 if isSecret and vehTypeCompDescr not in self.vehCDCaps else self.vehCDCaps.get(vehTypeCompDescr, self.vehLevelCaps[getVehicleLevel(vehTypeCompDescr) - 1])

    def capBonus(self, vehLevel):
        return self.capBonusList()[vehLevel - 1]

    def capBonusForVehTypeCompDescr(self, vehTypeCompDescr):
        return self.capBonusList()[getVehicleLevel(vehTypeCompDescr) - 1]

    def vehicleContribution(self, vehTypeCompDescr):
        return self.vehicleCapacity(vehTypeCompDescr) + self.capBonusForVehTypeCompDescr(vehTypeCompDescr)

    def alignedPointsFromSumPoints(self, sumPoints):
        if sumPoints >= self.maxBasePoints:
            return sumPoints - self.maxBasePoints
        else:
            return sumPoints

    def bonusPointsList(self, vehTypeCompDescr=None, isWinner=True):
        teamKey = 'win' if isWinner else 'lose'
        teamPoints = self._config.get('season', {}).get('points', {})
        if vehTypeCompDescr in teamPoints:
            teamPoints = teamPoints[vehTypeCompDescr]
        return teamPoints.get(teamKey, [0] * BattlePassConfig.MAX_RANKS)

    def bonusPointsDiffList(self, vehTypeCompDescr):
        defaultDiff = [0] * BattlePassConfig.MAX_RANKS
        defaultPoints = self._config.get('season', {}).get('points', {})
        if vehTypeCompDescr in defaultPoints:
            specialPoints = defaultPoints[vehTypeCompDescr]
            defaultPoints = defaultPoints.get('win', defaultDiff)
            specialPoints = specialPoints.get('win', defaultDiff)
            return [ a - b for a, b in zip(specialPoints, defaultPoints) ]
        return defaultDiff

    def bonusPointsForBattle(self, vehTypeCompDescr, rank, isWinner=True):
        bonusPoints = self.bonusPointsList(vehTypeCompDescr=vehTypeCompDescr, isWinner=isWinner)
        return bonusPoints[rank - 1]

    def getSeasonRewards(self):
        return self._config.get('rewards', {})

    def hasSeasonRewards(self):
        return self.getSeasonRewards() is not None

    def getTags(self, level, rewardType):
        return self._config.get('rewards', {}).get(rewardType, {}).get(level, ({}, tuple()))[BattlePassConfig.TAGS_IDX]

    def getPostReward(self, level):
        return self._postRewards.get(level, self._postRewards.get(DEFAULT_REWARD_LEVEL, ({}, tuple())))[BattlePassConfig.REWARD_IDX]

    def getFreeReward(self, level):
        return self._freeRewards.get(level, ({}, tuple()))[BattlePassConfig.REWARD_IDX]

    def getPaidReward(self, level):
        return self._paidRewards.get(level, ({}, tuple()))[BattlePassConfig.REWARD_IDX]

    def getRewardByMask(self, level, rewardMask):
        return self.getRewardByType(level, MASK_TO_REWARD[rewardMask])

    def getRewardByType(self, level, rewardType):
        return self.getPostReward(level) if rewardType == BattlePassConsts.REWARD_POST else self._rewards.get(rewardType, {}).get(level, ({}, tuple()))[BattlePassConfig.REWARD_IDX]
