# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/paragons_controller.py
import itertools
import logging
from collections import defaultdict
import BigWorld
import typing
from adisp import adisp_process
from Event import Event
from constants import Configs, MAX_VEHICLE_LEVEL
from gui import SystemMessages
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.paragons.paragons_helpers.paragons_helpers import addParagonsUnlockIDToShow, setParagonsResetBranchToShow
from gui.limited_ui.lui_rules_storage import LuiRules
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.gui_items.processors.paragons import ParagonsResetBranchProcessor, ParagonsSetChapterProcessor
from gui.shared.items_cache import CACHE_SYNC_REASON
from gui.shared.money import Money
from gui.shared.utils.requesters import REQ_CRITERIA
from PlayerEvents import g_playerEvents as events
from helpers import dependency, server_settings
from paragons_helpers import pushParagonsBranchResetedNotification, pushParagonsBranchResetErrorNotification
from helpers.server_settings import ParagonsConfig
from items import vehicles, getTypeOfCompactDescr
from paragons_common import VehicleResetUnavailabilityReasons, PARAGONS_PDATA_KEY, PARAGONS_UNLOCKS_PDATA_KEY, PARAGONS_COINS_TOKEN, PARAGONS_SELECTED_REWARD_TOKEN_PREFIX, PARAGONS_CHAPTER_PROGRESS_PDATA_KEY, getParagonChapterToken, PARAGONS_ENTITLEMENT_TO_NUMBER_CODES, PARAGONS_SELECTED_REWARDS_PDATA_KEY
from skeletons.gui.game_control import IParagonsController, ILimitedUIController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from typing import Tuple, Set, Optional, Callable, Dict, Generator
    from account_helpers.paragons import Paragons
    from gui.shared.gui_items.Vehicle import Vehicle
    from helpers.server_settings import ServerSettings
    T_PROCESSOR_CALLBACK = Callable[[bool], None]
    T_PROCESSOR_CHAPTER_CALLBACK = Callable[[bool, int], None]
_logger = logging.getLogger(__name__)

