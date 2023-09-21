# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/event_battles_controller.py
import logging
import math
import typing
import BigWorld
import CGF
import Event
from shared_utils import nextTick
from shared_utils import first
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import CURRENT_VEHICLE, EVENT_VEHICLE, EVENT_SAVED_VEHICLE
from account_helpers.settings_core.settings_constants import WTEventStorageKeys, GRAPHICS
from adisp import adisp_process
from backports.functools_lru_cache import lru_cache
from CurrentVehicle import g_currentVehicle
from EventVehicle import EventVehicle
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.lobby.wt_event import wt_event_sound
from gui.prb_control import prbEntityProperty, prbDispatcherProperty
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.settings import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showWTWelcomeScreen
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, PeriodicNotifier
from gui.wt_event.wt_event_helpers import g_execute_after_all_event_vehicles_and_main_view_loaded
from gui.wt_event.wt_event_simple_bonus_packers import mergeWtProgressionBonuses
from helpers import dependency, time_utils, isPlayerAvatar
from helpers.statistics import HARDWARE_SCORE_PARAMS
from items.vehicles import VehicleDescr
from season_provider import SeasonProvider
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
from skeletons.prebattle_vehicle import IPrebattleVehicle
from skeletons.gui.game_control import IEventBattlesController, ILootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from helpers.server_settings import _EventBattlesConfig
_logger = logging.getLogger(__name__)

class WtLimitType(object):
    SYSTEM_DATA = 0
    HARDWARE_PARAMS = 1


class WtPerfProblems(object):
    HIGH_RISK = 1
    MEDIUM_RISK = 2
    LOW_RISK = 3


PERFORMANCE_GROUP_LIMITS = {WtPerfProblems.HIGH_RISK: [{WtLimitType.SYSTEM_DATA: {'clientBit': 1}},
                            {WtLimitType.SYSTEM_DATA: {'osBit': 1,
                                                       'graphicsEngine': 0}},
                            {WtLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_MEMORY: 490}},
                            {WtLimitType.SYSTEM_DATA: {'graphicsEngine': 0},
                             WtLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_RAM: 2900}}],
 WtPerfProblems.MEDIUM_RISK: [{WtLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_GPU_SCORE: 150}}, {WtLimitType.HARDWARE_PARAMS: {HARDWARE_SCORE_PARAMS.PARAM_CPU_SCORE: 50000}}]}

@lru_cache()
def _getSpecialBossCD():
    return VehicleDescr(typeName='germany:G98_Waffentrager_E100_TLXXL_S').type.compactDescr


