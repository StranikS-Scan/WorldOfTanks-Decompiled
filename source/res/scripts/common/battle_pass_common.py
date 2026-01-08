# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/battle_pass_common.py
import bisect
import struct
import time
from collections import namedtuple
import typing
from enum import Enum, unique
from battle_pass_integration import getBattlePassByGameMode
from constants import ARENA_BONUS_TYPE, MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL, OFFER_TOKEN_PREFIX
from debug_utils import LOG_ERROR
from items import parseIntCompactDescr, vehicles
if typing.TYPE_CHECKING:
    from typing import Dict, Generator, Sequence, Tuple, Union, List
BATTLE_PASS_TOKEN_PREFIX = 'battle_pass:'
BATTLE_PASS_TOKEN_PASS = BATTLE_PASS_TOKEN_PREFIX + 'pass:'
BATTLE_PASS_ENTITLEMENT_PASS = BATTLE_PASS_TOKEN_PASS.replace(':', '_')
BATTLE_PASS_SHOP_ENTITLEMENT_PASS = 'battle_pass_shop'
BATTLE_PASS_OFFER_TOKEN_PREFIX = OFFER_TOKEN_PREFIX + BATTLE_PASS_TOKEN_PREFIX
BATTLE_PASS_Q_CHAIN_TOKEN_PREFIX = BATTLE_PASS_TOKEN_PREFIX + 'q_chain:'
BATTLE_PASS_RANDOM_QUEST_TOKEN_PREFIX = BATTLE_PASS_TOKEN_PREFIX + 'random_quest:'
BATTLE_PASS_TOKEN_TROPHY_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'trophy:'
BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'trophy_gift:'
BATTLE_PASS_TOKEN_EXPEQUIPMENTS_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'expequipments:'
BATTLE_PASS_TOKEN_EXPEQUIPMENTS_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'expequipments_gift:'
BATTLE_PASS_TOKEN_NEW_DEVICE_MI_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_mi:'
BATTLE_PASS_TOKEN_NEW_DEVICE_FV_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_fv:'
BATTLE_PASS_TOKEN_NEW_DEVICE_MI_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_mi_gift:'
BATTLE_PASS_TOKEN_NEW_DEVICE_FV_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'new_device_fv_gift:'
BATTLE_PASS_TOKEN_BLUEPRINT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'blueprint:'
BATTLE_PASS_TOKEN_BLUEPRINT_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'blueprint_gift:'
BATTLE_PASS_TOKEN_BROCHURE_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'brochure:'
BATTLE_PASS_TOKEN_BROCHURE_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'brochure_gift:'
BATTLE_PASS_TOKEN_BOOK_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'book:'
BATTLE_PASS_TOKEN_BOOK_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'book_gift:'
BATTLE_PASS_TOKEN_GUIDE_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'guide:'
BATTLE_PASS_TOKEN_GUIDE_GIFT_OFFER = BATTLE_PASS_OFFER_TOKEN_PREFIX + 'guide_gift:'
BATTLE_PASS_TOKEN_3D_STYLE = BATTLE_PASS_TOKEN_PREFIX + '3D_style:'
BATTLE_PASS_RANDOM_QUEST_ID_PREFIX = 'battle_pass_random'
BATTLE_PASS_CHOICE_REWARD_OFFER_TOKENS = (BATTLE_PASS_TOKEN_TROPHY_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_MI_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_FV_OFFER,
 BATTLE_PASS_TOKEN_BLUEPRINT_OFFER,
 BATTLE_PASS_TOKEN_BROCHURE_OFFER,
 BATTLE_PASS_TOKEN_GUIDE_OFFER,
 BATTLE_PASS_TOKEN_BOOK_OFFER,
 BATTLE_PASS_TOKEN_EXPEQUIPMENTS_OFFER)
