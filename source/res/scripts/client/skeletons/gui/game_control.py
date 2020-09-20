# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_control.py
import typing
if typing.TYPE_CHECKING:
    from Event import Event
    from gui.battle_pass.battle_pass_bonuses_helper import DeviceTokensContainer
    from gui.game_control.event_progression_controller import PlayerLevelInfo
    from gui.shared.gui_items import Vehicle, Tankman
    from gui.periodic_battles.models import PrimeTime
    from gui.prb_control.items import ValidationResult
    from gui.ranked_battles.ranked_helpers.sound_manager import RankedSoundManager
    from gui.ranked_battles.ranked_helpers.web_season_provider import WebSeasonInfo, RankedWebSeasonProvider
    from gui.ranked_battles.ranked_helpers.stats_composer import RankedBattlesStatsComposer
    from gui.ranked_battles.ranked_models import PostBattleRankInfo, Rank, Division
    from gui.ranked_battles.constants import YearAwardsNames
    from gui.shared.gui_items.fitting_item import RentalInfoProvider
    from gui.server_events.event_items import RankedQuest
    from season_common import GameSeason
    from skeletons.account_helpers.settings_core import ISettingsCache
    from gui.ranked_battles.ranked_models import BattleRankInfo
    from gui.server_events.bonuses import SimpleBonus
    from gui.shared.gui_items import ItemsCollection

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

    def hasAnySeason(self):
        raise NotImplementedError

    def getCurrentCycleID(self):
        raise NotImplementedError

    def getSeasonPassed(self):
        raise NotImplementedError

    def getClosestStateChangeTime(self):
        raise NotImplementedError

    def getPrimeTimeStatus(self, peripheryID=None):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        raise NotImplementedError

    def getTimer(self):
        raise NotImplementedError

    def getCurrentOrNextActiveCycleNumber(self, season):
        raise NotImplementedError

    def getCurrentCycleInfo(self):
        raise NotImplementedError

    def getPreviousSeason(self):
        raise NotImplementedError

    def getCurrentSeason(self):
        raise NotImplementedError

    def getNextSeason(self):
        raise NotImplementedError

    def getSeason(self, seasonID):
        raise NotImplementedError

    def isWithinSeasonTime(self, seasonID):
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


class IInternalLinksController(IGameController):

    def getURL(self, name, callback):
        raise NotImplementedError


class ISoundEventChecker(IGameController):

    def lockPlayingSounds(self):
        raise NotImplementedError

    def unlockPlayingSounds(self):
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


