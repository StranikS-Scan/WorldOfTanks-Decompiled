# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/universal_flag_entry_point_controller/__init__.py
import logging
from Event import EventManager, Event
from gui.game_control.universal_flag_entry_point_controller.config import UniversalFlagConfig, MissionsMarathonTarget, FullScreenBrowserTarget, ShopPageTarget, NopeTarget, UniversalFlagState, universalFlagConfigSchema
from skeletons.gui.game_control import ILobbyCdnController
from gui.impl.lobby.universal_web_event_window.universal_web_event_view import UniversalWebEventWindow
from gui.server_events.events_dispatcher import showMissionsMarathon
from gui.shared.event_dispatcher import showShop
from constants import Configs
from gui.shared.utils.scheduled_notifications import SimpleNotifier
from helpers import dependency, time_utils
from skeletons.gui.game_control import IUniversalFlagEntryPointController
from helpers.events_handler import EventsHandler
from skeletons.gui.lobby_context import ILobbyContext
from helpers.server_settings import serverSettingsChangeListener
from gui.ClientUpdateManager import g_clientUpdateManager
from skeletons.gui.shared import IItemsCache
from skeletons.gui.game_control import IMarathonEventsController
from helpers import i18n
_logger = logging.getLogger(__name__)

class UniversalFlagEntryPointController(IUniversalFlagEntryPointController, EventsHandler):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    __marathonController = dependency.descriptor(IMarathonEventsController)
    __lobbyCdn = dependency.descriptor(ILobbyCdnController)

    def __init__(self):
        super(UniversalFlagEntryPointController, self).__init__()
        self.__config = UniversalFlagConfig()
        self.__eventsManager = EventManager()
        self.onDataUpdated = Event(self.__eventsManager)
        self.__notifier = SimpleNotifier(self.__getNextPhaseTimeDelta, self.__onNextPhaseTime)
        self.__eventCaption = ''
        self.__eventDescription = ''
        self.__flagBackground = IUniversalFlagEntryPointController.FlagBackground()
        self.__timerIconType = IUniversalFlagEntryPointController.TimerIconType.NONE
        self.__timerTime = 0
        self.__timerText = ''
        self.__tooltipBackground = ''
        self.__activeStateIndex = None
        return

    @property
    def visibilityState(self):
        if not self.__config.isEnabled:
            return IUniversalFlagEntryPointController.VisibilityState.HIDDEN
        elif self.__config.isPaused:
            return IUniversalFlagEntryPointController.VisibilityState.MAINTANANCE
        elif self.__activeStateIndex is None:
            return IUniversalFlagEntryPointController.VisibilityState.HIDDEN
        else:
            bg = self.__flagBackground
            return IUniversalFlagEntryPointController.VisibilityState.HIDDEN if not bg.active or not bg.activeHover or not bg.disabled or not bg.activeHover else IUniversalFlagEntryPointController.VisibilityState.SHOWN

    def openEvent(self):
        target = self.__config.target
        if isinstance(target, NopeTarget):
            return
        else:
            if isinstance(target, MissionsMarathonTarget):
                if self.__marathonController.getMarathon(target.marathonPrefix) is not None:
                    showMissionsMarathon(target.marathonPrefix)
                else:
                    _logger.error("Marathon %s isn't found. Check universal flag config", target.marathonPrefix)
            elif isinstance(target, FullScreenBrowserTarget):
                window = UniversalWebEventWindow(target.url)
                window.load()
            elif isinstance(target, ShopPageTarget):
                showShop(path=target.relativeUrl)
            else:
                _logger.error('Unknown flag target. Check universal flag config')
            return

    @property
    def eventCaption(self):
        return self.__eventCaption

    @property
    def eventDescription(self):
        return self.__eventDescription

    @property
    def flagBackground(self):
        return self.__flagBackground

    @property
    def timerTime(self):
        return self.__timerTime

    @property
    def timerIconType(self):
        return self.__timerIconType

    @property
    def timerText(self):
        return self.__timerText

    @property
    def tooltipBackground(self):
        return self.__tooltipBackground

    def _getEvents(self):
        return ((self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged), (self.__lobbyCdn.onSynced, self.__onCdnSynced))

    def onLobbyInited(self, event):
        self._subscribe()
        self.__readServerConfig()
        self.__notifier.startNotification()

    def onAccountBecomeNonPlayer(self):
        self._unsubscribe()
        self.__eventsManager.clear()
        self.__notifier.stopNotification()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def fini(self):
        self._unsubscribe()
        self.__eventsManager.clear()
        self.__notifier.stopNotification()
        self.__notifier.clear()
        g_clientUpdateManager.removeObjectCallbacks(self)

    def __getNextPhaseTimeDelta(self):
        if not self.__config.isEnabled or self.__config.isPaused:
            return 0
        time = time_utils.getServerUTCTime()
        stateChangesTime = []
        for state in self.__config.states:
            stateChangesTime.append(state.startTime)
            stateChangesTime.append(state.finishTime)

        for changeTime in sorted(stateChangesTime):
            if time < changeTime:
                return changeTime - time + 1

    def __onNextPhaseTime(self):
        self.__reloadState()

    @serverSettingsChangeListener(Configs.UNIVERSAL_FLAG_ENTRY_POINT_CONFIG.value)
    def __onServerSettingsChanged(self, diff):
        self.__readServerConfig()
        self.__notifier.startNotification()

    def __onCdnSynced(self):
        self.__reloadState()

    def __readServerConfig(self):
        settings = self.__lobbyContext.getServerSettings().universalFlagEntryPointConfig
        if 'isEnabled' not in settings or not settings['isEnabled']:
            self.__config = UniversalFlagConfig()
            self.__reloadState()
            return
        else:
            self.__config = universalFlagConfigSchema.deserialize(settings, silent=True)
            if self.__config is None:
                _logger.exception('Wrong flag config structure.')
                self.__config = UniversalFlagConfig()
            self.__reloadState()
            return

    def __formatString(self, s):
        return s if not s.startswith('#') else i18n.makeString(s)

    def __reloadState(self):
        self.__eventCaption = ''
        self.__eventDescription = ''
        self.__flagBackground = IUniversalFlagEntryPointController.FlagBackground()
        self.__timerIconType = IUniversalFlagEntryPointController.TimerIconType.NONE
        self.__timerTime = 0
        self.__timerText = ''
        self.__tooltipBackground = ''
        time = time_utils.getServerUTCTime()
        self.__activeStateIndex = -1
        while 1:
            self.__activeStateIndex + 1 < len(self.__config.states) and self.__config.states[self.__activeStateIndex + 1].startTime <= time and self.__activeStateIndex += 1

        if self.__activeStateIndex == -1 or time >= self.__config.states[self.__activeStateIndex].finishTime:
            self.__activeStateIndex = None
            self.onDataUpdated()
            return
        else:
            currentState = self.__config.states[self.__activeStateIndex]
            self.__eventCaption = self.__formatString(currentState.caption)
            self.__eventDescription = self.__formatString(currentState.description)
            self.__timerIconType = currentState.timer.iconType
            self.__timerTime = currentState.timer.time
            self.__timerText = self.__formatString(currentState.timer.text)
            bg = self.__flagBackground
            bg.disabled = self.__lobbyCdn.resolveCdnImage(currentState.background.disabled)
            bg.disabledHover = self.__lobbyCdn.resolveCdnImage(currentState.background.disabledHover)
            bg.active = self.__lobbyCdn.resolveCdnImage(currentState.background.active)
            bg.activeHover = self.__lobbyCdn.resolveCdnImage(currentState.background.activeHover)
            if currentState.tooltipBackground:
                self.__tooltipBackground = self.__lobbyCdn.resolveCdnImage(currentState.tooltipBackground)
            self.onDataUpdated()
            return
