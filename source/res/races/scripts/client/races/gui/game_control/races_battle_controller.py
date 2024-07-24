# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/gui/game_control/races_battle_controller.py
import logging
from CurrentVehicle import g_currentVehicle
from races.account_helpers.settings_core.settings_disable.races_disable_settings_controller import RacesDisableSettingsController
from races.gui.gui_constants import SCH_CLIENT_MSG_TYPE
from races.gui.prb_control.prb_config import FUNCTIONAL_FLAG, PREBATTLE_ACTION_NAME
from races_common.races_constants import QUEUE_TYPE, PREBATTLE_TYPE
from races_constants import EVENT_STATES
from typing import TYPE_CHECKING
import Event
from account_helpers import AccountSettings
from account_helpers.AccountSettings import BIRTHDAY_2024, RACES_STARTED_NOTIFICATION_VIEWED
from adisp import adisp_process
from constants import Configs
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.game_control.season_provider import SeasonProvider
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.dispatcher import g_prbLoader
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.listener import IPreQueueListener
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, EventPriority
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, TimerNotifier
from gui.shared.utils.requesters import REQ_CRITERIA
from gui.shared.gui_items.Vehicle import VEHICLE_TAGS
from helpers import dependency, time_utils, server_settings
from helpers.server_settings import RacesConfig
from shared_utils import first
from skeletons.gui.game_control import IRacesBattleController
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
if TYPE_CHECKING:
    from helpers.server_settings import ServerSettings
    from typing import Optional
    from typing import Optional, List, Dict
    from gui.impl.gen_utils import DynAccessor
    from enum import Enum
_logger = logging.getLogger(__name__)

