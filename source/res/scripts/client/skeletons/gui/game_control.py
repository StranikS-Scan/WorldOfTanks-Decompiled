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

    def onLobbyStarted(self, ctx):
        pass

    def onLobbyInited(self, event):
        pass


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

    def getRandomTankCD(self):
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


class IRefSystemController(IGameController):
    onUpdated = None
    onQuestsUpdated = None
    onPlayerBecomeReferrer = None
    onPlayerBecomeReferral = None

    def getReferrers(self):
        raise NotImplementedError

    def getReferrals(self):
        raise NotImplementedError

    def getQuests(self):
        raise NotImplementedError

    def isTotallyCompleted(self):
        raise NotImplementedError

    def getPosByXPinTeam(self):
        raise NotImplementedError

    def getTotalXP(self):
        raise NotImplementedError

    def getReferralsXPPool(self):
        raise NotImplementedError

    def getAvailableReferralsCount(self):
        raise NotImplementedError

    def showTankmanAwardWindow(self, tankman, completedQuestIDs):
        raise NotImplementedError

    def showVehicleAwardWindow(self, vehicle, completedQuestIDs):
        raise NotImplementedError

    def showCreditsAwardWindow(self, creditsValue, completedQuestIDs):
        raise NotImplementedError

    def showReferrerIntroWindow(self, invitesCount):
        raise NotImplementedError

    def showReferralIntroWindow(self, nickname, isNewbie=False):
        raise NotImplementedError

    @classmethod
    def getRefPeriods(cls):
        raise NotImplementedError

    @classmethod
    def getMaxReferralXPPool(cls):
        raise NotImplementedError

    @classmethod
    def getMaxNumberOfReferrals(cls):
        raise NotImplementedError

    @classmethod
    def isReferrer(cls):
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

    def showVersionsPatchPromo(self):
        raise NotImplementedError

    def isPatchPromoAvailable(self):
        raise NotImplementedError

    def isPatchChanged(self):
        raise NotImplementedError

    def showPromo(self, url, title, forced=False, handlers=None):
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


class IRankedBattlesController(IGameController):
    onUpdated = None
    onPrimeTimeStatusUpdated = None

    def isEnabled(self):
        raise NotImplementedError

    def isFrozen(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

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


class IMarathonEventController(IGameController):
    onFlagUpdateNotify = None

    def isEnabled(self):
        raise NotImplementedError

    def isAvailable(self):
        raise NotImplementedError

    def getMarathonFlagState(self, vehicle):
        raise NotImplementedError

    def checkForWarnings(self, vehicle):
        raise NotImplementedError

    def getState(self):
        raise NotImplementedError

    def getMarathonProgress(self):
        raise NotImplementedError

    def getQuestsData(self, prefix=None, postfix=None):
        raise NotImplementedError

    def getTokensData(self, prefix=None, postfix=None):
        raise NotImplementedError

    def getMarathonQuests(self):
        raise NotImplementedError

    def getFormattedRemainingTime(self):
        raise NotImplementedError

    def getExtraDaysToBuy(self):
        raise NotImplementedError

    def isVehicleObtained(self):
        raise NotImplementedError

    def getMarathonDiscount(self):
        raise NotImplementedError

    def getURL(self, callback):
        raise NotImplementedError


class IEpicBattleMetaGameController(IGameController):
    onUpdated = None
    onPrimeTimeStatusUpdated = None

    def isAvailable(self):
        raise NotImplementedError

    def isInPrimeTime(self):
        raise NotImplementedError

    def getPerformanceGroup(self):
        raise NotImplementedError

    def getMaxPlayerLevel(self):
        raise NotImplementedError

    def getPointsProgessForLevel(self, level):
        raise NotImplementedError

    def getPrimeTimes(self):
        raise NotImplementedError

    def hasAnySeason(self):
        raise NotImplementedError

    def getPrimeTimeStatus(self, peripheryID=None):
        raise NotImplementedError

    def getPointsForLevel(self, level):
        raise NotImplementedError

    def getLevelForPoints(self, points):
        raise NotImplementedError

    def getSkillInformation(self):
        raise NotImplementedError

    def getPlayerLevelInfo(self):
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

    def getSeasonEndTime(self):
        raise NotImplementedError

    def hasSuitableVehicles(self):
        raise NotImplementedError

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        raise NotImplementedError

    def hasAvailablePrimeTimeServers(self):
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


class IFootballMetaGame(IGameController):
    onPacketsOpened = None
    onMilestoneReached = None
    onPacketsUpdated = None
    onBuffonRecruited = None

    def getGuiDataStorage(self):
        raise NotImplementedError

    def getTokenInfo(self, tokenID):
        raise NotImplementedError

    def getDecks(self):
        raise NotImplementedError

    def getPackets(self):
        raise NotImplementedError

    def getProgress(self):
        raise NotImplementedError

    def hasPackets(self):
        raise NotImplementedError

    def isBuffonAvailable(self):
        raise NotImplementedError

    def isBuffonRecruited(self):
        raise NotImplementedError

    def getMilestone(self):
        raise NotImplementedError

    def openPackets(self):
        raise NotImplementedError

    def recruitBuffon(self, vehicleIntCD):
        raise NotImplementedError
