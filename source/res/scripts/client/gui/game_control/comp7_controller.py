# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/comp7_controller.py
import logging
import itertools
from collections import namedtuple
import typing
import Event
import adisp
from comp7_ranks_common import COMP7_RATING_ENTITLEMENT, COMP7_ELITE_ENTITLEMENT, COMP7_ACTIVITY_ENTITLEMENT
from constants import Configs, RESTRICTION_TYPE, ARENA_BONUS_TYPE, COMP7_SCENE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.comp7.shared import Comp7AlertData
from gui.event_boards.event_boards_items import Comp7LeaderBoard
from gui.prb_control import prb_getters
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, FUNCTIONAL_FLAG
from gui.shared import event_dispatcher
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, TimerNotifier, SimpleNotifier
from helpers import dependency
from helpers import int2roman
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import ONE_SECOND, getTimeDeltaFromNow, getServerUTCTime
from items import vehicles
from season_provider import SeasonProvider
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IComp7Controller, IHangarSpaceSwitchController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from helpers.server_settings import Comp7Config
    from items.artefacts import Equipment

class Comp7Controller(Notifiable, SeasonProvider, IComp7Controller, IGlobalListener):
    _ALERT_DATA_CLASS = Comp7AlertData
    __ENTITLEMENTS = {COMP7_RATING_ENTITLEMENT, COMP7_ELITE_ENTITLEMENT, COMP7_ACTIVITY_ENTITLEMENT}
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __hangarsSpace = dependency.descriptor(IHangarSpace)

    def __init__(self):
        super(Comp7Controller, self).__init__()
        self.__serverSettings = None
        self.__comp7Config = None
        self.__roleEquipmentsCache = None
        self.__viewData = {}
        self.__isOffline = False
        self.__rating = 0
        self.__isElite = False
        self.__activityPoints = 0
        self.__banTimer = CallbackDelayer()
        self.__banExpiryTime = None
        self.__leaderboardDataProvider = _LeaderboardDataProvider()
        self.onStatusUpdated = Event.Event()
        self.onStatusTick = Event.Event()
        self.onRankUpdated = Event.Event()
        self.onComp7ConfigChanged = Event.Event()
        self.onComp7RanksConfigChanged = Event.Event()
        self.onBanUpdated = Event.Event()
        self.onOfflineStatusUpdated = Event.Event()
        return

    @property
    def __roleEquipments(self):
        if self.__roleEquipmentsCache is None:
            equipmentsCache = vehicles.g_cache.equipments()
            roleEquipmentsConfig = self.getModeSettings().roleEquipments
            self.__roleEquipmentsCache = {role:equipmentsCache[equipmentConfig['equipmentID']] for role, equipmentConfig in roleEquipmentsConfig.iteritems() if equipmentConfig['equipmentID'] is not None}
        return self.__roleEquipmentsCache

    @property
    def rating(self):
        return self.__rating

    @property
    def isElite(self):
        return self.__isElite

    @property
    def activityPoints(self):
        return self.__activityPoints

    @property
    def isBanned(self):
        return self.banDuration > 0

    @property
    def banDuration(self):
        return max(0, getTimeDeltaFromNow(self.__banExpiryTime)) if self.__banExpiryTime is not None else 0

    @property
    def isOffline(self):
        return self.__isOffline

    @property
    def leaderboard(self):
        return self.__leaderboardDataProvider

    def init(self):
        super(Comp7Controller, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(TimerNotifier(self.getTimer, self.__timerTick))
        g_clientUpdateManager.addCallbacks({'cache.entitlements': self.__onEntitlementsChanged,
         'cache.comp7.isOnline': self.__onOfflineStatusChanged,
         'stats.restrictions': self.__onRestrictionsChanged})

    def fini(self):
        self.clearNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.onStatusUpdated.clear()
        self.onStatusTick.clear()
        self.__viewData = None
        self.__banTimer.clearCallbacks()
        self.__banTimer = None
        super(Comp7Controller, self).fini()
        return

    def onAccountBecomePlayer(self):
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onAccountBecomeNonPlayer(self):
        self.stopNotification()

    def onAvatarBecomePlayer(self):
        if self.__serverSettings is None:
            self.__lobbyContext.onServerSettingsChanged += self.__onServerSettingsChanged
        return

    def onConnected(self):
        self.__itemsCache.onSyncCompleted += self.__onItemsSyncCompleted
        self.__spaceSwitchController.onCheckSceneChange += self.__onCheckSceneChange

    def onDisconnected(self):
        self.stopNotification()
        self.__itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateComp7Settings
        self.__serverSettings = None
        self.__comp7Config = None
        self.__roleEquipmentsCache = None
        self.__viewData = {}
        self.__rating = 0
        self.__isElite = False
        self.__banTimer.clearCallbacks()
        self.__banExpiryTime = None
        self.stopGlobalListening()
        return

    def onLobbyInited(self, event):
        self.startNotification()
        self.startGlobalListening()

    def getModeSettings(self):
        return self.__comp7Config

    def isEnabled(self):
        return self.__comp7Config.isEnabled

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen() and self.getCurrentSeason() is not None

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def getRoleEquipment(self, roleName):
        return self.__roleEquipments.get(roleName)

    def isSuitableVehicle(self, vehicle):
        ctx = {}
        restriction = None
        config = self.__serverSettings.comp7Config
        if vehicle.compactDescr in config.forbiddenVehTypes:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_TYPE
            ctx = {'forbiddenType': vehicle.shortUserName}
        if vehicle.type in config.forbiddenClassTags:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_VEHICLE_CLASS
            ctx = {'forbiddenClass': vehicle.type}
        if vehicle.level not in config.levels:
            restriction = PRE_QUEUE_RESTRICTION.LIMIT_LEVEL
            ctx = {'levels': config.levels}
        return ValidationResult(False, restriction, ctx) if restriction is not None else None

    def getViewData(self, viewAlias):
        return self.__viewData.setdefault(viewAlias, {})

    def hasSuitableVehicles(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.INVENTORY)
        v = self.__itemsCache.items.getVehicles(criteria)
        return len(v) > 0

    def vehicleIsAvailableForBuy(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.UNLOCKED)
        criteria |= ~REQ_CRITERIA.VEHICLE.SECRET | ~REQ_CRITERIA.HIDDEN
        vUnlocked = self.__itemsCache.items.getVehicles(criteria)
        return len(vUnlocked) > 0

    def vehicleIsAvailableForRestore(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.VEHICLE.IS_RESTORE_POSSIBLE)
        vRestorePossible = self.__itemsCache.items.getVehicles(criteria)
        return len(vRestorePossible) > 0

    def hasPlayableVehicle(self):
        criteria = self.__filterEnabledVehiclesCriteria(REQ_CRITERIA.INVENTORY)
        criteria |= ~REQ_CRITERIA.VEHICLE.EXPIRED_RENT
        v = self.__itemsCache.items.getVehicles(criteria)
        return len(v) > 0

    def getAlertBlock(self):
        if self.isOffline:
            visible = True
            buttonCallback = None
        elif self.isBanned:
            visible = True
            buttonCallback = None
        elif not self.hasSuitableVehicles():
            visible = True
            buttonCallback = event_dispatcher.showComp7NoVehiclesScreen
        else:
            visible = not self.isInPrimeTime() and self.isEnabled()
            buttonCallback = event_dispatcher.showComp7PrimeTimeWindow
        alertData = None
        if visible:
            alertData = self._getAlertBlockData()
        return (buttonCallback, alertData or self._ALERT_DATA_CLASS(), visible and alertData is not None)

    def isComp7PrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.COMP7)

    def getPlatoonRatingRestriction(self):
        unitMgr = prb_getters.getClientUnitMgr()
        return self.__comp7Config.squadRatingRestriction.get(unitMgr.unit.getSquadSize(), 0) if unitMgr is not None and unitMgr.unit is not None else 0

    def _getAlertBlockData(self):
        if self.isOffline:
            return self._ALERT_DATA_CLASS.constructForOffline()
        if self.isBanned:
            return self._ALERT_DATA_CLASS.constructForBan(duration=self.banDuration)
        if not self.hasSuitableVehicles():
            config = self.getModeSettings()
            romanLevels = list(map(int2roman, config.levels))
            vehicleLevelsStr = ', '.join(romanLevels)
            return self._ALERT_DATA_CLASS.constructForVehicle(levelsStr=vehicleLevelsStr, vehicleIsAvailableForBuy=self.vehicleIsAvailableForBuy(), vehicleIsAvailableForRestore=self.vehicleIsAvailableForRestore())
        return super(Comp7Controller, self)._getAlertBlockData()

    def __onCheckSceneChange(self):
        if self.isComp7PrbActive():
            self.__spaceSwitchController.hangarSpaceUpdate(COMP7_SCENE)

    def __updateArenaBans(self):
        arenaBans = self.__itemsCache.items.stats.restrictions.get(RESTRICTION_TYPE.ARENA_BAN, {})
        comp7Bans = tuple((b for b in arenaBans.itervalues() if ARENA_BONUS_TYPE.COMP7 in b.get('bonusTypes', ())))
        if comp7Bans:
            ban = max(comp7Bans, key=lambda b: b.get('expiryTime', 0))
            expiryTime = ban['expiryTime']
            duration = getTimeDeltaFromNow(expiryTime)
            if duration <= 0:
                expiryTime = None
            else:
                self.__banTimer.delayCallback(duration + ONE_SECOND, self.__updateArenaBans)
        else:
            expiryTime = None
        if self.__banExpiryTime != expiryTime:
            self.__banExpiryTime = expiryTime
            self.onBanUpdated()
        return

    def __onRestrictionsChanged(self, _):
        self.__updateArenaBans()

    def __comp7Criteria(self, vehicle):
        return self.isSuitableVehicle(vehicle) is None

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onStatusUpdated(status)

    def __timerTick(self):
        self.onStatusTick()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateComp7Settings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__onUpdateComp7Settings
        self.__comp7Config = self.__serverSettings.comp7Config
        self.__roleEquipmentsCache = None
        return

    def __onUpdateComp7Settings(self, diff):
        if Configs.COMP7_CONFIG.value in diff:
            self.__comp7Config = self.__serverSettings.comp7Config
            self.__roleEquipmentsCache = None
            self.__resetTimer()
            self.onComp7ConfigChanged()
        if Configs.COMP7_PRESTIGE_RANKS_CONFIG.value in diff:
            self.onComp7RanksConfigChanged()
        return

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()

    def __filterEnabledVehiclesCriteria(self, criteria):
        criteria = criteria | REQ_CRITERIA.CUSTOM(self.__comp7Criteria)
        return criteria

    def __onItemsSyncCompleted(self, *_):
        self.__updateRank()
        self.__updateArenaBans()
        self.__updateOfflineStatus()

    def __onEntitlementsChanged(self, entitlements):
        if self.__ENTITLEMENTS & set(entitlements.keys()):
            self.__updateRank()

    def __updateRank(self):
        entitlements = self.__itemsCache.items.stats.entitlements
        self.__rating = entitlements.get(COMP7_RATING_ENTITLEMENT, 0)
        self.__isElite = bool(entitlements.get(COMP7_ELITE_ENTITLEMENT))
        self.__activityPoints = entitlements.get(COMP7_ACTIVITY_ENTITLEMENT, 0)
        self.onRankUpdated(self.__rating, self.__isElite)

    def __onOfflineStatusChanged(self, _):
        self.__updateOfflineStatus()

    def __updateOfflineStatus(self):
        isOffline = not self.__itemsCache.items.stats.comp7.get('isOnline', False)
        if self.__isOffline != isOffline:
            self.__isOffline = isOffline
            self.onOfflineStatusUpdated()


