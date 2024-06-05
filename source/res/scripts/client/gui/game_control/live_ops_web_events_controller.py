# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/live_ops_web_events_controller.py
import BigWorld
from enum import Enum
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.server_events import caches
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from skeletons.gui.game_control import ILiveOpsWebEventsController
from helpers import dependency, time_utils
from skeletons.gui.lobby_context import ILobbyContext
from Event import Event, EventManager
from constants import Configs
from account_helpers.AccountSettings import AccountSettings, LIVE_OPS_WEB_EVENTS_COUNTERS, LIVE_OPS_WEB_EVENTS_UI_FLAGS

class EventState(Enum):
    UNDEFINED = 'undefined'
    PRE_EVENT = 'preEvent'
    EVENT_ACTIVE = 'eventActive'
    POST_EVENT = 'postEvent'


_LOW_QUALITY_PRESETS = ('LOW', 'MIN')

class LiveOpsWebEventsController(Notifiable, ILiveOpsWebEventsController):
    __lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(LiveOpsWebEventsController, self).__init__()
        self.__em = EventManager()
        self.onSettingsChanged = Event(self.__em)
        self.onEventStateChanged = Event(self.__em)
        self.__previousEventState = None
        self.__currentEventState = None
        self.__isHighQualityPreset = None
        return

    def init(self):
        self.addNotificator(SimpleNotifier(self.__getTimerDelta, self.__timerUpdate))

    def onLobbyInited(self, event):
        self.startNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingsChange
        self.__currentEventState = self.__getEventState()

    def onAccountBecomeNonPlayer(self):
        self.__clear()

    def onDisconnected(self):
        self.__clear()

    def fini(self):
        self.__clear()
        self.clearNotification()

    @property
    def eventConfig(self):
        return self.__lobbyContext.getServerSettings().liveOpsWebEventsConfig

    @property
    def eventUniqueName(self):
        return self.eventConfig.eventUniqueName

    def isEnabled(self):
        return self.eventConfig.isEnabled

    @property
    def eventUrl(self):
        return self.eventConfig.url

    @property
    def preEventStart(self):
        return self.eventConfig.preEventStart

    @property
    def eventStart(self):
        return self.eventConfig.eventStart

    @property
    def postEventEnd(self):
        return self.eventConfig.postEventEnd

    @property
    def eventEnd(self):
        return self.eventConfig.eventEnd

    @property
    def eventState(self):
        return self.__currentEventState

    @property
    def previousEventState(self):
        return self.__previousEventState

    @property
    def isEntryPointSmall(self):
        return self.eventConfig.isEntryPointSmall

    @property
    def isHighQualityPreset(self):
        if self.__isHighQualityPreset is None:
            presetIdx = BigWorld.detectGraphicsPresetFromSystemSettings()
            lowQualityPresets = [ BigWorld.getSystemPerformancePresetIdFromName(pName) for pName in _LOW_QUALITY_PRESETS ]
            self.__isHighQualityPreset = presetIdx not in lowQualityPresets
        return self.__isHighQualityPreset

    def canShowHangarEntryPoint(self):
        return self.isEnabled() and self.eventState is not None

    def canShowEventsTab(self):
        return self.isEnabled() and self.eventState is not None

    def getEventTabVisited(self):
        return AccountSettings.getCounters(LIVE_OPS_WEB_EVENTS_COUNTERS).get(self.eventUniqueName, 1)

    def markEventTabVisited(self):
        counters = AccountSettings.getCounters(LIVE_OPS_WEB_EVENTS_COUNTERS)
        counters.update({self.eventUniqueName: 0})
        AccountSettings.setCounters(LIVE_OPS_WEB_EVENTS_COUNTERS, counters)

    def getIsFirstEventEntry(self):
        return AccountSettings.getUIFlag(LIVE_OPS_WEB_EVENTS_UI_FLAGS).get(self.eventUniqueName, True)

    def markEventEntered(self):
        settings = AccountSettings.getUIFlag(LIVE_OPS_WEB_EVENTS_UI_FLAGS)
        settings.update({self.eventUniqueName: False})
        AccountSettings.setUIFlag(LIVE_OPS_WEB_EVENTS_UI_FLAGS, settings)

    def __clear(self):
        self.__isHighQualityPreset = None
        self.__currentEventState = None
        self.__previousEventState = None
        self.stopNotification()
        self.__lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingsChange
        self.__em.clear()
        return

    def __onServerSettingsChange(self, diff):
        if Configs.LIVE_OPS_EVENTS_CONFIG.value in diff:
            state = self.__getEventState()
            if state != self.__currentEventState:
                self.__previousEventState = self.__currentEventState
                self.__currentEventState = state
            self.onSettingsChanged()
            self.__updateSavedTab()
            self.__resetTimer()

    def __updateSavedTab(self):
        cachedTab = caches.getNavInfo().getMissionsTab()
        isLiveOpsTabLatest = cachedTab == QUESTS_ALIASES.LIVE_OPS_WEB_EVENTS_VIEW_PY_ALIAS
        isMarathonsTabLatest = cachedTab == QUESTS_ALIASES.MISSIONS_GROUPED_VIEW_PY_ALIAS
        canShowEventsTab = self.canShowEventsTab()
        if not canShowEventsTab and isLiveOpsTabLatest or canShowEventsTab and isMarathonsTabLatest:
            caches.getNavInfo().setMissionsTab(None)
        return

    def __getEventState(self):
        time = self.__getTimeNow()
        if 0 < self.preEventStart < time < self.eventStart:
            return EventState.PRE_EVENT
        elif self.eventStart < time < self.eventEnd:
            return EventState.EVENT_ACTIVE
        else:
            return EventState.POST_EVENT if self.eventEnd < time < self.postEventEnd else None

    def __getTimerDelta(self):
        if self.isEnabled():
            timeNow = self.__getTimeNow()
            startTime = 0
            if timeNow < self.preEventStart:
                startTime = self.preEventStart
            elif timeNow < self.eventStart:
                startTime = self.eventStart
            elif timeNow < self.eventEnd:
                startTime = self.eventEnd
            elif timeNow < self.postEventEnd:
                startTime = self.postEventEnd
            return max(0, startTime - timeNow)

    @staticmethod
    def __getTimeNow():
        return time_utils.getCurrentLocalServerTimestamp()

    def __timerUpdate(self):
        self.__previousEventState = self.__currentEventState
        self.__currentEventState = self.__getEventState()
        self.__updateSavedTab()
        self.onEventStateChanged()

    def __resetTimer(self):
        self.startNotification()
