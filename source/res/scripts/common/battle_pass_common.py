# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_pass_common.py
import bisect
import time
import struct
from battle_pass_integration import getBattlePassByGameMode
from constants import MAX_VEHICLE_LEVEL, OFFER_TOKEN_PREFIX, ARENA_BONUS_TYPE
from collections import namedtuple
from items import vehicles, parseIntCompactDescr
BATTLE_PASS_TOKEN_PREFIX = 'battle_pass:'
BATTLE_PASS_TOKEN_PASS = BATTLE_PASS_TOKEN_PREFIX + 'pass:'
BATTLE_PASS_ENTITLEMENT_PASS = BATTLE_PASS_TOKEN_PASS.replace(':', '_')
BATTLE_PASS_OFFER_TOKEN_PREFIX = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX
BATTLE_PASS_TOKEN_TROPHY_OFFER_2020 = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'trophy'
BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER_2020 = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'trophy_gift'
BATTLE_PASS_TOKEN_NEW_DEVICE_OFFER_2020 = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device'
BATTLE_PASS_TOKEN_NEW_DEVICE_GIFT_OFFER_2020 = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_gift'
BATTLE_PASS_TOKEN_TROPHY_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'trophy:'
BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'trophy_gift:'
BATTLE_PASS_TOKEN_NEW_DEVICE_MI_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_mi:'
BATTLE_PASS_TOKEN_NEW_DEVICE_FV_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_fv:'
BATTLE_PASS_TOKEN_NEW_DEVICE_MI_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_mi_gift:'
BATTLE_PASS_TOKEN_NEW_DEVICE_FV_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_fv_gift:'
BATTLE_PASS_TOKEN_BLUEPRINT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'blueprint:'
BATTLE_PASS_TOKEN_BLUEPRINT_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'blueprint_gift:'
BATTLE_PASS_TOKEN_BROCHURE_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'brochure:'
BATTLE_PASS_TOKEN_BROCHURE_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'brochure_gift:'
BATTLE_PASS_TOKEN_GUIDE_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'guide:'
BATTLE_PASS_TOKEN_GUIDE_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'guide_gift:'
BATTLE_PASS_TOKEN_3D_STYLE = BATTLE_PASS_TOKEN_PREFIX + '3D_style:'
BATTLE_PASS_CHOICE_REWARD_OFFER_TOKENS = (BATTLE_PASS_TOKEN_TROPHY_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_MI_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_FV_OFFER,
 BATTLE_PASS_TOKEN_BLUEPRINT_OFFER,
 BATTLE_PASS_TOKEN_BROCHURE_OFFER,
 BATTLE_PASS_TOKEN_GUIDE_OFFER)
BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS = (BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_MI_GIFT_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_FV_GIFT_OFFER,
 BATTLE_PASS_TOKEN_BLUEPRINT_GIFT_OFFER,
 BATTLE_PASS_TOKEN_BROCHURE_GIFT_OFFER,
 BATTLE_PASS_TOKEN_GUIDE_GIFT_OFFER)
BATTLE_PASS_CHOICE_REWARD_OFFER_TOKEN_FREE_POSTFIX = 'free:'
BATTLE_PASS_CHOICE_REWARD_OFFER_TOKEN_PAID_POSTFIX = 'paid:'
BATTLE_PASS_CONFIG_NAME = 'battlePass_config'
BATTLE_PASS_SELECT_BONUS_NAME = 'battlePassSelectToken'
BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME = 'styleProgressToken'
BATTLE_PASS_BADGE_ID = 90
USE_BATTLE_PASS_BADGE = False
MAX_BADGE_LEVEL = 100
ENDLESS_TIME = 4104777660L
DEFAULT_REWARD_LEVEL = 0
NON_VEH_CD = 0
BattlePassInBattleProgress = namedtuple('BattlePassInBattleProgress', ['chapter',
 'level',
 'pointsNew',
 'pointsTotal',
 'pointsDiff',
 'isDone',
 'pointsBattleDiff',
 'awards',
 'isEnabled'])

