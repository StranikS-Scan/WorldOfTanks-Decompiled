# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/paragons_common.py
import time
from calendar import timegm
import typing
from enum import Enum
if typing.TYPE_CHECKING:
    from typing import Dict, Set, Tuple, Optional
    T_BRANCH_STATE = Tuple[int]
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
PARAGONS_SELECTED_REWARDS_ORDER_PDATA_KEY = 'selectedRewardOrder'
PARAGONS_CHAPTER_PROGRESS_PDATA_KEY = 'chaptersProgress'
PARAGONS_COINS_TOKEN = 'paragonsCoin'
ENDLESS_TOKEN_TIME_STRING = '28.01.2100 00:01'
ENDLESS_TOKEN_TIME = int(timegm(time.strptime(ENDLESS_TOKEN_TIME_STRING, '%d.%m.%Y %H:%M')))
PARAGONS_SELECTED_REWARD_TOKEN_PREFIX = 'paragonsSelectedRewards'
PARAGONS_SELECTED_VEHICLE_TOKEN_PREFIX = PARAGONS_SELECTED_REWARD_TOKEN_PREFIX + ':vehicle'

class ParagonsEntitlements(Enum):
    V_11 = 'v_11'
    LOCKED_TECH_TREE = 'locked_tech_tree'

    @classmethod
    def all(cls):
        return {entitlementId.value for entitlementId in cls}


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
    CHAPTER_SELECTION_IMPOSSIBLE_CURRENT_NOT_FINISHED = 'chapter_selection_impossible_current_not_finished'
    CHAPTER_SELECTION_IMPOSSIBLE_WRONG_CHAPTER = 'chapter_selection_impossible_wrong_chapter'
    CHAPTER_SELECTION_IMPOSSIBLE_ANNOUNCEMENT_CHAPTER = 'chapter_selection_impossible_announcement_chapter'
    SELECTED_REWARD_ALREADY_ADDED_TO_HISTORY = 'selected_reward_already_added_to_history'

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


TOKEN_PREFIX_TO_ENT_CODE = {PARAGONS_SELECTED_VEHICLE_TOKEN_PREFIX: getParagonsEntitlement(ParagonsEntitlements.V_11.value)}
PARAGONS_ENT_NUMBER_CODE_TO_ENTITLEMENTS = {intCode:ent for intCode, ent in enumerate(getAllParagonsEntitlements())}
PARAGONS_ENTITLEMENT_TO_NUMBER_CODES = {v:k for k, v in PARAGONS_ENT_NUMBER_CODE_TO_ENTITLEMENTS.iteritems()}
SELECTED_REWARD_TOKEN_PREFIX_TO_BONUS_TYPE = {PARAGONS_SELECTED_VEHICLE_TOKEN_PREFIX: 'vehicles'}

class BaseParagonsBranchState(object):
    __slots__ = ('_branchId', '_pendingVehicles', 'resetsCount')

    def __init__(self, branchId, pendingVehicles=None, resetCounts=None):
        self._branchId = branchId
        self._pendingVehicles = pendingVehicles or set()
        self.resetsCount = resetCounts or 0

    @property
    def id(self):
        return self._branchId

    @property
    def isReset(self):
        return self.resetsCount > 0 and self._pendingVehicles

    def toRawData(self):
        return (self.resetsCount,)


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
        return set(self._storage['resetBranches'].keys())

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
    def selectedRewardOrder(self):
        return self._storage.get('selectedRewardOrder', {})

    def clear(self):
        self.__data = None
        return

    def isBranchStateExists(self, branchID):
        return branchID in self._storage['resetBranches']

    def getBranchStateById(self, branchID):
        return self.BRANCH_STATE_CLASS(branchID, self.branchPendingVehicles(branchID), self._storage['resetBranches'].get(branchID))

    def getProgress(self, chapterID=None):
        chaptersProgress = self.chaptersProgress
        return chaptersProgress.get(self.chosenChapterID if chapterID is None else chapterID, 0)

    @staticmethod
    def makeDefaultStorage():
        return {'resetVehicles': {},
         'resetBranches': {},
         'paragonsUnlocks': set(),
         'chosenChapter': None,
         'chaptersProgress': {},
         'selectedRewardOrder': {}}


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

    def getSelectedRewardsOrder(self, entNumberCode):
        return self.storage.selectedRewardOrder.get(entNumberCode, {})

    def getSelectedRewardsOrderByEntitlementID(self, entitlementID):
        return self.getSelectedRewardsOrder(PARAGONS_ENTITLEMENT_TO_NUMBER_CODES[entitlementID])
