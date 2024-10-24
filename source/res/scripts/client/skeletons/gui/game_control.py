# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_control.py
import typing
from constants import ARENA_BONUS_TYPE
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union, Sequence
    from armory_yard.gui.game_control.armory_yard_controller import _ServerSettings
    from battle_pass_common import FinalReward
    from collections_common import Collection, CollectionItem
    from Event import Event
    from gui.collection.resources.cdn.cache import CollectionsCdnCacheMgr
    from fun_random.gui.feature.models.common import FunSubModesStatus
    from fun_random.gui.feature.models.notifications import FunNotification
    from fun_random.gui.feature.models.progressions import FunProgression
    from fun_random.gui.feature.sub_modes.base_sub_mode import IFunSubMode
    from fun_random.helpers.server_settings import FunRandomConfig, FunMetaProgressionConfig
    from fun_random.gui.shared.events import FunEventScope, FunEventType
    from gui.Scaleform.daapi.view.lobby.comp7.shared import Comp7AlertData
    from gui.Scaleform.daapi.view.lobby.hangar.Hangar import Hangar
    from gui.battle_pass.state_machine.delegator import BattlePassRewardLogic
    from gui.comp7.entitlements_cache import EntitlementsCache
    from gui.game_control.comp7_controller import _LeaderboardDataProvider
    from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
    from gui.game_control.mapbox_controller import ProgressionData
    from gui.game_control.trade_in import TradeInDiscounts
    from gui.game_control.early_access_controller import _EarlyAccessSystemMessagesController
    from gui.impl.lobby.early_access.hangar_feature_state import EarlyAccessHangarFeatureState
    from gui.gift_system.hubs.base.hub_core import IGiftEventHub
    from gui.hangar_presets.hangar_gui_config import HangarGuiPreset
    from gui.limited_ui.lui_rules_storage import LuiRules
    from gui.mapbox.mapbox_survey_manager import MapboxSurveyManager
    from gui.periodic_battles.models import AlertData, PeriodInfo, PrimeTime
    from gui.prb_control.items import ValidationResult
    from gui.ranked_battles.constants import YearAwardsNames
    from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager
    from gui.ranked_battles.ranked_helpers.stats_composer import RankedBattlesStatsComposer
    from gui.ranked_battles.ranked_helpers.web_season_provider import RankedWebSeasonProvider, WebSeasonInfo
    from gui.ranked_battles.ranked_models import BattleRankInfo, Division, PostBattleRankInfo, Rank
    from gui.server_events.bonuses import BattlePassSelectTokensBonus, BattlePassStyleProgressTokenBonus, SimpleBonus, TokensBonus, WoTPlusBonus, SelectableBonus
    from gui.server_events.event_items import RankedQuest, Quest
    from gui.shared.event_bus import SharedEvent
    from gui.shared.gui_items import Tankman, Vehicle, ItemsCollection
    from gui.shared.gui_items.artefacts import OptionalDevice
    from gui.shared.gui_items.fitting_item import RentalInfoProvider
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.gui_items.loot_box import LootBox, LootBoxKey
    from gui.shared.gui_items.Tankman import TankmanSkill
    from gui.shared.money import Currency, DynamicMoney, Money, CURRENCY_TYPE
    from gui.shared.utils.requesters.EpicMetaGameRequester import EpicMetaGameRequester
    from helpers.server_settings import BattleRoyaleConfig, EpicGameConfig, GiftSystemConfig, RankedBattlesConfig, VehiclePostProgressionConfig, _MapboxConfig, Comp7Config, WinbackConfig, EarlyAccessConfig, ModeSelectorConfig
    from items.vehicles import VehicleType
    from season_common import GameSeason, GameSeasonCycle
    from items.artefacts import Equipment
    from skeletons.gui.battle_session import IClientArenaVisitor
    from renewable_subscription_common.settings_constants import WotPlusState
    from gui.entitlements.entitlement_model import AgateEntitlement
    from gui.server_events.event_items import Quest
    from gui.Scaleform.framework.entities.View import ViewKeyDynamic
    BattlePassBonusOpts = Optional[TokensBonus, BattlePassSelectTokensBonus]
    BonusOpts = Optional[TokensBonus, SelectableBonus]

class IGameController(object):

    def init(self):
        pass

    def fini(self):
        pass

    def onConnected(self):
        pass

    def onDisconnected(self):
        pass

    def onAvatarBecomePlayer(self):
        pass

    def onAccountBecomePlayer(self):
        pass

    def onAccountBecomeNonPlayer(self):
        pass

    def onServerReplayEntering(self):
        pass

    def onServerReplayExiting(self):
        pass

    def onLobbyInited(self, event):
        pass

    def onLobbyStarted(self, ctx):
        pass


class IGameWindowController(IGameController):

    def hideWindow(self):
        pass

    def showWindow(self, url=None, invokedFrom=None):
        pass

    def getUrl(self, callback=lambda *args: None):
        raise NotImplementedError

    def _getUrl(self):
        raise NotImplementedError


class ISeasonProvider(object):
    onUpdated = None

    def isAvailable(self):
        raise NotImplementedError

    def isBattlesPossible(self):
        raise NotImplementedError

    def isInPrimeTime(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def isNotSet(self, now=None, peripheryID=None):
        raise NotImplementedError

    def isWithinSeasonTime(self, seasonID):
        raise NotImplementedError

    def hasAnySeason(self):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self, now=None):
        raise NotImplementedError

    def hasConfiguredPrimeTimeServers(self, now=None):
        raise NotImplementedError

    def hasPrimeTimesLeftForCurrentCycle(self):
        raise NotImplementedError

    def getClosestStateChangeTime(self, now=None):
        raise NotImplementedError

    def getCurrentCycleID(self):
        raise NotImplementedError

    def getCurrentCycleInfo(self):
        raise NotImplementedError

    def getCurrentSeason(self, now=None):
        raise NotImplementedError

    def getCurrentOrNextActiveCycleNumber(self, season):
        raise NotImplementedError

    def getEventEndTimestamp(self):
        raise NotImplementedError

    def getModeSettings(self):
        raise NotImplementedError

    def getNextSeason(self, now=None):
        raise NotImplementedError

    def getPeriodInfo(self, now=None, peripheryID=None):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        raise NotImplementedError

    def getPrimeTimeStatus(self, now=None, peripheryID=None):
        raise NotImplementedError

    def getPreviousSeason(self, now=None):
        raise NotImplementedError

    def getSeason(self, seasonID):
        raise NotImplementedError

    def getSeasonPassed(self, now=None):
        raise NotImplementedError

    def getTimer(self, now=None, peripheryID=None):
        raise NotImplementedError

    def getLeftTimeToPrimeTimesEnd(self, now=None):
        raise NotImplementedError

    def getAnyPrimeStatusServerID(self, states, now=None):
        raise NotImplementedError

    def isLastSeasonDay(self):
        raise NotImplementedError

    def hasPrimeTimesPassedForCurrentCycle(self):
        raise NotImplementedError


class IGameStateTracker(IGameController):

    def onAccountShowGUI(self, ctx):
        raise NotImplementedError

    def addController(self, controller):
        raise NotImplementedError


class IReloginController(IGameController):

    @property
    def isActive(self):
        return NotImplementedError

    def doRelogin(self, peripheryID, onStoppedHandler=None, extraChainSteps=None):
        raise NotImplementedError


class IAOGASController(IGameController):
    onNotifyAccount = None


class IGameSessionController(IGameController):
    onClientNotify = None
    onTimeTillBan = None
    onNewDayNotify = None
    onPremiumNotify = None
    onPremiumTypeChanged = None
    onParentControlNotify = None
    onNotifyTimeTillKick = None

    def isSessionStartedThisDay(self):
        raise NotImplementedError

    def getDailyPlayTimeLeft(self):
        raise NotImplementedError

    def getWeeklyPlayTimeLeft(self):
        raise NotImplementedError

    @property
    def isParentControlEnabled(self):
        raise NotImplementedError

    @property
    def isParentControlActive(self):
        raise NotImplementedError

    @property
    def sessionStartedAt(self):
        raise NotImplementedError

    @property
    def sessionDuration(self):
        raise NotImplementedError

    @property
    def lastBanMsg(self):
        raise NotImplementedError

    @property
    def battlesCount(self):
        raise NotImplementedError

    @property
    def isAdult(self):
        raise NotImplementedError

    @property
    def isPlayTimeBlock(self):
        raise NotImplementedError

    def incBattlesCounter(self):
        raise NotImplementedError

    def getCurfewBlockTime(self):
        raise NotImplementedError

    def getParentControlNotificationMeta(self):
        raise NotImplementedError

    def getKickAtTime(self):
        raise NotImplementedError


class IRentalsController(IGameController):
    onRentChangeNotify = None

    def getRentPackagesInfo(self, rentPrices, currentRentInfo):
        raise NotImplementedError

    def filterRentPackages(self, rentPrices):
        raise NotImplementedError

    def getRentPriceOfPackage(self, vehicle, rentType, packageID, package):
        raise NotImplementedError


class ISeasonsController(IGameController):
    onSeasonChangeNotify = None

    def hasAnySeason(self, seasonType):
        raise NotImplementedError

    def getCurrentSeason(self, seasonType):
        raise NotImplementedError

    def getCurrentCycleID(self, seasonType):
        raise NotImplementedError

    def getSeason(self, seasonType, seasonID):
        raise NotImplementedError

    def isSeasonActive(self, seasonID, seasonType):
        raise NotImplementedError

    def isWithinSeasonTime(self, seasonID, seasonType):
        raise NotImplementedError

    def isSeasonCycleActive(self, cycleID, seasonType):
        raise NotImplementedError


class IRestoreController(IGameController):
    onRestoreChangeNotify = None
    onTankmenBufferUpdated = None

    def getMaxTankmenBufferLength(self):
        raise NotImplementedError

    def getDismissedTankmen(self):
        raise NotImplementedError

    def getTankmenBeingDeleted(self, newTankmenCount=1):
        raise NotImplementedError

    def getTankmenDeletedBySelling(self, *vehicles):
        raise NotImplementedError


class IIGRController(IGameController):
    onIgrTypeChanged = None

    def getXPFactor(self):
        raise NotImplementedError

    def getRoomType(self):
        raise NotImplementedError


class IWalletController(IGameController):
    onWalletStatusChanged = None

    @property
    def status(self):
        raise NotImplementedError

    @property
    def componentsStatuses(self):
        raise NotImplementedError

    @property
    def dynamicComponentsStatuses(self):
        raise NotImplementedError

    @property
    def isSyncing(self):
        raise NotImplementedError

    @property
    def isNotAvailable(self):
        raise NotImplementedError

    @property
    def isAvailable(self):
        raise NotImplementedError

    @property
    def useGold(self):
        raise NotImplementedError

    @property
    def useFreeXP(self):
        raise NotImplementedError


class INotifyController(IGameController):
    pass


class IEpicModeController(IGameController):
    pass