class _LeaderboardDataProvider(object):
    __EVENT_ID = 'comp7'
    __LEADERBOARD_ID = 0
    __FIRST_PAGE_ID = 0
    __MASTER_RANK_ID = 5
    __eventsController = dependency.descriptor(IEventBoardController)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _OwnData = namedtuple('_OwnData', 'isSuccess, position, points, battlesCount')

    def __init__(self):
        self.__lastUpdateTimestamp = 0
        self.__nextUpdateTimestamp = None
        self.__pageSize = 0
        self.__recordsCount = 0
        self.__eliteRankPositionThreshold = None
        self.__eliteRankPointsThreshold = None
        self.__cachedPages = {}
        return

    def getEliteRankPercent(self):
        return self.__getRanksConfig().eliteRankPercent

    def getMinimumPointsNeeded(self):
        divisions = [ d for d in self.__getRanksConfig().divisions if d.rank == self.__MASTER_RANK_ID ]
        return min((division.range.begin for division in divisions))

    @adisp.adisp_async
    @adisp.adisp_process
    def getRecordsCount(self, callback):
        isSuccess = yield self.__invalidateMetaData()
        callback((self.__recordsCount, isSuccess))

    @adisp.adisp_async
    @adisp.adisp_process
    def getLastElitePosition(self, callback):
        isSuccess = yield self.__invalidateMetaData()
        callback((self.__eliteRankPositionThreshold, isSuccess))

    @adisp.adisp_async
    @adisp.adisp_process
    def getLastEliteRating(self, callback):
        isSuccess = yield self.__invalidateMetaData()
        callback((self.__eliteRankPointsThreshold, isSuccess))

    @adisp.adisp_async
    @adisp.adisp_process
    def getOwnData(self, callback):
        myInfo = yield self.__eventsController.getMyLeaderboardInfo(self.__EVENT_ID, self.__LEADERBOARD_ID, showNotification=False)
        if myInfo is not None:
            position = myInfo.getRank()
            if position is not None:
                yield self.__invalidateMetaData()
                if position > self.__recordsCount:
                    position = None
            callback(self._OwnData(True, position, myInfo.getP2(), myInfo.getBattlesCount()))
        else:
            callback(self._OwnData(False, None, None, None))
        return

    @adisp.adisp_async
    @adisp.adisp_process
    def getLastUpdateTime(self, callback):
        isSuccess = yield self.__invalidateMetaData()
        callback((self.__lastUpdateTimestamp, isSuccess))

    @adisp.adisp_async
    @adisp.adisp_process
    def getTableRecords(self, limit, offset, callback=None):
        if not self.__pageSize:
            yield self.__loadPageSize()
            if not self.__pageSize:
                _logger.error('Something went wrong during requesting comp7 leaderboard page: invalid page size')
                callback(None)
                return
        (startPage, endPage), (startRecord, endRecord) = self.__getRanges(limit, offset, self.__pageSize)
        pageIDs = range(startPage, endPage + 1)
        result = yield self.__requestPages(pageIDs)
        if result:
            records = list(itertools.chain.from_iterable((self.__cachedPages.get(pID, ()) for pID in pageIDs)))
            records = records[startRecord:endRecord + 1]
        else:
            records = None
        callback(records)
        return

    def flushTableRecords(self):
        self.__cachedPages.clear()

    @adisp.adisp_async
    @adisp.adisp_process
    def __invalidateMetaData(self, callback):
        result = True
        if self.__nextUpdateTimestamp is None or getServerUTCTime() > self.__nextUpdateTimestamp:
            result = yield self.__requestPages([self.__FIRST_PAGE_ID])
        callback(result)
        return

    @adisp.adisp_async
    @adisp.adisp_process
    def __requestPages(self, pageIDs, callback=None):
        if self.__nextUpdateTimestamp and self.__nextUpdateTimestamp <= getServerUTCTime():
            self.__clearCache()
        if not self.__eventsController.hasEvents():
            _logger.debug('Empty events on controller while requesting pages. Reloading.')
            yield self.__eventsController.getEvents(onlySettings=True)
        for pageID in self.__getPagesToLoad(pageIDs):
            page = yield self.__eventsController.getLeaderboard(self.__EVENT_ID, self.__LEADERBOARD_ID, pageID + 1, leaderBoardClass=Comp7LeaderBoard, showNotification=False)
            if page is None:
                result = False
                break
            updateTimestamp = page.getLastLeaderboardRecalculationTS()
            if updateTimestamp > self.__lastUpdateTimestamp:
                self.__clearCache()
                self.__lastUpdateTimestamp = updateTimestamp
                self.__nextUpdateTimestamp = page.getNextLeaderboardRecalculationTS()
                self.__eliteRankPositionThreshold = page.getLastEliteUserPosition()
                self.__eliteRankPointsThreshold = page.getLastEliteUserRating()
                self.__recordsCount = page.getRecordsCount()
            self.__cachedPages[pageID] = page.getExcelItems()
        else:
            result = True

        callback(result)
        return

    def __getPagesToLoad(self, pageIDs):
        reqiredSet = set(pageIDs)
        while not reqiredSet.issubset(set(self.__cachedPages.keys())):
            yield (reqiredSet - set(self.__cachedPages.keys())).pop()

    @adisp.adisp_async
    @adisp.adisp_process
    def __loadPageSize(self, callback):
        if not self.__eventsController.hasEvents():
            yield self.__eventsController.getEvents(onlySettings=True)
        eventSettings = self.__eventsController.getEventsSettingsData()
        if eventSettings and eventSettings.getEvent(self.__EVENT_ID):
            self.__pageSize = eventSettings.getEvent(self.__EVENT_ID).getPageSize()
        else:
            self.__pageSize = 0
        callback(None)
        return

    def __clearCache(self):
        self.__lastUpdateTimestamp = 0
        self.__eliteRankPositionThreshold = None
        self.__eliteRankPointsThreshold = None
        self.__masterRankPositionThreshold = None
        self.__cachedPages.clear()
        return

    def __getRanksConfig(self):
        return self.__lobbyContext.getServerSettings().comp7PrestigeRanksConfig

    @staticmethod
    def __getRanges(limit, offset, pageSize):
        startPage, startRecord = divmod(offset, pageSize)
        endPage = (offset + limit - 1) // pageSize
        endRecord = startRecord + limit - 1
        return ((startPage, endPage), (startRecord, endRecord))