class BattlePassRewardReason(object):
    DEFAULT = 0
    BATTLE = 1
    PURCHASE_BATTLE_PASS = 2
    PURCHASE_BATTLE_PASS_LEVELS = 3
    INVOICE = 4
    SELECT_STYLE = 5
    SELECT_TROPHY_DEVICE = 6
    PURCHASE_BATTLE_PASS_MULTIPLE = 7
    PURCHASE_REASONS = (PURCHASE_BATTLE_PASS, PURCHASE_BATTLE_PASS_LEVELS, PURCHASE_BATTLE_PASS_MULTIPLE)


class BattlePassState(object):
    BASE = 0
    POST = 1
    COMPLETED = 2
    PAUSED = 3


class BattlePassConsts(object):
    REWARD_FREE = 'free'
    REWARD_PAID = 'paid'
    REWARD_BOTH = 'both'
    RARE_REWARD_TAG = 'rare'
    FREE_MASK = 1
    PAID_MASK = 2
    PROGRESSION_INFO = 'progressionInfo'
    PROGRESSION_INFO_PREV = 'progressionInfoPrev'
    FAKE_QUEST_ID = 'battlePassFakeQuestID'
    MINIMAL_CHAPTER_NUMBER = 1


MASK_TO_REWARD = {BattlePassConsts.FREE_MASK: BattlePassConsts.REWARD_FREE,
 BattlePassConsts.PAID_MASK: BattlePassConsts.REWARD_PAID}
AWARD_TYPE_TO_TOKEN_POSTFIX = {BattlePassConsts.REWARD_FREE: BATTLE_PASS_CHOICE_REWARD_OFFER_TOKEN_FREE_POSTFIX,
 BattlePassConsts.REWARD_PAID: BATTLE_PASS_CHOICE_REWARD_OFFER_TOKEN_PAID_POSTFIX}

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

        return BattlePassStatsCommon.SeasonStats(seasonID, tuple(vehCDs), tuple(vehPoints), tuple(seasonStats['reachedCaps']), BattlePassStatsCommon.OtherStats(seasonStats['battles'], seasonStats['maxBase'], seasonStats.get('maxPost', 0)))

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
         'battles': 0,
         'reachedCaps': set(),
         'chosenItems': {}}


def getVehicleLevel(vehTypeCompDescr):
    _, nationID, innationID = parseIntCompactDescr(vehTypeCompDescr)
    return vehicles.g_list.getList(nationID)[innationID].level


def getBattlePassPassTokenName(season, chapter):
    return BATTLE_PASS_TOKEN_PASS + '{}:{}'.format(season, chapter)


def getBattlePassPassEntitlementName(season):
    return '{}{}'.format(BATTLE_PASS_ENTITLEMENT_PASS, season)


def getSeasonAndChapterFromBattlePassToken(tokenID):
    seasonAndChapter = tokenID.split(BATTLE_PASS_TOKEN_PASS)[-1].split(':')
    return (int(seasonAndChapter[0]), int(seasonAndChapter[1]))


def isBattlePassPassToken(token):
    return token.startswith(BATTLE_PASS_TOKEN_PASS)


