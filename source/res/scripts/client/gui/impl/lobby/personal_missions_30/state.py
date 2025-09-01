# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/state.py
import logging
from collections import OrderedDict
import typing
import SoundGroups
from cgf_components.pm30_hangar_components import PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from frameworks.wulf import ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.user_missions.states import UserMissionsState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import OperationState, MissionCategory
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_model import MainScreenState
from gui.impl.lobby.hangar.states import HangarState
from gui.impl.lobby.personal_missions_30.camera_mover import PersonalMissions3CameraMover
from gui.impl.lobby.personal_missions_30.hangar_helpers import AssemblingManager
from gui.impl.lobby.personal_missions_30.personal_mission_constants import SoundsKeys, IntroKeys
from gui.impl.lobby.personal_missions_30.views_helpers import openInfoPageScreen, isIntroShown, getOperationStatus
from gui.impl.lobby.vehicle_hub.states import OverviewState, VehicleHubState
from gui.lobby_state_machine.states import SubScopeSubLayerState, LobbyStateDescription, LobbyState, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition, NavigationTransition
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showPM30IntroWindow, showPM30OperationIntroWindow
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroupConfig, SubhangarStateGroups
from helpers import dependency
from helpers.events_handler import EventsHandler
from personal_missions import PM_BRANCH
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.impl.lobby.personal_missions_30.main_view import MainView
    from gui.shared.events import NavigationEvent
_logger = logging.getLogger(__name__)
_OPAQUE_BACKGROUND_ALPHA = 1.0

def registerStates(machine):
    machine.addState(CampaignSelectorState())
    machine.addState(PersonalMissions3EntryState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(CampaignSelectorState))
    machine.addNavigationTransitionFromParent(machine.getStateByCls(PersonalMissions3EntryState))


@SubScopeSubLayerState.parentOf
class CampaignSelectorState(ViewLobbyState):
    STATE_ID = VIEW_ALIAS.CAMPAIGN_SELECTOR
    VIEW_KEY = ViewKey(VIEW_ALIAS.CAMPAIGN_SELECTOR)

    def registerTransitions(self):
        machine = self.getMachine()
        entryState = machine.getStateByCls(PersonalMissions3EntryState)
        self.addNavigationTransition(entryState, record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.campaign_selector()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=openInfoPageScreen, tooltipBody=backport.text(R.strings.personal_missions.pages.button.infopage.description())), LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.VIDEO, onMoreInfoRequested=lambda : showPM30IntroWindow(force=True), tooltipBody=backport.text(R.strings.personal_missions.pages.button.video.description()))))

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.campaignSelector())


@SubScopeSubLayerState.parentOf
class PersonalMissions3EntryState(LobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = 'personalMissions3Entry'
    __uiLoader = dependency.descriptor(IGuiLoader)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PersonalMissions3EntryState, self).__init__(flags)
        self.assemblingManager = None
        self.__cachedParams = {}
        return

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((SubhangarStateGroups.PersonalMissions,), PersonalMissions3CameraMover(callback=self.moveCamera))

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(_LoadingState(flags=StateFlags.INITIAL))
        lsm.addState(PersonalMissions3State())

    def serializeParams(self):
        mainView = self.__uiLoader.windowsManager.getViewByLayoutID(R.views.mono.personal_missions_30.main())
        return {'operationID': mainView.getOperationID(),
         'state': mainView.viewModel.getMainScreenState().value} if mainView and mainView.viewStatus == ViewStatus.LOADED else self.__cachedParams

    def _onEntered(self, event):
        super(PersonalMissions3EntryState, self)._onEntered(event)
        self.assemblingManager = AssemblingManager()
        self.__cachedParams = dict(event.params)

    def _onExited(self):
        self.assemblingManager.deactivate()
        self.assemblingManager.destroy()
        self.assemblingManager = None
        self.__cachedParams.clear()
        super(PersonalMissions3EntryState, self)._onExited()
        return

    def moveCamera(self):
        if self.__cachedParams:
            operationID = self.__cachedParams.get('operationID')
            state = self.__cachedParams.get('state')
            operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operationID)
            if state == MainScreenState.ASSEMBLING.value or operation.isFullCompleted():
                self.assemblingManager.switchCameraToFreePosition(instantly=True)
            elif self.assemblingManager.isSwitchingToTopCameraNeeded():
                self.assemblingManager.startTopCameraAnimation()
        else:
            _logger.error('PersonalMissions3EntryState cachedParams is empty')