class RacesBattleController(IRacesBattleController, SeasonProvider, Notifiable, IPreQueueListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __systemMessages = dependency.descriptor(ISystemMessages)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(RacesBattleController, self).__init__()
        self.__disableSettingsCtrl = RacesDisableSettingsController()
        self.onRacesConfigChanged = Event.Event()
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onStatusTick = Event.Event()
        self.__isPrimeTime = False
        self.__lastSelectedRaceVehicleCD = 0
        self.__lastSelectedRegularVehicleInvID = None
        self.__isEnabled = False
        self.__isBattleEnabled = False
        return

    def init(self):
        super(RacesBattleController, self).init()
        self.__disableSettingsCtrl.init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.addNotificator(TimerNotifier(self.__getTimer, self.__timerTick))

    def fini(self):
        self.__unsubscribeFromEvents()
        self.onPrimeTimeStatusUpdated.clear()
        self.onRacesConfigChanged.clear()
        self.onStatusTick.clear()
        self.clearNotification()
        self.__disableSettingsCtrl.fini()
        self.__disableSettingsCtrl = None
        super(RacesBattleController, self).fini()
        return

    def onAccountBecomePlayer(self):
        super(RacesBattleController, self).onAccountBecomePlayer()
        self.__disableSettingsCtrl.onAccountBecomePlayer()
        self.__setSuspendedFlags(self.__lobbyContext.getServerSettings())

    def onAvatarBecomePlayer(self):
        super(RacesBattleController, self).onAvatarBecomePlayer()
        self.__disableSettingsCtrl.onAvatarBecomePlayer()

    def onAccountBecomeNonPlayer(self):
        super(RacesBattleController, self).onAccountBecomeNonPlayer()
        self.__unsubscribeFromEvents()

    def onDisconnected(self):
        super(RacesBattleController, self).onDisconnected()
        self.__disableSettingsCtrl.onDisconnected()
        self.__unsubscribeFromEvents()

    def onLobbyInited(self, event):
        super(RacesBattleController, self).onLobbyInited(event)
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChanged
        g_eventBus.addListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__disableSettingsCtrl.onLobbyInited(event)
        self.__restoreHangarSelectedVehicle()

    @property
    def isRacesPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.RACES)

    @property
    def isEnabled(self):
        return self.getModeSettings().isEnabled

    def isFrozen(self):
        primeTimeStatus = self.getPrimeTimeStatus()[0]
        return primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def isBattleAvailable(self):
        return self.getModeSettings().isBattleEnabled

    def isInQueue(self):
        return self.prbEntity and self.prbEntity.isInQueue()

    def isTemporaryUnavailable(self):
        return self.getCurrentSeason() is not None and (not self.isEnabled or not self.isBattleAvailable())

    def isAvailable(self):
        return self.isEnabled and not self.isFrozen() and self.getCurrentSeason() is not None

    def isRacesMode(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is None:
            return False
        else:
            state = prbDispatcher.getFunctionalState()
            isInPreQueue = state.isInPreQueue(queueType=QUEUE_TYPE.RACES)
            isInUnit = state.isInUnit(prbType=PREBATTLE_TYPE.RACES)
            return isInUnit or isInPreQueue

    def getModeSettings(self):
        return self.__lobbyContext.getServerSettings().racesConfig

    def getRacesVehiclesInfo(self):
        return self.getModeSettings().racesVehicles

    def getRacesVehicles(self):
        racesVehicles = self.getRacesVehiclesInfo()
        return sorted(racesVehicles.keys(), key=lambda key: racesVehicles[key]['order'])

    def getSelectedRacesVehicleDescr(self):
        selectedTank = self.getLastSelectedTank()
        racesVehicles = self.getRacesVehicles()
        return racesVehicles[selectedTank]

    def getLastSelectedTank(self):
        return self.__lastSelectedRaceVehicleCD

    def setLastSelectedTank(self, tankCompDescr):
        self.__lastSelectedRaceVehicleCD = tankCompDescr

    def saveLastSelectedRegularVehicle(self):
        if g_currentVehicle.intCD not in self.getRacesVehiclesInfo():
            self.__lastSelectedRegularVehicleInvID = g_currentVehicle.invID

    def getRacesAccountSettings(self, name):
        return AccountSettings.getSettings(BIRTHDAY_2024).get(name)

    def setRacesAccountSettings(self, name, value):
        section = AccountSettings.getSettings(BIRTHDAY_2024)
        if name in section:
            section[name] = value
            AccountSettings.setSettings(BIRTHDAY_2024, section)
        else:
            _logger.error("Cann't set value in %s section for %s.", BIRTHDAY_2024, name)

    def selectRandomBattle(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            self.__doSelectRandomPrb(dispatcher)
            return

    def selectRaces(self):
        if self.isTemporaryUnavailable():
            return
        self.__selectRaces()

    def closePostBattleScreen(self):
        contentID = R.views.races.lobby.RacesPostBattleView()
        self.__closeRacesView(contentID)

    def closeRewardScreen(self):
        contentID = R.views.races.lobby.reward_view.RewardView()
        self.__closeRacesView(contentID)

    def onPrbEnter(self):
        g_eventBus.addListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY, priority=EventPriority.VERY_LOW)

    def onPrbLeave(self):
        g_eventBus.removeListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.closeEventLobby()
        self.__restoreHangarSelectedVehicle()

    def openEventLobby(self, *args, **kwargs):
        uiLoader = dependency.instance(IGuiLoader)
        contentID = R.views.races.lobby.races_lobby_view.RacesLobbyView()
        if uiLoader.windowsManager.getViewByLayoutID(contentID) is None:
            from races.gui.impl.lobby.races_lobby_view.races_lobby_view import RacesLobbyView
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=RacesLobbyView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def getProgressionQuestPrefix(self):
        return self.getModeSettings().rewardSettings.get('questPrefix', '')

    def openProgressionView(self, *args, **kwargs):
        uiLoader = dependency.instance(IGuiLoader)
        contentID = R.views.races.lobby.RacesProgressionView()
        if uiLoader.windowsManager.getViewByLayoutID(contentID) is None:
            from races.gui.impl.lobby.races_lobby_view.races_progression_view import RacesProgressionView
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=RacesProgressionView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def getTokenProgressionID(self):
        return self.getModeSettings().rewardSettings.get('rewardToken', '')

    def closeEventLobby(self):
        contentID = R.views.races.lobby.races_lobby_view.RacesLobbyView()
        self.__closeRacesView(contentID)

    def openQueueView(self):
        from races.gui.impl.lobby.races_queue_view.races_queue_view import RacesQueueView
        contentID = R.views.races.lobby.races_queue_view.RacesQueueView()
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=RacesQueueView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)

    def isEventStartedNotificationViewed(self):
        return self.getRacesAccountSettings(RACES_STARTED_NOTIFICATION_VIEWED)

    def setEventStartedNotificationViewed(self, status):
        self.setRacesAccountSettings(RACES_STARTED_NOTIFICATION_VIEWED, status)

    def __unsubscribeFromEvents(self):
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChanged
        g_eventBus.removeListener(events.HangarVehicleEvent.SELECT_VEHICLE_IN_HANGAR, self.__onSelectVehicleInHangar, scope=EVENT_BUS_SCOPE.LOBBY)

    def __selectRaces(self):
        dispatcher = g_prbLoader.getDispatcher()
        if dispatcher is None:
            _logger.error('Prebattle dispatcher is not defined')
            return
        else:
            entityType = dispatcher.getEntity().getEntityType()
            if entityType == QUEUE_TYPE.RACES:
                self.openEventLobby()
            else:
                self.__doSelectRacesPrb(dispatcher)
            return

    @server_settings.serverSettingsChangeListener(Configs.RACES_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.onRacesConfigChanged()
        self.__resetTimer()
        if not (self.isAvailable() and self.isBattleAvailable()) and self.isRacesPrbActive:
            self.selectRandomBattle()
        wasSuspended = self.__isEnabled is not True or self.__isBattleEnabled is not True
        isSuspended = self.isTemporaryUnavailable()
        racesConfig = diff[Configs.RACES_CONFIG.value]
        self.__isEnabled = racesConfig.get('isEnabled', False)
        self.__isBattleEnabled = racesConfig.get('isBattleEnabled', False)
        if isSuspended is not wasSuspended:
            eventType = EVENT_STATES.SUSPEND if isSuspended else EVENT_STATES.RESUME
            self.__triggerEventStateNotification(eventType)

    def __triggerEventStateNotification(self, eventType):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'state': eventType}, SCH_CLIENT_MSG_TYPE.RACES_STATE)

    def __triggerLootBoxesAccrualNotification(self):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({}, SCH_CLIENT_MSG_TYPE.RACES_LOOT_BOXES_ACCRUAL)

    def __triggerSeasonStateNotification(self):
        if self.__isPrimeTime:
            isSuspended = self.isTemporaryUnavailable()
            if not isSuspended and self.isEnabled:
                if not self.isEventStartedNotificationViewed():
                    self.__showStartedNotification()
            return
        else:
            wasLastSeason = self.__getActiveSeason() is None
            if wasLastSeason:
                self.__triggerEventStateNotification(EVENT_STATES.FINISH)
                self.setEventStartedNotificationViewed(False)
            return

    def __showStartedNotification(self):
        self.__triggerEventStateNotification(EVENT_STATES.START)
        self.__triggerLootBoxesAccrualNotification()
        self.setEventStartedNotificationViewed(True)

    def __getActiveSeason(self):
        return self.getCurrentSeason() or self.getNextSeason()

    def __setSuspendedFlags(self, serverSettings):
        settings = serverSettings.getSettings()
        if Configs.RACES_CONFIG.value in settings:
            racesConfig = settings[Configs.RACES_CONFIG.value]
            self.__isEnabled = racesConfig.get('isEnabled', False)
            self.__isBattleEnabled = racesConfig.get('isBattleEnabled', False)

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > time_utils.ONE_DAY else time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

    def __updateHangar(self):
        if not (self.isAvailable() and self.isBattleAvailable()) and self.isRacesPrbActive:
            self.selectRandomBattle()

    def __timerUpdate(self):
        status, _, isPrimeTime = self.getPrimeTimeStatus()
        if isPrimeTime and self.__isPrimeTime:
            if not self.isEventStartedNotificationViewed():
                self.__showStartedNotification()
        elif isPrimeTime is not self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            self.__triggerSeasonStateNotification()
        self.__updateHangar()
        self.onPrimeTimeStatusUpdated(status)

    def __timerTick(self):
        self.onStatusTick()

    def __closeRacesView(self, contentID):
        uiLoader = dependency.instance(IGuiLoader)
        view = uiLoader.windowsManager.getViewByLayoutID(contentID)
        if view is not None:
            view.destroyWindow()
        return

    def __viewLoaded(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            if self.isEnabled and self.isBattleAvailable() and self.isRacesPrbActive:
                self.openEventLobby()
            else:
                self.selectRandomBattle()

    @adisp_process
    def fightClick(self):
        dispatcher = g_prbLoader.getDispatcher()
        if not dispatcher:
            return
        lobbyContext = dependency.instance(ILobbyContext)
        navigationPossible = yield lobbyContext.isHeaderNavigationPossible()
        fightButtonPressPossible = yield lobbyContext.isFightButtonPressPossible()
        if navigationPossible and fightButtonPressPossible:
            if dispatcher:
                dispatcher.doAction(PrbAction(PREBATTLE_ACTION_NAME.RACES))
            else:
                _logger.error('Prebattle dispatcher is not defined')

    def getEventEndTimestamp(self):
        if self.hasPrimeTimesLeftForCurrentCycle() or self.isInPrimeTime():
            actualSeason = self.getCurrentSeason()
            return actualSeason.getEndDate()
        else:
            return None

    def __restoreHangarSelectedVehicle(self):
        if self.isRacesPrbActive:
            return
        else:
            if self.__lastSelectedRegularVehicleInvID:
                g_currentVehicle.selectVehicle(self.__lastSelectedRegularVehicleInvID)
                self.__lastSelectedRegularVehicleInvID = None
            elif g_currentVehicle.intCD in self.getRacesVehiclesInfo():
                storedVehInvID = 0
                criteria = REQ_CRITERIA.INVENTORY | ~REQ_CRITERIA.VEHICLE.MODE_HIDDEN
                criteria |= ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.BATTLE_ROYALE])
                vehicle = first(self.__itemsCache.items.getVehicles(criteria=criteria).itervalues())
                if vehicle:
                    storedVehInvID = vehicle.invID
                g_currentVehicle.selectVehicle(storedVehInvID)
            return

    def __onSelectVehicleInHangar(self, event):
        if not self.isRacesPrbActive:
            return
        vehicleInvID = event.ctx['vehicleInvID']
        vehicle = self.__itemsCache.items.getVehicle(vehicleInvID)
        if vehicle and vehicle.intCD not in self.getRacesVehiclesInfo():
            dispatcher = g_prbLoader.getDispatcher()
            if dispatcher:
                self.__doSelectRandomPrb(dispatcher)

    @adisp_process
    def __doSelectRacesPrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RACES))

    @adisp_process
    def __doSelectRandomPrb(self, dispatcher):
        yield dispatcher.doSelectAction(PrbAction(PREBATTLE_ACTION_NAME.RANDOM))