BATTLE_PASS_CHOICE_REWARD_OFFER_GIFT_TOKENS = (BATTLE_PASS_TOKEN_TROPHY_GIFT_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_MI_GIFT_OFFER,
 BATTLE_PASS_TOKEN_NEW_DEVICE_FV_GIFT_OFFER,
 BATTLE_PASS_TOKEN_BLUEPRINT_GIFT_OFFER,
 BATTLE_PASS_TOKEN_BROCHURE_GIFT_OFFER,
 BATTLE_PASS_TOKEN_GUIDE_GIFT_OFFER,
 BATTLE_PASS_TOKEN_BOOK_GIFT_OFFER,
 BATTLE_PASS_TOKEN_EXPEQUIPMENTS_GIFT_OFFER)
BATTLE_PASS_CHOICE_REWARD_OFFER_TOKEN_FREE_POSTFIX = 'free:'
BATTLE_PASS_CHOICE_REWARD_OFFER_TOKEN_PAID_POSTFIX = 'paid:'
BATTLE_PASS_PDATA_KEY = 'battlePass'
BATTLE_PASS_CONFIG_NAME = 'battlePass_config'
BATTLE_PASS_SELECT_BONUS_NAME = 'battlePassSelectToken'
BATTLE_PASS_STYLE_PROGRESS_BONUS_NAME = 'styleProgressToken'
BATTLE_PASS_Q_CHAIN_BONUS_NAME = 'battlePassQuestChainToken'
BATTLE_PASS_RANDOM_QUEST_BONUS_NAME = 'randomQuestToken'
NON_VEH_CD = 0
MAX_NON_CHAPTER_POINTS = 1000000
BATTLE_PASS_TOKEN_LIFETIME = 4320
BATTLE_PASS_COST_CURRENCIES = {'gold', 'freeXP'}
BATTLE_PASS_MARATHON_COST_CURRENCIES = {'gold', 'freeXP'}
VEHICLE_POINTS_INDEX = 0
VEHICLE_WEEK_CAP_SHIFT_INDEX = 1

class _Enum(Enum):

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_


@unique
class FinalReward(Enum):
    STYLE = 'style'
    TANKMAN = 'tankman'
    VEHICLE = 'vehicle'
    MIXED = 'mixed'


@unique
class CurrencyBP(Enum):
    BIT = 'bpbit'


@unique
class BattlePassChapterType(_Enum):
    DEFAULT = 'default'
    MARATHON = 'marathon'
    RESOURCE = 'resource'


@unique
class BattlePassCapsFlow(_Enum):
    WEEK = 'week'
    FACTOR = 'factor'


class BattlePassRewardReason(object):
    DEFAULT = 0
    BATTLE = 1
    PURCHASE_BATTLE_PASS = 2
    PURCHASE_BATTLE_PASS_LEVELS = 3
    INVOICE = 4
    STYLE_UPGRADE = 5
    SELECT_REWARD = 6
    PURCHASE_BATTLE_PASS_MULTIPLE = 7
    SELECT_CHAPTER = 8
    GIFT_CHAPTER = 9
    PURCHASE_REASONS = (PURCHASE_BATTLE_PASS,
     PURCHASE_BATTLE_PASS_LEVELS,
     PURCHASE_BATTLE_PASS_MULTIPLE,
     GIFT_CHAPTER)


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
    FAKE_QUEST_ID = 'battlePassFakeQuestID'
    MINIMAL_CHAPTER_NUMBER = 1


MASK_TO_REWARD = {BattlePassConsts.FREE_MASK: BattlePassConsts.REWARD_FREE,
 BattlePassConsts.PAID_MASK: BattlePassConsts.REWARD_PAID}

