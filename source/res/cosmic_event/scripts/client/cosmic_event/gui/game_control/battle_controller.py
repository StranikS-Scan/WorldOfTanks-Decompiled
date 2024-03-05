# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/gui/game_control/battle_controller.py
import logging
from typing import TYPE_CHECKING
import Event
import adisp
from cosmic_constants import EVENT_STATES
from cosmic_event.account_helpers.settings_core.settings_disable.cosmic_disable_settings_controller import CosmicDisableSettingsController
from cosmic_event.gui.gui_constants import SCH_CLIENT_MSG_TYPE
from cosmic_event.gui.impl.gen.view_models.views.lobby.cosmic_lobby_view.cosmic_lobby_view_model import LobbyRouteEnum
from cosmic_event.gui.prb_control import prb_config
from cosmic_event.gui.prb_control.prb_config import FUNCTIONAL_FLAG
from cosmic_event.settings import CosmicEventConfig
from cosmic_event.skeletons.battle_controller import ICosmicEventBattleController
from cosmic_event_common.cosmic_constants import COSMIC_EVENT_GAME_PARAMS_KEY, QUEUE_TYPE
from cosmic_sound import CosmicHangarSounds
from cosmic_account_settings import isEventStartedNotificationViewed, setEventStartedNotificationViewed
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.managers.loaders import GuiImplViewLoadParams
from gui.game_control.season_provider import SeasonProvider
from gui.impl.gen import R
from gui.periodic_battles.models import PrimeTimeStatus
from gui.prb_control.entities.base.ctx import PrbAction
from gui.prb_control.entities.base.pre_queue.listener import IPreQueueListener
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE, EventPriority
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier, TimerNotifier
from helpers import dependency, time_utils
from shared_utils import makeTupleByDict
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from wotdecorators import condition
from gui.prb_control.dispatcher import g_prbLoader
from cosmic_event_common import cosmic_constants
_logger = logging.getLogger(__name__)
if TYPE_CHECKING:
    from helpers.server_settings import ServerSettings
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.impl.gen_utils import DynAccessor
    from typing import Optional, List, Dict
    from gui.impl.lobby.mode_selector.mode_selector_view import ModeSelectorView

