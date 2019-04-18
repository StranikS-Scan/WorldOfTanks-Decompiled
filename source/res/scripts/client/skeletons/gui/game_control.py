# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_control.py
from Event import Event
from adisp import async, process

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

    def getTankmenDeletedBySelling(self, vehicle):
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
    pass


class IHeroTankController(IGameController):
    onUpdated = None
    onInteractive = None

    def getRandomTankCD(self):
        raise NotImplementedError

    def setInteractive(self, interactive):
        raise NotImplementedError

    def getCurrentTankCD(self):
        raise NotImplementedError

    def getCurrentTankStyleId(self):
        raise NotImplementedError

    def getCurrentRelatedURL(self):
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


class IEventsNotificationsController(IGameController):
    onEventNotificationsChanged = None

    def getEventsNotifications(self, filterFunc=None):
        raise NotImplementedError


class IAwardController(IGameController):
    pass


class IBoostersController(IGameController):
    onBoosterChangeNotify = None


class IScreenCastController(IGameController):
    pass


class IClanLockController(IGameController):
    onClanLockUpdate = None


class IVehicleComparisonBasket(IGameController):
    onChange = None
    onParametersChange = None
    onSwitchChange = None

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


class IEncyclopediaController(IGameController):
    onNewRecommendationReceived = None
    onStateChanged = None

    def isActivated(self):
        raise NotImplementedError

    def hasNewRecommendations(self):
        raise NotImplementedError

    def getRecommendations(self):
        raise NotImplementedError

    def addEncyclopediaRecommendation(self, recId):
        raise NotImplementedError

    def moveEncyclopediaRecommendationToEnd(self, recId):
        raise NotImplementedError

    def resetHasNew(self):
        raise NotImplementedError

    def buildUrl(self, callback):
        raise NotImplementedError


class IChinaController(IGameController):

    def showBrowser(self):
        raise NotImplementedError


class ITradeInController(IGameController):

    def getTradeInInfo(self, item):
        raise NotImplementedError

    def getTradeOffVehicles(self, level):
        raise NotImplementedError

    def isEnabled(self):
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


class IRankedBattlesController(IGameController, ISeasonProvider):
    onUpdated = None
    onPrimeTimeStatusUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getRank(self, rankID, vehicle=None):
        raise NotImplementedError

    def getCurrentRank(self, vehicle=None):
        raise NotImplementedError

    def getMaxRank(self, vehicle=None):
        raise NotImplementedError

    def getMaxRankForCycle(self, cycleID):
        raise NotImplementedError

    def getLastRank(self, vehicle=None):
        raise NotImplementedError

    def setLastRank(self, vehicle=None):
        raise NotImplementedError

    def setLastShields(self):
        raise NotImplementedError

    @async
    @process
    def getLeagueData(self, callback):
        raise NotImplementedError

    def getLeagueAwards(self):
        raise NotImplementedError

    def hasProgress(self):
        raise NotImplementedError

    def getAccRanksTotal(self):
        raise NotImplementedError

    def isAccountMastered(self):
        raise NotImplementedError

    def getConsolationQuest(self):
        raise NotImplementedError

    def getRanksChain(self):
        raise NotImplementedError

    def getVehicleRanksChain(self, vehicle):
        raise NotImplementedError

    def getAllRanksChain(self, vehicle=None):
        raise NotImplementedError

    def buildRanksChain(self, currentProgress, maxProgress, lastProgress):
        raise NotImplementedError

    def buildVehicleRanksChain(self, currentProgress, maxProgress, lastProgress, vehicle):
        raise NotImplementedError

    def runQuests(self, quests):
        raise NotImplementedError

    def getQuestsForCycle(self, cycleID, completedOnly=False):
        raise NotImplementedError

    def getVehicleQuestForCycle(self, cycleID):
        raise NotImplementedError

    def getVehicleMastersCount(self, cycleID):
        raise NotImplementedError

    def awardWindowShouldBeShown(self, rankChangeInfo):
        raise NotImplementedError

    @staticmethod
    def setAwardWindowShown(rankID):
        raise NotImplementedError

    def wasAwardWindowShown(self):
        raise NotImplementedError

    def getRankChangeStatus(self, changeInfo):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def getPrimeTimeStatus(self, peripheryID=None):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
        raise NotImplementedError

    def hasAnyPeripheryWithPrimeTime(self):
        raise NotImplementedError

    def openWebLeaguePage(self, ctx=None):
        raise NotImplementedError

    def getCycleRewards(self, cycleID):
        raise NotImplementedError

    def getRanksChanges(self, isLoser=False):
        pass

    def getRanksTops(self, isLoser=False, stepDiff=None):
        pass

    def getMinXp(self):
        pass

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        pass

    def getAllAwardsForCycle(self, cycleID):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def getSuitableVehicleLevels(self):
        raise NotImplementedError

    def getShieldStatus(self, rank, isStatic=False):
        raise NotImplementedError

    def getCurrentCycleStats(self):
        raise NotImplementedError

    def showRankedAwardWindow(self, rankInfo, vehicle, questsProgress):
        raise NotImplementedError

    def getLadderPoints(self):
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

    def getFirstAvailableMarathon(self):
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


class IEpicBattleMetaGameController(IGameController, ISeasonProvider):
    onUpdated = None
    onPrimeTimeStatusUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def isInPrimeTime(self):
        raise NotImplementedError

    def getPerformanceGroup(self):
        raise NotImplementedError

    def getMaxPlayerLevel(self):
        raise NotImplementedError

    def getRewardVehicles(self):
        raise NotImplementedError

    def getStageLimit(self):
        raise NotImplementedError

    def getMaxPlayerPrestigeLevel(self):
        raise NotImplementedError

    def getPointsProgressForLevel(self, level):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def getPrimeTimeStatus(self, peripheryID=None):
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

    def getCurrentCycleInfo(self):
        raise NotImplementedError

    def getCycleInfo(self, cycleID):
        raise NotImplementedError

    def getCycleOrdinalNumber(self, cycleID):
        raise NotImplementedError

    def getSeasonTimeRange(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
        raise NotImplementedError

    def isWelcomeScreenUpToDate(self, serverSettings):
        raise NotImplementedError

    def openURL(self, url=None):
        raise NotImplementedError

    def showCustomScreen(self, screen):
        raise NotImplementedError

    def getStoredEpicDiscount(self):
        return NotImplementedError


class IManualController(IGameController):

    def isActivated(self):
        raise NotImplementedError

    def clear(self):
        raise NotImplementedError

    def getBootcampRunCount(self):
        raise NotImplementedError

    def runBootcamp(self):
        raise NotImplementedError


class ICalendarController(IGameController):
    pass


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