class BattlePassStatsCommon(object):
    _CNT_SEASONS_FORMAT = '<I'
    _SEASON_ID_FORMAT = '<I'
    _OTHER_STATS_FORMAT = '<3I'
    OtherStats = namedtuple('OtherStats', 'battles maxBase maxPost')
    SeasonStats = namedtuple('SeasonStats', 'seasonID vehCDs vehPoints reachedCaps otherStats weekCapShift')

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
        weekCapShift = []
        for vehCD, (curVehCDPoints, curVehCDWeekShift) in vehiclePoints.iteritems():
            vehCDs.append(vehCD)
            vehPoints.append(curVehCDPoints)
            weekCapShift.append(curVehCDWeekShift)

        return BattlePassStatsCommon.SeasonStats(seasonID, tuple(vehCDs), tuple(vehPoints), tuple(seasonStats['reachedCaps']), BattlePassStatsCommon.OtherStats(seasonStats['battles'], sum((chapterStats.points for chapterStats in seasonStats.get('chaptersStats', {}).itervalues())), seasonStats.get('maxPost', 0)), tuple(weekCapShift))

    @staticmethod
    def packSeasonStats(seasonStats):
        res = []
        res.append(struct.pack(BattlePassStatsCommon._SEASON_ID_FORMAT, seasonStats.seasonID))
        res.append(BattlePassStatsCommon._packList(seasonStats.vehCDs))
        res.append(BattlePassStatsCommon._packList(seasonStats.vehPoints))
        res.append(BattlePassStatsCommon._packList(seasonStats.reachedCaps))
        res.append(struct.pack(BattlePassStatsCommon._OTHER_STATS_FORMAT, *tuple(seasonStats.otherStats)))
        res.append(BattlePassStatsCommon._packList(seasonStats.weekCapShift))
        return ''.join(res)

    @staticmethod
    def unpackSeasonStats(packed, offset=0):
        seasonID = struct.unpack_from(BattlePassStatsCommon._SEASON_ID_FORMAT, packed, offset)
        offset += struct.calcsize(BattlePassStatsCommon._SEASON_ID_FORMAT)
        vehCDs, offset = BattlePassStatsCommon._unpackList(packed, offset)
        vehPoints, offset = BattlePassStatsCommon._unpackList(packed, offset)
        reachedCaps, offset = BattlePassStatsCommon._unpackList(packed, offset)
        battles, maxBase, maxPost = struct.unpack_from(BattlePassStatsCommon._OTHER_STATS_FORMAT, packed, offset)
        weekCapShift, offset = BattlePassStatsCommon._unpackList(packed, offset)
        offset += struct.calcsize(BattlePassStatsCommon._OTHER_STATS_FORMAT)
        return (BattlePassStatsCommon.SeasonStats(seasonID, vehCDs, vehPoints, reachedCaps, BattlePassStatsCommon.OtherStats(battles, maxBase, maxPost), weekCapShift), offset)

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
        return {'chaptersStats': {},
         'nonChapterPoints': 0,
         'battles': 0,
         'reachedCaps': set()}

    @staticmethod
    def initialChapterData():
        return {'points': 0,
         'level': 0,
         'styleLevel': 0}


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


def getPresentLevel(rawLevel):
    return rawLevel + 1


