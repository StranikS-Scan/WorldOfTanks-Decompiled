# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/user_missions/states.py
from __future__ import absolute_import
from account_helpers.AccountSettings import ChallengesMissions
from frameworks_common.state_machine import StateFlags
from frameworks_common.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.challenges.challenges_helpers import getChallengesInfoUrl, getSettings, setSettings
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.user_missions.hub.tabs.tab_id import TabId
from gui.impl.gen.view_models.views.lobby.user_missions.info_page_model import InfoPageModel
from gui.impl.lobby.common.info_view import getInfoWindowProc, createContentData
from gui.impl.lobby.user_missions.info_page_view import InfoPageView
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyStateDescription, LobbyState, getNavigationDescriptionSafe
from gui.shared import EVENT_BUS_SCOPE, g_eventBus
from gui.shared.events import UserMissionsEvent
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from helpers.events_handler import EventsHandler
from shared_utils import first
from skeletons.gui.impl import IGuiLoader

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

    @classmethod
    def goTo(cls, tab=None, subTab=None, eventID=None, groupID=None, marathonPrefix=None, anchor=None, showMissionDetails=None, questId=None, challengeID=None):
        super(UserMissionsState, cls).goTo(tab=tab, subTab=subTab, eventID=eventID, groupID=groupID, marathonPrefix=marathonPrefix, anchor=anchor, showMissionDetails=showMissionDetails, questId=questId, challengeID=challengeID)

    def registerStates(self):
        self.addChildState(_EntryState(StateFlags.INITIAL))
        self.addChildState(_BasicMissionTab())
        self.addChildState(_CommonMissionTab())
        self.addChildState(_ChallengeMissionTab())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.vehicle_preview.states import StylePreviewState
        from gui.impl.lobby.vehicle_hub.states import OverviewState
        lsm = self.getMachine()
        self.addNavigationTransition(self, TransitionType.EXTERNAL)
        self.addNavigationTransition(lsm.getStateByCls(StylePreviewState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        for state in self.getChildrenStates():
            self.addNavigationTransition(state)

    def getBackNavigationDescription(self, params):
        childState = self.__findChildState(params.get('tab'))
        return getNavigationDescriptionSafe(childState).title if childState is not None else LobbyStateDescription().title

    def serializeParams(self):
        childState = self.__findChildState(self.__cachedParams.get('tab'))
        if childState is not None:
            self.__cachedParams.update(childState.serializeParams())
        return self.__cachedParams

    def _getListeners(self):
        return ((UserMissionsEvent.CHANGE_TAB, self.__onTabChanged, EVENT_BUS_SCOPE.LOBBY),)

    def _onEntered(self, event):
        super(UserMissionsState, self)._onEntered(event)
        self._subscribe()
        self.__cachedParams = event.params
        childState = self.__findChildState(event.params.get('tab'))
        if childState is not None:
            childState.goTo(**self.__cachedParams)
        return

    def _onExited(self):
        super(UserMissionsState, self)._onExited()
        self._unsubscribe()
        self.__cachedParams = {}

    def compareParams(self, params, otherParams):
        return True if params.get('tab') == TabId.CHALLENGES else super(UserMissionsState, self).compareParams(params, otherParams)

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}

    def __onTabChanged(self, event):
        targetTab = event.tabID
        self.__cachedParams['tab'] = targetTab
        childState = self.__findChildState(targetTab)
        if childState is not None:
            childState.goTo(**self.__cachedParams)
        return

    def __findChildState(self, tabID):
        return None if tabID is None else first(self.getChildren(lambda n: isinstance(n, MISSION_TABS) and tabID == n.TAB_ID))


@UserMissionsState.parentOf
class _EntryState(LobbyState):
    STATE_ID = 'entry'


@UserMissionsState.parentOf
class _BasicMissionTab(LobbyState):
    STATE_ID = TabId.BASIC
    TAB_ID = TabId.BASIC
    LOBBY_STATE_DESCR = LobbyStateDescription(title=backport.text(R.strings.pages.titles.userMissions()), infos=(LobbyStateDescription.Info(tooltipHeader=backport.text(R.strings.user_missions.tooltip.hub.info_button.header()), tooltipBody=backport.text(R.strings.user_missions.tooltip.hub.info_button.body()), onMoreInfoRequested=_onMoreInfoRequested),))

    def registerTransitions(self):
        from gui.impl.lobby.personal_missions_30.state import ProgressionState
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(_CommonMissionTab))
        self.addNavigationTransition(lsm.getStateByCls(_ChallengeMissionTab))
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(ProgressionState), record=True)

    def getNavigationDescription(self):
        return self.LOBBY_STATE_DESCR