class EventBattlesController(IEventBattlesController, Notifiable, SeasonProvider, IGlobalListener):
    __itemsCache = dependency.descriptor(IItemsCache)
    __eventsCache = dependency.descriptor(IEventsCache)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __prebattleVehicle = dependency.descriptor(IPrebattleVehicle)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __boxesCtrl = dependency.descriptor(ILootBoxesController)
    __appLoader = dependency.descriptor(IAppLoader)
    __hangarsSpace = dependency.descriptor(IHangarSpace)
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EventBattlesController, self).__init__()
        self.__serverSettings = None
        self.__eventBattlesConfig = None
        self.__enterSound = wt_event_sound.WTEventHangarEnterSound()
        self.__lootBoxAreaSoundMgr = wt_event_sound.LootBoxAreaSound()
        self.__selectedVehicleSoundMgr = wt_event_sound.WTEventVehicleSoundPlayer()
        self.__eventManager = Event.EventManager()
        self.onPrimeTimeStatusUpdated = Event.Event(self.__eventManager)
        self.onUpdated = Event.Event(self.__eventManager)
        self.onProgressUpdated = Event.Event(self.__eventManager)
        self.onEventPrbChanged = Event.Event(self.__eventManager)
        self.onGameEventTick = Event.Event(self.__eventManager)
        self.onTicketsUpdate = Event.Event(self.__eventManager)
        self.__mainViewLoaded = False
        return

    def init(self):
        super(EventBattlesController, self).init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.addNotificator(SimpleNotifier(self.__getClosestStateChangeTimeLeft, self.__updateStates))
        self.addNotificator(PeriodicNotifier(self.__getTimer, self.__timerTick))

    def fini(self):
        self.__eventManager.clear()
        self.__eventManager = None
        self.clearNotification()
        self.__clear()
        self.__selectedVehicleSoundMgr = None
        super(EventBattlesController, self).fini()
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def isEventPrbActive(self):
        return self.prbEntity and self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.EVENT > 0

    def isEventBattleActive(self):
        return isPlayerAvatar() and self.__sessionProvider.arenaVisitor.gui.isEventBattle()

    def getEnterSound(self):
        return self.__enterSound

    @adisp_process
    def doSelectEventPrb(self):
        if self.isEventPrbActive():
            return
        if not self.isAvailable():
            self.__showWelcomeScreen()
            return
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            return
        yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE))

    @adisp_process
    def doSelectEventPrbAndCallback(self, callback):
        if self.isEventPrbActive():
            callback()
            return
        navigationPossible = yield self.__lobbyContext.isHeaderNavigationPossible()
        if not navigationPossible:
            return
        result = yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.EVENT_BATTLE))
        if result:
            callback()

    @adisp_process
    def doLeaveEventPrb(self):
        if self.isEventPrbActive():
            yield self.prbDispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))

    @g_execute_after_all_event_vehicles_and_main_view_loaded
    def onPrbEntitySwitched(self):
        wt_event_sound.playHangarCameraFly(forward=self.isEventPrbActive())
        if self.isEventPrbActive() and self.isEnabled():
            self.__checkAndCloseCustomizationView()
            self.__prebattleVehicle.selectAny()
            if not self.isWelcomeScreenShown():
                self.__showWelcomeScreen()
        else:
            self.__prebattleVehicle.selectNone()
            self.__selectRandomFavoriteVehicle()
            self.onUpdated()
        self.onEventPrbChanged(self.isEventPrbActive())
        self.__enterSound.update(self.isEventPrbActive())
        if not self.isEventPrbActive():
            self.__selectedVehicleSoundMgr.stopAll()

    def onLobbyInited(self, ctx):
        super(EventBattlesController, self).onLobbyInited(ctx)
        self.startGlobalListening()
        self.__enterSound.clear()
        self.__enterSound.update(self.isEventPrbActive())
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensUpdate})
        if self.isEventPrbActive() and not self.isEnabled():
            g_currentVehicle.selectVehicle()
        g_eventBus.addListener(events.HangarSimpleEvent.HANGAR_LOADED, self.__onViewLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarSimpleEvent.HANGAR_UNLOADED, self.__onViewUnLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarSimpleEvent.VEHICLE_PREVIEW_LOADED, self.__onViewLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.HangarSimpleEvent.VEHICLE_PREVIEW_UNLOADED, self.__onViewUnLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__hangarsSpace.onSpaceChangedByAction += self.__onSpaceChanged
        self.__hangarsSpace.onSpaceChanged += self.__onSpaceChanged
        if not self.__hangarsSpace.spaceInited or self.__hangarsSpace.spaceLoading():
            self.__hangarsSpace.onSpaceCreate += self.__onSpaceCreate
        self.analyzeClientSystem()
        g_playerEvents.onArenaCreated += self.__onArenaCreated
        nextTick(self.__eventAvailabilityUpdate)()

    def onLobbyStarted(self, ctx):
        super(EventBattlesController, self).onLobbyStarted(ctx)
        self.onUpdated()

    def onAccountBecomePlayer(self):
        super(EventBattlesController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())

    def onDisconnected(self):
        super(EventBattlesController, self).onDisconnected()
        self.__enterSound.onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(EventBattlesController, self).onAvatarBecomePlayer()
        self.__clear()

    def isEnabled(self):
        return self.getConfig().isEnabled

    def isModeActive(self):
        _, isCycleActive = self.getCurrentCycleInfo()
        isSeason = self.getCurrentSeason() is not None
        return self.isEnabled() and isSeason and isCycleActive

    def isAvailable(self):
        isSeason = self.getCurrentSeason() is not None
        return self.isEnabled() and not self.isFrozen() and isSeason

    def isFrozen(self):
        for primeTime in self.getPrimeTimes().values():
            if primeTime.hasAnyPeriods():
                return False

        return True

    def isHangarAvailable(self):
        query = CGF.Query(self.__hangarsSpace.spaceID, EventVehicle)
        return not query.empty()

    def isWelcomeScreenShown(self):
        eventStorage = self.__settingsCore.serverSettings.getEventStorage()
        return eventStorage.get(WTEventStorageKeys.WT_INTRO_SHOWN, False)

    def getConfig(self):
        return self.__lobbyContext.getServerSettings().eventBattlesConfig

    def getModeSettings(self):
        return self.getConfig()

    def getCurrentStampsCount(self):
        config = self.getConfig()
        return self.__itemsCache.items.tokens.getTokenCount(config.stamp)

    def getTotalStampsCount(self):
        return self.getStampsCountPerLevel() * self.getTotalLevelsCount()

    def getStampsCountPerLevel(self):
        config = self.getConfig()
        return config.stampsPerProgressionStage

    def getTotalLevelsCount(self):
        progression = self.getConfig().progression
        return len(progression)

    def getFinishedLevelsCount(self):
        stampsCount = self.getCurrentStampsCount()
        stampsPerLevel = self.getStampsCountPerLevel()
        totalLevels = self.getTotalLevelsCount()
        return min(int(math.floor(stampsCount / stampsPerLevel)), totalLevels)

    def getCurrentLevel(self):
        finishedLevelsCount = self.getFinishedLevelsCount()
        totalLevels = self.getTotalLevelsCount()
        return min(finishedLevelsCount + 1, totalLevels)

    def getTicketCount(self):
        config = self.getConfig()
        return self.__itemsCache.items.tokens.getTokenCount(config.ticketToken)

    def getQuickTicketCount(self):
        config = self.getConfig()
        return self.__itemsCache.items.tokens.getTokenCount(config.quickBossTicketToken)

    def getQuickTicketExpiryTime(self):
        config = self.getConfig()
        return self.__itemsCache.items.tokens.getTokenExpiryTime(config.quickBossTicketToken)

    def getQuickHunterTicketCount(self):
        config = self.getConfig()
        return self.__itemsCache.items.tokens.getTokenCount(config.quickHunterTicketToken)

    def getQuickHunterTicketExpiryTime(self):
        config = self.getConfig()
        return self.__itemsCache.items.tokens.getTokenExpiryTime(config.quickHunterTicketToken)

    def getLootBoxAreaSoundMgr(self):
        return self.__lootBoxAreaSoundMgr

    def getSelectedVehicleSoundMgr(self):
        return self.__selectedVehicleSoundMgr

    def hasEnoughTickets(self, useQuickTicket=True):
        config = self.getConfig()
        return True if useQuickTicket and self.getQuickTicketCount() else self.getTicketCount() >= config.ticketsToDraw

    def hasSpecialBoss(self):
        return self.__itemsCache.items.inventory.getItemData(_getSpecialBossCD()) is not None

    def getQuestRewards(self, questID):
        quests = self.__eventsCache.getAllQuests(lambda quest: quest.getID() == questID)
        bonuses = quests[questID].getBonuses()
        return mergeWtProgressionBonuses(bonuses)

    def getDisplayedCollectionProgress(self, questID):
        for stage in self.getConfig().progression:
            if stage['quest'] == questID:
                return stage['level']

        _logger.error('Invalid collection progress to show in the award view')
        return self.getCurrentStampsCount()

    @lru_cache()
    def analyzeClientSystem(self):
        stats = BigWorld.wg_getClientStatistics()
        stats['graphicsEngine'] = self.__settingsCore.getSetting(GRAPHICS.RENDER_PIPELINE)
        for groupName, conditions in PERFORMANCE_GROUP_LIMITS.iteritems():
            for currentLimit in conditions:
                condValid = True
                systemStats = currentLimit.get(WtLimitType.SYSTEM_DATA, {})
                for key, limit in systemStats.iteritems():
                    currValue = stats.get(key, None)
                    if currValue is None or currValue != limit:
                        condValid = False

                hardwareParams = currentLimit.get(WtLimitType.HARDWARE_PARAMS, {})
                for key, limit in hardwareParams.iteritems():
                    currValue = BigWorld.getAutoDetectGraphicsSettingsScore(key)
                    if currValue >= limit:
                        condValid = False

                if condValid:
                    return groupName

        return WtPerfProblems.LOW_RISK

    def __onSpaceChanged(self):
        self.onUpdated()

    def __onSpaceCreate(self):
        self.__ensureVehicleSelection()
        self.onUpdated()

    def __onViewLoaded(self, _):
        self.__mainViewLoaded = True

    def __onViewUnLoaded(self, _):
        self.__mainViewLoaded = False

    def __onArenaCreated(self):
        if self.isEventPrbActive():
            vehicleInvID = AccountSettings.getFavorites(EVENT_VEHICLE)
            AccountSettings.setFavorites(EVENT_SAVED_VEHICLE, vehicleInvID)

    def __selectRandomFavoriteVehicle(self):
        storedVehInvID = AccountSettings.getFavorites(CURRENT_VEHICLE)
        if not storedVehInvID:
            criteria = REQ_CRITERIA.INVENTORY
            criteria |= criteria | REQ_CRITERIA.VEHICLE.ACTIVE_IN_NATION_GROUP
            criteria |= ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE
            criteria |= ~REQ_CRITERIA.VEHICLE.EVENT
            vehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).values())
            if vehicle:
                storedVehInvID = vehicle.invID
        if storedVehInvID:
            g_currentVehicle.selectVehicle(storedVehInvID)
        else:
            g_currentVehicle.selectNoVehicle()

    @property
    def mainViewLoaded(self):
        return self.__mainViewLoaded

    def __onTokensUpdate(self, diff):
        config = self.getConfig()
        if config.stamp in diff:
            self.onProgressUpdated()
        if config.ticketToken in diff:
            self.onTicketsUpdate()

    def __eventAvailabilityUpdate(self, *_):
        if self.prbEntity is None:
            return
        elif not self.isEventPrbActive():
            return
        else:
            if not self.isAvailable():
                self.doLeaveEventPrb()
                g_currentVehicle.selectVehicle()
            return

    def __updateStates(self):
        self.onUpdated()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateEventBattlesSettings
        self.__resetTimer()
        return

    def __updateEventBattlesSettings(self, diff):
        if 'event_battles_config' in diff:
            self.onUpdated()
            self.__resetTimer()

    def __clear(self):
        self.__lootBoxAreaSoundMgr.leave()
        self.__selectedVehicleSoundMgr.destroy()
        self.stopGlobalListening()
        self.stopNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateEventBattlesSettings
        self.__serverSettings = None
        g_eventBus.removeListener(events.HangarSimpleEvent.HANGAR_LOADED, self.__onViewLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarSimpleEvent.HANGAR_UNLOADED, self.__onViewUnLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarSimpleEvent.VEHICLE_PREVIEW_LOADED, self.__onViewLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.HangarSimpleEvent.VEHICLE_PREVIEW_UNLOADED, self.__onViewUnLoaded, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__hangarsSpace.onSpaceChangedByAction -= self.__onSpaceChanged
        self.__hangarsSpace.onSpaceChanged -= self.__onSpaceChanged
        self.__hangarsSpace.onSpaceCreate -= self.__onSpaceCreate
        g_playerEvents.onArenaCreated -= self.__onArenaCreated
        return

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __ensureVehicleSelection(self):
        if self.isEventPrbActive() and self.isEnabled() and not self.__prebattleVehicle.item:
            self.__prebattleVehicle.selectAny()

    def __getClosestStateChangeTimeLeft(self):
        timeLeft = self.getClosestStateChangeTime() - time_utils.getCurrentLocalServerTimestamp()
        return timeLeft + 1 if timeLeft > 0 else 0

    def __resetTimer(self):
        self.startNotification()
        self.__updateStates()
        self.__timerUpdate()

    def __timerUpdate(self):
        status, _, _ = self.getPrimeTimeStatus()
        self.onPrimeTimeStatusUpdated(status)
        nextTick(self.__eventAvailabilityUpdate)()

    def __timerTick(self):
        self.onGameEventTick()

    def __showWelcomeScreen(self):
        if self.__settingsCore.isReady:
            self.__settingsCore.serverSettings.saveInEventStorage({WTEventStorageKeys.WT_INTRO_SHOWN: True})
        else:
            _logger.error('Can not save WT intro settings: settings are not ready')
        showWTWelcomeScreen()

    def __checkAndCloseCustomizationView(self):
        app = self.__appLoader.getApp()
        if app is None:
            return
        else:
            view = app.containerManager.getViewByKey(ViewKey(VIEW_ALIAS.LOBBY_CUSTOMIZATION))
            if view is None:
                return
            view.destroy()
            return