class IExternalLinksController(IGameController):

    def open(self, url):
        raise NotImplementedError

    def getURL(self, name, params, callback):
        raise NotImplementedError

    def externalAllowed(self, url):
        raise NotImplementedError


class IInternalLinksController(IGameController):

    def getURL(self, name, callback):
        raise NotImplementedError


class ISoundEventChecker(IGameController):

    def lockPlayingSounds(self):
        raise NotImplementedError

    def unlockPlayingSounds(self, restore=True):
        raise NotImplementedError


class IHeroTankController(IGameController):
    onUpdated = None
    onInteractive = None
    onHidden = None

    def hasAdventHero(self):
        raise NotImplementedError

    def isAdventHero(self):
        raise NotImplementedError

    def getRandomTankCD(self):
        raise NotImplementedError

    def setInteractive(self, interactive):
        raise NotImplementedError

    def setHidden(self, isHidden):
        raise NotImplementedError

    def getCurrentTankCD(self):
        raise NotImplementedError

    def getCurrentTankStyleId(self):
        raise NotImplementedError

    def getCurrentTankCrew(self):
        raise NotImplementedError

    def getCurrentRelatedURL(self):
        raise NotImplementedError

    def getCurrentVehicleName(self):
        raise NotImplementedError

    def getCurrentShopUrl(self):
        raise NotImplementedError


class IPlatoonController(IGameController):
    onFilterUpdate = None
    onMembersUpdate = None
    onPlatoonTankUpdated = None
    onPlatoonTankVisualizationChanged = None
    onChannelControllerChanged = None
    onAvailableTiersForSearchChanged = None
    onAutoSearchCooldownChanged = None
    onPlatoonTankRemove = None

    def buildExtendedSquadInfoVo(self):
        raise NotImplementedError

    def getUserSearchFlags(self):
        raise NotImplementedError

    def getCurrentSearchFlags(self):
        raise NotImplementedError

    def saveUserSearchFlags(self, value):
        raise NotImplementedError

    def resetUnitTierFilter(self):
        raise NotImplementedError

    def evaluateVisibility(self, xPopoverOffset=0, toggleUI=False):
        raise NotImplementedError

    def createPlatoon(self, startAutoSearchOnUnitJoin=False):
        raise NotImplementedError

    def leavePlatoon(self, isExit=True, ignoreConfirmation=False, parent=None):
        raise NotImplementedError

    def isPlayerRoleAutoSearch(self):
        raise NotImplementedError

    def isAnyPlatoonUIShown(self):
        raise NotImplementedError

    def isInSearch(self):
        raise NotImplementedError

    def isInQueue(self):
        raise NotImplementedError

    def isInPlatoon(self):
        raise NotImplementedError

    def isSearchingForPlayersEnabled(self):
        raise NotImplementedError

    def isTankLevelPreferenceEnabled(self):
        raise NotImplementedError

    def getAllowedTankLevels(self, prebattleType):
        raise NotImplementedError

    def isVOIPEnabled(self):
        raise NotImplementedError

    def isInCoolDown(self, requestType):
        raise NotImplementedError

    def canStartSearch(self):
        raise NotImplementedError

    def getPrbEntity(self):
        raise NotImplementedError

    def getQueueType(self):
        raise NotImplementedError

    def destroyUI(self, hideOnly=False):
        raise NotImplementedError

    def getExpandedSearchFlags(self):
        raise NotImplementedError

    def setPlatoonPopoverPosition(self, xPopoverOffset):
        raise NotImplementedError

    def togglePlayerReadyAction(self, callback):
        raise NotImplementedError

    def getChannelController(self):
        raise NotImplementedError

    def requestPlayerQueueInfo(self):
        raise NotImplementedError

    def canSelectSquadSize(self):
        raise NotImplementedError

    def hasSearchSupport(self):
        raise NotImplementedError

    def hasWelcomeWindow(self):
        raise NotImplementedError

    def getPlatoonSlotsData(self):
        raise NotImplementedError

    def hasFreeSlot(self):
        raise NotImplementedError

    def getMaxSlotCount(self):
        raise NotImplementedError

    def getPlayerInfo(self):
        raise NotImplementedError

    def cancelSearch(self):
        raise NotImplementedError

    def startSearch(self):
        raise NotImplementedError

    def registerPlatoonTank(self, platoonTank):
        raise NotImplementedError

    def getPermissions(self):
        raise NotImplementedError

    def getPrbEntityType(self):
        raise NotImplementedError

    def isUnitWithPremium(self):
        raise NotImplementedError

    def getFunctionalState(self):
        raise NotImplementedError

    def hasVehiclesForSearch(self, tierLevel=None):
        raise NotImplementedError

    def orderSlotsBasedOnDisplaySlotsIndices(self, slots):
        raise NotImplementedError

    def processPlatoonActions(self, mapID, entity, currentVehicle, callback):
        raise NotImplementedError


class IServerStatsController(IGameController):
    onStatsReceived = None

    def getFormattedStats(self):
        raise NotImplementedError

    def getStats(self):
        raise NotImplementedError


class IBrowserController(IGameController):
    onBrowserDeleted = None
    onBrowserAdded = None

    def addFilterHandler(self, handler):
        raise NotImplementedError

    def removeFilterHandler(self, handler):
        raise NotImplementedError

    def load(self, url=None, title=None, showActionBtn=True, showWaiting=True, browserID=None, isAsync=False, browserSize=None, isDefault=True, callback=None, showCloseBtn=False, useBrowserWindow=True, isModal=False, showCreateWaiting=False, handlers=None, showBrowserCallback=None, isSolidBorder=False):
        raise NotImplementedError

    def getAllBrowsers(self):
        raise NotImplementedError

    def getBrowser(self, browserID):
        raise NotImplementedError

    def delBrowser(self, browserID):
        raise NotImplementedError


