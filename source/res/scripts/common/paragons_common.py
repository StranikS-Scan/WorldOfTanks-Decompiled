# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/paragons_common.py
import time
from calendar import timegm
import typing
from enum import Enum
if typing.TYPE_CHECKING:
    from typing import Dict, Set, List, Tuple, Optional
    T_BRANCH_STATE = Tuple[int, int, int]
PARAGONS_VEHICLE_LEVELS = (6, 7, 8, 9, 10)
PARAGONS_MIN_VEHICLE_COUNT = 3
PARAGONS_MAX_VEHICLE_LEVEL = PARAGONS_VEHICLE_LEVELS[-1]
PARAGONS_MIN_VEHICLE_LEVEL = PARAGONS_VEHICLE_LEVELS[0]
COMPLETE_VEHICLE_PROGRESS_WINS_COUNT = 1
PARAGONS_PREFIX = 'paragon'
PARAGONS_ENTITLEMENT = 'rewards_choice'
PARAGONS_STOREFRONT_AGATE = 'paragons'
PARAGONS_STOREFRONT_SHOP = 'paragons_storefront'
PARAGONS_PDATA_KEY = 'paragons'
PARAGONS_QUESTS_PREFIX = 'paragons'
PARAGONS_UNLOCKS_PDATA_KEY = 'paragonsUnlocks'
PARAGONS_REWARDS_PDATA_KEY = 'rewards'
PARAGONS_SELECTED_REWARDS_PDATA_KEY = 'selectedRewards'
PARAGONS_CHAPTER_PROGRESS_PDATA_KEY = 'chaptersProgress'
PARAGONS_COINS_TOKEN = 'paragonsCoin'
ENDLESS_TOKEN_TIME_STRING = '28.01.2100 00:01'
ENDLESS_TOKEN_TIME = int(timegm(time.strptime(ENDLESS_TOKEN_TIME_STRING, '%d.%m.%Y %H:%M')))
PARAGONS_SELECTED_REWARD_TOKEN_PREFIX = 'paragonsSelectedRewards'
PARAGONS_COINS_CHAPTER_TOKEN_PREFIX = PARAGONS_COINS_TOKEN + ':c:'
PARAGONS_COINS_CHAPTER_TOKEN_FORMAT = PARAGONS_COINS_CHAPTER_TOKEN_PREFIX + '{}'
PARAGONS_SEASON_PRODUCT_TAG_PREFIX = 'paragons_s'

class _Enum(Enum):

    @classmethod
    def hasValue(cls, value):
        return value in cls._value2member_map_


class ParagonsEntitlements(Enum):
    V_11 = 'v_11_common'
    V_11_S1 = 'v_11_s1'
    V_11_S2 = 'v_11_s2'

    @classmethod
    def all(cls):
        return [ entitlementId.value for entitlementId in cls ]

    @classmethod
    def vehicleEntitlements(cls):
        return (cls.V_11.value, cls.V_11_S1.value, cls.V_11_S2.value)


class ErrorReasons(Enum):
    UNKNOWN_BRANCH = 'unknown_branch'
    BRANCH_ALREADY_RESET = 'branch_already_reset'
    UNSUPPORTED_ITEM = 'unsupported_item'
    ITEM_ALREADY_UNLOCKED = 'item_already_unlocked'
    ITEM_UNLOCK_CONFIG_MISSING = 'item_unlock_config_missing'
    NOT_ENOUGH_LEVEL = 'not_enough_level'
    NOT_ENOUGH_ACCESS_POINTS = 'not_enough_access_points'
    ACCESS_POINTS_FAILED_TO_GRANT = 'access_points_failed_to_grant'
    REWARDS_FAILED_TO_GRANT = 'rewards_failed_to_grant'
    RESET_NOT_AVAILABLE = 'reset_is_not_available'
    BRANCH_RESET_IMPOSSIBLE = 'branch_reset_impossible'
    RESET_IMPOSSIBLE_DOSSIER_NOT_CACHED = 'reset_impossible_dossier_not_cached'
    RESET_IMPOSSIBLE_VEHICLE_IS_LOCKED = 'reset_impossible_vehicle_is_locked'
    RESET_IMPOSSIBLE_VEHICLE_IS_BROKEN = 'reset_impossible_vehicle_is_broken'
    CHAPTER_SELECTION_IMPOSSIBLE_CHAPTER_FINISHED = 'chapter_selection_impossible_finished'
    CHAPTER_SELECTION_IMPOSSIBLE_WRONG_CHAPTER = 'chapter_selection_impossible_wrong_chapter'
    CHAPTER_SELECTION_IMPOSSIBLE_ANNOUNCEMENT_CHAPTER = 'chapter_selection_impossible_announcement_chapter'
    SELECTED_REWARD_ALREADY_ADDED_TO_HISTORY = 'selected_reward_already_added_to_history'
    CHAPTER_SELECTION_IMPOSSIBLE_PARAGONS_NOT_UNLOCKED = 'chapter_selection_impossible_paragons_not_unlocked'

    @classmethod
    def all(cls):
        return {reason.value for reason in cls}