def extendBaseAvatarResultsForBattlePass(results):
    results.update({'basePointsDiff': 0,
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


def getMaxAvalable3DStyleProgressInChapter(seasonID, chapter, tokensIds):
    level = 0
    prefixStyleTokenInChapter = '{}{}:{}'.format(BATTLE_PASS_TOKEN_3D_STYLE, seasonID, chapter)
    for token in tokensIds:
        if token.startswith(prefixStyleTokenInChapter):
            _, _, _, _, levelStyle = token.split(':')
            levelStyle = int(levelStyle)
            if levelStyle > level:
                level = levelStyle

    return level


def get3DStyleProgressToken(seasonID, chapter, progressLevel):
    return '{}{}:{}:{}'.format(BATTLE_PASS_TOKEN_3D_STYLE, seasonID, chapter, progressLevel)


class BattlePassConfig(object):
    REWARD_IDX = 0
    TAGS_IDX = 1

    def __init__(self, config):
        self._config = config
        self._season = config.get('season', {})
        self._rewards = config.get('rewards', {})
        self._freeRewards = config.get('rewards', {}).get(BattlePassConsts.REWARD_FREE, {})
        self._paidRewards = config.get('rewards', {}).get(BattlePassConsts.REWARD_PAID, {})

    @property
    def mode(self):
        return self._config.get('mode', 'disabled')

    @property
    def seasonID(self):
        return self._season.get('seasonID', 0)

    @property
    def seasonNum(self):
        return self._season.get('seasonNum', 0)

    @property
    def seasonStart(self):
        return self._season.get('seasonStart', 0)

    @property
    def seasonFinish(self):
        return self._season.get('seasonFinish', 0)

    @property
    def points(self):
        return self._season.get('points', {})

    @property
    def basePoints(self):
        return self._season.get('base', [0])

    @property
    def maxBaseLevel(self):
        return len(self.basePoints)

    @property
    def finalLevelsInChapter(self):
        return self._season.get('finalLevelsInChapter', [1])

    @property
    def maxBasePoints(self):
        return self.basePoints[-1]

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
    def selectedReward(self):
        return self._config.get('selectedReward', {})

    @property
    def seasonsHistory(self):
        return self._config.get('seasonsHistory', {})

    def getSumPointsTo(self, level):
        return self.basePoints[level - 1] if level else 0

    def iterRewardRanges(self, prevLvl, newLvl, rewardMask):
        for fromLvl, toLvl, mask in ((prevLvl, newLvl, BattlePassConsts.FREE_MASK), (prevLvl, newLvl, BattlePassConsts.PAID_MASK)):
            if mask & rewardMask:
                yield (fromLvl, toLvl, mask)

    def isEnabled(self):
        return self.mode == 'enabled'

    def isGameModeEnabled(self, gameMode):
        if not self._season or not self._season['points']:
            return False
        return self.points[gameMode]['enabled'] if gameMode in self._season['points'] else False

    def isPaused(self):
        return self.mode == 'paused'

    def isDisabled(self):
        return self.mode == 'disabled'

    def isBuyingAllowed(self):
        return self.isActive(int(time.time()))

    def isActive(self, curTime):
        return self.isEnabled() and self.seasonStart <= curTime < self.seasonFinish

    def isSeasonTimeOver(self, curTime):
        return int(curTime) >= self.seasonFinish

    def getSpecialVehicles(self):
        return self._season.get('specialVehicles', [])

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

    def bonusPointsList(self, vehTypeCompDescr=None, isWinner=True, gameMode=ARENA_BONUS_TYPE.REGULAR):
        teamKey = 'win' if isWinner else 'lose'
        teamPoints = self._config.get('season', {}).get('points', {}).get(gameMode, {})
        if vehTypeCompDescr in teamPoints:
            teamPoints = teamPoints[vehTypeCompDescr]
        return teamPoints.get(teamKey) or [0] * getBattlePassByGameMode(gameMode).getTeamSize()

    def getSeasonRewards(self):
        return self._config.get('rewards', {})

    def hasSeasonRewards(self):
        return self.getSeasonRewards() is not None

    def getTags(self, level, rewardType):
        return self._config.get('rewards', {}).get(rewardType, {}).get(level, ({}, tuple()))[BattlePassConfig.TAGS_IDX]

    def getPostReward(self, level):
        return {}

    def getFreeReward(self, level):
        return self._freeRewards.get(level, ({}, tuple()))[BattlePassConfig.REWARD_IDX]

    def getPaidReward(self, level):
        return self._paidRewards.get(level, ({}, tuple()))[BattlePassConfig.REWARD_IDX]

    def getRewardByMask(self, level, rewardMask):
        return self.getRewardByType(level, MASK_TO_REWARD[rewardMask])

    def getRewardByType(self, level, rewardType):
        return self._rewards.get(rewardType, {}).get(level, ({}, tuple()))[BattlePassConfig.REWARD_IDX]

    def getChapter(self, level):
        for i, finalLevelInChapter in enumerate(self.finalLevelsInChapter):
            if finalLevelInChapter > level:
                return i + 1

        return len(self.finalLevelsInChapter)

    def getChapterBorders(self, chapter):
        startLevel = self.finalLevelsInChapter[chapter - 2] if chapter > 1 else 0
        endLevel = self.finalLevelsInChapter[chapter - 1] if chapter else self.maxBaseLevel
        return (startLevel, endLevel)

    def getChapterNumbers(self):
        for i, finalLevelInChapter in enumerate(self.finalLevelsInChapter):
            yield i + 1

    def getAvailableStyles(self):
        return [ item['id'] for item in self.selectedReward.get('customizations', []) if item['custType'] == 'style' ]
