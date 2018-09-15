# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/missions/missions_provider.py
import BigWorld
from adisp import process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui import DialogsInterface
from gui.Scaleform.framework import g_entitiesFactories
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.prb_control.entities.listener import IGlobalListener
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
from gui.Scaleform.genConsts.QUESTS_ALIASES import QUESTS_ALIASES
from gui.shared.personality import ServicesLocator
TIME_TO_UPDATE_HANGAR_FLAG = 60

class ClientMissionsProvider(IGlobalListener):
    """
    Handle Missions page events
    Check server settings for isElenEnabled flag change
    and show info popup if ELEN is disabled
    """
    lobbyContext = dependency.descriptor(ILobbyContext)

    def __init__(self):
        super(ClientMissionsProvider, self).__init__()
        self.__formActive = False
        self.__elenActive = False
        self.__elenFlagTimerID = None
        self.__elenTimerID = None
        return

    def start(self):
        self.startGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange += self.__onServerSettingChanged
        g_eventBus.addListener(events.MissionsEvent.ON_ACTIVATE, self.__onMissionsActivate, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(events.MissionsEvent.ON_DEACTIVATE, self.__onMissionsDeactivate, EVENT_BUS_SCOPE.LOBBY)
        self.__startEventboardsTimer()

    def stop(self):
        self.stopGlobalListening()
        self.lobbyContext.getServerSettings().onServerSettingsChange -= self.__onServerSettingChanged
        g_eventBus.removeListener(events.MissionsEvent.ON_ACTIVATE, self.__onMissionsActivate, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.MissionsEvent.ON_TAB_CHANGED, self.__onMissionsTabChanged, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.removeListener(events.MissionsEvent.ON_DEACTIVATE, self.__onMissionsDeactivate, EVENT_BUS_SCOPE.LOBBY)
        self.__stopEventboardsTimer()

    def __onServerSettingChanged(self, diff):
        """
        Check server settings for isElenEnabled flag change
        and show info popup if ELEN is disabled
        """
        if self.__formActive:
            if 'elenSettings' in diff and 'isElenEnabled' in diff['elenSettings']:
                enabled = diff['elenSettings']['isElenEnabled']
                if not enabled:
                    if self.__elenActive:
                        self.__showElenPopupDlg()
                else:
                    g_eventBus.handleEvent(events.MissionsEvent(events.MissionsEvent.PAGE_INVALIDATE), scope=EVENT_BUS_SCOPE.LOBBY)

    @process
    def __showElenPopupDlg(self):
        yield DialogsInterface.showI18nInfoDialog('elenDisabled')
        g_eventBus.handleEvent(g_entitiesFactories.makeLoadEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def __onMissionsActivate(self, _):
        self.__formActive = True

    def __onMissionsDeactivate(self, _):
        self.__formActive = False

    def __onMissionsTabChanged(self, event):
        self.__elenActive = event.ctx == QUESTS_ALIASES.MISSIONS_EVENT_BOARDS_VIEW_PY_ALIAS

    def __startEventboardsTimer(self):
        """
        Start Eventboards timer for get new events and hangar flag when player in lobby, 1.0 sec for first request
        """
        if self.__elenTimerID is not None or self.__elenFlagTimerID is not None:
            self.__stopEventboardsTimer()
        timeToUpdate = ServicesLocator.lobbyContext.getServerSettings().elenUpdateInterval()
        self.__elenTimerID = BigWorld.callback(timeToUpdate, self.__updateEventboardsTimer)
        self.__elenFlagTimerID = BigWorld.callback(TIME_TO_UPDATE_HANGAR_FLAG, self.__updateEventboardsFlagTimer)
        return

    def __stopEventboardsTimer(self):
        """
        Stop Eventboards timer for get new events and hangar flag when player go to battle
        """
        if self.__elenTimerID is not None:
            BigWorld.cancelCallback(self.__elenTimerID)
        if self.__elenFlagTimerID is not None:
            BigWorld.cancelCallback(self.__elenFlagTimerID)
        self.__elenTimerID = None
        self.__elenFlagTimerID = None
        return

    def __updateEventboardsTimer(self):
        """
        Update Eventsboard info with request events static settings
        """
        timeToUpdate = ServicesLocator.lobbyContext.getServerSettings().elenUpdateInterval()
        self.__elenTimerID = BigWorld.callback(timeToUpdate, self.__updateEventboardsTimer)
        self.__requestEventboardsData()

    def __updateEventboardsFlagTimer(self):
        """
        Update Eventsboard hangar flag
        """
        self.__elenFlagTimerID = BigWorld.callback(TIME_TO_UPDATE_HANGAR_FLAG, self.__updateEventboardsFlagTimer)
        if ServicesLocator.lobbyContext.getServerSettings().isElenEnabled():
            ServicesLocator.eventsController.updateHangarFlag()

    @process
    def __requestEventboardsData(self):
        """
        Request events static settings from WG ELEN, only if enabled
        """
        if ServicesLocator.lobbyContext.getServerSettings().isElenEnabled():
            yield ServicesLocator.eventsController.getEvents(onlySettings=True)