class VehicleResetUnavailabilityReasons(Enum):
    UNAVAILABLE = 'unavailable'
    ALREADY_RESET = 'alreadyReset'
    NOT_UNLOCKED = 'notUnlocked'
    EARLY_ACCESS = 'earlyAccess'
    NOT_ELITE = 'notElite'
    IN_BATTLE = 'inBattle'
    AWAITING_BATTLE = 'awaitingBattle'
    IN_UNIT = 'inUnit'
    IN_PREBATTLE = 'inPrebattle'
    BROKEN = 'broken'

    @classmethod
    def all(cls):
        return {reason.value for reason in cls}


def getNationIdByBranchId(branchID):
    return int(str(branchID)[:-2]) - 1


def getResetVehicles(paragonsStorage):
    resetVehicles = set()
    if not paragonsStorage:
        return resetVehicles
    for treeCD, vehicleCD in paragonsStorage['resetVehicles'].iteritems():
        resetVehicles.update(vehicleCD)

    return resetVehicles


def isParagonsQuestID(questID):
    return questID.startswith(PARAGONS_QUESTS_PREFIX)


def getParagonsEntitlement(id):
    return '_'.join((PARAGONS_PREFIX, PARAGONS_ENTITLEMENT, id))


def getAllParagonsEntitlements():
    return {getParagonsEntitlement(entSuffix) for entSuffix in ParagonsEntitlements.all()}


def getVehicleParagonsEntitlements():
    return {getParagonsEntitlement(entSuffix) for entSuffix in ParagonsEntitlements.vehicleEntitlements()}


PARAGONS_ENT_NUMBER_CODE_TO_STRING_CODE = {0: ParagonsEntitlements.V_11.value,
 1: ParagonsEntitlements.V_11_S1.value,
 2: ParagonsEntitlements.V_11_S2.value}
PARAGONS_ENT_NUMBER_CODE_TO_ENTITLEMENTS = {k:getParagonsEntitlement(v) for k, v in PARAGONS_ENT_NUMBER_CODE_TO_STRING_CODE.iteritems()}
PARAGONS_ENTITLEMENT_TO_NUMBER_CODES = {v:k for k, v in PARAGONS_ENT_NUMBER_CODE_TO_ENTITLEMENTS.iteritems()}
FRIEND_ENT_CODES = {0: (0, 1, 2)}

def getSelectedRewardToken(entCode, bonusCD):
    return '{}:{}:{}'.format(PARAGONS_SELECTED_REWARD_TOKEN_PREFIX, PARAGONS_ENT_NUMBER_CODE_TO_STRING_CODE[entCode], bonusCD)


def getSelectedRewardTokenTemplate(entCode):
    return '{}:{}'.format(PARAGONS_SELECTED_REWARD_TOKEN_PREFIX, PARAGONS_ENT_NUMBER_CODE_TO_STRING_CODE[entCode])


class BaseParagonsBranchState(object):
    __slots__ = ('_branchId', '_pendingVehicles', '_resetsCount', 'bonusCount')

    def __init__(self, branchId, pendingVehicles=None, resetCounts=0, bonusCount=0, _=0):
        self._branchId = branchId
        self._pendingVehicles = pendingVehicles or set()
        self._resetsCount = resetCounts
        self.bonusCount = bonusCount

    @property
    def id(self):
        return self._branchId

    @property
    def resetsCount(self):
        return self._resetsCount

    @resetsCount.setter
    def resetsCount(self, value):
        self._resetsCount = value

    @property
    def isReset(self):
        return bool(self._resetsCount > 0 and self._pendingVehicles)

    def toRawData(self):
        return (self._resetsCount, self.bonusCount, 0)