class ParagonsController(IParagonsController):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __limitedUiController = dependency.descriptor(ILimitedUIController)

    def __init__(self):
        super(ParagonsController, self).__init__()
        self.onSettingsChanged = Event()
        self.onAvailabilityChanged = Event()
        self.onLevelIncreased = Event()
        self.onProgressPointsChanged = Event()
        self.onFeatureStateChanged = Event()
        self.onParagonsUnlocksChanged = Event()
        self.onParagonsUnlocksStateChanged = Event()
        self.onParagonsStateChanged = Event()
        self.onSelectedRewardMarked = Event()
        self.onSelectedRewardTokenReceived = Event()
        self.__serverSettings = None
        self.__availabilityBeforeSync = False
        self.__lockedItems = None
        self.__maxLevelVehiclesCds = None
        self.__isPaused = False
        self.__isEnabled = False
        self.__paragonsUnlocksIsEnabled = {}
        self.__completedChapterIDs = None
        self.__branchesController = _ParagonsBranchesController()
        return

    @property
    def serverSettings(self):
        return self.__serverSettings

    @property
    def isConsumesEntitlements(self):
        return True

    @property
    def paragons(self):
        return BigWorld.player().paragons

    @property
    def branches(self):
        return self.__branchesController

    @property
    def config(self):
        if self.__lobbyContext:
            return self.__lobbyContext.getServerSettings().paragonsConfig
        _logger.error('[Paragons]: attempt to access Paragons config before it is created')
        return ParagonsConfig.defaults()

    @property
    def isEnabled(self):
        return self.config.isEnabled

    @property
    def isPaused(self):
        return self.config.isPaused

    @property
    def isInactive(self):
        return not self.config.isEnabled or self.config.isPaused

    @property
    def isBranchResetAvailable(self):
        return self.branches.isBranchResetAvailable

    @property
    def wasBranchResetEverAvailable(self):
        return bool(self.paragons.resetBranchesIds) or self.isBranchResetAvailable

    @property
    def isLimitedUiRuleCompleted(self):
        return self.__limitedUiController.isRuleCompleted(LuiRules.PARAGONS_ENTRY_POINT)

    @property
    def isLimitedUiParagonsButtonsRuleCompleted(self):
        return self.__limitedUiController.isRuleCompleted(LuiRules.PARAGONS_BUTTONS)

    @property
    def isLimitedUiParagonsTreeBranchesRuleCompleted(self):
        return self.__limitedUiController.isRuleCompleted(LuiRules.PARAGONS_TREE_BRANCHES)

    @property
    def isLimitedUiParagonsNotificationRuleCompleted(self):
        return self.__limitedUiController.isRuleCompleted(LuiRules.PARAGONS_NOTIFICATION)

    @property
    def chapterID(self):
        return self.paragons.chapter

    @property
    def availableChapters(self):
        return self.config.getChapterIDs() - self.config.getAnnouncementChapterIDs()

    @property
    def isAnyChapterAvailable(self):
        return bool(self.chapterID is None and not all((self.isChapterComplete(chapterID) for chapterID in self.availableChapters)))

    def isPreviewChapter(self, chapterID):
        return chapterID != self.chapterID

    @property
    def progress(self):
        return self.getProgressPoints(self.chapterID)

    @property
    def level(self):
        return self.paragons.level

    @property
    def minUnlockedNecessaryLevelVehiclesCount(self):
        return self.config.minUnlockXLevelVehiclesCount

    @property
    def unlockedNecessaryLevelVehicleCDs(self):
        return self.paragons.getUnlockedNecessaryLevelVehiclesCDs()

    @property
    def unlockedNecessaryLevelVehiclesCount(self):
        return len(self.unlockedNecessaryLevelVehicleCDs)

    @property
    def paragonsUnlockIDs(self):
        return self.paragons.paragonsUnlockIDs

    @property
    def lockedItems(self):
        if self.__lockedItems is None:
            self.__lockedItems = set()
            unlocksConfig = self.config.paragonsUnlocks
            grantedUnlocks = self.paragonsUnlockIDs
            for paragonUnlockID, paragonsUnlock in unlocksConfig.iteritems():
                if paragonUnlockID in grantedUnlocks:
                    continue
                for lockedItems in paragonsUnlock.get('lockedItemsByItemTypeName', {}).itervalues():
                    self.__lockedItems.update(lockedItems)

        return self.__lockedItems

    @property
    def resetVehicles(self):
        return self.paragons.resetVehicles

    @property
    def allChapterIDs(self):
        return self.config.getChapterIDs()

    @property
    def availableChapterIDs(self):
        return self.allChapterIDs - self.config.getAnnouncementChapterIDs()

    @property
    def completedChapterIDs(self):
        if self.__completedChapterIDs is None:
            self.__completedChapterIDs = [ chapterID for chapterID in sorted(self.availableChapters) if self.isChapterComplete(chapterID) ]
        return self.__completedChapterIDs

    def clearCache(self):
        self.__invalidatePropertiesCache()

    def getFirstChapterWithAvailableRewards(self):
        if self.paragons.chapter is not None:
            return self.paragons.chapter
        else:
            for chapterID in reversed(self.completedChapterIDs):
                if not self.isAllSelectablesClaimed(chapterID):
                    return chapterID

            return

    def isAllSelectablesClaimed(self, chapterID):
        selectedRewardsRecevied = sum((1 for cID, _, _ in self.paragons.storage.selectedRewards if cID == chapterID))
        possibleSelectedRewards = sum((1 for cID, _, _ in self.config.defaultSelectedRewardOrder if cID == chapterID))
        return selectedRewardsRecevied >= possibleSelectedRewards

    def getProgressPoints(self, chapterID):
        return self.__itemsCache.items.tokens.getTokenCount(getParagonChapterToken(chapterID))

    def getSelectedRewardBonusCD(self, chapterID, levelID, entitlementID):
        return self.paragons.getSelectedReward(chapterID, levelID, PARAGONS_ENTITLEMENT_TO_NUMBER_CODES[entitlementID])

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        if self.isEnabled:
            self.__addListeners()
        self.__isPaused = self.isPaused
        self.__isEnabled = self.isEnabled
        self.__paragonsUnlocksIsEnabled = {paragonsUnlockID:self.config.isParagonsUnlockEnabled(paragonsUnlockID) for paragonsUnlockID in self.config.paragonsUnlocks.iterkeys()}

    def onAccountBecomeNonPlayer(self):
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        setParagonsResetBranchToShow(isShow=False)
        self.__removeListeners()

    def onDisconnected(self):
        self.__serverSettings = None
        setParagonsResetBranchToShow(isShow=False)
        self.__invalidatePropertiesCache()
        return

    def isChapterComplete(self, chapterID=None):
        announcementChapters = self.config.getAnnouncementChapterIDs()
        if chapterID is not None:
            if chapterID in announcementChapters:
                return False
            chapterLvl = self.paragons.getProgressByChapterID(chapterID)
            return chapterLvl == max(self.config.getChapterLevelIDs(chapterID))
        else:
            chosenChapter = self.paragons.chapter
            return False if chosenChapter is None or chosenChapter in announcementChapters else self.level == max(self.config.getChapterLevelIDs(chosenChapter))

    def isChapterPaused(self, chapterID=None):
        return chapterID is not None and self.__itemsCache.items.tokens.isTokenAvailable(getParagonChapterToken(chapterID)) and chapterID != self.chapterID and not self.isChapterComplete(chapterID)

    def isVehicleReset(self, compDescr):
        return self.isEnabled and self.paragons.isVehicleReset(compDescr)

    def isNextResetVehUnlocked(self, compDescr):
        if not self.isEnabled:
            return
        for _, _, nextLevelCD, _ in self.__itemsCache.items.getItemByCD(compDescr).getUnlocksDescrs():
            if getTypeOfCompactDescr(nextLevelCD) == GUI_ITEM_TYPE.VEHICLE and self.__itemsCache.items.getItemByCD(nextLevelCD).isUnlocked and self.paragons.isVehicleWasReset(nextLevelCD):
                return True

        return False

    def isItemLocked(self, itemDescr):
        return itemDescr in self.lockedItems

    def getDefaultVehicleProgressPoints(self, vehicleLevel):
        defaultResetVehicleConfig = self.config.defaultResetVehicleConfigs.get(vehicleLevel)
        return defaultResetVehicleConfig.progressPointsAmount if defaultResetVehicleConfig else 0

    def getVehicleProgressPoints(self, compDescr):
        resetVehicleConfig = self.config.getResetVehicleConfig(compDescr)
        return resetVehicleConfig.progressPointsAmount if resetVehicleConfig else 0

    def isVehicleFirstUnlockPointsAvailable(self, vehicle, includeParagonsAvailable=True):
        isAvailable = self.wasBranchResetEverAvailable if includeParagonsAvailable else True
        return isAvailable and not vehicle.isUnlocked and not self.paragons.isVehicleWasReset(vehicle.compactDescr)

    def getVehicleFirstUnlockPoints(self, vehicle, includeParagonsAvailable=True):
        if not self.isVehicleFirstUnlockPointsAvailable(vehicle, includeParagonsAvailable):
            return 0
        resetVehicleConfig = self.config.getResetVehicleConfig(vehicle.compactDescr)
        return resetVehicleConfig.firstUnlockPoints if resetVehicleConfig else 0

    def getVehicleProgressPointsMultiplier(self, compDescr):
        branchIds = vehicles.g_cache.paragonsBranchesToReset.getResetBranchIdsByVehicleCd(compDescr)
        return 0 if not branchIds else self.config.getResetVehicleConfig(compDescr).progressPointsMultiplier

    def getDefaultVehicleResetBonusBlueprintsCount(self, vehicleLevel):
        defaultResetVehicleConfig = self.config.defaultResetVehicleConfigs.get(vehicleLevel)
        return defaultResetVehicleConfig.resetBonusBlueprintsCount if defaultResetVehicleConfig else 0

    def getVehicleResetBonusBlueprintsCount(self, compDescr):
        resetVehicleConfig = self.config.getResetVehicleConfig(compDescr)
        return resetVehicleConfig.resetBonusBlueprintsCount if resetVehicleConfig else 0

    def getBranchResetVehicles(self, branchID):
        vehiclesCDs = vehicles.g_cache.paragonsBranchesToReset.getResetBranchById(branchID).resetVehicles
        return tuple((self.__itemsCache.items.getItemByCD(intCD) for intCD in vehiclesCDs))

    def getLockedResetVehicles(self, branchID):
        return sorted((item for item in self.getBranchResetVehicles(branchID) if not item.isUnlocked), key=lambda x: x.level)

    def isFirstUnlockBranchAvailable(self, branchID, includeParagonsAvailable=True):
        lockedResetVehicles = self.getLockedResetVehicles(branchID)
        for vehicle in lockedResetVehicles:
            if self.isVehicleFirstUnlockPointsAvailable(vehicle, includeParagonsAvailable):
                return True

        return False

    def getMaxLevelVehicles(self):
        if self.__maxLevelVehiclesCds is None:
            criteria = REQ_CRITERIA.VEHICLE.LEVEL(MAX_VEHICLE_LEVEL)
            self.__maxLevelVehiclesCds = set(self.__itemsCache.items.getVehicles(criteria))
        return set((self.__itemsCache.items.getItemByCD(vehicleCd) for vehicleCd in self.__maxLevelVehiclesCds))

    def getHiddenUIItems(self):
        return set(itertools.chain.from_iterable((self.config.getParagonsUnlockVehicles(paragonsUnlockID) for paragonsUnlockID in self.config.paragonsUnlocks if not self.config.isParagonsUnlockEnabled(paragonsUnlockID) and paragonsUnlockID not in self.paragons.storage.paragonsUnlockIDs)))

    def getCompleteBonusCoinsForBranch(self, branchID):
        limit = self.config.getBranchCompleteBonusLimit()
        bonusCoins = self.config.getBranchCompleteBonus()
        if limit and bonusCoins:
            branchState = self.paragons.storage.getBranchStateById(branchID)
            if branchState.bonusCount < limit:
                return bonusCoins
            return 0

    def getCoinsForBranchReset(self):
        return self.config.getCoinsForBranchReset()

    def isBranchReset(self, branchID):
        return self.paragons.storage.getBranchStateById(branchID).isReset

    @adisp_process
    def setChapter(self, chapterID, callback=None):
        result = yield ParagonsSetChapterProcessor(chapterID).request()
        SystemMessages.pushMessagesFromResult(result)
        if callback is not None:
            callback(result.success, chapterID)
        return

    def getChapterCloseoutTimeStamp(self, chapterID):
        return self.config.getChapterCloseoutTimeStamp(chapterID)

    def __addListeners(self):
        paragons = self.paragons
        paragons.onParagonsStateChanged += self.__onParagonsStateChange
        paragons.onLevelIncreased += self.__onLevelIncreased
        events.onClientUpdated += self.__onClientUpdate
        g_clientUpdateManager.addCallback('tokens', self.__onTokensUpdate)
        self.__itemsCache.onSyncStarted += self.__onItemsSyncStarted
        self.__itemsCache.onSyncCompleted += self.__onItemsSyncCompleted

    def __removeListeners(self):
        paragons = self.paragons
        paragons.onParagonsStateChanged -= self.__onParagonsStateChange
        paragons.onLevelIncreased -= self.__onLevelIncreased
        events.onClientUpdated -= self.__onClientUpdate
        g_clientUpdateManager.removeObjectCallbacks(self, True)
        self.__itemsCache.onSyncStarted -= self.__onItemsSyncStarted
        self.__itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onServerSettingsChange
        self.__serverSettings = serverSettings
        self.__onServerSettingsChange(serverSettings.getSettings())
        self.__serverSettings.onServerSettingsChange += self.__onServerSettingsChange
        return

    @server_settings.serverSettingsChangeListener(Configs.PARAGONS_CONFIG.value)
    def __onServerSettingsChange(self, serverSettings):
        self.__invalidatePropertiesCache()
        if self.isEnabled:
            self.__addListeners()
        else:
            self.__removeListeners()
        self.__checkFeatureStateChanged()
        self.__checkParagonsUnlocksStateChanged()
        self.onSettingsChanged(serverSettings.get(Configs.PARAGONS_CONFIG.value))

    def __onItemsSyncStarted(self, syncReason):
        if syncReason in (CACHE_SYNC_REASON.STATS_RESYNC, CACHE_SYNC_REASON.CLIENT_UPDATE):
            self.__availabilityBeforeSync = self.isBranchResetAvailable
            self.branches.onItemsSyncStarted()

    def __onItemsSyncCompleted(self, syncReason, syncedItems):
        if GUI_ITEM_TYPE.VEHICLE in syncedItems.keys() or syncReason == CACHE_SYNC_REASON.STATS_RESYNC:
            self.__invalidatePropertiesCache()
            if self.isBranchResetAvailable != self.__availabilityBeforeSync:
                self.__availabilityChanged()
            self.branches.onItemsSyncCompleted()

    def __invalidatePropertiesCache(self):
        self.__lockedItems = None
        self.__maxLevelVehiclesCds = None
        self.__completedChapterIDs = None
        self.branches.invalidateCache()
        return

    def __checkFeatureStateChanged(self):
        if self.__isPaused != self.isPaused:
            self.__isPaused = self.isPaused
        if self.__isEnabled != self.isEnabled:
            self.__isEnabled = self.isEnabled
        self.onFeatureStateChanged(self.__isPaused, self.__isEnabled)

    def __checkParagonsUnlocksStateChanged(self):
        newParagonsUnlocksStates = {paragonsUnlockID:self.config.isParagonsUnlockEnabled(paragonsUnlockID) for paragonsUnlockID in self.config.paragonsUnlocks.iterkeys()}
        diff = {}
        for paragonsUnlockID, prevState in self.__paragonsUnlocksIsEnabled.iteritems():
            newState = newParagonsUnlocksStates.get(paragonsUnlockID, prevState)
            if prevState != newState:
                diff[paragonsUnlockID] = newState

        self.__paragonsUnlocksIsEnabled = newParagonsUnlocksStates
        if diff:
            self.onParagonsUnlocksStateChanged(diff)

    def __availabilityChanged(self):
        self.onAvailabilityChanged()

    def __onParagonsStateChange(self):
        self.onParagonsStateChanged()
        self.__invalidatePropertiesCache()

    def __onLevelIncreased(self, _):
        self.onLevelIncreased()

    def __onParagonsUnlocksChanged(self, paragonsUnlockIDs, isGranted, isFullSync):
        if isGranted and not isFullSync:
            for paragonsUnlockID in paragonsUnlockIDs:
                addParagonsUnlockIDToShow(paragonsUnlockID)

        self.onParagonsUnlocksChanged(paragonsUnlockIDs, isGranted)

    def __onClientUpdate(self, diff, isFullSync):
        if PARAGONS_PDATA_KEY in diff:
            self.__invalidatePropertiesCache()
            self.__processParagonsUnlocksUpdate(diff.get(PARAGONS_PDATA_KEY), isFullSync)
            self.__processSelectedRewardsOrder(diff.get(PARAGONS_PDATA_KEY))
            self.__processChaptersProgress(diff.get(PARAGONS_PDATA_KEY))

    def __onTokensUpdate(self, diff):
        if PARAGONS_COINS_TOKEN in diff or getParagonChapterToken(self.chapterID) in diff:
            self.onProgressPointsChanged()
        needEmitSelectedReward = self.onSelectedRewardTokenReceived and any((t.startswith(PARAGONS_SELECTED_REWARD_TOKEN_PREFIX) for t in diff))
        if needEmitSelectedReward:
            self.onSelectedRewardTokenReceived(diff)

    def __processParagonsUnlocksUpdate(self, paragonsDiff, isFullSync):
        for paragonsDiffKey, paragonsDiffValue in paragonsDiff.iteritems():
            if paragonsDiffKey == PARAGONS_UNLOCKS_PDATA_KEY:
                self.__onParagonsUnlocksChanged(paragonsDiffValue, isGranted=True, isFullSync=isFullSync)
            if paragonsDiffKey == (PARAGONS_UNLOCKS_PDATA_KEY, '_d'):
                self.__onParagonsUnlocksChanged(paragonsDiffValue, isGranted=False, isFullSync=isFullSync)

    def __processSelectedRewardsOrder(self, diff):
        if PARAGONS_SELECTED_REWARDS_PDATA_KEY in diff:
            for data, bonusCD in diff[PARAGONS_SELECTED_REWARDS_PDATA_KEY].iteritems():
                chapterID, levelID, _ = data
                self.onSelectedRewardMarked(chapterID, levelID, bonusCD)

    def __processChaptersProgress(self, diff):
        if PARAGONS_CHAPTER_PROGRESS_PDATA_KEY in diff:
            for chapterID, _ in diff[PARAGONS_CHAPTER_PROGRESS_PDATA_KEY].iteritems():
                if self.isChapterComplete(chapterID):
                    self.__completedChapterIDs = None

        return


