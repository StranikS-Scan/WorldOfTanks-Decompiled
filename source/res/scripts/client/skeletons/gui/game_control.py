# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_control.py
import typing
from constants import ARENA_BONUS_TYPE
if typing.TYPE_CHECKING:
    from Event import Event
    from gui.Scaleform.daapi.view.lobby.epicBattle.epic_helpers import EpicBattleScreens
    from gui.game_control.mapbox_controller import ProgressionData
    from gui.game_control.epic_meta_game_ctrl import EpicMetaGameSkill
    from gui.shared.gui_items import Vehicle, Tankman
    from gui.periodic_battles.models import PrimeTime, PeriodInfo, AlertData
    from gui.prb_control.items import ValidationResult
    from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager
    from gui.ranked_battles.ranked_helpers.web_season_provider import WebSeasonInfo, RankedWebSeasonProvider
    from gui.ranked_battles.ranked_helpers.stats_composer import RankedBattlesStatsComposer
    from gui.ranked_battles.ranked_models import PostBattleRankInfo, Rank, Division
    from gui.ranked_battles.constants import YearAwardsNames
    from gui.shared.gui_items.fitting_item import RentalInfoProvider
    from gui.shared.utils.requesters.EpicMetaGameRequester import EpicMetaGameRequester
    from gui.server_events.event_items import RankedQuest
    from helpers.server_settings import _MapboxConfig
    from season_common import GameSeason
    from gui.ranked_battles.ranked_models import BattleRankInfo
    from gui.server_events.bonuses import SimpleBonus
    from gui.battle_pass.state_machine.delegator import BattlePassRewardLogic
    from helpers.server_settings import BattleRoyaleConfig, EpicGameConfig, RankedBattlesConfig, VehiclePostProgressionConfig
    from items.vehicles import VehicleType

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

    def isFrozen(self):
        raise NotImplementedError

    def getModeSettings(self):
        raise NotImplementedError

    def getCurrentCycleID(self):
        raise NotImplementedError

    def hasAnySeason(self):
        raise NotImplementedError

    def hasConfiguredPrimeTimeServers(self, now=None):
        raise NotImplementedError

    def getClosestStateChangeTime(self, now=None):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        raise NotImplementedError

    def getCurrentOrNextActiveCycleNumber(self, season):
        raise NotImplementedError

    def getEventEndTimestamp(self):
        raise NotImplementedError

    def getCurrentCycleInfo(self):
        raise NotImplementedError

    def getCurrentSeason(self, now=None):
        raise NotImplementedError

    def getNextSeason(self, now=None):
        raise NotImplementedError

    def getPeriodInfo(self, now=None, peripheryID=None):
        raise NotImplementedError

    def getPrimeTimeStatus(self, now=None, peripheryID=None):
        raise NotImplementedError

    def getSeason(self, seasonID):
        raise NotImplementedError

    def isWithinSeasonTime(self, seasonID):
        raise NotImplementedError

    def hasPrimeTimesLeftForCurrentCycle(self):
        raise NotImplementedError

    def getPreviousSeason(self, now=None):
        raise NotImplementedError

    def isInPrimeTime(self):
        raise NotImplementedError

    def getSeasonPassed(self, now=None):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
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

    def getActiveTradeOffVehicle(self):
        raise NotImplementedError

    def getActiveTradeOffVehicleCD(self):
        raise NotImplementedError

    def setActiveTradeOffVehicleCD(self, value):
        raise NotImplementedError

    def getActiveTradeOffVehicleState(self):
        raise NotImplementedError

    def getTradeInInfo(self, item):
        raise NotImplementedError

    def getStartEndTimestamps(self):
        raise NotImplementedError

    def getMinAcceptableSellPrice(self):
        raise NotImplementedError

    def getAllowedVehicleLevels(self, maxLevel=None):
        raise NotImplementedError

    def getTradeOffVehicles(self, maxLevel=None):
        raise NotImplementedError

    def tradeOffSelectedApplicableForLevel(self, maxLevel):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def getTradeInPrice(self, vehicle):
        raise NotImplementedError

    def addTradeInPriceIfNeeded(self, vehicle, money):
        raise NotImplementedError