class IPromoController(IGameController):
    onNewTeaserReceived = None
    onPromoCountChanged = None
    onTeaserShown = None
    onTeaserClosed = None

    @property
    def isPromoOpen(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def getPromoCount(self):
        raise NotImplementedError

    def showPromo(self, url, handlers=None, source=None):
        raise NotImplementedError

    def setNewTeaserData(self, teaserData):
        raise NotImplementedError

    def showFieldPost(self):
        raise NotImplementedError

    def showLastTeaserPromo(self):
        raise NotImplementedError

    def setUnreadPromoCount(self, count):
        raise NotImplementedError

    def isTeaserOpen(self):
        raise NotImplementedError


class IEventsNotificationsController(IGameController):
    onEventNotificationsChanged = None

    def getEventsNotifications(self, filterFunc=None):
        raise NotImplementedError


class IAnonymizerController(IGameController):
    onStateChanged = None

    @property
    def isInBattle(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isRestricted(self):
        raise NotImplementedError

    @property
    def isAnonymized(self):
        raise NotImplementedError

    def setAnonymized(self, value):
        raise NotImplementedError


class IAwardController(IGameController):

    def addMonitoredDynamicViewKey(self, viewKey):
        raise NotImplementedError


class IBoostersController(IGameController):
    onBoosterChangeNotify = None
    onReserveTimerTick = None
    onGameModeStatusChange = None

    def isGameModeSupported(self, category):
        raise NotImplementedError

    def selectRandomBattle(self):
        raise NotImplementedError


class IScreenCastController(IGameController):
    pass


class IClanLockController(IGameController):
    onClanLockUpdate = None


class IVehicleComparisonBasket(IGameController):
    onChange = None
    onParametersChange = None
    onSwitchChange = None
    onNationChange = None

    def applyNewParameters(self, index, vehicle, crewLvl, crewSkills, selectedShellIndex=0):
        raise NotImplementedError

    def addVehicle(self, vehicleCompactDesr, initParameters=None, settings=None):
        raise NotImplementedError

    def addVehicles(self, vehCDs):
        raise NotImplementedError

    def removeVehicleByIdx(self, index):
        raise NotImplementedError

    def removeAllVehicles(self):
        raise NotImplementedError

    @property
    def maxVehiclesToCompare(self):
        raise NotImplementedError

    def isFull(self):
        raise NotImplementedError

    def isReadyToAdd(self, vehicle):
        raise NotImplementedError

    @property
    def isLocked(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def cloneVehicle(self, index):
        raise NotImplementedError

    def getVehiclesCDs(self):
        raise NotImplementedError

    def getVehiclesCount(self):
        raise NotImplementedError

    def getVehicleAt(self, index):
        raise NotImplementedError

    def getVehiclesPropertiesIter(self, getter):
        raise NotImplementedError

    def writeCache(self):
        raise NotImplementedError

    def revertVehicleByIdx(self, index):
        raise NotImplementedError


class IChinaController(IGameController):

    def showBrowser(self):
        raise NotImplementedError


class ITradeInController(IGameController):

    def getAllPossibleVehiclesToSell(self):
        raise NotImplementedError

    def getAllPossibleVehiclesToBuy(self):
        raise NotImplementedError

    def getPossibleVehiclesToBuy(self):
        raise NotImplementedError

    def selectVehicleToBuy(self, vehCD):
        raise NotImplementedError

    def getSelectedVehicleToBuy(self):
        raise NotImplementedError

    def selectVehicleToSell(self, vehCD):
        raise NotImplementedError

    def getSelectedVehicleToSell(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def hasAvailableOffer(self):
        raise NotImplementedError

    def getExpirationTime(self):
        raise NotImplementedError

    def getVehiclesToSell(self, respectSelectedVehicleToBuy):
        raise NotImplementedError

    def getVehiclesToBuy(self, respectSelectedVehicleToSell):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getTradeInDiscounts(self, item):
        raise NotImplementedError

    def validatePossibleVehicleToBuy(self, vehicle):
        raise NotImplementedError

    def getTradeInPrice(self, vehicle):
        raise NotImplementedError

    def addTradeInPriceIfNeeded(self, vehicle, money):
        raise NotImplementedError


class IQuestsController(IGameController):

    def getInventoryVehicles(self):
        raise NotImplementedError

    def isNewbiePlayer(self):
        raise NotImplementedError

    def getQuestForVehicle(self, vehicle):
        raise NotImplementedError

    def getAllAvailableQuests(self):
        raise NotImplementedError

    def isAnyQuestAvailable(self):
        raise NotImplementedError

    def getFirstAvailableQuest(self):
        raise NotImplementedError

    def getQuestGroups(self):
        raise NotImplementedError

    def getCurrentModeQuestsForVehicle(self, vehicle):
        raise NotImplementedError


class IRankedBattlesController(IGameController, ISeasonProvider):
    onEntitlementEvent = None
    onGameModeStatusTick = None
    onGameModeStatusUpdated = None
    onKillWebOverlays = None
    onUpdated = None
    onYearPointsChanges = None
    onSelectableRewardsChanged = None
    onRankedPrbClosing = None

    def isAccountMastered(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isRankedPrbActive(self):
        raise NotImplementedError

    def isRankedShopEnabled(self):
        raise NotImplementedError

    def isSeasonRewarding(self):
        raise NotImplementedError

    def isSuitableVehicle(self, vehicle):
        raise NotImplementedError

    def isUnset(self):
        raise NotImplementedError

    def isYearGap(self):
        raise NotImplementedError

    def isYearLBEnabled(self):
        raise NotImplementedError

    def isYearRewardEnabled(self):
        raise NotImplementedError

    def isLeagueRewardEnabled(self):
        raise NotImplementedError

    def hasSpecialSeason(self):
        raise NotImplementedError

    def hasPrimeTimesTotalLeft(self):
        raise NotImplementedError

    def hasPrimeTimesNextDayLeft(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def suitableVehicleIsAvailable(self):
        raise NotImplementedError

    def vehicleIsAvailableForBuy(self):
        raise NotImplementedError

    def vehicleIsAvailableForRestore(self):
        raise NotImplementedError

    def hasVehicleRankedBonus(self, compactDescr):
        raise NotImplementedError

    def getAlertBlock(self):
        raise NotImplementedError

    def getAwardTypeByPoints(self, points):
        pass

    def getBonusBattlesMultiplier(self):
        raise NotImplementedError

    def getStepsList(self):
        raise NotImplementedError

    def getStepsToEarnRank(self, rankID):
        raise NotImplementedError

    def getCanTakeReward(self, rankID):
        raise NotImplementedError

    def isUnburnableRank(self, rankID):
        raise NotImplementedError

    def getClientRank(self):
        raise NotImplementedError

    def getClientMaxRank(self):
        raise NotImplementedError

    def getClientShields(self):
        raise NotImplementedError

    def getClientSeasonInfo(self):
        raise NotImplementedError

    def getClientSeasonInfoUpdateTime(self):
        raise NotImplementedError

    def getClientEfficiency(self):
        raise NotImplementedError

    def getClientEfficiencyDiff(self):
        raise NotImplementedError

    def getClientBonusBattlesCount(self):
        raise NotImplementedError

    def getCompensation(self, points):
        pass

    def getCurrentDivision(self):
        raise NotImplementedError

    def getCurrentPointToCrystalRate(self):
        pass

    def getCurrentRank(self):
        raise NotImplementedError

    def getDivision(self, rankID):
        raise NotImplementedError

    def getDivisions(self):
        raise NotImplementedError

    def getEntitlementEvents(self):
        raise NotImplementedError

    def getExpectedSeasons(self):
        raise NotImplementedError

    def getWebSeasonProvider(self):
        raise NotImplementedError

    def getLeagueRewards(self, bonusName=None):
        raise NotImplementedError

    def getMaxPossibleRank(self):
        raise NotImplementedError

    def getMaxRank(self):
        raise NotImplementedError

    def getRank(self, rankID):
        raise NotImplementedError

    def getRankChangeStatus(self, changeInfo):
        raise NotImplementedError

    def getRankDisplayInfoForBattle(self, rankID):
        raise NotImplementedError

    def getRankedWelcomeCallback(self):
        raise NotImplementedError

    def getQuestsForRank(self, rankID):
        raise NotImplementedError

    def setRankedWelcomeCallback(self, value):
        raise NotImplementedError

    def getRanksChain(self, leftRequiredBorder, rightRequiredBorder):
        raise NotImplementedError

    def getRanksChainExt(self, currentProgress, lastProgress, maxProgress, shields, lastShields, isBonusBattle):
        raise NotImplementedError

    def getRanksChanges(self, isLoser=False):
        pass

    def getRanksTops(self, isLoser=False, stepDiff=None):
        pass

    def getSoundManager(self):
        raise NotImplementedError

    def getStatsComposer(self):
        raise NotImplementedError

    def getSuitableVehicleLevels(self):
        raise NotImplementedError

    def getTotalQualificationBattles(self):
        raise NotImplementedError

    def getYearAwardsPointsMap(self):
        raise NotImplementedError

    def getYearLBSize(self):
        raise NotImplementedError

    def getYearLBState(self):
        raise NotImplementedError

    def getYearRewards(self, points):
        raise NotImplementedError

    def getCompletedYearQuest(self):
        raise NotImplementedError

    def getYearRewardPoints(self):
        raise NotImplementedError

    def getWebOpenPageCtx(self):
        raise NotImplementedError

    def getQualificationQuests(self, quests=None):
        raise NotImplementedError

    def awardWindowShouldBeShown(self, rankChangeInfo):
        raise NotImplementedError

    def clearRankedWelcomeCallback(self):
        raise NotImplementedError

    def clearWebOpenPageCtx(self):
        raise NotImplementedError

    def runQuests(self, quests):
        raise NotImplementedError

    def showRankedAwardWindow(self, rankInfo, questsProgress):
        raise NotImplementedError

    def showRankedBattlePage(self, ctx):
        raise NotImplementedError

    def updateClientValues(self):
        raise NotImplementedError

    def doActionOnEntryPointClick(self):
        raise NotImplementedError

    def getYearRewardCount(self):
        raise NotImplementedError

    def takeRewardForRank(self, rank):
        raise NotImplementedError

    def hasAnyRewardToTake(self):
        raise NotImplementedError

    def replaceOfferByReward(self, bonuses):
        raise NotImplementedError


class IBootcampController(IGameController):

    @property
    def replayCtrl(self):
        raise NotImplementedError

    @property
    def nationData(self):
        raise NotImplementedError

    @property
    def nation(self):
        raise NotImplementedError

    @property
    def version(self):
        raise NotImplementedError

    def getBootcampOutfit(self, vehDescr):
        raise NotImplementedError

    def isInBootcamp(self):
        raise NotImplementedError

    def startBootcamp(self, inBattle):
        raise NotImplementedError

    def stopBootcamp(self, inBattle):
        raise NotImplementedError

    def getContext(self):
        raise NotImplementedError

    def hasFinishedBootcampBefore(self):
        raise NotImplementedError

    def runCount(self):
        raise NotImplementedError

    def isReferralEnabled(self):
        raise NotImplementedError

    def needAwarding(self):
        raise NotImplementedError

    def setAutomaticStart(self, enable):
        raise NotImplementedError

    def isInBootcampAccount(self):
        raise NotImplementedError

    def showActionWaitWindow(self):
        raise NotImplementedError

    def hideActionWaitWindow(self):
        raise NotImplementedError

    def getLessonNum(self):
        raise NotImplementedError

    def getAwardVehicles(self):
        raise NotImplementedError

    def isEnableCriticalDamageIcon(self):
        raise NotImplementedError

    def getCheckpoint(self):
        raise NotImplementedError

    def saveCheckpoint(self, checkpoint):
        raise NotImplementedError

    def changeNation(self, nationIndex):
        raise NotImplementedError

    def getDisabledSettings(self):
        raise NotImplementedError

    def showFinalVideo(self, callback):
        raise NotImplementedError

    def finishBootcamp(self):
        raise NotImplementedError

    def runBootcamp(self):
        raise NotImplementedError

    def canRun(self):
        raise NotImplementedError


class IMarathonEventsController(IGameController):
    onFlagUpdateNotify = None
    onMarathonDataChanged = None
    onVehicleReceived = None

    def addMarathon(self, data):
        raise NotImplementedError

    def delMarathon(self, prefix):
        raise NotImplementedError

    def getMarathon(self, prefix):
        raise NotImplementedError

    def getMarathons(self):
        raise NotImplementedError

    def getPrimaryMarathon(self):
        raise NotImplementedError

    def getFirstEnabledMarathon(self):
        raise NotImplementedError

    def getPrefix(self, eventID):
        raise NotImplementedError

    def getVisibleInPostBattleQuests(self):
        raise NotImplementedError

    def getQuestsData(self, prefix=None, postfix=None):
        raise NotImplementedError

    def getTokensData(self, prefix=None, postfix=None):
        raise NotImplementedError

    def isAnyActive(self):
        raise NotImplementedError

    def doesShowAnyMissionsTab(self):
        raise NotImplementedError


class IEpicBattleMetaGameController(IGameController, ISeasonProvider):
    onUpdated = None
    onPrimeTimeStatusUpdated = None
    onEventEnded = None
    onGameModeStatusTick = None
    TOKEN_QUEST_ID = ''
    DAILY_QUEST_ID = ''
    FINAL_BADGE_QUEST_ID = ''

    def isEnabled(self):
        raise NotImplementedError

    def isEpicPrbActive(self):
        raise NotImplementedError

    def isCurrentCycleActive(self):
        raise NotImplementedError

    def getLevelsToUPGAllReserves(self):
        raise NotImplementedError

    def isBattlePassDataEnabled(self):
        raise NotImplementedError

    def getTooltipData(self, tooltip):
        raise NotImplementedError

    def isUnlockVehiclesInBattleEnabled(self):
        raise NotImplementedError

    def isDailyQuestsUnlocked(self):
        raise NotImplementedError

    def isDailyQuestsRefreshAvailable(self):
        raise NotImplementedError

    def getPerformanceGroup(self):
        raise NotImplementedError

    def getMaxPlayerLevel(self):
        raise NotImplementedError

    def getStageLimit(self):
        raise NotImplementedError

    def getAbilityPointsForLevel(self):
        raise NotImplementedError

    def getValidVehicleLevels(self):
        raise NotImplementedError

    def getForbiddenVehicles(self):
        raise NotImplementedError

    def getUnlockableInBattleVehLevels(self):
        raise NotImplementedError

    def getUnlockableInBattleVehLevelStr(self):
        raise NotImplementedError

    def getSuitableForQueueVehicleLevels(self):
        raise NotImplementedError

    def getSuitableForQueueVehicleLevelStr(self):
        raise NotImplementedError

    def getPointsProgressForLevel(self, level):
        raise NotImplementedError

    def getPointsForLevel(self, level):
        raise NotImplementedError

    def getLevelProgress(self):
        raise NotImplementedError

    def getLevelForPoints(self, points):
        raise NotImplementedError

    def getAllSkillsInformation(self):
        raise NotImplementedError

    def getOrderedSkillTree(self):
        raise NotImplementedError

    def getPlayerLevelInfo(self):
        raise NotImplementedError

    def getSkillLevelRanks(self):
        raise NotImplementedError

    def getPlayerRanksInfo(self):
        raise NotImplementedError

    def getPlayerRanksWithBonusInfo(self):
        raise NotImplementedError

    def getSeasonData(self):
        raise NotImplementedError

    def getCurrentSeasonID(self):
        raise NotImplementedError

    def getSkillPoints(self):
        raise NotImplementedError

    def getSkillLevels(self):
        raise NotImplementedError

    def getSelectedSkills(self, vehicleCD):
        raise NotImplementedError

    def increaseSkillLevel(self, skillID, callback=None):
        raise NotImplementedError

    def changeEquippedSkills(self, skillIDArray, vehicleCD, callback=None, classVehs=False):
        raise NotImplementedError

    def getAllUnlockedSkillInfoBySkillId(self):
        raise NotImplementedError

    def getUnlockedAbilityIds(self):
        raise NotImplementedError

    def getNumAbilitySlots(self, vehicleType):
        raise NotImplementedError

    def getAbilitySlotsOrder(self, vehicleType):
        raise NotImplementedError

    def getAbilitySlotsUnlockOrder(self, vehicleType):
        raise NotImplementedError

    def getAllLevelRewards(self):
        raise NotImplementedError

    def getLevelRewards(self, level):
        raise NotImplementedError

    def getMergedLevelRewards(self):
        raise NotImplementedError

    def getDestructiblesArmor(self):
        raise NotImplementedError

    def isNeedToTakeReward(self):
        raise NotImplementedError

    def getNotChosenRewardCount(self):
        raise NotImplementedError

    def showProgressionDuringSomeStates(self, showDefaultTab=False):
        raise NotImplementedError

    def selectEpicBattle(self):
        raise NotImplementedError

    def hasAnyOfferGiftToken(self):
        raise NotImplementedError

    def replaceOfferByReward(self, bonuses):
        raise NotImplementedError

    def replaceOfferByGift(self, bonuses):
        raise NotImplementedError

    def getCurrentCycleInfo(self):
        raise NotImplementedError

    def getCycleInfo(self, cycleID=None):
        raise NotImplementedError

    def getCycleOrdinalNumber(self, cycleID):
        raise NotImplementedError

    def getSeasonTimeRange(self):
        raise NotImplementedError

    def getActiveSeason(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def hasVehiclesToRent(self):
        raise NotImplementedError

    def getStoredEpicDiscount(self):
        raise NotImplementedError

    def getStats(self):
        raise NotImplementedError

    def showWelcomeScreenIfNeed(self):
        raise NotImplementedError

    def storeCycle(self):
        raise NotImplementedError


class IBattleRoyaleController(IGameController, ISeasonProvider):
    onUpdated = None
    onPrimeTimeStatusUpdated = None
    onWidgetUpdate = None
    TOKEN_QUEST_ID = ''

    def isEnabled(self):
        raise NotImplementedError

    def isShowTimeLeft(self):
        raise NotImplementedError

    def getDefaultAmmoCount(self, itemKey, intCD=None, vehicleName=None):
        raise NotImplementedError

    def getPerformanceGroup(self):
        raise NotImplementedError

    def getEndTime(self):
        raise NotImplementedError

    def fightClick(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isBattleRoyaleMode(self):
        raise NotImplementedError

    def isBattlePassAvailable(self, bonusType):
        raise NotImplementedError

    def isInBattleRoyaleSquad(self):
        raise NotImplementedError

    def selectRoyaleBattle(self):
        raise NotImplementedError

    def isGeneralHangarEntryPoint(self):
        raise NotImplementedError

    def setDefaultHangarEntryPoint(self):
        raise NotImplementedError

    def selectRandomBattle(self):
        raise NotImplementedError

    def wasInLobby(self):
        raise NotImplementedError

    def getBrVehicleEquipmentIds(self, vehicleName):
        raise NotImplementedError

    def getStats(self):
        raise NotImplementedError

    @staticmethod
    def getBrCommanderSkills():
        raise NotImplementedError

    def openURL(self, url=None):
        raise NotImplementedError

    @staticmethod
    def showIntroWindow(ctx=None, parent=None, guiLoader=None):
        raise NotImplementedError

    def getQuests(self):
        raise NotImplementedError

    def isDailyQuestsRefreshAvailable(self):
        raise NotImplementedError

    def getIntroVideoURL(self):
        raise NotImplementedError

    def getProgressionPointsTableData(self):
        raise NotImplementedError


class IBattleRoyaleTournamentController(IGameController):
    onUpdatedParticipants = None
    onSelectBattleRoyaleTournament = None

    def isAvailable(self):
        raise NotImplementedError

    def getSelectedToken(self):
        raise NotImplementedError

    def getTokens(self):
        raise NotImplementedError

    def updateParticipants(self, participants):
        raise NotImplementedError

    def getParticipants(self):
        raise NotImplementedError

    def selectBattleRoyaleTournament(self, token):
        raise NotImplementedError

    def join(self, tokenStr):
        raise NotImplementedError

    def leave(self):
        raise NotImplementedError

    def ready(self, vehicleID):
        raise NotImplementedError

    def notReady(self):
        raise NotImplementedError

    def leaveCurrentAndJoinToAnotherTournament(self, newTournamentID):
        raise NotImplementedError

    def leaveBattleRoyaleTournament(self, isChangingToBattleRoyaleHangar=False):
        raise NotImplementedError

    def isSelected(self):
        raise NotImplementedError

    def resetReady(self):
        raise NotImplementedError


class IBattleRoyaleRentVehiclesController(IGameController):
    onBalanceUpdated = None
    onPriceInfoUpdated = None
    onRentInfoUpdated = None
    onUpdated = None

    def getRentState(self, intCD=None):
        raise NotImplementedError

    def isRentable(self, intCD=None):
        raise NotImplementedError

    def getTestDrivePrice(self, intCD=None):
        raise NotImplementedError

    def getRentPrice(self, intCD=None):
        raise NotImplementedError

    def getRentDaysLeft(self, intCD=None):
        raise NotImplementedError

    def getRentTimeLeft(self, intCD=None):
        raise NotImplementedError

    def getFormatedRentTimeLeft(self, intCD=None, isRoundUp=True):
        raise NotImplementedError

    def getPendingRentDays(self, intCD=None):
        raise NotImplementedError

    def getNextTestDriveDaysTotal(self, intCD=None):
        raise NotImplementedError

    def getNextRentDaysTotal(self, intCD=None):
        raise NotImplementedError

    def isInTestDriveRent(self, intCD=None):
        raise NotImplementedError

    def isEnoughMoneyToPurchase(self, intCD=None, state=None):
        raise NotImplementedError

    def purchaseRent(self, intCD=None):
        raise NotImplementedError

    def getBRCoinBalance(self, default=None):
        raise NotImplementedError

    def watchRentVehicles(self, callback, vehIntCDs=None):
        raise NotImplementedError

    def unwatchRentVehicles(self, callback, runWatch=True):
        raise NotImplementedError

    def setRentUpdateCurrentVehicleCallback(self, callback):
        raise NotImplementedError

    def clearRentUpdateCurrentVehicleCallback(self, callback):
        raise NotImplementedError


class IBRProgressionOnTokensController(IGameController):
    progressionToken = ''
    PROGRESSION_COMPLETE_TOKEN = ''
    onProgressPointsUpdated = None
    onSettingsChanged = None

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def setSettings(self, settings):
        raise NotImplementedError

    def saveCurPoints(self):
        raise NotImplementedError

    def getPrevPoints(self):
        raise NotImplementedError

    def getCurPoints(self):
        raise NotImplementedError

    def getCurrentStageData(self):
        raise NotImplementedError

    def getProgressionLevelsData(self):
        raise NotImplementedError

    def getProgessionPointsData(self):
        raise NotImplementedError

    def getProgressionData(self):
        raise NotImplementedError

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isFinished(self):
        raise NotImplementedError


class IManualController(IGameController):

    def isActivated(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def getBootcampRunCount(self):
        raise NotImplementedError

    def runBootcamp(self):
        raise NotImplementedError

    def getNewContentCount(self):
        raise NotImplementedError

    def pageFilter(self, pageType):
        raise NotImplementedError

    def show(self, lessonID=None, backCallback=None):
        raise NotImplementedError

    def getView(self):
        raise NotImplementedError


class ICraftmachineController(IGameController):

    def getModuleName(self):
        raise NotImplementedError


class ICalendarController(IGameController):

    def updateHeroAdventActionInfo(self):
        raise NotImplementedError

    def getHeroAdventActionInfo(self):
        raise NotImplementedError

    def showWindow(self, url=None, invokedFrom=None):
        raise NotImplementedError

    def hideWindow(self):
        raise NotImplementedError


class IReferralProgramController(IGameController):
    onReferralProgramEnabled = None
    onReferralProgramDisabled = None
    onReferralProgramUpdated = None
    onPointsChanged = None

    def isFirstIndication(self):
        raise NotImplementedError

    def getBubbleCount(self):
        raise NotImplementedError

    def updateBubble(self):
        raise NotImplementedError

    def isScoresLimitReached(self):
        raise NotImplementedError


class IClanNotificationController(IGameController):

    def getCounters(self, aliases=None):
        raise NotImplementedError

    def setCounters(self, alias, count, isIncrement=False):
        raise NotImplementedError

    def resetCounters(self):
        raise NotImplementedError


class IFestivityController(IGameController):
    onStateChanged = None

    def isEnabled(self):
        raise NotImplementedError

    def getHangarQuestsFlagData(self):
        raise NotImplementedError


class IBadgesController(IGameController):
    onUpdated = None

    def select(self, badges):
        raise NotImplementedError

    def getPrefix(self):
        raise NotImplementedError

    def getSuffix(self):
        raise NotImplementedError


class ISpecialSoundCtrl(IGameController):

    @property
    def arenaMusicSetup(self):
        raise NotImplementedError

    @property
    def specialVoice(self):
        raise NotImplementedError

    def setPlayerVehicle(self, vehiclePublicInfo, isPlayerVehicle):
        raise NotImplementedError


class IBattlePassController(IGameController):
    onPointsUpdated = None
    onLevelUp = None
    onBattlePassIsBought = None
    onSelectTokenUpdated = None
    onSeasonStateChanged = None
    onBattlePassSettingsChange = None
    onFinalRewardStateChange = None
    onRewardSelectChange = None
    onOffersUpdated = None
    onChapterChanged = None
    onMarathonChapterExpired = None

    def isEnabled(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isVisible(self):
        raise NotImplementedError

    def isDisabled(self):
        raise NotImplementedError

    def isPaused(self):
        raise NotImplementedError

    def isSeasonStarted(self):
        raise NotImplementedError

    def isSeasonFinished(self):
        raise NotImplementedError

    def isValidBattleType(self, prbEntity):
        raise NotImplementedError

    def isCompleted(self):
        raise NotImplementedError

    def isResourceCompleted(self):
        raise NotImplementedError

    def getLevelByPoints(self, chapterID, points):
        raise NotImplementedError

    def getProgressionByPoints(self, chapterID, points, level):
        raise NotImplementedError

    def getMaxLevelInChapter(self, chapterId):
        raise NotImplementedError

    def hasMarathon(self):
        raise NotImplementedError

    def hasResource(self):
        raise NotImplementedError

    def isValidChapterID(self, chapterID):
        raise NotImplementedError

    def getChapterType(self, chapterID):
        raise NotImplementedError

    def getAvailableChapterTypes(self):
        raise NotImplementedError

    def getRegularChapterIds(self):
        raise NotImplementedError

    def getMarathonChapterID(self):
        raise NotImplementedError

    def getResourceChapterID(self):
        raise NotImplementedError

    def getRewardType(self, chapterID):
        raise NotImplementedError

    def isChapterExists(self, chapterID):
        raise NotImplementedError

    def getChapterIDs(self):
        raise NotImplementedError

    def isMarathonChapter(self, chapterID):
        raise NotImplementedError

    def allRegularChaptersPurchased(self):
        raise NotImplementedError

    def isResourceChapter(self, chapterID):
        raise NotImplementedError

    def isResourceChapterAvailable(self):
        raise NotImplementedError

    def getBattlePassCost(self, chapterID):
        raise NotImplementedError

    def getChapterExpiration(self, chapterID):
        raise NotImplementedError

    def getChapterRemainingTime(self, chapterID):
        raise NotImplementedError

    def getLevelInChapter(self, chapterID):
        raise NotImplementedError

    def getCurrentChapterID(self):
        raise NotImplementedError

    def hasActiveChapter(self):
        raise NotImplementedError

    def activateChapter(self, chapterID, seasonID=None):
        raise NotImplementedError

    def getCurrentLevel(self):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def isBought(self, chapterID, seasonID=None):
        raise NotImplementedError

    def isOfferEnabled(self):
        raise NotImplementedError

    def isGameModeEnabled(self, arenaBonusType):
        raise NotImplementedError

    def getSupportedArenaBonusTypes(self):
        raise NotImplementedError

    def getLevelPoints(self, chapterID, level):
        raise NotImplementedError

    def getFullChapterPoints(self, chapterID):
        raise NotImplementedError

    def isRareLevel(self, chapterID, level):
        raise NotImplementedError

    def isFinalLevel(self, chapterID, level):
        raise NotImplementedError

    def getSingleAward(self, chapterId, level, awardType='free', needSort=True):
        raise NotImplementedError

    def getAwardsInterval(self, chapterId, fromLevel, toLevel, awardType='free'):
        raise NotImplementedError

    def replaceOfferByReward(self, bonuses):
        raise NotImplementedError

    def getPackedAwardsInterval(self, chapterId, fromLevel, toLevel, awardType='free'):
        raise NotImplementedError

    def isNeedToTakeReward(self, awardType, chapterId, level):
        raise NotImplementedError

    def isChooseRewardEnabled(self, awardType, chapterId, level):
        raise NotImplementedError

    def canChooseAnyReward(self):
        raise NotImplementedError

    def getLevelsConfig(self, chapterId):
        raise NotImplementedError

    def getChapterConfig(self):
        raise NotImplementedError

    def getChapterLevelInterval(self, chapter):
        raise NotImplementedError

    def getChapterState(self, chapterID):
        raise NotImplementedError

    def isChapterActive(self, chapterID):
        raise NotImplementedError

    def isChapterCompleted(self, chapterID):
        raise NotImplementedError

    def getChapterIndex(self, chapterID):
        raise NotImplementedError

    def getRewardLogic(self):
        raise NotImplementedError

    def getPointsInChapter(self, chapterID):
        raise NotImplementedError

    def getLevelProgression(self, chapterID):
        raise NotImplementedError

    def getPerBattlePoints(self, gameMode=ARENA_BONUS_TYPE.REGULAR, vehCompDesc=None):
        raise NotImplementedError

    def getPerBattleRoyalePoints(self, gameMode=ARENA_BONUS_TYPE.BATTLE_ROYALE_SOLO, vehCompDesc=None):
        raise NotImplementedError

    def isSpecialVehicle(self, intCD):
        raise NotImplementedError

    def getSpecialVehicles(self):
        raise NotImplementedError

    def getPointsDiffForVehicle(self, intCD, gameMode=ARENA_BONUS_TYPE.REGULAR):
        raise NotImplementedError

    def getVehicleProgression(self, intCD):
        raise NotImplementedError

    def getSpecialVehicleCapBonus(self):
        raise NotImplementedError

    def getVehicleCapBonus(self, intCD):
        raise NotImplementedError

    def getSeasonTimeLeft(self):
        raise NotImplementedError

    def getFinalOfferTimeLeft(self):
        raise NotImplementedError

    def getSeasonStartTime(self):
        raise NotImplementedError

    def getSeasonFinishTime(self):
        raise NotImplementedError

    def hasMaxPointsOnVehicle(self, intCD):
        raise NotImplementedError

    def isProgressionOnVehiclePossible(self, intCD):
        raise NotImplementedError

    def getSeasonID(self):
        raise NotImplementedError

    def getSeasonNum(self):
        raise NotImplementedError

    def getCurrentCollectionId(self):
        raise NotImplementedError

    def getFinalOfferTime(self):
        raise NotImplementedError

    def isShopOfferActive(self):
        raise NotImplementedError

    def getShopOfferFinishTimeLeft(self):
        raise NotImplementedError

    def getSeasonsHistory(self):
        raise NotImplementedError

    def getStylesConfig(self):
        raise NotImplementedError

    def getNotChosenRewardCount(self):
        raise NotImplementedError

    def getFreePoints(self):
        raise NotImplementedError

    def takeRewardForLevel(self, chapterID, level):
        raise NotImplementedError

    def takeAllRewards(self):
        raise NotImplementedError

    def hasAnyOfferGiftToken(self):
        raise NotImplementedError

    def getChapterStyleProgress(self, chapter):
        raise NotImplementedError


class IHangarLoadingController(IGameController):
    onHangarLoadedAfterLogin = None


class IReactiveCommunicationService(IGameController):
    onChannelMessage = None
    onChannelClosed = None
    onSubscriptionClosed = None

    @property
    def isChannelSubscriptionAvailable(self):
        raise NotImplementedError

    def subscribeToChannel(self, subscription):
        raise NotImplementedError

    def unsubscribeFromChannel(self, subscription):
        raise NotImplementedError

    def getLastMessageFromChannel(self, subscription):
        raise NotImplementedError

    def getChannelHistory(self, name):
        raise NotImplementedError

    def getChannelStatus(self, name):
        raise NotImplementedError


class IRTSBattlesController(IGameController):

    def isVisible(self):
        raise NotImplementedError


class IBlueprintsConvertSaleController(IGameController):
    pass


class IMapboxController(IGameController, ISeasonProvider):
    onPrimeTimeStatusUpdated = None
    onMapboxSurveyShown = None
    onMapboxSurveyCompleted = None

    @property
    def surveyManager(self):
        raise NotImplementedError

    def addProgressionListener(self, listener):
        raise NotImplementedError

    def removeProgressionListener(self, listener):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isMapboxMode(self):
        raise NotImplementedError

    def isMapboxPrbActive(self):
        raise NotImplementedError

    def selectMapboxBattle(self):
        raise NotImplementedError

    def getProgressionData(self):
        raise NotImplementedError

    def getProgressionRestartTime(self):
        raise NotImplementedError

    def selectCrewbookNation(self, itemID):
        raise NotImplementedError

    def handleSurveyCompleted(self, surveyData):
        raise NotImplementedError

    def getUnseenItemsCount(self):
        raise NotImplementedError

    def showSurvey(self, mapName):
        raise NotImplementedError

    def addVisitedMap(self, mapName):
        raise NotImplementedError

    def storeReward(self, numBattles, rewardIdx, rewardIconName):
        raise NotImplementedError

    def getStoredReward(self, numBattles, rewardIdx):
        raise NotImplementedError

    def setPrevBattlesPlayed(self, numBattles):
        raise NotImplementedError

    def getPrevBattlesPlayed(self):
        raise NotImplementedError

    def isMapVisited(self, mapName):
        raise NotImplementedError

    def forceUpdateProgressData(self):
        raise NotImplementedError

    def getModeSettings(self):
        raise NotImplementedError


class IOverlayController(IGameController):

    def isActive(self):
        raise NotImplementedError

    def setOverlayState(self, state):
        raise NotImplementedError

    def waitShow(self):
        raise NotImplementedError


class ISteamCompletionController(IGameController):

    @property
    def isSteamAccount(self):
        raise NotImplementedError


class IDemoAccCompletionController(IGameController):

    @property
    def isDemoAccount(self):
        raise NotImplementedError

    @property
    def isDemoAccountOnce(self):
        raise NotImplementedError

    @property
    def isInDemoAccRegistration(self):
        raise NotImplementedError

    @isInDemoAccRegistration.setter
    def isInDemoAccRegistration(self, value):
        raise NotImplementedError

    def runDemoAccRegistration(self):
        raise NotImplementedError

    def updateOverlayState(self, waitingID=None, onComplete=None):
        raise NotImplementedError


class IMapsTrainingController(IGameController):
    onUpdated = None

    @property
    def isMapsTrainingEnabled(self):
        raise NotImplementedError

    @property
    def isMapsTrainingPrbActive(self):
        raise NotImplementedError

    @property
    def preferences(self):
        raise NotImplementedError

    def showMapsTrainingPage(self, ctx=None):
        raise NotImplementedError

    def showMapsTrainingQueue(self):
        raise NotImplementedError

    def selectMapsTrainingMode(self):
        raise NotImplementedError

    def selectRandomMode(self):
        raise NotImplementedError

    def getSelectedMap(self):
        raise NotImplementedError

    def setSelectedMap(self, mapName):
        raise NotImplementedError

    def getSelectedVehicle(self):
        raise NotImplementedError

    def updateSelectedVehicle(self):
        raise NotImplementedError

    def setSelectedVehicle(self, vehicleName):
        raise NotImplementedError

    def getSelectedTeam(self):
        raise NotImplementedError

    def setSelectedTeam(self, team):
        raise NotImplementedError

    def isValid(self):
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError

    def requestInitialDataFromServer(self, callback):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def onEnter(self):
        raise NotImplementedError

    def onExit(self):
        raise NotImplementedError

    def getPageCtx(self):
        raise NotImplementedError


class IVehiclePostProgressionController(IGameController):

    def isDisabledFor(self, vehicle, settings=None, skipRentalIsOver=False):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isExistsFor(self, vehType, settings=None):
        raise NotImplementedError

    def isSwitchSetupFeatureEnabled(self):
        raise NotImplementedError

    def getSettings(self):
        raise NotImplementedError

    def getInvalidProgressions(self, diff, existingIDs):
        raise NotImplementedError

    def processVehExtData(self, vehCD, extData):
        raise NotImplementedError


class IWotPlusController(IGameController):
    onDataChanged = None
    onAttendanceUpdated = None
    onStateUpdate = None
    onPendingRentChanged = None

    def processSwitchNotifications(self):
        raise NotImplementedError

    def selectIdleCrewXPVehicle(self, vehicleInvID, successCallback=None, errorCallback=None):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isFreeToDemount(self, device):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def getExpiryTime(self):
        raise NotImplementedError

    def getStartTime(self):
        raise NotImplementedError

    def getGoldReserve(self):
        raise NotImplementedError

    def hasVehicleCrewIdleXP(self, vehicleInvID):
        raise NotImplementedError

    def getVehicleIDWithIdleXP(self):
        raise NotImplementedError

    def getExclusiveVehicles(self):
        raise NotImplementedError

    def getActiveExclusiveVehicle(self):
        raise NotImplementedError

    def getActiveExclusiveVehicleName(self):
        raise NotImplementedError

    def getEnabledBonuses(self):
        raise NotImplementedError

    def toggleWotPlusDev(self):
        raise NotImplementedError

    def activateWotPlusDev(self, expirySecondsInFuture):
        raise NotImplementedError

    def simulateNewGameDay(self):
        raise NotImplementedError

    def setReservesDev(self, creditsVal, goldVal):
        raise NotImplementedError

    def smashPiggyBankDev(self):
        raise NotImplementedError

    def isWotPlusEnabled(self):
        raise NotImplementedError

    def onDailyAttendanceUpdate(self):
        raise NotImplementedError

    def resolveState(self):
        raise NotImplementedError

    def synchronize(self):
        raise NotImplementedError

    def isDailyAttendanceQuest(self, questID):
        raise NotImplementedError

    def getFormattedDailyAttendanceBonuses(self, bonuses):
        raise NotImplementedError


class IEntitlementsConsumer(object):

    @property
    def isConsumesEntitlements(self):
        raise NotImplementedError


class IEntitlementsController(IGameController):
    onCacheUpdated = None

    def updateCache(self, codes):
        raise NotImplementedError

    def forceUpdateCache(self, codes):
        raise NotImplementedError

    def getBalanceEntitlementFromCache(self, code):
        raise NotImplementedError

    def isCacheInited(self):
        raise NotImplementedError

    def getConsumedEntitlementFromCache(self, code):
        raise NotImplementedError

    def getGrantedEntitlementFromCache(self, code):
        raise NotImplementedError

    def isCodesWasFailedInLastRequest(self, codes):
        raise NotImplementedError


class IGuiLootBoxesController(IGameController, IEntitlementsConsumer):
    onStatusChange = None
    onAvailabilityChange = None
    onBoxesCountChange = None
    onKeysUpdate = None
    onBoxesHistoryUpdate = None
    onBoxInfoUpdated = None

    @property
    def isConsumesEntitlements(self):
        raise NotImplementedError

    def getSetting(self, setting):
        raise NotImplementedError

    def setSetting(self, setting, value):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isLootBoxesAvailable(self):
        raise NotImplementedError

    def isBuyAvailable(self):
        raise NotImplementedError

    def isFirstStorageEnter(self):
        raise NotImplementedError

    def setStorageVisited(self):
        raise NotImplementedError

    def getDayLimit(self):
        raise NotImplementedError

    def openShop(self, lootboxID=None):
        raise NotImplementedError

    def getStoreInfo(self, category):
        raise NotImplementedError

    def getBoxesIDs(self, category):
        raise NotImplementedError

    def getBoxesCount(self):
        raise NotImplementedError

    def getBoxKeysCount(self):
        raise NotImplementedError

    def getKeyByID(self, keyID):
        raise NotImplementedError

    def getKeyByTokenID(self, tokenID):
        raise NotImplementedError

    def getBonusesOrder(self, category=None):
        raise NotImplementedError

    def getHangarOptimizer(self):
        raise NotImplementedError

    def addShopWindowHandler(self, keyHandler, handler):
        raise NotImplementedError

    def hasLootboxKey(self):
        raise NotImplementedError

    def hasInfiniteLootboxes(self):
        raise NotImplementedError

    def getGuiLootBoxes(self):
        raise NotImplementedError

    def getGuiLootBoxByTokenID(self, tokenID):
        raise NotImplementedError


class IGuiLootBoxesIntroController(IGameController):

    def tryShowIntro(self):
        raise NotImplementedError


class ITelecomRentalsNotificationController(IGameController):

    def processSwitchNotifications(self):
        raise NotImplementedError


class IEventBattlesController(IGameController, ISeasonProvider):
    onPrimeTimeStatusUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError


class IGiftSystemController(IGameController):
    onEventHubsCreated = None
    onEventHubsDestroyed = None

    def getEventHub(self, eventID):
        raise NotImplementedError

    def getSettings(self):
        raise NotImplementedError

    def requestWebState(self, eventID):
        raise NotImplementedError


class IShopSalesEventController(IGameController):
    onSettingsChanged = None
    onPhaseChanged = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def currentEventPhase(self):
        raise NotImplementedError

    @property
    def currentEventPhaseTimeRange(self):
        raise NotImplementedError

    @property
    def activePhaseStartTime(self):
        raise NotImplementedError

    @property
    def activePhaseFinishTime(self):
        raise NotImplementedError

    @property
    def eventFinishTime(self):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError

    def getEventPhase(self, timestamp):
        raise NotImplementedError

    def getEventPhaseTimeRange(self, state):
        raise NotImplementedError

    def openMainView(self, url=None, origin=None):
        raise NotImplementedError


class ISeniorityAwardsController(IGameController):
    onUpdated = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def timeLeft(self):
        raise NotImplementedError

    @property
    def clockOnNotification(self):
        raise NotImplementedError

    @property
    def isRewardReceived(self):
        raise NotImplementedError

    @property
    def seniorityQuestPrefix(self):
        raise NotImplementedError

    @property
    def isNeedToShowRewardNotification(self):
        raise NotImplementedError

    @property
    def pendingReminderTimestamp(self):
        raise NotImplementedError

    def claimReward(self):
        raise NotImplementedError

    def markRewardReceived(self):
        raise NotImplementedError

    def getSACoin(self):
        raise NotImplementedError


class IResourceWellController(IGameController):
    onEventUpdated = None
    onSettingsChanged = None
    onNumberRequesterUpdated = None
    onEventStateChanged = None

    def isEnabled(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isStarted(self):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isPaused(self):
        raise NotImplementedError

    def isNotStarted(self):
        raise NotImplementedError

    def getSeason(self):
        raise NotImplementedError

    def getRewardLimit(self, isTop):
        raise NotImplementedError

    def getFinishTime(self):
        raise NotImplementedError

    def getStartTime(self):
        raise NotImplementedError

    def getCurrentPoints(self):
        raise NotImplementedError

    def getMaxPoints(self):
        raise NotImplementedError

    def getRewardVehicle(self):
        raise NotImplementedError

    def getRewardStyleID(self):
        raise NotImplementedError

    def getRewardSequence(self, isTop):
        raise NotImplementedError

    def getRewardLeftCount(self, isTop):
        raise NotImplementedError

    def isRewardEnabled(self, isTop):
        raise NotImplementedError

    def isRewardCountAvailable(self, isTop=True):
        raise NotImplementedError

    def getReminderTime(self):
        raise NotImplementedError

    def isCompleted(self):
        raise NotImplementedError

    def getResources(self):
        raise NotImplementedError

    def getRewards(self):
        raise NotImplementedError

    def getRewardID(self, isTop):
        raise NotImplementedError

    def startNumberRequesters(self):
        raise NotImplementedError

    def stopNumberRequesters(self):
        raise NotImplementedError


class ICollectiveGoalEntryPointController(IGameController):
    onSettingsChanged = None
    onEventUpdated = None
    onDataUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isCompleted(self):
        raise NotImplementedError

    def isStarted(self):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isForbidden(self):
        raise NotImplementedError

    def getEventStartTime(self):
        raise NotImplementedError

    def getActivePhaseStartTime(self):
        raise NotImplementedError

    def getActivePhaseFinishTime(self):
        raise NotImplementedError

    def getEventFinishTime(self):
        raise NotImplementedError

    def getCurrentPoints(self):
        raise NotImplementedError

    def getStagePoints(self):
        raise NotImplementedError

    def getDiscounts(self):
        raise NotImplementedError

    def getCurrentDiscount(self):
        raise NotImplementedError

    def getMarathonPrefix(self):
        raise NotImplementedError

    def getMarathonName(self):
        raise NotImplementedError

    def getGoalType(self):
        raise NotImplementedError

    def getGoalDescription(self):
        raise NotImplementedError

    def getRulesCaption(self):
        raise NotImplementedError


class ICollectiveGoalMarathonsController(IGameController):
    onMarathonUpdated = None


class IFunRandomController(IGameController):

    class IFunSubSystem(object):

        def fini(self):
            pass

        def clear(self):
            pass

    class IFunHiddenVehicles(IFunSubSystem):

        def startVehiclesListening(self):
            raise NotImplementedError

        def stopVehiclesListening(self):
            raise NotImplementedError

        def updateCurrentVehicle(self, desiredSubMode):
            raise NotImplementedError

    class IFunNotifications(IFunSubSystem):

        def isNotificationsAllowed(self):
            raise NotImplementedError

        def isNotificationsEnabled(self):
            raise NotImplementedError

        def addToQueue(self, notification):
            raise NotImplementedError

        def markSeenAsFrozen(self, subModesIDs):
            raise NotImplementedError

        def pushNotification(self, notification):
            raise NotImplementedError

        def startNotificationPushing(self):
            raise NotImplementedError

        def stopNotificationPushing(self):
            raise NotImplementedError

        def updateSettings(self, settings):
            raise NotImplementedError

    class IFunProgressions(IFunSubSystem):

        def isProgressionExecutor(self, questID):
            raise NotImplementedError

        def getActiveProgression(self):
            raise NotImplementedError

        def getProgressionTimer(self):
            raise NotImplementedError

        def getSettings(self):
            raise NotImplementedError

        def startProgressListening(self):
            raise NotImplementedError

        def stopProgressListening(self):
            raise NotImplementedError

        def updateSettings(self, progressionSettings):
            raise NotImplementedError

    class IFunSubscription(IFunSubSystem):

        def addListener(self, eventType, handler, scope=None):
            raise NotImplementedError

        def removeListener(self, eventType, handler, scope=None):
            raise NotImplementedError

        def handleEvent(self, event, scope=None):
            raise NotImplementedError

        def addSubModesWatcher(self, method, desiredOnly=False, withTicks=False):
            raise NotImplementedError

        def removeSubModesWatcher(self, method, desiredOnly=False, withTicks=False):
            raise NotImplementedError

        def resume(self):
            raise NotImplementedError

        def suspend(self):
            raise NotImplementedError

    class IFunSubModesHolder(IFunSubSystem):

        def getBattleSubMode(self, arenaVisitor=None):
            raise NotImplementedError

        def getBattleSubModeID(self, arenaVisitor=None):
            raise NotImplementedError

        def getDesiredSubMode(self):
            raise NotImplementedError

        def getDesiredSubModeID(self):
            raise NotImplementedError

        def getSubMode(self, subModeID):
            raise NotImplementedError

        def getSubModes(self, subModesIDs=None, isOrdered=False):
            raise NotImplementedError

        def getSubModesIDs(self):
            raise NotImplementedError

        def setDesiredSubModeID(self, subModeID, trustedSource=False):
            raise NotImplementedError

        def startNotification(self):
            raise NotImplementedError

        def stopNotification(self):
            raise NotImplementedError

        def updateSettings(self, prevSettings, newSettings):
            raise NotImplementedError

    class IFunSubModesInfo(IFunSubSystem):

        def isAvailable(self):
            raise NotImplementedError

        def isEntryPointAvailable(self):
            raise NotImplementedError

        def getLeftTimeToPrimeTimesEnd(self, now=None, subModes=None):
            raise NotImplementedError

        def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
            raise NotImplementedError

        def getSubModesStatus(self, subModesIDs=None):
            raise NotImplementedError

    @property
    def notifications(self):
        raise NotImplementedError

    @property
    def progressions(self):
        raise NotImplementedError

    @property
    def subModesHolder(self):
        raise NotImplementedError

    @property
    def subModesInfo(self):
        raise NotImplementedError

    @property
    def subscription(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isFunRandomPrbActive(self):
        raise NotImplementedError

    def getAssetsPointer(self):
        raise NotImplementedError

    def getLocalsResRoot(self):
        raise NotImplementedError

    def getIconsResRoot(self):
        raise NotImplementedError

    def getSettings(self):
        raise NotImplementedError

    def setDesiredSubModeID(self, subModeID, trustedSource=False):
        raise NotImplementedError

    def selectFunRandomBattle(self, desiredSubModeID, callback=None):
        raise NotImplementedError


class IComp7Controller(IGameController, ISeasonProvider):
    onStatusUpdated = None
    onStatusTick = None
    onRankUpdated = None
    onComp7ConfigChanged = None
    onComp7RanksConfigChanged = None
    onBanUpdated = None
    onOfflineStatusUpdated = None
    onQualificationBattlesUpdated = None
    onQualificationStateUpdated = None
    onSeasonPointsUpdated = None
    onComp7RewardsConfigChanged = None
    onComp7BattleFinished = None

    @property
    def rating(self):
        raise NotImplementedError

    @property
    def isElite(self):
        raise NotImplementedError

    @property
    def isBanned(self):
        raise NotImplementedError

    @property
    def banDuration(self):
        raise NotImplementedError

    @property
    def isOffline(self):
        raise NotImplementedError

    @property
    def leaderboard(self):
        raise NotImplementedError

    @property
    def activityPoints(self):
        raise NotImplementedError

    @property
    def battleModifiers(self):
        raise NotImplementedError

    @property
    def qualificationBattlesNumber(self):
        raise NotImplementedError

    @property
    def qualificationBattlesStatuses(self):
        raise NotImplementedError

    @property
    def qualificationState(self):
        raise NotImplementedError

    @property
    def entitlementsCache(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def isQualificationActive(self):
        raise NotImplementedError

    def isQualificationResultsProcessing(self):
        raise NotImplementedError

    def isQualificationCalculationRating(self):
        raise NotImplementedError

    def isQualificationSquadAllowed(self):
        raise NotImplementedError

    def getRoleEquipment(self, roleName):
        raise NotImplementedError

    def getEquipmentStartLevel(self, roleName):
        raise NotImplementedError

    def getViewData(self, viewAlias):
        raise NotImplementedError

    def isSuitableVehicle(self, vehicle):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def vehicleIsAvailableForBuy(self):
        raise NotImplementedError

    def vehicleIsAvailableForRestore(self):
        raise NotImplementedError

    def hasPlayableVehicle(self):
        raise NotImplementedError

    def isComp7PrbActive(self):
        raise NotImplementedError

    def isBattleModifiersAvailable(self):
        raise NotImplementedError

    def getAlertBlock(self):
        raise NotImplementedError

    def getPlatoonRatingRestriction(self):
        raise NotImplementedError

    def getStatsSeasonsKeys(self):
        raise NotImplementedError

    def getReceivedSeasonPoints(self):
        raise NotImplementedError

    def getYearlyRewards(self):
        raise NotImplementedError

    def getBattleModifiersObject(self):
        raise NotImplementedError

    def isYearlyRewardReceived(self):
        raise NotImplementedError


class IArmoryYardController(IGameController):
    onUpdated = None
    onProgressUpdated = None
    onStatusChange = None
    onQuestsUpdated = None
    onCheckNotify = None
    onAnnouncement = None
    onPayed = None
    onPayedError = None
    onBundleOutTime = None
    onServerSwitchChange = None
    onStyleQuestEnds = None
    onCollectReward = None
    cameraManager = None
    isVehiclePreview = None
    bundlesProducts = None
    onTabIdChanged = None
    onCollectFinalReward = None
    onBundlesDisabled = None
    onAYCoinsUpdate = None

    @property
    def isArmoryVisiting(self):
        raise NotImplementedError

    @property
    def serverSettings(self):
        raise NotImplementedError

    @property
    def isFinalQuestCompleted(self):
        raise NotImplementedError

    def getCollectableRewards(self):
        raise NotImplementedError

    def isChapterFinished(self, cycle):
        raise NotImplementedError

    def receivedTokensInChapter(self, cycleID):
        raise NotImplementedError

    def iterCycleProgressionQuests(self, cycleID):
        raise NotImplementedError

    def getTokensInfo(self):
        raise NotImplementedError

    def getSeasonInterval(self):
        raise NotImplementedError

    def getProgressionTimes(self):
        raise NotImplementedError

    def getPostProgressionTimes(self):
        raise NotImplementedError

    def totalTokensInChapter(self, cycleID):
        raise NotImplementedError

    def iterProgressionQuests(self):
        raise NotImplementedError

    def getCurrencyTokenCount(self):
        raise NotImplementedError

    def getProgressionLevel(self):
        raise NotImplementedError

    def getCurrentProgress(self):
        raise NotImplementedError

    def getTotalSteps(self):
        raise NotImplementedError

    def getStepsRewards(self):
        raise NotImplementedError

    def getFinalRewardVehicle(self):
        raise NotImplementedError

    def getCurrencyTokenCost(self, currency):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def goToArmoryYard(self, tabId, ctx=None):
        raise NotImplementedError

    def goToArmoryYardQuests(self):
        raise NotImplementedError

    def hasCurrentRewards(self):
        raise NotImplementedError

    def isProgressionQuest(self, questID):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isClaimedFinalReward(self):
        raise NotImplementedError

    def isQuestActive(self):
        raise NotImplementedError

    def isSceneLoaded(self):
        raise NotImplementedError

    def isPostProgressionActive(self):
        raise NotImplementedError

    def getAvailableQuestsCount(self):
        raise NotImplementedError

    def getNextCycle(self, currentTime=None):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def update(self):
        raise NotImplementedError

    def onLoadingHangar(self):
        raise NotImplementedError

    def unloadScene(self, isReload=True):
        raise NotImplementedError

    def isCompleted(self):
        raise NotImplementedError

    def isStarterPackAvailable(self):
        raise NotImplementedError

    def disableVideoStreaming(self):
        raise NotImplementedError

    def getStarterPackSettings(self):
        raise NotImplementedError

    def refreshBundle(self):
        raise NotImplementedError

    def checkAnnouncement(self):
        raise NotImplementedError

    def payedTokensLeft(self):
        raise NotImplementedError

    def isPostProgressionEnabled(self):
        raise NotImplementedError

    def getTokenCurrencies(self):
        raise NotImplementedError

    def subtrahendStageToken(self):
        raise NotImplementedError

    def getHangarFlagData(self):
        raise NotImplementedError


class IArmoryYardShopController(IGameController):
    onProductsUpdate = None
    onAYCoinsUpdate = None
    onSettingsUpdate = None
    onPurchaseComplete = None
    onPurchaseError = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def ayCoins(self):
        raise NotImplementedError

    @property
    def conversionPrices(self):
        raise NotImplementedError

    @property
    def products(self):
        raise NotImplementedError

    @property
    def isSeasonCompleted(self):
        raise NotImplementedError

    def isBundle(self, productId):
        raise NotImplementedError


class IHangarSpaceSwitchController(IGameController):
    onCheckSceneChange = None
    onSpaceUpdated = None

    def hangarSpaceUpdate(self, sceneName):
        raise NotImplementedError

    def lockHangarOverride(self, sceneName):
        raise NotImplementedError


class ICollectionsSystemController(IGameController):
    onServerSettingsChanged = None
    onBalanceUpdated = None
    onAvailabilityChanged = None

    @property
    def cache(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def getCollections(self, reverseSort=False):
        raise NotImplementedError

    def getCollection(self, collectionId):
        raise NotImplementedError

    def getCollectionByName(self, collectionName):
        raise NotImplementedError

    def isRelatedEventActive(self, collectionId):
        raise NotImplementedError

    def getLinkedCollections(self, collectionId):
        raise NotImplementedError

    def getCollectionIDs(self):
        raise NotImplementedError

    def getCollectionItem(self, collectionId, itemId):
        raise NotImplementedError

    def getNewLinkedCollectionsItemCount(self, collectionId):
        raise NotImplementedError

    def getNewCollectionItemCount(self, collectionId):
        raise NotImplementedError

    def getReceivedItemCount(self, collectionId):
        raise NotImplementedError

    def isCollectionCompleted(self, collectionId):
        raise NotImplementedError

    def getMaxItemCount(self, collectionId):
        raise NotImplementedError

    def getMaxProgressItemCount(self, collectionId):
        raise NotImplementedError

    def getReceivedProgressItemCount(self, collectionId):
        raise NotImplementedError

    def isRewardReceived(self, collectionId, requiredCount):
        raise NotImplementedError

    def isItemReceived(self, collectionId, itemId):
        raise NotImplementedError


class IWinbackController(IGameController):
    onConfigUpdated = None
    onStateUpdated = None
    onTokensUpdated = None

    @property
    def winbackConfig(self):
        raise NotImplementedError

    @property
    def activeProgressionConfig(self):
        raise NotImplementedError

    @property
    def winbackProgression(self):
        raise NotImplementedError

    @property
    def winbackQuests(self):
        raise NotImplementedError

    @property
    def winbackPromoURL(self):
        raise NotImplementedError

    @property
    def winbackInfoPageURL(self):
        raise NotImplementedError

    @property
    def progressionName(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isWidgetEnabled(self):
        raise NotImplementedError

    def isProgressionEnabled(self):
        raise NotImplementedError

    def isVersusAIPrbActive(self):
        raise NotImplementedError

    def isWinbackQuest(self, quest):
        raise NotImplementedError

    def isFinished(self):
        raise NotImplementedError

    def isWinbackOfferToken(self, offerToken):
        raise NotImplementedError

    def hasWinbackOfferGiftToken(self):
        raise NotImplementedError

    def winbackOfferGiftTokenCount(self):
        raise NotImplementedError

    def isPromoEnabled(self):
        raise NotImplementedError

    def versusAIModeShouldBeDefault(self):
        raise NotImplementedError

    def getHeaderFlagState(self):
        raise NotImplementedError


class IDailyQuestIntroPresenter(IGameController):
    pass


class IAchievements20Controller(IGameController):
    onUpdate = None
    onRankIncrease = None
    onRankDecrease = None

    def showNewSummaryEnabled(self):
        raise NotImplementedError

    def showRatingUpgrade(self):
        raise NotImplementedError

    def showRatingChanged(self):
        raise NotImplementedError

    def showRankedComplete(self):
        raise NotImplementedError

    def showEditAvailable(self):
        raise NotImplementedError

    def onSummaryPageVisited(self):
        raise NotImplementedError

    def getAchievementsTabCounter(self):
        raise NotImplementedError

    def getPrevAchievementsList(self):
        raise NotImplementedError

    def setPrevAchievementsList(self, value):
        raise NotImplementedError

    def getInitialBattleCount(self):
        raise NotImplementedError

    def setInitialBattleCount(self, value):
        raise NotImplementedError

    def getWtrPrevPointsNotification(self):
        raise NotImplementedError

    def setMaxWtrPoints(self, points):
        raise NotImplementedError

    def getMaxWtrPoints(self):
        raise NotImplementedError

    def setWtrPrevPointsNotification(self, points):
        raise NotImplementedError

    def getWtrPrevPoints(self):
        raise NotImplementedError

    def setWtrPrevPoints(self, points):
        raise NotImplementedError

    def getWtrPrevRank(self):
        raise NotImplementedError

    def setWtrPrevRank(self, rank):
        raise NotImplementedError

    def getWtrPrevSubRank(self):
        raise NotImplementedError

    def setWtrPrevSubRank(self, subRank):
        raise NotImplementedError

    def getFirstEntryStatus(self):
        raise NotImplementedError

    def setFirstEntryStatus(self, value):
        raise NotImplementedError

    def getRatingCalculatedStatus(self):
        raise NotImplementedError

    def setRatingCalculatedStatus(self, value):
        raise NotImplementedError

    def getMedalAddedStatus(self):
        raise NotImplementedError

    def setMedalAddedStatus(self, value):
        raise NotImplementedError

    def getAchievementEditingEnabledStatus(self):
        raise NotImplementedError

    def setAchievementEditingEnabledStatus(self, value):
        raise NotImplementedError

    def getRatingChangedStatus(self):
        raise NotImplementedError

    def setRatingChangedStatus(self, value):
        raise NotImplementedError

    def getMedalCountInfo(self):
        raise NotImplementedError

    def setMedalCountInfo(self, value):
        raise NotImplementedError


class ILimitedUIController(IGameController):
    onStateChanged = None
    onConfigChanged = None
    onVersionUpdated = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isInited(self):
        raise NotImplementedError

    @property
    def configVersion(self):
        raise NotImplementedError

    @property
    def version(self):
        raise NotImplementedError

    @property
    def isOnlyUISpamOff(self):
        raise NotImplementedError

    @property
    def isUserSettingsMayShow(self):
        raise NotImplementedError

    @property
    def isFullCompleted(self):
        raise NotImplementedError

    def isRuleCompleted(self, ruleID):
        raise NotImplementedError

    def completeRule(self, ruleID):
        raise NotImplementedError

    def completeAllRules(self):
        raise NotImplementedError

    def startObserve(self, ruleID, handler):
        raise NotImplementedError

    def stopObserve(self, ruleID, handler):
        raise NotImplementedError


class IHangarGuiController(IGameController):

    def isComponentAvailable(self, componentType):
        raise NotImplementedError

    def getCurrentPreset(self):
        raise NotImplementedError

    def getAmmoInjectViewAlias(self):
        raise NotImplementedError

    def getHangarCarouselSettings(self):
        raise NotImplementedError

    def getHangarVehicleParamsSettings(self):
        raise NotImplementedError

    def holdHangar(self, hangar):
        raise NotImplementedError

    def releaseHangar(self):
        raise NotImplementedError

    def updateChangeableComponents(self, isVisible, forced=False):
        raise NotImplementedError

    def updateComponentsVisibility(self, preset=None):
        raise NotImplementedError


class IDebutBoxesController(IGameController):
    onConfigChanged = None
    onStateChanged = None
    onQuestsChanged = None

    def isEnabled(self):
        raise NotImplementedError

    def isQuestsCompletedOnVehicle(self, vehicle):
        raise NotImplementedError

    def isQuestsAvailableOnVehicle(self, vehicle):
        raise NotImplementedError

    def getQuestForVehicle(self, vehicle):
        raise NotImplementedError

    def getQuestsIDs(self):
        raise NotImplementedError

    def getGroupID(self):
        raise NotImplementedError

    def getInfoPageUrl(self):
        raise NotImplementedError


class IModeSelectorController(IGameController):

    def getModeSettings(self):
        raise NotImplementedError

    def getColumnSettings(self):
        raise NotImplementedError


class IEarlyAccessController(IGameController, ISeasonProvider):
    onQuestsUpdated = None
    onBalanceUpdated = None
    onUpdated = None
    cgfCameraManager = None
    onPayed = None
    onStartEvent = None
    onFinishEvent = None
    onStartAnnouncement = None
    onFinishAnnouncement = None
    onFeatureStateChanged = None

    @property
    def sysMessageController(self):
        raise NotImplementedError

    @property
    def hangarFeatureState(self):
        raise NotImplementedError

    @staticmethod
    def isProgressionQuest(questID):
        raise NotImplementedError

    @staticmethod
    def isPostProgressionQuest(questID):
        raise NotImplementedError

    def getModeSettings(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isPaused(self):
        raise NotImplementedError

    def getInfoPageLink(self):
        raise NotImplementedError

    def getAffectedVehiclesOrderedList(self):
        raise NotImplementedError

    def getAffectedVehicles(self):
        raise NotImplementedError

    def getBlockedVehicles(self):
        raise NotImplementedError

    def getVehiclePrice(self, intCD):
        raise NotImplementedError

    def getTokensBalance(self):
        raise NotImplementedError

    def getFirstVehicleCD(self):
        raise NotImplementedError

    def getCurrProgressVehicleCD(self):
        raise NotImplementedError

    def getNationID(self):
        raise NotImplementedError

    def getTokenCost(self):
        raise NotImplementedError

    def getTokenCompensation(self, currency):
        raise NotImplementedError

    def getReceivedTokensCount(self):
        raise NotImplementedError

    def getTotalVehiclesPrice(self):
        raise NotImplementedError

    def getTokensForQuest(self, questID):
        raise NotImplementedError

    def getEAToken(self):
        raise NotImplementedError

    def iterProgressionQuests(self):
        raise NotImplementedError

    def iterCycleProgressionQuests(self, cycleID):
        raise NotImplementedError

    def iterAllCycles(self, now=None):
        raise NotImplementedError

    def isQuestActive(self):
        raise NotImplementedError

    def getPostProgressionVehiclesForQuest(self, questID):
        raise NotImplementedError

    def getPostProgressionVehicles(self):
        raise NotImplementedError

    def getRequiredVehicleTypeAndLevelsForQuest(self, questID):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def getSeasonInterval(self):
        raise NotImplementedError

    def getCurrentSeasonID(self):
        raise NotImplementedError

    def getProgressionTimes(self):
        raise NotImplementedError

    def getPostprogressionTimes(self):
        raise NotImplementedError

    def getCycleProgressionTimes(self, cycleId=None):
        raise NotImplementedError

    def hasPostprogressionVehicle(self):
        raise NotImplementedError

    def getReceivedTokensForQuests(self):
        raise NotImplementedError

    def isGroupQuestsCompleted(self, groupName):
        raise NotImplementedError

    def isPostProgressionQueueSelected(self):
        raise NotImplementedError

    def isAnyQuestAvailable(self):
        raise NotImplementedError

    def isFilterDisabledInQueue(self):
        raise NotImplementedError

    def getVehicleTypeAndLevelsByVehicleCD(self, vehCD):
        raise NotImplementedError


class ILootBoxesController(IGameController):
    onUpdated = None
    onUpdatedConfig = None

    def getLootBoxesByType(self):
        raise NotImplementedError

    def getLootBoxesCountByType(self, lottBoxType):
        raise NotImplementedError

    def getLootBoxesCountByTypeForUI(self, lootBoxType):
        raise NotImplementedError

    def getLootBoxByTypeInInventory(self, lootBoxType):
        raise NotImplementedError

    def getLootBoxLimitsInfo(self, lootBoxType):
        raise NotImplementedError

    def getLootBoxesRewards(self, lootBoxType):
        raise NotImplementedError

    def getLastViewedCount(self):
        raise NotImplementedError

    def updateLastViewedCount(self):
        raise NotImplementedError

    def getCollectionType(self, itemID):
        raise NotImplementedError

    def isCollectionElement(self, intCD, collection):
        raise NotImplementedError

    def claimReRolledReward(self, boxType, count, parentWindow, callbackUpdate=None):
        raise NotImplementedError

    def getLootBoxDailyPurchaseLimit(self):
        raise NotImplementedError

    def getPurchasedLootBoxesCount(self):
        raise NotImplementedError

    def getAvailableForPurchaseLootBoxesCount(self):
        raise NotImplementedError


class IEventSettingsController(IGameController):

    @property
    def disabledSettings(self):
        raise NotImplementedError


class IWhiteTigerController(IGameController, ISeasonProvider):
    onPrimeTimeStatusUpdated = None
    onProgressUpdated = None
    onEventPrbChanged = None
    onUpdated = None
    onTicketsUpdate = None

    def isEnabled(self):
        raise NotImplementedError

    def isEventPrbActive(self):
        raise NotImplementedError

    def doSelectEventPrb(self):
        raise NotImplementedError

    def doSelectEventPrbAndCallback(self, callback):
        raise NotImplementedError

    def doLeaveEventPrb(self):
        raise NotImplementedError

    def isModeActive(self):
        raise NotImplementedError

    def isBattlesEnd(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def isHangarAvailable(self):
        raise NotImplementedError

    def isWelcomeScreenShown(self):
        raise NotImplementedError

    def getCurrentStampsCount(self):
        raise NotImplementedError

    def getCurrentMainPrizeDiscountTokensCount(self):
        raise NotImplementedError

    def getTotalStampsCount(self):
        raise NotImplementedError

    def getStampsCountPerLevel(self):
        raise NotImplementedError

    def getMainPrizeDiscountPerToken(self):
        raise NotImplementedError

    def getTotalLevelsCount(self):
        raise NotImplementedError

    def getFinishedLevelsCount(self):
        raise NotImplementedError

    def getCurrentLevel(self):
        raise NotImplementedError

    def getTicketCount(self):
        raise NotImplementedError

    def getQuickTicketCount(self):
        raise NotImplementedError

    def getQuickTicketExpiryTime(self):
        raise NotImplementedError

    def getQuickHunterTicketCount(self):
        raise NotImplementedError

    def getQuickHunterTicketExpiryTime(self):
        raise NotImplementedError

    def getLootBoxAreaSoundMgr(self):
        raise NotImplementedError

    def getSelectedVehicleSoundMgr(self):
        raise NotImplementedError

    def hasEnoughTickets(self, useQuickTicket=True):
        raise NotImplementedError

    def hasSpecialBoss(self):
        raise NotImplementedError

    def getSpecialBossBattlesRemaining(self):
        raise NotImplementedError

    def getQuestRewards(self, questID):
        raise NotImplementedError

    def getDisplayedCollectionProgress(self, questID):
        raise NotImplementedError

    @property
    def mainViewLoaded(self):
        raise NotImplementedError

    def analyzeClientSystem(self):
        raise NotImplementedError

    def showIntroVideo(self, onVideoClosed=None):
        raise NotImplementedError

    def isOutroVideoAvailable(self):
        raise NotImplementedError

    def needToShowOutroVideo(self):
        raise NotImplementedError

    def showOutroVideo(self):
        raise NotImplementedError


class IVersusAIController(IGameController):

    def isEnabled(self):
        raise NotImplementedError

    def isVersusAIPrbActive(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def shouldBeDefaultMode(self):
        raise NotImplementedError
