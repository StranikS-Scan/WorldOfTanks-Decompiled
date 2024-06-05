# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/comp7_controller.py
import itertools
import logging
import time
from collections import namedtuple
import adisp
import typing
import Event
from Event import EventManager
from comp7_common import Comp7QualificationState, SEASON_POINTS_ENTITLEMENTS, qualificationTokenBySeasonNumber, ratingEntNameBySeasonNumber, eliteRankEntNameBySeasonNumber, activityPointsEntNameBySeasonNumber, maxRankEntNameBySeasonNumber, COMP7_YEARLY_REWARD_TOKEN, COMP7_OFFER_PREFIX, COMP7_OFFER_GIFT_PREFIX
from constants import Configs, RESTRICTION_TYPE, ARENA_BONUS_TYPE, COMP7_SCENE
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.Scaleform.daapi.view.lobby.comp7.shared import Comp7AlertData
from gui.comp7.entitlements_cache import EntitlementsCache
from gui.event_boards.event_boards_items import Comp7LeaderBoard
from gui.impl.lobby.comp7.comp7_gui_helpers import isSeasonStasticsShouldBeShown
from gui.prb_control import prb_getters
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.items import ValidationResult
from gui.prb_control.settings import PRE_QUEUE_RESTRICTION, FUNCTIONAL_FLAG
from gui.shared import event_dispatcher
from gui.shared.gui_items.Vehicle import Vehicle
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, TimerNotifier, SimpleNotifier, PeriodicNotifier
from helpers import dependency, time_utils
from helpers import int2roman
from helpers.CallbackDelayer import CallbackDelayer
from helpers.time_utils import ONE_SECOND, getTimeDeltaFromNow, getServerUTCTime, getCurrentTimestamp
from items import vehicles
from season_provider import SeasonProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.event_boards_controllers import IEventBoardController
from skeletons.gui.game_control import IComp7Controller, IHangarSpaceSwitchController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)
if typing.TYPE_CHECKING:
    from helpers.server_settings import Comp7Config
    from items.artefacts import Equipment