class BattlePassConfig(object):
    REWARD_IDX = 0
    TAGS_IDX = 1

    def __init__(self, config):
        self._config = config
        self._season = config.get('season') or {}
        self._rewards = config.get('rewards') or {}
        self._chaptersType = {}
        if not self.chapters:
            return
        for chapterID, chapterData in self.chapters.iteritems():
            if self._chaptersType.get(chapterData['chapterType']):
                self._chaptersType[chapterData['chapterType']].add(chapterID)
            self._chaptersType[chapterData['chapterType']] = {chapterID}

    @property
    def mode(self):
        return self._config.get('mode', 'disabled')

    @property
    def seasonID(self):
        return self._season.get('seasonID', 0)

    @property
    def levelsToTriggerHint(self):
        return self._season.get('levelsToTriggerHint', 1)

    @property
    def seasonNum(self):
        return self._season.get('seasonNum', 0)

    @property
    def currentCollectionId(self):
        return self._season.get('currentCollectionId', 0)

    @property
    def seasonStart(self):
        return self._season.get('seasonStart', 0)

    @property
    def seasonFinish(self):
        return self._season.get('seasonFinish', 0)

    @property
    def finalOfferTime(self):
        return self._season.get('finalOfferTime', 0)

    @property
    def shopOfferFinishTime(self):
        return self._season.get('shopOfferFinishTime', 0)

    @property
    def points(self):
        return self._season.get('points', {})

    @property
    def chapters(self):
        return self._season.get('chapters', {})

    @property
    def isSingleChapter(self):
        return len(self.chapters) == 1

    @property
    def minVehLevelToEarnPoints(self):
        return self._season.get('minVehLevelToEarnPoints', MIN_VEHICLE_LEVEL)

    @property
    def vehWeekCaps(self):
        return self._season.get('vehWeekCaps', ())

    @property
    def vehCapFactor(self):
        return self._season.get('vehCapFactor', 0)

    @property
    def capsFlow(self):
        return self._season.get('capsFlow', BattlePassCapsFlow.WEEK.value)

    @property
    def vehCapBase(self):
        return self._season.get('vehCapBase', 0)

    def vehWeekCapByShift(self, index):
        if len(self.vehWeekCaps) <= index:
            LOG_ERROR('BattlePass cannot get vehWeekCaps list item by its index, len(vehWeekCaps)={}, index={}'.format(len(self.vehWeekCaps), index))
            return 0
        return self.vehWeekCaps[index]

    def vehFactorCapByShift(self, index):
        return self.vehCapBase + self.vehCapFactor * index

    @property
    def vehOverrides(self):
        return self._season.get('vehOverrides', {})

    def getRewardType(self, chapterID):
        if chapterID not in self.chapters:
            LOG_ERROR('BattlePass wrong chapter={}, exists: {}'.format(chapterID, self.chapters))
            return None
        else:
            return FinalReward(self.chapters[chapterID]['finalRewardType'])

    def getChapterLevels(self, chapterID):
        return self.getChapter(chapterID).get('levels', (0,))

    def getMaxChapterLevel(self, chapterID):
        return len(self.getChapterLevels(chapterID)) if chapterID else 0

    def getMaxChapterPoints(self, chapterID):
        return self.getChapterLevels(chapterID)[-1] if chapterID else MAX_NON_CHAPTER_POINTS

    def getRegularChapterIds(self):
        return self._chaptersType.get(BattlePassChapterType.DEFAULT.value, set())

    def getResourceChapterIds(self):
        return self._chaptersType.get(BattlePassChapterType.RESOURCE.value, set())

    def iterBySpecialChapterIds(self):
        for chapterID in self._chaptersType.get(BattlePassChapterType.MARATHON.value, set()):
            yield chapterID

        for chapterID in self._chaptersType.get(BattlePassChapterType.RESOURCE.value, set()):
            yield chapterID

    def getbattlePassCost(self, chapterID):
        return self.chapters.get(chapterID, {}).get('battlePassCost', {'gold': 0})

    @staticmethod
    def iterRewardRanges(prevLvl, newLvl, rewardMask):
        return ((fromLvl, toLvl, mask) for fromLvl, toLvl, mask in ((prevLvl, newLvl, BattlePassConsts.FREE_MASK), (prevLvl, newLvl, BattlePassConsts.PAID_MASK)) if mask & rewardMask)

    def isGameModeEnabled(self, gameMode):
        return self.points.get(gameMode, {}).get('enabled', False)

    def isBuyingAllowed(self):
        return self.isActive(int(time.time()))

    def isActive(self, curTime):
        return self.isEnabled() and self.seasonStart <= curTime < self.seasonFinish

    def isEnabled(self):
        return self.mode == 'enabled'

    def isPaused(self):
        return self.mode == 'paused'

    def isDisabled(self):
        return self.mode == 'disabled'

    def isSeasonTimeOver(self, curTime):
        return int(curTime) >= self.seasonFinish

    def isMarathonChapter(self, chapterID):
        return chapterID in self._chaptersType.get(BattlePassChapterType.MARATHON.value, [])

    def isResourceChapter(self, chapterID):
        return chapterID in self._chaptersType.get(BattlePassChapterType.RESOURCE.value, [])

    def isRegularChapter(self, chapterID):
        return chapterID in self._chaptersType.get(BattlePassChapterType.DEFAULT.value, [])

    def getChapterExpireTimestamp(self, chapterID):
        return self.getChapter(chapterID).get('expires', 0)

    def getChapterStartTimestamp(self, chapterID):
        return self.getChapter(chapterID).get('startDate', 0)

    def getGroupChapterByType(self):
        return self._chaptersType

    def getSpecialVehicles(self):
        return self._season.get('specialVehicles', [])

    def isSpecialVehicle(self, vehTypeCompDescr):
        return vehTypeCompDescr in self.getSpecialVehicles()

    @property
    def capBonusList(self):
        return self._season.get('capBonuses', (0,) * MAX_VEHICLE_LEVEL)

    def getVehCapBonus(self, index):
        if len(self.capBonusList) <= index:
            LOG_ERROR('BattlePass cannot get capBonuses list item by its index, len(capBonuses)={}, index={}'.format(len(self.capBonusList), index))
            return 0
        return self.capBonusList[index]

    def capBonusByVehTypeCompDescr(self, vehTypeCompDescr):
        vehCapBonus = self.vehOverrides.get(vehTypeCompDescr, {}).get('capBonus')
        return vehCapBonus if vehCapBonus else self.getVehCapBonus(getVehicleLevel(vehTypeCompDescr) - 1)

    def bonusPointsList(self, vehTypeCompDescr=None, isWinner=True, gameMode=ARENA_BONUS_TYPE.REGULAR):
        teamKey = 'win' if isWinner else 'lose'
        teamPoints = self.points.get(gameMode, {})
        if vehTypeCompDescr in teamPoints:
            teamPoints = teamPoints[vehTypeCompDescr]
        return teamPoints.get(teamKey) or (0,) * getBattlePassByGameMode(gameMode).getTeamSize()

    def getSeasonRewards(self):
        return self._rewards

    def getChapterRewards(self, chapterID, rewardType):
        return self._rewards.get(chapterID, {}).get(rewardType, {})

    def getTags(self, chapterID, level, rewardType):
        return self.getChapterRewards(chapterID, rewardType).get(level, ({}, tuple()))[BattlePassConfig.TAGS_IDX]

    def getRewardByMask(self, chapterID, level, rewardMask):
        return self.getRewardByType(chapterID, level, MASK_TO_REWARD[rewardMask])

    def getFreeReward(self, chapterID, level):
        return self.getRewardByType(chapterID, level, BattlePassConsts.REWARD_FREE)

    def getPaidReward(self, chapterID, level):
        return self.getRewardByType(chapterID, level, BattlePassConsts.REWARD_PAID)

    def getRewardByType(self, chapterID, level, rewardType):
        return self.getChapterRewards(chapterID, rewardType).get(level, ({}, tuple()))[BattlePassConfig.REWARD_IDX]

    def getChapterBorders(self, chapterID):
        fromLevel = 1
        toLevel = len(self.getChapterLevels(chapterID))
        return (fromLevel, toLevel)

    def getChapterIDs(self):
        return list(self.chapters.iterkeys())

    def getAvailableStyles(self):
        return tuple((chapter['styleId'] for chapter in self.chapters.itervalues()))

    def getChapterStyleID(self, chapterID):
        return self.chapters.get(chapterID, {}).get('styleId')

    def getChapter(self, chapterID):
        return self.chapters.get(chapterID, {})