class IPersonalTradeInController(IGameController):
    onActiveSaleVehicleChanged = None
    onActiveBuyVehicleChanged = None

    def getSaleVehicleCDs(self):
        raise NotImplementedError

    def getBuyVehicleCDs(self):
        raise NotImplementedError

    def getActiveTradeInSaleVehicleCD(self):
        raise NotImplementedError

    def getActiveTradeInSaleVehicle(self):
        raise NotImplementedError

    def setActiveTradeInSaleVehicleCD(self, value):
        raise NotImplementedError

    def getActiveTradeInBuyVehicleCD(self):
        raise NotImplementedError

    def setActiveTradeInBuyVehicleCD(self, value):
        raise NotImplementedError

    def getActiveTradeInBuyVehicle(self):
        raise NotImplementedError

    def getPersonalTradeInPrice(self, veh):
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

    def getYearRewardPoints(self):
        raise NotImplementedError

    def getWebOpenPageCtx(self):
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
    onSpaceUpdated = None
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

    def getQuests(self):
        raise NotImplementedError

    def isDailyQuestsRefreshAvailable(self):
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


class IManualController(IGameController):

    def isActivated(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def getBootcampRunCount(self):
        raise NotImplementedError

    def runBootcamp(self):
        raise NotImplementedError

    def countNewContent(self):
        raise NotImplementedError

    def getNewContentCount(self):
        raise NotImplementedError

    def pageFilter(self, pageType):
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
    onSeasonStateChange = None
    onBattlePassSettingsChange = None
    onFinalRewardStateChange = None
    onDeviceSelectChange = None
    onRewardSelectChange = None
    onOffersUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isVisible(self):
        raise NotImplementedError

    def isOffSeasonEnable(self):
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

    def getLevelByPoints(self, points):
        raise NotImplementedError

    def getProgressionByPoints(self, points, level):
        raise NotImplementedError

    def getCurrentLevel(self):
        raise NotImplementedError

    def getCurrentChapter(self):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def getMaxLevel(self):
        raise NotImplementedError

    def isBought(self, seasonID=None, chapter=None):
        raise NotImplementedError

    def isOfferEnabled(self):
        raise NotImplementedError

    def getOldTrophySelectTokensCount(self):
        raise NotImplementedError

    def isGameModeEnabled(self, arenaBonusType):
        raise NotImplementedError

    def getSupportedArenaBonusTypes(self):
        raise NotImplementedError

    def getOldNewDeviceSelectTokensCount(self):
        raise NotImplementedError

    def getLevelPoints(self, level):
        raise NotImplementedError

    def getFullChapterPoints(self, chapter, includeCurrent):
        raise NotImplementedError

    def isRareLevel(self, level):
        raise NotImplementedError

    def isFinalLevel(self, level):
        raise NotImplementedError

    def getSingleAward(self, level, awardType='free', needSort=True):
        raise NotImplementedError

    def getAwardsInterval(self, fromLevel, toLevel, awardType='free'):
        raise NotImplementedError

    def replaceOfferByReward(self, bonuses):
        raise NotImplementedError

    def getPackedAwardsInterval(self, fromLevel, toLevel, awardType='free'):
        raise NotImplementedError

    def isNeedToTakeReward(self, awardType, level):
        raise NotImplementedError

    def isChooseRewardEnabled(self, awardType, level):
        raise NotImplementedError

    def canChooseAnyReward(self):
        raise NotImplementedError

    def getLevelsConfig(self):
        raise NotImplementedError

    def getChapterConfig(self):
        raise NotImplementedError

    def getChapterLevelInterval(self, chapter):
        raise NotImplementedError

    def getFinalRewards(self):
        raise NotImplementedError

    def getFreeFinalRewardDict(self):
        raise NotImplementedError

    def getRewardLogic(self):
        raise NotImplementedError

    def getCurrentPoints(self):
        raise NotImplementedError

    def getMaxPoints(self):
        raise NotImplementedError

    def getLevelProgression(self):
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

    def getCapacityList(self):
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

    def getChapterByLevel(self, level):
        raise NotImplementedError

    def takeRewardForLevel(self, level):
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

    def selectMapboxBattle(self):
        raise NotImplementedError

    def getProgressionData(self):
        raise NotImplementedError

    def selectCrewbookNation(self, itemID):
        raise NotImplementedError

    def handleSurveyCompleted(self, mapName):
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

    def switchOverlay(self):
        raise NotImplementedError

    def setOverlayState(self, state):
        raise NotImplementedError

    def waitShow(self):
        raise NotImplementedError


class ISteamRegistrationOverlay(IOverlayController):

    def switchOverlay(self):
        raise NotImplementedError

    def setOverlayState(self, state):
        raise NotImplementedError

    def waitShow(self):
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