class CosmicEventBattleController(ICosmicEventBattleController, Notifiable, SeasonProvider, IPreQueueListener):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __systemMessages = dependency.descriptor(ISystemMessages)
    ifEnabled = condition('isEnabled')
    ifCosmicPrbActive = condition('isCosmicPrbActive')

    def __init__(self):
        super(CosmicEventBattleController, self).__init__()
        self.__serverSettings = None
        self.__cosmicEventConfig = None
        self.__disableSettingsCtrl = CosmicDisableSettingsController()
        self.__isPrimeTime = False
        self.onPrimeTimeStatusUpdated = Event.Event()
        self.onCosmicConfigChanged = Event.Event()
        self.onStatusTick = Event.Event()
        self.onLobbyRouteChange = Event.Event()
        self.lobbyViewRoute = LobbyRouteEnum.MAIN
        return

    @property
    def isCosmicPrbActive(self):
        return False if self.prbEntity is None else bool(self.prbEntity.getModeFlags() & FUNCTIONAL_FLAG.COSMIC_EVENT)

    @property
    def isEnabled(self):
        return self._isEnabled()

    def getEventVehicle(self):
        vehCD = self.__cosmicEventConfig.eventVehicleCD if self.__cosmicEventConfig else None
        return None if vehCD is None else self.__itemsCache.items.getItemByCD(vehCD)

    def init(self):
        super(CosmicEventBattleController, self).init()
        self.__disableSettingsCtrl.init()
        self.addNotificator(SimpleNotifier(self.__getTimer, self.__timerUpdate))
        self.addNotificator(TimerNotifier(self.__getStateTimer, self.__timerTick))

    def fini(self):
        self.onPrimeTimeStatusUpdated.clear()
        self.onCosmicConfigChanged.clear()
        self.onStatusTick.clear()
        self.clearNotification()
        self.__clear()
        self.__disableSettingsCtrl.fini()
        self.__disableSettingsCtrl = None
        super(CosmicEventBattleController, self).fini()
        return

    def onDisconnected(self):
        super(CosmicEventBattleController, self).onDisconnected()
        self.__disableSettingsCtrl.onDisconnected()
        self.__clear()

    def onAvatarBecomePlayer(self):
        super(CosmicEventBattleController, self).onAvatarBecomePlayer()
        self.__disableSettingsCtrl.onAvatarBecomePlayer()
        self.__clear()

    def onAccountBecomePlayer(self):
        super(CosmicEventBattleController, self).onAccountBecomePlayer()
        self.__onServerSettingsChanged(self.__lobbyContext.getServerSettings())
        self.__disableSettingsCtrl.onAccountBecomePlayer()

    def onLobbyInited(self, event):
        super(CosmicEventBattleController, self).onLobbyInited(event)
        self.__disableSettingsCtrl.onLobbyInited(event)
        g_eventBus.addListener(events.CosmicEvent.OPEN_COSMIC, self.__onOpenEventPrb, scope=EVENT_BUS_SCOPE.LOBBY)

    @adisp.adisp_process
    def switchPrb(self):
        if not self.isEnabled:
            return
        else:
            prbDispatcher = g_prbLoader.getDispatcher()
            if prbDispatcher is not None:
                entityType = prbDispatcher.getEntity().getEntityType()
                if entityType == QUEUE_TYPE.COSMIC_EVENT:
                    self.openEventLobby()
                else:
                    yield prbDispatcher.doSelectAction(PrbAction(prb_config.PREBATTLE_ACTION_NAME.COSMIC_EVENT))
            return

    def onPrbEnter(self):
        CosmicHangarSounds.playCosmicPrbEnter()
        g_eventBus.addListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY, priority=EventPriority.VERY_LOW)

    def onPrbLeave(self):
        CosmicHangarSounds.playCosmicPrbExit()
        g_eventBus.removeListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY)
        self.closeEventLobby()
        self.closePostBattleScreen()

    def isAvailable(self):
        return self.isEnabled and not self.isFrozen() and self.getCurrentSeason() is not None

    def isTemporaryUnavailable(self):
        return self.getCurrentSeason() is not None and (not self.isEnabled or not self.isBattleAvailable())

    def isBattleAvailable(self):
        return self.__cosmicEventConfig.isBattleEnabled if self.__cosmicEventConfig else False

    def isFrozen(self):
        primeTimeStatus = self.getPrimeTimeStatus()[0]
        return primeTimeStatus != PrimeTimeStatus.AVAILABLE

    def getModeSettings(self):
        if self.__cosmicEventConfig is None:
            self.__setCosmicEventConfig(self.__lobbyContext.getServerSettings())
        return self.__cosmicEventConfig

    def openQueueView(self):
        from cosmic_event.gui.impl.lobby.queue_view.queue_view import QueueView
        g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(R.views.cosmic_event.lobby.queue_view.QueueView(), QueueView, ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)

    def closeRewardScreen(self):
        contentID = R.views.cosmic_event.lobby.rewards_view.RewardsView()
        self.__closeCosmicView(contentID)

    def closeEventLobby(self):
        contentID = R.views.cosmic_event.lobby.cosmic_lobby_view.CosmicLobbyView()
        self.__closeCosmicView(contentID)

    def closePostBattleScreen(self):
        contentID = R.views.cosmic_event.lobby.cosmic_post_battle.CosmicPostBattleView()
        self.__closeCosmicView(contentID)

    def openEventLobby(self, *args, **kwargs):
        uiLoader = dependency.instance(IGuiLoader)
        contentID = R.views.cosmic_event.lobby.cosmic_lobby_view.CosmicLobbyView()
        if uiLoader.windowsManager.getViewByLayoutID(contentID) is None:
            from cosmic_event.gui.impl.lobby.cosmic_lobby_view.cosmic_lobby_view import CosmicLobbyView
            g_eventBus.handleEvent(events.LoadGuiImplViewEvent(GuiImplViewLoadParams(layoutID=contentID, viewClass=CosmicLobbyView, scope=ScopeTemplates.LOBBY_SUB_SCOPE)), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def getTokenProgressionID(self):
        return self.__cosmicEventConfig.rewardSettings.get('rewardToken') if self.__cosmicEventConfig else ''

    def getProgressionQuestPrefix(self):
        return self.__cosmicEventConfig.rewardSettings.get('questPrefix') if self.__cosmicEventConfig else ''

    def getVehicleRentQuestID(self):
        return self.__cosmicEventConfig.vehicleRentQuestID if self.__cosmicEventConfig else ''

    def getProgressionFinishedToken(self):
        return self.__cosmicEventConfig.progressionFinishedToken if self.__cosmicEventConfig else ''

    def isCosmicMode(self):
        prbDispatcher = g_prbLoader.getDispatcher()
        if prbDispatcher is None:
            return False
        else:
            state = prbDispatcher.getFunctionalState()
            isInPreQueue = state.isInPreQueue(cosmic_constants.QUEUE_TYPE.COSMIC_EVENT)
            isInUnit = state.isInUnit(cosmic_constants.PREBATTLE_TYPE.COSMIC_EVENT)
            return isInUnit or isInPreQueue

    def _isEnabled(self):
        return self.getModeSettings().isEnabled

    @ifEnabled
    @ifCosmicPrbActive
    def __viewLoaded(self, event):
        if event.alias == VIEW_ALIAS.LOBBY_HANGAR:
            self.openEventLobby()

    def __setCosmicEventConfig(self, serverSettings):
        settings = serverSettings.getSettings()
        if COSMIC_EVENT_GAME_PARAMS_KEY in settings:
            self.__cosmicEventConfig = makeTupleByDict(CosmicEventConfig, settings[COSMIC_EVENT_GAME_PARAMS_KEY])
        else:
            self.__cosmicEventConfig = CosmicEventConfig.defaults()

    def __onServerSettingsChanged(self, serverSettings):
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateCosmicEventSettings
        self.__serverSettings = serverSettings
        self.__serverSettings.onServerSettingsChange += self.__updateCosmicEventSettings
        self.__setCosmicEventConfig(serverSettings)
        return

    def __closeCosmicView(self, contentID):
        uiLoader = dependency.instance(IGuiLoader)
        view = uiLoader.windowsManager.getViewByLayoutID(contentID)
        if view is not None:
            view.destroyWindow()
        return

    def __updateCosmicEventSettings(self, ssDiff):
        if COSMIC_EVENT_GAME_PARAMS_KEY in ssDiff:
            wasSuspended = self.isTemporaryUnavailable()
            self.__cosmicEventConfig = makeTupleByDict(CosmicEventConfig, ssDiff[COSMIC_EVENT_GAME_PARAMS_KEY])
            isSuspended = self.isTemporaryUnavailable()
            if isSuspended is not wasSuspended:
                eventType = EVENT_STATES.SUSPEND if isSuspended else EVENT_STATES.RESUME
                self.__triggerEventStateNotification(eventType)
            self.__resetTimer()
            self.onCosmicConfigChanged()
            uiLoader = dependency.instance(IGuiLoader)
            contentID = R.views.lobby.mode_selector.ModeSelectorView()
            view = uiLoader.windowsManager.getViewByLayoutID(contentID)
            if view:
                view.refresh()

    def __triggerEventStateNotification(self, eventType):
        self.__systemMessages.proto.serviceChannel.pushClientMessage({'state': eventType}, SCH_CLIENT_MSG_TYPE.COSMIC_EVENT_STATE)

    def __getActiveSeason(self):
        return self.getCurrentSeason() or self.getNextSeason()

    def __showStartedNotification(self):
        self.__triggerEventStateNotification(EVENT_STATES.START)
        setEventStartedNotificationViewed(True)

    def __triggerSeasonStateNotification(self):
        if self.__isPrimeTime:
            isSuspended = self.isTemporaryUnavailable()
            if not isSuspended:
                if not isEventStartedNotificationViewed():
                    self.__showStartedNotification()
            return
        else:
            wasLastSeason = self.__getActiveSeason() is None
            if wasLastSeason:
                self.__triggerEventStateNotification(EVENT_STATES.FINISH)
            return

    def __clear(self):
        self.stopNotification()
        g_eventBus.removeListener(events.ViewEventType.LOAD_VIEW, self.__viewLoaded, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.CosmicEvent.OPEN_COSMIC, self.__onOpenEventPrb, scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__serverSettings is not None:
            self.__serverSettings.onServerSettingsChange -= self.__updateCosmicEventSettings
        self.__serverSettings = None
        self.__cosmicEventConfig = None
        return

    def __getTimer(self):
        _, timeLeft, _ = self.getPrimeTimeStatus()
        return timeLeft + 1 if timeLeft > 0 else time_utils.ONE_MINUTE

    def __getStateTimer(self):
        return time_utils.ONE_MINUTE

    def __resetTimer(self):
        self.startNotification()
        self.__timerUpdate()
        self.__timerTick()

    def __timerUpdate(self):
        status, _, isPrimeTime = self.getPrimeTimeStatus()
        if isPrimeTime and self.__isPrimeTime:
            if not isEventStartedNotificationViewed():
                self.__showStartedNotification()
        elif isPrimeTime is not self.__isPrimeTime:
            self.__isPrimeTime = isPrimeTime
            self.__triggerSeasonStateNotification()
        self.onPrimeTimeStatusUpdated(status)

    def __timerTick(self):
        self.onStatusTick()

    def __onOpenEventPrb(self, *_, **__):
        self.switchPrb()

    def getLobbyRoute(self):
        return self.lobbyViewRoute

    def setLobbyRoute(self, route, notify=False):
        if self.lobbyViewRoute != route:
            self.lobbyViewRoute = route
            if notify:
                self.onLobbyRouteChange(route)

    def isVehicleRentQuest(self, questID):
        return questID == self.getVehicleRentQuestID()