@PersonalMissions3EntryState.parentOf
class _LoadingState(LobbyState, EventsHandler):
    STATE_ID = 'loading'
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LoadingState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(PersonalMissions3State))

    def _getListeners(self):
        return ((PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY, self.__onSubHangarReady, EVENT_BUS_SCOPE.LOBBY),)

    def _onEntered(self, event):
        super(_LoadingState, self)._onEntered(event)
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(_OPAQUE_BACKGROUND_ALPHA)
        self.__cachedParams = dict(event.params)
        if self.getParent().assemblingManager.isVehicleGOForOperationReady(self.__cachedParams.get('operationID')):
            self.__onSubHangarReady(self)
            self.getParent().moveCamera()
        else:
            self._subscribe()

    def _onExited(self):
        self.__cachedParams.clear()
        self._unsubscribe()
        super(_LoadingState, self)._onExited()

    def __onSubHangarReady(self, _):
        if self.__cachedParams.get('useBackNavigation', False):
            self.goBack()
        else:
            PersonalMissions3State.goTo(**self.__cachedParams)


@PersonalMissions3EntryState.parentOf
class PersonalMissions3State(ViewLobbyState):
    STATE_ID = VIEW_ALIAS.PERSONAL_MISSIONS_3
    VIEW_KEY = ViewKey(VIEW_ALIAS.PERSONAL_MISSIONS_3)
    __uiLoader = dependency.descriptor(IGuiLoader)
    __appLoader = dependency.descriptor(IAppLoader)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PersonalMissions3State, self).__init__(flags=flags)
        self.__isForcedLeave = False

    def _getViewLoadCtx(self, event):
        ctx = dict(event.params)
        ctx.pop('category', None)
        ctx['assemblingManager'] = self.getParent().assemblingManager
        return ctx

    def registerStates(self):
        self.addChildState(ProgressionState(flags=StateFlags.INITIAL))
        self.addChildState(MissionsState())
        self.addChildState(AssemblingState())

    def registerTransitions(self):
        machine = self.getMachine()
        progression = machine.getStateByCls(ProgressionState)
        userMissionsHub = machine.getStateByCls(UserMissionsState)
        missions = machine.getStateByCls(MissionsState)
        assembling = machine.getStateByCls(AssemblingState)
        vehicleHubOverview = machine.getStateByCls(OverviewState)
        self.addNavigationTransition(progression, record=True)
        self.addNavigationTransition(missions, record=True)
        self.addNavigationTransition(assembling, record=True)
        self.addNavigationTransition(userMissionsHub, record=True)
        self.addNavigationTransition(vehicleHubOverview, record=True)
        machine.getStateByCls(VehicleHubState).addNavigationTransition(self)
        missions.addGuardTransition(missions, self.__isAnimationPlayed)
        assembling.addGuardTransition(assembling, self.__isAnimationPlayed)
        self.addTransition(HijackTransition(HangarState, self.__isAnimationPlayed, transitionType=TransitionType.INTERNAL), self)
        missions.addTransition(HijackTransition(HangarState, self.__isAnimationPlayed, transitionType=TransitionType.INTERNAL), missions)
        assembling.addTransition(HijackTransition(HangarState, self.__isAnimationPlayed, transitionType=TransitionType.INTERNAL), assembling)

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.dashboard())

    def setForceLeave(self):
        self.__isForcedLeave = True

    def _onEntered(self, event):
        super(PersonalMissions3State, self)._onEntered(event)
        self.__isForcedLeave = False
        operationID = event.params['operationID']
        pm3Operations = OrderedDict(sorted(self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).items()))
        operation = pm3Operations[operationID]
        if not isIntroShown(IntroKeys.OPERATION_INTRO_VIEW.value % operation.getID()) and getOperationStatus(operation, pm3Operations) != OperationState.UNAVAILABLE:
            showPM30OperationIntroWindow(operation.getID())
        mainView = self.__uiLoader.windowsManager.getViewByLayoutID(R.views.mono.personal_missions_30.main())
        if mainView and self.getParent().assemblingManager.isVehicleGOForOperationReady(mainView.getOperationID()):
            mainView.initCurrentOperation()

    def _onExited(self):
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(_OPAQUE_BACKGROUND_ALPHA)
        super(PersonalMissions3State, self)._onExited()

    def __isAnimationPlayed(self, event):
        from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_model import AnimationState
        mainView = self.__uiLoader.windowsManager.getViewByLayoutID(R.views.mono.personal_missions_30.main())
        animationPlaying = (mainView.viewModel.getAnimationState() != AnimationState.IDLE or mainView.viewModel.getCameraFlightInProgress()) and not self.__isForcedLeave
        return animationPlaying


class _SpecialPM3Transition(NavigationTransition):

    def getPriority(self):
        return super(_SpecialPM3Transition, self).getPriority() + 1