class Comp7Controller(Notifiable, SeasonProvider, IComp7Controller, IGlobalListener):
    _ALERT_DATA_CLASS = Comp7AlertData
    __SEASON_ENTITLEMENT_NAME_FACTORIES = {ratingEntNameBySeasonNumber, eliteRankEntNameBySeasonNumber, activityPointsEntNameBySeasonNumber}
    __STATS_SEASONS_KEYS = ('1', '2', '3')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __spaceSwitchController = dependency.descriptor(IHangarSpaceSwitchController)
    __settingsCore = dependency.descriptor(ISettingsCore)

    def __init__(self):
        super(Comp7Controller, self).__init__()
        self.__serverSettings = None
        self.__comp7Config = None
        self.__comp7RanksConfig = None
        self.__roleEquipmentsCache = None
        self.__viewData = {}
        self.__isOffline = False
        self.__qualificationBattlesStatuses = []
        self.__qualificationState = None
        self.__rating = 0
        self.__isElite = False
        self.__activityPoints = 0
        self.__banTimer = CallbackDelayer()
        self.__banExpiryTime = None
        self.__isYearlyRewardsAnimationSeen = False
        self.__entitlementsCache = EntitlementsCache()
        self.__leaderboardDataProvider = _LeaderboardDataProvider()
        self.__isTournamentBannerEnabled = None
        self.__eventsManager = em = EventManager()
        self.onStatusUpdated = Event.Event(em)
        self.onStatusTick = Event.Event(em)
        self.onRankUpdated = Event.Event(em)
        self.onComp7ConfigChanged = Event.Event(em)
        self.onComp7RanksConfigChanged = Event.Event(em)
        self.onBanUpdated = Event.Event(em)
        self.onOfflineStatusUpdated = Event.Event(em)
        self.onQualificationBattlesUpdated = Event.Event(em)
        self.onQualificationStateUpdated = Event.Event(em)
        self.onSeasonPointsUpdated = Event.Event(em)
        self.onComp7RewardsConfigChanged = Event.Event(em)
        self.onHighestRankAchieved = Event.Event(em)
        self.onEntitlementsUpdated = Event.Event(em)
        self.onTournamentBannerStateChanged = Event.Event(em)
        return

    @property
    def __roleEquipments(self):
        if not self.__roleEquipmentsCache:
            self.__roleEquipmentsCache = {}
            equipmentsCache = vehicles.g_cache.equipments()
            roleEquipmentsConfig = self.getModeSettings().roleEquipments
            for role, equipmentConfig in roleEquipmentsConfig.iteritems():
                if equipmentConfig['equipmentID'] is not None:
                    startCharge = equipmentConfig['startCharge']
                    startLevel = len([ levelCost for levelCost in equipmentConfig['cost'] if levelCost <= startCharge ])
                    self.__roleEquipmentsCache[role] = {'item': equipmentsCache[equipmentConfig['equipmentID']],
                     'startLevel': startLevel}

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

    @property
    def battleModifiers(self):
        return self.getModeSettings().battleModifiersDescr

    @property
    def qualificationBattlesNumber(self):
        return self.getModeSettings().qualification.battlesNumber

    @property
    def qualificationBattlesStatuses(self):
        return self.__qualificationBattlesStatuses

    @property
    def qualificationState(self):
        return self.__qualificationState

    @property
    def isTournamentBannerEnabled(self):
        if self.__isTournamentBannerEnabled is None:
            self.__isTournamentBannerEnabled = self.getTournamentBannerAvailability()
        return self.__isTournamentBannerEnabled

    @property
    def remainingOfferTokensNotifications(self):
        return self.getModeSettings().remainingOfferTokensNotifications

    def init(self):
        super(Comp7Controller, self).init()
        self.addNotificator(SimpleNotifier(self.getTimer, self.__timerUpdate))
        self.addNotificator(TimerNotifier(self.getTimer, self.__timerTick))
        g_clientUpdateManager.addCallbacks({'cache.entitlements': self.__onEntitlementsChanged,
         'cache.comp7.isOnline': self.__onOfflineStatusChanged,
         'stats.restrictions': self.__onRestrictionsChanged,
         'cache.comp7.qualification.battles': self.__onQualificationBattlesChanged,
         'cache.comp7.qualification.state': self.__onQualificationStateChanged})

    def fini(self):
        self.clearNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        self.__eventsManager.clear()
        self.__viewData = None
        self.__qualificationBattlesStatuses = None
        self.__qualificationState = None
        self.__banTimer.clearCallbacks()
        self.__banTimer = None
        self.__entitlementsCache.clear()
        self.__entitlementsCache = None
        super(Comp7Controller, self).fini()
        return

    def onAccountBecomePlayer(self):
        settings = self.__lobbyContext.getServerSettings().getSettings()
        if not settings:
            return
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
        self.addNotificator(PeriodicNotifier(lambda : time_utils.ONE_MINUTE, self.__updateTournamentBannerState, periods=(time_utils.ONE_MINUTE,)))

    def onDisconnected(self):
        self.stopNotification()
        self.__itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted
        self.__lobbyContext.onServerSettingsChanged -= self.__onServerSettingsChanged
        self.__spaceSwitchController.onCheckSceneChange -= self.__onCheckSceneChange
        self.__entitlementsCache.reset()
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__onUpdateComp7Settings
        self.__serverSettings = None
        self.__comp7Config = None
        self.__comp7RanksConfig = None
        self.__roleEquipmentsCache = None
        self.__viewData = {}
        self.__rating = 0
        self.__isElite = False
        self.__banTimer.clearCallbacks()
        self.__banExpiryTime = None
        self.__isYearlyRewardsAnimationSeen = False
        self.stopGlobalListening()
        return

    def onLobbyInited(self, event):
        self.startNotification()
        self.startGlobalListening()

    @adisp.adisp_process
    def onPrbEntitySwitched(self):
        result = yield self.updateEntitlementsCache()
        self.__onEntitlementsCacheUpdated(result)

    def getModeSettings(self):
        return self.__comp7Config

    def isEnabled(self):
        return self.__comp7Config is not None and self.__comp7Config.isEnabled and self.__isRanksConfigAvailable()

    def isAvailable(self):
        return self.isEnabled() and not self.isFrozen()

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def isTrainingEnabled(self):
        return self.__comp7Config is not None and self.__comp7Config.isTrainingEnabled

    def hasActiveSeason(self):
        return self.isAvailable() and self.getCurrentSeason() is not None

    def getActualSeasonNumber(self):
        season = self.getCurrentSeason() or self.getPreviousSeason()
        return season.getNumber() if season else None

    def isQualificationActive(self):
        return Comp7QualificationState.isQualificationActive(self.__qualificationState)

    def isQualificationResultsProcessing(self):
        return Comp7QualificationState.isResultsProcessing(self.__qualificationState)

    def isQualificationCalculationRating(self):
        return Comp7QualificationState.isCalculationQualificationRating(self.__qualificationState)

    def isQualificationSquadAllowed(self):
        return Comp7QualificationState.isUnitAllowed(self.__qualificationState)

    def isYearlyRewardsAnimationSeen(self):
        return self.__isYearlyRewardsAnimationSeen

    def getRoleEquipment(self, roleName):
        return self.__roleEquipments.get(roleName, {}).get('item')

    def getEquipmentStartLevel(self, roleName):
        return self.__roleEquipments.get(roleName, {}).get('startLevel')

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

    def isBattleModifiersAvailable(self):
        return len(self.battleModifiers) > 0

    def getPlatoonRatingRestriction(self):
        unitMgr = prb_getters.getClientUnitMgr()
        return self.__comp7Config.squadRatingRestriction.get(unitMgr.unit.getSquadSize(), 0) if unitMgr is not None and unitMgr.unit is not None else 0

    def getStatsSeasonsKeys(self):
        return self.__STATS_SEASONS_KEYS

    def getReceivedSeasonPoints(self):
        return {entCode:self.__getEntitlementCount(entCode) for entCode in SEASON_POINTS_ENTITLEMENTS}

    def getMaxAvailableSeasonPoints(self):
        return len(self.__comp7RanksConfig.ranks)

    def isYearlyRewardReceived(self):
        return self.__itemsCache.items.tokens.getTokens().get(COMP7_YEARLY_REWARD_TOKEN, 0) > 0

    def getRatingForSeason(self, seasonNumber):
        return self.__getEntitlementCount(ratingEntNameBySeasonNumber(str(seasonNumber)))

    def getMaxRankNumberForSeason(self, seasonNumber=None):
        seasonNumber = seasonNumber or self.getActualSeasonNumber()
        return self.__getEntitlementCount(maxRankEntNameBySeasonNumber(str(seasonNumber)))

    def isEliteForSeason(self, seasonNumber=None):
        seasonNumber = seasonNumber or self.getActualSeasonNumber()
        return bool(self.__getEntitlementCount(eliteRankEntNameBySeasonNumber(str(seasonNumber))))

    def getTournamentBannerAvailability(self):
        isBannedEnabled = self.getModeSettings().tournaments['isBannerEnabled']
        if not isBannedEnabled:
            return False
        bannerData = self.getTournamentBannerData()
        if not bannerData:
            return False
        currentTime = getCurrentTimestamp()
        startTime = bannerData['startTime']
        endTime = bannerData['endTime']
        return startTime <= currentTime <= endTime

    def getTournamentBannerData(self):
        banners = self.getModeSettings().tournaments.get('widgets')
        if not banners:
            return None
        else:
            currentTime = time.time()
            for banner in banners:
                startBannerTime = banner['startTime']
                endBannerTime = banner['endTime']
                if startBannerTime <= currentTime <= endBannerTime:
                    return banner

            return None

    def setYearlyRewardsAnimationSeen(self):
        self.__isYearlyRewardsAnimationSeen = True

    def getYearlyRewards(self):
        return self.__lobbyContext.getServerSettings().comp7RewardsConfig

    def isQualificationPassedInSeason(self, seasonNumber):
        qualificationToken = qualificationTokenBySeasonNumber(seasonNumber)
        return self.__itemsCache.items.tokens.getTokens().get(qualificationToken, 0) > 0

    def isComp7OfferToken(self, tokenName):
        return tokenName.startswith(COMP7_OFFER_PREFIX)

    def isComp7OfferGiftToken(self, tokenName):
        return tokenName.startswith(COMP7_OFFER_GIFT_PREFIX)

    def hasAvailableOfferTokens(self):
        tokens = self.__itemsCache.items.tokens.getTokens()
        return any((amount > 0 and self.isComp7OfferGiftToken(name) for name, amount in tokens.iteritems()))

    @adisp.adisp_async
    @adisp.adisp_process
    def updateEntitlementsCache(self, force=False, retryTimes=None, callback=None):
        if self.isComp7PrbActive() and self.__entitlementsCache.isExpired() or force:
            result = yield self.__entitlementsCache.update(retryTimes)
            callback(result)

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

    def __isRanksConfigAvailable(self):
        if not self.__comp7RanksConfig:
            return False
        if not self.__comp7RanksConfig.ranks:
            _logger.error('No ranks data available.')
            return False
        return True

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
        self.__comp7RanksConfig = self.__serverSettings.comp7RanksConfig
        self.__updateMainConfig()
        self.__roleEquipmentsCache = None
        return

    def __onUpdateComp7Settings(self, diff):
        if Configs.COMP7_RANKS_CONFIG.value in diff:
            self.__comp7RanksConfig = self.__serverSettings.comp7RanksConfig
            self.onComp7RanksConfigChanged()
        if Configs.COMP7_CONFIG.value in diff:
            self.__updateMainConfig()
            self.__roleEquipmentsCache = None
            self.__resetTimer()
            self.__updateTournamentBannerState()
            self.onComp7ConfigChanged()
        if Configs.COMP7_REWARDS_CONFIG.value in diff:
            self.onComp7RewardsConfigChanged()
        return

    def __updateMainConfig(self):
        self.__comp7Config = self.__serverSettings.comp7Config

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
        self.__updateQualificationBattles()
        self.__updateQualificationState()

    def __onEntitlementsChanged(self, entitlements):
        if self.__getActualEntitlements() & set(entitlements.keys()):
            self.__updateRank()
        updatedSeasonPointCodes = set(SEASON_POINTS_ENTITLEMENTS) & set(entitlements.keys())
        if updatedSeasonPointCodes:
            self.__tryToShowSeasonStatistics()
            self.onSeasonPointsUpdated()
        seasonNumber = self.getActualSeasonNumber()
        if seasonNumber and maxRankEntNameBySeasonNumber(seasonNumber) in entitlements:
            self.onHighestRankAchieved()

    def __updateRank(self):
        actualSeasonNumber = self.getActualSeasonNumber()
        if actualSeasonNumber:
            self.__rating = self.getRatingForSeason(actualSeasonNumber)
            self.__isElite = self.isEliteForSeason(actualSeasonNumber)
            self.__activityPoints = self.__getEntitlementCount(activityPointsEntNameBySeasonNumber(actualSeasonNumber))
        else:
            self.__rating = 0
            self.__isElite = False
            self.__activityPoints = 0
        self.onRankUpdated(self.__rating, self.__isElite)

    def __onOfflineStatusChanged(self, _):
        self.__updateOfflineStatus()

    def __updateOfflineStatus(self):
        isOffline = not self.__itemsCache.items.stats.comp7.get('isOnline', False)
        if self.__isOffline != isOffline:
            self.__isOffline = isOffline
            self.onOfflineStatusUpdated()

    def __updateTournamentBannerState(self):
        if not self.isComp7PrbActive():
            return
        bannerEnable = self.getTournamentBannerAvailability()
        if self.__isTournamentBannerEnabled != bannerEnable:
            self.__isTournamentBannerEnabled = bannerEnable
            self.onTournamentBannerStateChanged()

    def __onQualificationBattlesChanged(self, _):
        self.__updateQualificationBattles()

    def __onQualificationStateChanged(self, _):
        self.__updateQualificationState()

    def __updateQualificationBattles(self):
        self.__qualificationBattlesStatuses = self.__itemsCache.items.stats.comp7.get('qualification', {}).get('battles', [None])
        self.onQualificationBattlesUpdated()
        return

    def __updateQualificationState(self):
        self.__qualificationState = self.__itemsCache.items.stats.comp7.get('qualification', {}).get('state', Comp7QualificationState.NOT_STARTED)
        self.onQualificationStateUpdated()

    def __onEntitlementsCacheUpdated(self, isSuccess):
        if isSuccess:
            self.onEntitlementsUpdated()
            self.__updateRank()
            self.__tryToShowSeasonStatistics()

    def __getActualEntitlements(self):
        actualSeasonNumber = self.getActualSeasonNumber()
        return set() if not actualSeasonNumber else {nameFactory(actualSeasonNumber) for nameFactory in self.__SEASON_ENTITLEMENT_NAME_FACTORIES}

    def __getEntitlementCount(self, entitlementName):
        return self.__entitlementsCache.getEntitlementCount(entitlementName) if self.__entitlementsCache.isEntitlementCached(entitlementName) else self.__itemsCache.items.stats.entitlements.get(entitlementName, 0)

    def __tryToShowSeasonStatistics(self):
        if not isSeasonStasticsShouldBeShown():
            return
        event_dispatcher.showComp7SeasonStatisticsScreen()


class _LeaderboardDataProvider(object):
    __EVENT_ID = 'comp7'
    __LEADERBOARD_ID = 0
    __FIRST_PAGE_ID = 0
    __MASTER_RANK_ID = 2
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
            _logger.warn('Empty events on controller while requesting pages. Reloading.')
            yield self.__eventsController.getEvents(onlySettings=True)
            if not self.__eventsController.hasEvents():
                _logger.error('Leaderboard pages request failed. Pages ids: %s', pageIDs)
                callback(False)
                return
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
        return self.__lobbyContext.getServerSettings().comp7RanksConfig

    @staticmethod
    def __getRanges(limit, offset, pageSize):
        startPage, startRecord = divmod(offset, pageSize)
        endPage = (offset + limit - 1) // pageSize
        endRecord = startRecord + limit - 1
        return ((startPage, endPage), (startRecord, endRecord))