class _ParagonsBranchesController(object):
    __ctrl = dependency.descriptor(IParagonsController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        self.__resettableBranchIds = None
        self.__resettableBranchIdsBeforeSync = set()
        self.__isBranchResetAvailable = None
        self.onResettableBranchesChanged = Event()
        return

    @adisp_process
    def resetBranch(self, branchID, isStockVehConfiguration=False, ctx=None, callback=None):
        result = yield ParagonsResetBranchProcessor(branchID, isStockVehConfiguration, ctx).request()
        if result is not None and result.success:
            pushParagonsBranchResetedNotification(**result.auxData)
        else:
            pushParagonsBranchResetErrorNotification()
        if callback is not None:
            callback(result.success)
        return

    @property
    def isBranchResetAvailable(self):
        if not self.__itemsCache.isSynced():
            return False
        else:
            if self.__isBranchResetAvailable is None:
                self.__isBranchResetAvailable = self.__ctrl.isEnabled and self.__ctrl.unlockedNecessaryLevelVehiclesCount >= self.__ctrl.minUnlockedNecessaryLevelVehiclesCount and self.resetBranchesCount < self.maxResetBranchesCount
            return self.__isBranchResetAvailable

    @property
    def availableToResetBranchIds(self):
        return {branchID for branchID in self.resettableBranchIds if self.isBranchCanBeReset(branchID)[0]}

    @property
    def maxResetBranchesCount(self):
        return self.__ctrl.config.maxResetBranchesCount

    @property
    def resetBranchesCount(self):
        return self.__ctrl.paragons.resetBranchesCount

    @property
    def resettableBranchIds(self):
        if self.__resettableBranchIds is None:
            if not self.__ctrl.isEnabled or not self.isBranchResetAvailable:
                return set()
            self.__resettableBranchIds = set()
            self.__resettableBranchIds.update(self.__ctrl.paragons.resetBranchesIds)
            for vehCD in self.__ctrl.unlockedNecessaryLevelVehicleCDs:
                self.__resettableBranchIds.update(vehicles.g_cache.paragonsBranchesToReset.getResetBranchIdsByVehicleCd(vehCD))

        return self.__resettableBranchIds

    def resetBranchIdsByNationId(self, nationID):
        return vehicles.g_cache.paragonsBranchesToReset.getResetBranchIdsByNationId(nationID)

    def isBranchReset(self, branchID):
        return self.__ctrl.paragons.getBranchStateById(branchID).isReset

    def getBranchResetCompensation(self, branchID):
        vehiclesCDs = vehicles.g_cache.paragonsBranchesToReset.getResetBranchById(branchID).resetVehicles
        res = Money()
        for intCD in vehiclesCDs:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            if vehicle.isInInventory:
                res += vehicle.sellPrices.itemPrice.defPrice

        return int(res.credits or 0)

    def isBranchCanBeReset(self, branchID):
        result = defaultdict(list)
        for resetVehicle in self.__ctrl.getBranchResetVehicles(branchID):
            self.checkFeatureConditions(branchID, resetVehicle, result)
            self.checkVehicleConditions(resetVehicle, result)

        return (not bool(result), {reason:tuple(resetVehicles) for reason, resetVehicles in result.iteritems()})

    def checkFeatureConditions(self, branchID, vehicle, result):
        conditions = {VehicleResetUnavailabilityReasons.UNAVAILABLE: not self.__ctrl.isEnabled or not self.isBranchResetAvailable,
         VehicleResetUnavailabilityReasons.ALREADY_RESET: self.isBranchReset(branchID)}
        self.__groupVehiclesByReason(conditions, vehicle, result)

    def checkVehicleConditions(self, vehicle, result):
        conditions = {VehicleResetUnavailabilityReasons.EARLY_ACCESS: vehicle.isEarlyAccess,
         VehicleResetUnavailabilityReasons.ALREADY_RESET: vehicle.isResetParagons,
         VehicleResetUnavailabilityReasons.NOT_UNLOCKED: not vehicle.isUnlocked,
         VehicleResetUnavailabilityReasons.IN_BATTLE: vehicle.isInBattle,
         VehicleResetUnavailabilityReasons.AWAITING_BATTLE: vehicle.isAwaitingBattle,
         VehicleResetUnavailabilityReasons.IN_UNIT: vehicle.isInUnit,
         VehicleResetUnavailabilityReasons.IN_PREBATTLE: vehicle.isInPrebattle,
         VehicleResetUnavailabilityReasons.BROKEN: vehicle.isBroken}
        self.__groupVehiclesByReason(conditions, vehicle, result)

    def onItemsSyncStarted(self):
        self.__resettableBranchIdsBeforeSync = self.resettableBranchIds

    def onItemsSyncCompleted(self):
        if self.resettableBranchIds != self.__resettableBranchIdsBeforeSync:
            self.onResettableBranchesChanged(self.resettableBranchIds - self.__resettableBranchIdsBeforeSync)

    def invalidateCache(self):
        self.__isBranchResetAvailable = None
        self.__resettableBranchIds = None
        return

    def __groupVehiclesByReason(self, conditions, vehicle, result):
        for reason, condition in conditions.iteritems():
            if condition:
                result[reason].append(vehicle)
