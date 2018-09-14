# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/game_control.py
from Event import Event

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


class IExternalLinksController(IGameController):

    def open(self, url):
        raise NotImplementedError

    def getURL(self, name, callback):
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

    def load(self, url=None, title=None, showActionBtn=True, showWaiting=True, browserID=None, isAsync=False, browserSize=None, isDefault=True, callback=None, showCloseBtn=False, useBrowserWindow=True, isModal=False, showCreateWaiting=False, handlers=None, showBrowserCallback=None):
        raise NotImplementedError

    def getBrowser(self, browserID):
        raise NotImplementedError

    def delBrowser(self, browserID):
        raise NotImplementedError


class IPromoController(IGameController):

    def showCurrentVersionPatchPromo(self, isAsync=False):
        raise NotImplementedError

    def showVersionsPatchPromo(self):
        raise NotImplementedError

    def isPatchPromoAvailable(self):
        raise NotImplementedError

    def isPatchChanged(self):
        raise NotImplementedError

    def showPromo(self, url, title):
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

    def addVehicle(self, vehicleCompactDesr, initParameters):
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