@PersonalMissions3State.parentOf
class ProgressionState(LobbyState):
    STATE_ID = 'progression'
    __uiLoader = dependency.descriptor(IGuiLoader)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(ProgressionState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        machine = self.getMachine()
        loading = machine.getStateByCls(_LoadingState)
        self.addNavigationTransition(loading, record=True)
        self.addTransition(_SpecialPM3Transition(transitionType=TransitionType.EXTERNAL), self)

    def getNavigationDescription(self):
        operationID = self.__cachedParams.get('operationID')
        operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operationID)
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.operation(), operationName=operation.getUserName()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=openInfoPageScreen, tooltipBody=backport.text(R.strings.personal_missions.pages.button.infopage.description())),))

    def _onEntered(self, event):
        super(ProgressionState, self)._onEntered(event)
        self.__cachedParams = dict(event.params) or self.__cachedParams
        mainView = self.__uiLoader.windowsManager.getViewByLayoutID(R.views.mono.personal_missions_30.main())
        assemblingManager = self.getParent().getParent().assemblingManager
        assemblingManager.activateSelectableLogic()
        if not mainView or not assemblingManager.isVehicleGOForOperationReady(mainView.getOperationID()):
            _LoadingState.goTo(useBackNavigation=True, **self.__cachedParams)
            return
        mainView.setProgressionState()

    def _onExited(self):
        self.getParent().getParent().assemblingManager.deactivateSelectableLogic()
        super(ProgressionState, self)._onExited()


@PersonalMissions3State.parentOf
class MissionsState(LobbyState):
    STATE_ID = 'missions'
    __uiLoader = dependency.descriptor(IGuiLoader)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(MissionsState, self).__init__(flags=flags)
        self.__cachedParams = {}

    @classmethod
    def goTo(cls, category=MissionCategory.ASSAULT):
        super(MissionsState, cls).goTo(category=category.value)

    def serializeParams(self):
        view = self.getMachine().getRelatedView(self)
        if view and view.viewStatus == ViewStatus.LOADED:
            self.__cachedParams['category'] = view.viewModel.missionsModel.getMissionsCategory().value
        return self.__cachedParams

    def registerTransitions(self):
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(_LoadingState), record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.personal_missions()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=openInfoPageScreen, tooltipBody=backport.text(R.strings.personal_missions.pages.button.infopage.description())),))

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.missions())

    def _onEntered(self, event):
        super(MissionsState, self)._onEntered(event)
        params = event.params
        self.__cachedParams = params
        mainView = self.__uiLoader.windowsManager.getViewByLayoutID(R.views.mono.personal_missions_30.main())
        assemblingManager = self.getParent().getParent().assemblingManager
        if not mainView or not assemblingManager.isVehicleGOForOperationReady(mainView.getOperationID()):
            _LoadingState.goTo(useBackNavigation=True, **dict(params))
            return
        mainView.setMissionsState()
        mainView.setMissionViewCategory(MissionCategory(params.get('category', MissionCategory.ASSAULT.value)))

    def _onExited(self):
        super(MissionsState, self)._onExited()
        self.__cachedParams = {}


@PersonalMissions3State.parentOf
class AssemblingState(LobbyState):
    STATE_ID = 'assembling'
    __uiLoader = dependency.descriptor(IGuiLoader)

    def registerTransitions(self):
        machine = self.getMachine()
        vehicleHubOverview = machine.getStateByCls(OverviewState)
        loading = machine.getStateByCls(_LoadingState)
        self.addNavigationTransition(loading, record=True)
        self.addNavigationTransition(vehicleHubOverview, record=True)
        machine.getStateByCls(VehicleHubState).addNavigationTransition(self)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.assembling()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=openInfoPageScreen, tooltipBody=backport.text(R.strings.personal_missions.pages.button.infopage.description())),))

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.assembling())

    def _onEntered(self, event):
        super(AssemblingState, self)._onEntered(event)
        SoundGroups.g_instance.playSound2D(SoundsKeys.TO_ASSEMBLING)
        mainView = self.__uiLoader.windowsManager.getViewByLayoutID(R.views.mono.personal_missions_30.main())
        assemblingManager = self.getParent().getParent().assemblingManager
        if not mainView or not assemblingManager.isVehicleGOForOperationReady(mainView.getOperationID()):
            _LoadingState.goTo(useBackNavigation=True, **dict(event.params))
            return
        mainView.setAssemblingState()

    def _onExited(self):
        super(AssemblingState, self)._onExited()
        SoundGroups.g_instance.playSound2D(SoundsKeys.FROM_ASSEMBLING)