class ISpecialModeController(IGameController):

    def getPrimeTimes(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        raise NotImplementedError


class IRankedBattlesController(ISpecialModeController, ISeasonProvider):
    onEntitlementEvent = None
    onGameModeStatusTick = None
    onGameModeStatusUpdated = None
    onKillWebOverlays = None
    onUpdated = None
    onYearPointsChanges = None

    def isAvailable(self):
        raise NotImplementedError

    def isAccountMastered(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isFrozen(self):
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

    def hasAvailablePrimeTimeServers(self):
        raise NotImplementedError

    def hasConfiguredPrimeTimeServers(self):
        raise NotImplementedError

    def hasPrimeTimesTotalLeft(self):
        raise NotImplementedError

    def hasPrimeTimesNextDayLeft(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def hasVehicleRankedBonus(self, compactDescr):
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

    def getPrimeTimeStatus(self, peripheryID=None):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        pass

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

    def getTimer(self):
        raise NotImplementedError

    def getTotalQualificationBattles(self):
        raise NotImplementedError

    def getYearAwardsPointsMap(self):
        raise NotImplementedError

    def getYearLBSize(self):
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


class IBootcampController(IGameController):

    def isInBootcamp(self):
        raise NotImplementedError

    def startBootcamp(self, inBattle):
        raise NotImplementedError

    def stopBootcamp(self, inBattle):
        raise NotImplementedError

    @property
    def replayCtrl(self):
        raise NotImplementedError

    @property
    def nationData(self):
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

    def getCheckpoint(self):
        raise NotImplementedError

    def getSkipDialogConstants(self):
        raise NotImplementedError

    def saveCheckpoint(self, checkpoint):
        raise NotImplementedError

    @property
    def nation(self):
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


class IEventProgressionController(IGameController):
    onUpdated = None

    @property
    def isEnabled(self):
        raise NotImplementedError

    @property
    def isFrontLine(self):
        raise NotImplementedError

    @property
    def isSteelHunter(self):
        raise NotImplementedError

    @property
    def url(self):
        raise NotImplementedError

    @property
    def questPrefix(self):
        raise NotImplementedError

    @property
    def actualRewardPoints(self):
        raise NotImplementedError

    @property
    def seasonRewardPoints(self):
        raise NotImplementedError

    @property
    def maxRewardPoints(self):
        raise NotImplementedError

    @property
    def rewardPointsTokenID(self):
        raise NotImplementedError

    @property
    def rewardVehicles(self):
        raise NotImplementedError

    @property
    def questCardLevelTxtId(self):
        raise NotImplementedError

    @property
    def flagIconId(self):
        raise NotImplementedError

    @property
    def questTooltipHeaderIconId(self):
        raise NotImplementedError

    @property
    def questTooltipHeaderTxtId(self):
        raise NotImplementedError

    @property
    def selectorLabelTxtId(self):
        raise NotImplementedError

    @property
    def selectorRibbonResId(self):
        raise NotImplementedError

    @property
    def aboutEventProgressionResId(self):
        raise NotImplementedError

    @property
    def selectorData(self):
        raise NotImplementedError

    @property
    def selectorType(self):
        raise NotImplementedError

    @property
    def selectorQueueType(self):
        raise NotImplementedError

    def getProgressionXPTokenID(self):
        raise NotImplementedError

    def getCurrentModeAlias(self):
        raise NotImplementedError

    def getExchangeInfo(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def modeIsEnabled(self):
        raise NotImplementedError

    def modeIsAvailable(self):
        raise NotImplementedError

    def isActive(self):
        raise NotImplementedError

    def isDailyQuestsRefreshAvailable(self):
        raise NotImplementedError

    def getPlayerLevelInfo(self):
        raise NotImplementedError

    def getActiveQuestIDs(self):
        raise NotImplementedError

    def getActiveQuestsAsDict(self):
        pass

    def getQuestForVehicle(self, vehicle, sortByPriority, questIDs):
        raise NotImplementedError

    def isUnavailableQuestByID(self, questID):
        raise NotImplementedError

    def getUnavailableQuestMessage(self, questID):
        raise NotImplementedError

    def getRewardVehiclePrice(self, vehicleCD):
        raise NotImplementedError

    def getAllLevelAwards(self):
        raise NotImplementedError

    def getLevelAwards(self, level):
        raise NotImplementedError

    def openURL(self, url=None):
        raise NotImplementedError

    def showCustomScreen(self, screen):
        raise NotImplementedError

    def onPrimeTimeStatusUpdatedAddEvent(self, event):
        raise NotImplementedError

    def onPrimeTimeStatusUpdatedRemoveEvent(self, event):
        raise NotImplementedError

    def getTimer(self):
        raise NotImplementedError

    def isInPrimeTime(self):
        raise NotImplementedError

    def getCurrentSeason(self):
        raise NotImplementedError

    def getNextSeason(self):
        raise NotImplementedError

    def getPreviousSeason(self):
        raise NotImplementedError

    def hasAnySeason(self):
        raise NotImplementedError

    def validateSeasonData(self, seasonID, cycleID):
        raise NotImplementedError

    def getMostRelevantSeasons(self):
        raise NotImplementedError

    def getCalendarInfo(self):
        raise NotImplementedError

    def getCurrentOrNextActiveCycleNumber(self, season):
        raise NotImplementedError

    def getMaxPlayerLevel(self):
        raise NotImplementedError

    def isNeedAchieveMaxLevelForDailyQuest(self):
        raise NotImplementedError

    def getCurrentCycleInfo(self):
        raise NotImplementedError

    def getPrimeTimeTitle(self):
        raise NotImplementedError

    def getPrimeTimeBg(self):
        raise NotImplementedError

    def getPrimeTimeStatus(self, peripheryID=None):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def getPerformanceGroup(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def getCurrentCycleTimeLeft(self):
        raise NotImplementedError

    def getCurrentPrimeTimeEnd(self):
        raise NotImplementedError

    def hasPrimeTimesLeft(self):
        raise NotImplementedError

    def getStats(self):
        raise NotImplementedError

    def getPointsProgressForLevel(self, level):
        raise NotImplementedError

    def getEpicMetascreenData(self):
        raise NotImplementedError


class IEpicBattleMetaGameController(IGameController, ISeasonProvider):
    onUpdated = None
    onPrimeTimeStatusUpdated = None
    onEventEnded = None
    TOKEN_QUEST_ID = ''
    DAILY_QUEST_ID = ''
    MODE_ALIAS = ''
    PROGRESSION_XP_TOKEN = ''

    def getPerformanceGroup(self):
        raise NotImplementedError

    def getMaxPlayerLevel(self):
        raise NotImplementedError

    def getStageLimit(self):
        raise NotImplementedError

    def getMaxPlayerPrestigeLevel(self):
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

    def getAllUnlockedSkillLevels(self):
        raise NotImplementedError

    def getAllUnlockedSkillLevelsBySkillId(self):
        raise NotImplementedError

    def getUnlockedAbilityIds(self):
        raise NotImplementedError

    def getNumAbilitySlots(self, vehicleType):
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

    def isWelcomeScreenUpToDate(self, serverSettings):
        raise NotImplementedError

    def getStoredEpicDiscount(self):
        raise NotImplementedError

    def getStats(self):
        raise NotImplementedError


class IBattleRoyaleController(IGameController, ISeasonProvider):
    onUpdated = None
    onPrimeTimeStatusUpdated = None
    TOKEN_QUEST_ID = ''
    DAILY_QUEST_ID = ''
    MODE_ALIAS = ''
    PROGRESSION_XP_TOKEN = ''

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

    def isBattleRoyaleMode(self):
        raise NotImplementedError

    def isInBattleRoyaleSquad(self):
        raise NotImplementedError

    def selectRoyaleBattle(self):
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

    def getPlayerLevelInfo(self):
        raise NotImplementedError

    def getMaxPlayerLevel(self):
        raise NotImplementedError

    def getPointsProgressForLevel(self, level):
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
    onVoted = None
    onBattlePassIsBought = None
    onSeasonStateChange = None
    onUnlimitedPurchaseUnlocked = None
    onBattlePassSettingsChange = None
    onFinalRewardStateChange = None
    onOnboardingChange = None
    onDeviceSelectChange = None

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

    def isPlayerVoted(self):
        raise NotImplementedError

    def isSeasonStarted(self):
        raise NotImplementedError

    def isSeasonFinished(self):
        raise NotImplementedError

    def isSellAnyLevelsUnlocked(self):
        raise NotImplementedError

    def isValidBattleType(self, prbEntity):
        raise NotImplementedError

    def getLevelByPoints(self, points):
        raise NotImplementedError

    def getProgressionByPoints(self, points, state, level):
        raise NotImplementedError

    def getCurrentLevel(self):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def getMaxLevel(self, isBase=True):
        raise NotImplementedError

    def isBought(self, seasonID=None):
        raise NotImplementedError

    def isOnboardingActive(self):
        raise NotImplementedError

    def isChooseDeviceEnabled(self):
        raise NotImplementedError

    def getTrophySelectTokensCount(self):
        raise NotImplementedError

    def getNewDeviceSelectTokensCount(self):
        raise NotImplementedError

    def getLevelPoints(self, level, isBase=True):
        raise NotImplementedError

    def isRareLevel(self, level, isBase=True):
        raise NotImplementedError

    def getSplitFinalAwards(self):
        raise NotImplementedError

    def getFinalAwardsForPurchaseLevels(self):
        raise NotImplementedError

    def getVotingRequester(self):
        raise NotImplementedError

    def getSingleAward(self, level, awardType='free', needSort=True):
        raise NotImplementedError

    def getAwardsInterval(self, fromLevel, toLevel, awardType='free'):
        raise NotImplementedError

    def getPackedAwardsInterval(self, fromLevel, toLevel, awardType='free'):
        raise NotImplementedError

    def getAwardsList(self, awardType='free'):
        raise NotImplementedError

    def getLevelsConfig(self, isBase=True):
        raise NotImplementedError

    def getFinalRewards(self):
        raise NotImplementedError

    def getFreeFinalRewardDict(self):
        raise NotImplementedError

    def getBadgeData(self):
        raise NotImplementedError

    def getFinalRewardLogic(self):
        raise NotImplementedError

    def getCurrentPoints(self, aligned=False):
        raise NotImplementedError

    def getMaxPoints(self, isBase=True):
        raise NotImplementedError

    def getLevelProgression(self):
        raise NotImplementedError

    def getPerBattlePoints(self, vehCompDesc=None):
        raise NotImplementedError

    def isSpecialVehicle(self, intCD):
        raise NotImplementedError

    def getSpecialVehicles(self):
        raise NotImplementedError

    def getPointsDiffForVehicle(self, intCD):
        raise NotImplementedError

    def getVehicleProgression(self, intCD):
        raise NotImplementedError

    def getVehicleCapBonus(self, intCD):
        raise NotImplementedError

    def getSeasonTimeLeft(self):
        raise NotImplementedError

    def getSellAnyLevelsUnlockTimeLeft(self):
        raise NotImplementedError

    def getFinalOfferTimeLeft(self):
        raise NotImplementedError

    def getSeasonStartTime(self):
        raise NotImplementedError

    def getSeasonFinishTime(self):
        raise NotImplementedError

    def getSellAnyLevelsUnlockTime(self):
        raise NotImplementedError

    def hasMaxPointsOnVehicle(self, intCD):
        raise NotImplementedError

    def isProgressionOnVehiclePossible(self, intCD):
        raise NotImplementedError

    def isPlayerNewcomer(self):
        raise NotImplementedError

    def getSeasonID(self):
        raise NotImplementedError

    def getCapacityList(self):
        raise NotImplementedError

    def getFinalOfferTime(self):
        raise NotImplementedError

    def getMaxSoldLevelsBeforeUnlock(self):
        raise NotImplementedError

    def getBoughtLevels(self):
        raise NotImplementedError

    def getVoteOption(self):
        raise NotImplementedError

    def getPrevSeasonsStats(self):
        raise NotImplementedError

    def getLastFinishedSeasonStats(self):
        raise NotImplementedError

    def getSeasonsHistory(self):
        raise NotImplementedError

    def getAlternativeVoteOption(self):
        raise NotImplementedError

    def canPlayerParticipate(self):
        raise NotImplementedError

    def getDeviceTokensContainer(self, bonusName):
        raise NotImplementedError


class IHangarLoadingController(IGameController):
    onHangarLoadedAfterLogin = None

    def getWasInBootcamp(self):
        raise NotImplementedError

    def getConnectedAsACcount(self):
        raise NotImplementedError


class ITenYearsCountdownController(IGameController):
    onEventStateChanged = None
    onEventBlockChanged = None
    onEventMonthsChanged = None
    onActivePhasesDatesChanged = None
    onEventFinishChanged = None
    onEventDataUpdated = None
    onBlocksDataValidityChanged = None

    def isEnabled(self):
        raise NotImplementedError

    def getCurrentBlock(self):
        raise NotImplementedError

    def isCurrentBlockActive(self):
        raise NotImplementedError

    def getCurrentBlockNumber(self):
        raise NotImplementedError

    def getCurrentBlockState(self):
        raise NotImplementedError

    def getMonths(self):
        raise NotImplementedError

    def getMonth(self, blockNumber):
        raise NotImplementedError

    def getActivePhaseDates(self, blockNumber):
        raise NotImplementedError

    def getEventFinish(self):
        raise NotImplementedError

    def getBlocksCount(self):
        raise NotImplementedError

    def getEventBaseURL(self):
        raise NotImplementedError

    def isBlocksDataValid(self):
        raise NotImplementedError

    def isEventInProgress(self):
        raise NotImplementedError


class ILowTierRewardsController(IGameController):

    def isEnabled(self):
        raise NotImplementedError

    def getEventBaseURL(self):
        raise NotImplementedError

    def isRewardReady(self):
        raise NotImplementedError


class ILowTierMMController(IGameController):

    def isEnabled(self):
        raise NotImplementedError

    def getDateFinish(self):
        raise NotImplementedError


class IBobController(IGameController, ISeasonProvider):
    onPrimeTimeStatusUpdated = None
    onUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isModeActive(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
        raise NotImplementedError

    def hasAnyPeripheryWithPrimeTime(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        raise NotImplementedError

    def getPrimeTimeStatus(self, peripheryID=None):
        raise NotImplementedError

    def getSuitableVehicles(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def isSuitableVehicle(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def getCurrentRealm(self):
        raise NotImplementedError


class IBobSoundController(IGameController):
    pass
