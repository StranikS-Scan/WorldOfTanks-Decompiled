# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/user_missions/states.py
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.tab_id import TabId
from gui.impl.gen.view_models.views.lobby.user_missions.info_page_model import InfoPageModel
from gui.impl.lobby.common.info_view import getInfoWindowProc, createContentData
from gui.impl.lobby.user_missions.info_page_view import InfoPageView
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription, LobbyState
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import UserMissionsEvent
from helpers.events_handler import EventsHandler
from shared_utils import first

def registerStates(machine):
    machine.addState(UserMissionsState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(UserMissionsState))


def _onMoreInfoRequested():
    getInfoWindowProc(R.views.mono.user_missions.info_page(), createContentData(InfoPageView, InfoPageModel)).show()


@SubScopeSubLayerState.parentOf
class UserMissionsState(SFViewLobbyState, EventsHandler):
    STATE_ID = VIEW_ALIAS.USER_MISSIONS_HUB_CONTAINER
    VIEW_KEY = ViewKey(VIEW_ALIAS.USER_MISSIONS_HUB_CONTAINER)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(UserMissionsState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerStates(self):
        self.addChildState(_BasicMissionTab(StateFlags.INITIAL))
        self.addChildState(_CommonMissionTab())

    def registerTransitions(self):
        self.addNavigationTransition(self, TransitionType.EXTERNAL)

    def serializeParams(self):
        return self.__cachedParams

    def _getListeners(self):
        return ((UserMissionsEvent.CHANGE_TAB, self.__onTabChanged, EVENT_BUS_SCOPE.LOBBY),)

    def _onEntered(self, event):
        super(UserMissionsState, self)._onEntered(event)
        self._subscribe()
        self.__cachedParams = event.params
        g_eventBus.handleEvent(UserMissionsEvent(UserMissionsEvent.TRANSITION_TO_MISSION, tabID=event.params.get('tab'), questId=event.params.get('questId'), showMissionDetails=event.params.get('showMissionDetails'), eventID=event.params.get('eventID'), groupID=event.params.get('groupID')), EVENT_BUS_SCOPE.LOBBY)

    def _onExited(self):
        super(UserMissionsState, self)._onExited()
        self._unsubscribe()
        self.__cachedParams = {}

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}

    def __onTabChanged(self, event):
        self.__cachedParams['tab'] = event.tabID
        childState = first(self.getChildren(lambda n: isinstance(n, MISSION_TABS) and n.TAB_ID == event.tabID))
        if childState:
            childState.goTo()


@UserMissionsState.parentOf
class _BasicMissionTab(LobbyState):
    STATE_ID = TabId.BASIC
    TAB_ID = TabId.BASIC
    LOBBY_STATE_DESCR = LobbyStateDescription(title=backport.text(R.strings.pages.titles.userMissions()), infos=(LobbyStateDescription.Info(tooltipHeader=backport.text(R.strings.user_missions.tooltip.hub.info_button.header()), tooltipBody=backport.text(R.strings.user_missions.tooltip.hub.info_button.body()), onMoreInfoRequested=_onMoreInfoRequested),))

    def registerTransitions(self):
        lsm = self.getMachine()
        commonTab = lsm.getStateByCls(_CommonMissionTab)
        self.addNavigationTransition(commonTab)

    def getNavigationDescription(self):
        return self.LOBBY_STATE_DESCR


@UserMissionsState.parentOf
class _CommonMissionTab(LobbyState):
    STATE_ID = TabId.COMMON
    TAB_ID = TabId.COMMON
    LOBBY_STATE_DESCR = LobbyStateDescription(title=backport.text(R.strings.pages.titles.userMissions()))

    def getNavigationDescription(self):
        return self.LOBBY_STATE_DESCR

    def registerTransitions(self):
        lsm = self.getMachine()
        basicTab = lsm.getStateByCls(_BasicMissionTab)
        self.addNavigationTransition(basicTab)


MISSION_TABS = (_BasicMissionTab, _CommonMissionTab)
