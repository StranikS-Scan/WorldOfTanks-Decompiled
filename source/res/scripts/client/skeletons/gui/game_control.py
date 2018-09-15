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


class IServerStatsController(IGameController):
    """Controller holds last statistic containing number of player on server and region,
    fires event when new statistics is received from server."""
    onStatsReceived = None

    def getFormattedStats(self):
        """Gets server stats that are formatted as a single string with applied GUI style.
        :return: tuple containing string with stats and type of tooltip (one of STATS_TYPE.*).
        """
        raise NotImplementedError

    def getStats(self):
        """Gets server stats separately for cluster and region without GUI style.
        :return: tuple containing formatted number of players on cluster,
            formatted number of players on region and type of tooltip (one of STATS_TYPE.*).
        """
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


class IFalloutController(IGameController):
    onSettingsChanged = None
    onAutomatchChanged = None
    onVehiclesChanged = None

    def isAvailable(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isSelected(self):
        raise NotImplementedError

    def setEnabled(self, isEnabled):
        raise NotImplementedError

    def getBattleType(self):
        raise NotImplementedError

    def setBattleType(self, battleType):
        raise NotImplementedError

    def getSelectedVehicles(self):
        raise NotImplementedError

    def addSelectedVehicle(self, vehInvID):
        raise NotImplementedError

    def removeSelectedVehicle(self, vehInvID):
        raise NotImplementedError

    def moveSelectedVehicle(self, vehInvID):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def getSelectedSlots(self):
        raise NotImplementedError

    def getEmptySlots(self):
        raise NotImplementedError

    def getRequiredSlots(self):
        raise NotImplementedError

    def canSelectVehicle(self, vehicle):
        raise NotImplementedError

    def mustSelectRequiredVehicle(self):
        raise NotImplementedError

    def requiredVehicleSelected(self):
        raise NotImplementedError

    def carouselSelectionButtonTooltip(self):
        raise NotImplementedError

    def canChangeBattleType(self):
        raise NotImplementedError

    def canAutomatch(self):
        raise NotImplementedError

    def isAutomatch(self):
        raise NotImplementedError

    def setAutomatch(self, isAutomatch):
        raise NotImplementedError

    def isSuitableVeh(self, vehicle):
        raise NotImplementedError


class IEventBattlesController(IGameController):
    onSettingsChanged = None
    onVehicleChanged = None
    onSquadStatusChanged = None

    def isAvailable(self):
        raise NotImplementedError

    def isEnabled(self):
        raise NotImplementedError

    def isSelected(self):
        raise NotImplementedError

    def setEnabled(self, isEnabled):
        raise NotImplementedError

    def getBattleType(self):
        raise NotImplementedError

    def setBattleType(self, battleType):
        raise NotImplementedError

    def getSelectedVehicle(self):
        raise NotImplementedError

    def getConfig(self):
        raise NotImplementedError

    def carouselSelectionButtonTooltip(self):
        raise NotImplementedError

    def canChangeBattleType(self):
        raise NotImplementedError

    def isSuitableVeh(self, vehicle):
        raise NotImplementedError


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
        raise NotImplemented


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

    def runQuest(self, quest):
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

    def hasAnyPeripheryWithPrimeTime(self):
        raise NotImplementedError

    def openWebLeaguePage(self, ctx=None):
        raise NotImplementedError

    def getPrevRanks(self, accRank, vehRank, rankChange):
        raise NotImplementedError

    def getCycleRewards(self, cycleID):
        """
        returns reward for max rank achieved in current season for given cycle ID
        """
        raise NotImplementedError

    def getRanksChanges(self, isLoser=False):
        """
        returns ranks changes depends on team match result (win or lose)
        """
        pass

    def getRanksTops(self, isLoser=False, earned=False, notRecieved=False, lost=False):
        """
        returns ranks changes top values depends on team match result (win or lose)
        """
        pass

    def getMinXp(self):
        """
        returns minXP value
        """
        pass

    def getPrimeTimesForDay(self, selectedTime, groupIdentical=False):
        """
        :return: dict, contains prime times in day based on periphery id
        (peripheries are keys, primes are values)
        :param groupIdentical: grouping peripheries with identical prime times in one key (exmp. 'RU1, RU2' etc.)
        :param selectedTime: returns prime times for this day
        """
        pass

    def getAllAwardsForCycle(self, cycleID):
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

    @property
    def nation(self):
        raise NotImplementedError

    def getDefaultLobbySettings(self):
        raise NotImplementedError

    def getLobbySettings(self):
        raise NotImplementedError

    def setLobbySettings(self, value):
        raise NotImplementedError

    def updateLobbySettingsVisibility(self, element, value):
        raise NotImplementedError

    def getDisabledSettings(self):
        raise NotImplementedError


class ICalendarController(IGameController):
    pass