class BaseParagonsStorage(object):
    __slots__ = ('__data',)
    BRANCH_STATE_CLASS = BaseParagonsBranchState

    def __init__(self, data):
        self.__data = data

    @property
    def _storage(self):
        return self.__data

    @property
    def paragonsUnlockIDs(self):
        return self._storage.get('paragonsUnlocks', set())

    @property
    def resetBranchesIds(self):
        return set(self._storage['resetBranches'].iterkeys())

    def wasBranchEverReset(self):
        return bool(self._storage['resetBranches'])

    @property
    def resetBranchesCount(self):
        return sum(((1 if self.getBranchStateById(branchID).isReset else 0) for branchID in self.resetBranchesIds))

    @property
    def resetVehicles(self):
        return getResetVehicles(self._storage)

    def pendingVehicles(self):
        return self._storage.get('resetVehicles', {})

    def branchPendingVehicles(self, branchID):
        return self._storage.get('resetVehicles', {}).get(branchID, frozenset())

    @property
    def chosenChapterID(self):
        return self._storage.get('chosenChapter', None)

    @property
    def chaptersProgress(self):
        return self._storage.get('chaptersProgress', None)

    @property
    def selectedRewards(self):
        return self._storage.get('selectedRewards', {})

    @property
    def checkAvailability(self):
        return self._storage.get('checkAvailability', False)

    def clear(self):
        self.__data = None
        return

    def isBranchStateExists(self, branchID):
        return branchID in self._storage['resetBranches']

    def getBranchStateById(self, branchID):
        return self.BRANCH_STATE_CLASS(branchID, self.branchPendingVehicles(branchID), *self._storage['resetBranches'].get(branchID, (0, 0, 0)))

    def getProgress(self, chapterID=None):
        chaptersProgress = self.chaptersProgress
        return chaptersProgress.get(self.chosenChapterID if chapterID is None else chapterID, 0)

    def setChapterProgress(self, chapterID, level):
        pass

    def resetCheckAvailability(self):
        pass

    def addParagonsUnlockID(self, paragonsUnlockID):
        pass

    def setChapter(self, chapterID):
        pass

    def setResetVehicles(self, branchID, vehicles):
        pass

    def removeVehicleFromPending(self, branchID, vehCD):
        pass

    def takeBackParagonsUnlockID(self, paragonsUnlockID):
        pass

    def setBranchState(self, branchState):
        pass

    def addSelectedReward(self, chapterID, levelID, entCode, bonusCD):
        pass

    @staticmethod
    def makeDefaultStorage():
        return {'resetVehicles': {},
         'resetBranches': {},
         'paragonsUnlocks': set(),
         'chosenChapter': None,
         'chaptersProgress': {},
         'selectedRewards': {}}


class BaseParagons(object):
    __slots__ = ('__storage',)

    def __init__(self, storage):
        self.__storage = storage

    def destroy(self):
        self.__storage.clear()
        self.__storage = None
        return

    @property
    def storage(self):
        return self.__storage

    @property
    def chapter(self):
        return self.__storage.chosenChapterID

    @property
    def level(self):
        level = self.storage.getProgress()
        return level

    @property
    def chaptersProgress(self):
        return self.storage.chaptersProgress

    @property
    def paragonsUnlockIDs(self):
        return self.storage.paragonsUnlockIDs

    @property
    def resetVehicles(self):
        return self.storage.resetVehicles

    def getProgressByChapterID(self, chapterID):
        return self.storage.getProgress(chapterID)

    def getSelectedReward(self, chapterId, levelID, entCode):
        return self.storage.selectedRewards.get((chapterId, levelID, entCode))


def getParagonChapterToken(chapterId=None):
    return PARAGONS_COINS_CHAPTER_TOKEN_FORMAT.format(chapterId) if chapterId is not None else PARAGONS_COINS_TOKEN


def getChapterByProgressToken(tokenId):
    return None if tokenId == PARAGONS_COINS_TOKEN else int(tokenId.split(':')[-1])


class ParagonsGrantCoinsSourceIDs(_Enum):
    BATTLE = 'battle'
    FIRST_UNLOCK = 'firstUnlock'
    BRANCH_RESET = 'branchReset'

    @classmethod
    def getFirstUnlockLogInfo(cls, vehicleCD):
        return '{}:{}'.format(cls.FIRST_UNLOCK.value, vehicleCD)

    @classmethod
    def getBranchResetLogInfo(cls, branchID):
        return '{}:{}'.format(cls.BRANCH_RESET.value, branchID)

    @classmethod
    def getBattleLogInfo(cls, arenaUniqueID):
        return '{}:{}'.format(cls.BATTLE.value, arenaUniqueID)