@UserMissionsState.parentOf
class _CommonMissionTab(LobbyState):
    STATE_ID = TabId.COMMON
    TAB_ID = TabId.COMMON
    LOBBY_STATE_DESCR = LobbyStateDescription(title=backport.text(R.strings.pages.titles.userMissions()))

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_CommonMissionTab, self).__init__(flags=flags)
        self.__cachedParams = {}

    def getNavigationDescription(self):
        return self.LOBBY_STATE_DESCR

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(_BasicMissionTab))
        self.addNavigationTransition(lsm.getStateByCls(_ChallengeMissionTab))
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)

    def _onEntered(self, event):
        super(_CommonMissionTab, self)._onEntered(event)
        self.__cachedParams = event.params
        g_eventBus.handleEvent(UserMissionsEvent(UserMissionsEvent.TRANSITION_TO_MISSION, tabID=event.params.get('tab'), questId=event.params.get('questId'), showMissionDetails=event.params.get('showMissionDetails'), eventID=event.params.get('eventID'), groupID=event.params.get('groupID')), EVENT_BUS_SCOPE.LOBBY)

    def _onExited(self):
        super(_CommonMissionTab, self)._onExited()
        self.__cachedParams = {}


@UserMissionsState.parentOf
class _ChallengeMissionTab(LobbyState):
    STATE_ID = TabId.CHALLENGES
    TAB_ID = TabId.CHALLENGES
    LOBBY_STATE_DESCR = LobbyStateDescription(title=backport.text(R.strings.user_missions.hub.challenge_missions.header()), infos=(LobbyStateDescription.Info(tooltipHeader=backport.text(R.strings.user_missions.hub.challenge_missions.tooltip.info_button()), tooltipBody=backport.text(R.strings.user_missions.tooltip.hub.info_button.body()), onMoreInfoRequested=lambda : showBrowserOverlayView(getChallengesInfoUrl(), VIEW_ALIAS.CHALLENGES_INFO)),))
    __guiLoader = dependency.descriptor(IGuiLoader)

    def registerTransitions(self):
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(_BasicMissionTab))
        self.addNavigationTransition(lsm.getStateByCls(_CommonMissionTab))

    def getNavigationDescription(self):
        return self.LOBBY_STATE_DESCR

    def serializeParams(self):
        params = {}
        views = self.__guiLoader.windowsManager.findViews(lambda view: view.layoutID == R.views.mono.user_missions.hub())
        if views:
            hubView = first(views)
            challengesTabView = hubView.getTabView(self.TAB_ID)
            if challengesTabView is not None:
                selectedChallenge = challengesTabView.selectedChallenge
                if selectedChallenge is not None:
                    params['challengeID'] = selectedChallenge.challengeID
        return params

    def _onEntered(self, event):
        super(_ChallengeMissionTab, self)._onEntered(event)
        if not getSettings(ChallengesMissions.CHALLENGES_INFO_SHOWN):
            showBrowserOverlayView(getChallengesInfoUrl(), VIEW_ALIAS.CHALLENGES_INFO)
            setSettings(ChallengesMissions.CHALLENGES_INFO_SHOWN, True)


MISSION_TABS = (_BasicMissionTab, _CommonMissionTab, _ChallengeMissionTab)
