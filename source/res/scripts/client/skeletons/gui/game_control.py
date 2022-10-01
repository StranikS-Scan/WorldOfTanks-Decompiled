# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_control.py
import typing
from constants import ARENA_BONUS_TYPE
if typing.TYPE_CHECKING:
    from typing import Callable, Dict, Iterable, Iterator, List, Optional, Set, Tuple, Union, Sequence
    from battle_pass_common import FinalReward
    from Event import Event
    from battle_modifiers.gui.feature.modifiers_data_provider import ModifiersDataProvider
    from gui.Scaleform.daapi.view.lobby.comp7.shared import Comp7AlertData
    from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import EpicBattleScreens
    from gui.Scaleform.daapi.view.lobby.comp7.shared import Comp7AlertData
    from gui.battle_pass.state_machine.delegator import BattlePassRewardLogic
    from gui.game_control.comp7_controller import _LeaderboardDataProvider
    from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
    from gui.game_control.mapbox_controller import ProgressionData
    from gui.game_control.trade_in import TradeInDiscounts
    from gui.gift_system.hubs.base.hub_core import IGiftEventHub
    from gui.mapbox.mapbox_survey_manager import MapboxSurveyManager
    from gui.periodic_battles.models import AlertData, PeriodInfo, PrimeTime
    from gui.prb_control.items import ValidationResult
    from gui.ranked_battles.constants import YearAwardsNames
    from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager
    from gui.ranked_battles.ranked_helpers.stats_composer import RankedBattlesStatsComposer
    from gui.ranked_battles.ranked_helpers.web_season_provider import RankedWebSeasonProvider, WebSeasonInfo
    from gui.ranked_battles.ranked_models import BattleRankInfo, Division, PostBattleRankInfo, Rank
    from gui.server_events.bonuses import BattlePassSelectTokensBonus, BattlePassStyleProgressTokenBonus, SimpleBonus, TokensBonus
    from gui.server_events.event_items import RankedQuest
    from gui.shared.gui_items import Tankman, Vehicle
    from gui.shared.gui_items.fitting_item import RentalInfoProvider
    from gui.shared.gui_items.gui_item_economics import ItemPrice
    from gui.shared.gui_items.Tankman import TankmanSkill
    from gui.shared.money import Money, DynamicMoney
    from gui.shared.utils.requesters.EpicMetaGameRequester import EpicMetaGameRequester
    from helpers.server_settings import BattleRoyaleConfig, EpicGameConfig, GiftSystemConfig, RankedBattlesConfig, VehiclePostProgressionConfig, _MapboxConfig, Comp7Config
    from items.vehicles import VehicleType
    from season_common import GameSeason
    from items.artefacts import Equipment
    from gui.entitlements.entitlement_model import AgateEntitlement
    BattlePassBonusOpts = Optional[TokensBonus, BattlePassSelectTokensBonus]

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

    def isAvailable(self):
        raise NotImplementedError

    def isBattlesPossible(self):
        raise NotImplementedError

    def isInPrimeTime(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def isWithinSeasonTime(self, seasonID):
        raise NotImplementedError

    def hasAnySeason(self):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
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

    def getLeftTimeToPrimeTimesEnd(self):
        raise NotImplementedError


class IGameStateTracker(IGameController):

    def onAccountShowGUI(self, ctx):
        raise NotImplementedError

    def addController(self, controller):
        raise NotImplementedError


class IReloginController(IGameController):

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

    def hasAdventHero(self):
        raise NotImplementedError

    def isAdventHero(self):
        raise NotImplementedError

    def getRandomTankCD(self):
        raise NotImplementedError

    def setInteractive(self, interactive):
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

    def leavePlatoon(self, isExit=True, ignoreConfirmation=False):
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
    pass


class IBoostersController(IGameController):
    onBoosterChangeNotify = None
    onReserveTimerTick = None
    onGameModeStatusChange = None

    def isGameModeSupported(self):
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

    def addVehicle(self, vehicleCompactDesr, initParameters=None):
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

    def getUnlockableInBattleVehLevels(self):
        raise NotImplementedError

    def getSuitableForQueueVehicleLevels(self):
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

    def getPlayerLevelInfo(self):
        raise NotImplementedError

    def getPlayerRanksInfo(self):
        raise NotImplementedError

    def getSeasonData(self):
        raise NotImplementedError

    def getSkillPoints(self):
        raise NotImplementedError

    def getSkillLevels(self):
        raise NotImplementedError

    def getSelectedSkills(self, vehicleCD):
        raise NotImplementedError

    def increaseSkillLevel(self, skillID):
        raise NotImplementedError

    def changeEquippedSkills(self, skillIDArray, vehicleCD, callback=None):
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

    def isNeedToTakeReward(self):
        raise NotImplementedError

    def getNotChosenRewardCount(self):
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

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def getStoredEpicDiscount(self):
        raise NotImplementedError

    def getStats(self):
        raise NotImplementedError

    def openURL(self):
        raise NotImplementedError

    def showCustomScreen(self, screen):
        raise NotImplementedError


class IBattleRoyaleController(IGameController, ISeasonProvider):
    onUpdated = None
    onPrimeTimeStatusUpdated = None
    onWidgetUpdate = None
    TOKEN_QUEST_ID = ''

    def isEnabled(self):
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

    def isFirstIndication(self):
        raise NotImplementedError

    def getBubbleCount(self):
        raise NotImplementedError

    def updateBubble(self):
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
    onExtraChapterExpired = None

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

    def getLevelByPoints(self, chapterID, points):
        raise NotImplementedError

    def getProgressionByPoints(self, chapterID, points, level):
        raise NotImplementedError

    def getMaxLevelInChapter(self, chapterId):
        raise NotImplementedError

    def hasExtra(self):
        raise NotImplementedError

    def isRegularProgressionCompleted(self):
        raise NotImplementedError

    def getExtraChapterID(self):
        raise NotImplementedError

    def getRewardType(self, chapterID):
        raise NotImplementedError

    def isChapterExists(self, chapterID):
        raise NotImplementedError

    def getChapterIDs(self):
        raise NotImplementedError

    def isExtraChapter(self, chapterID):
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

    def getFinalOfferTime(self):
        raise NotImplementedError

    def getPrevSeasonsStats(self):
        raise NotImplementedError

    def getLastFinishedSeasonStats(self):
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


class IUISpamController(IGameController):

    def checkRule(self, ruleId):
        raise NotImplementedError

    def shouldBeHidden(self, aliasId):
        raise NotImplementedError

    def setVisited(self, aliasId):
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


class IWotPlusNotificationController(IGameController):

    def processSwitchNotifications(self):
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


class ICNLootBoxesController(IGameController, IEntitlementsConsumer):
    onStatusChange = None
    onAvailabilityChange = None
    onBoxesCountChange = None
    onIntroShownChanged = None
    onBoxesUpdate = None
    onBoxInfoUpdated = None

    @property
    def boxCountToGuaranteedBonus(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isLootBoxesAvailable(self):
        raise NotImplementedError

    def isBuyAvailable(self):
        raise NotImplementedError

    def isIntroWasShown(self):
        raise NotImplementedError

    def useExternalShop(self):
        raise NotImplementedError

    def setIntroWasShown(self, value):
        raise NotImplementedError

    def getDayLimit(self):
        raise NotImplementedError

    def getGuaranteedBonusLimit(self, boxType):
        raise NotImplementedError

    def getEventActiveTime(self):
        raise NotImplementedError

    def openShop(self):
        raise NotImplementedError

    def getDayInfoStatistics(self):
        raise NotImplementedError

    def getExpiresAtLootBoxBuyCounter(self):
        raise NotImplementedError

    def getTimeLeftToResetPurchase(self):
        raise NotImplementedError

    def getCommonBoxInfo(self):
        raise NotImplementedError

    def getPremiumBoxInfo(self):
        raise NotImplementedError

    def getBoxInfo(self, boxType):
        raise NotImplementedError

    def getStoreInfo(self):
        raise NotImplementedError

    def getBoxesIDs(self):
        raise NotImplementedError

    def getBoxesCount(self):
        raise NotImplementedError

    def getBoxesInfo(self):
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


class ISeniorityAwardsController(IGameController):
    onUpdated = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def endTimestamp(self):
        raise NotImplementedError

    @property
    def showNotificationLastCallTimestamp(self):
        raise NotImplementedError

    @property
    def needShowNotification(self):
        raise NotImplementedError

    def getSACoin(self):
        raise NotImplementedError


class IResourceWellController(IGameController):
    onEventUpdated = None
    onSettingsChanged = None
    onNumberRequesterUpdated = None

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

    def getSeason(self):
        raise NotImplementedError

    def getRewardLimit(self, isTop):
        raise NotImplementedError

    def getFinishTime(self):
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


class IFunRandomController(IGameController, ISeasonProvider):
    onUpdated = None
    onGameModeStatusTick = None
    onGameModeStatusUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isFunRandomPrbActive(self):
        raise NotImplementedError

    def isSuitableVehicle(self, vehicle, isSquad=False):
        raise NotImplementedError

    def isSuitableVehicleAvailable(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def canGoToMode(self):
        raise NotImplementedError

    def getAlertBlock(self):
        raise NotImplementedError

    def getModifiersDataProvider(self):
        raise NotImplementedError

    def selectFunRandomBattle(self):
        raise NotImplementedError


class IComp7Controller(IGameController, ISeasonProvider):
    onStatusUpdated = None
    onStatusTick = None
    onRankUpdated = None
    onComp7ConfigChanged = None
    onComp7RanksConfigChanged = None
    onBanUpdated = None
    onOfflineStatusUpdated = None

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

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def getRoleEquipment(self, roleName):
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

    def getAlertBlock(self):
        raise NotImplementedError

    def getPlatoonRatingRestriction(self):
        raise NotImplementedError


class IHangarSpaceSwitchController(IGameController):
    onCheckSceneChange = None
    onSpaceUpdated = None

    def hangarSpaceUpdate(self, sceneName):
        raise NotImplementedError
