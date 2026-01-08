# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/personal_missions_30/state.py
import logging
from functools import partial
import typing
import SoundGroups
from cgf_components.pm30_hangar_components import PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from frameworks.wulf import ViewStatus
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.missions.missions_helper import getCurrentOperationLastInstalledDetail
from gui.Scaleform.daapi.view.lobby.user_missions.states import UserMissionsState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.personal_missions_30.common.enums import OperationState, MissionCategory
from gui.impl.gen.view_models.views.lobby.personal_missions_30.main_view_model import MainScreenState, AnimationState
from gui.impl.lobby.hangar.states import HangarState
from gui.impl.lobby.personal_missions_30.camera_mover import PersonalMissions3CameraMover
from gui.impl.lobby.personal_missions_30.hangar_helpers import AssemblingManager
from gui.impl.lobby.personal_missions_30.personal_mission_constants import SoundsKeys, IntroKeys
from gui.impl.lobby.personal_missions_30.views_helpers import openInfoPageScreen, isIntroShown, getOperationStatus, getSortedPm3Operations
from gui.impl.lobby.vehicle_hub.states import OverviewState
from gui.lobby_state_machine.states import SubScopeSubLayerState, LobbyStateDescription, LobbyState, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition, NavigationTransition
from gui.shared import EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showHangar, showPM30IntroWindow, showPM30OperationIntroWindow
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroupConfig, SubhangarStateGroups
from helpers import dependency
from helpers.events_handler import EventsHandler
from personal_missions import PM_BRANCH
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.impl import IGuiLoader
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared.utils import IHangarSpace
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
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(ProgressionState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(AssemblingState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(MissionsState), record=True)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.campaign_selector()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=openInfoPageScreen, tooltipBody=backport.text(R.strings.personal_missions.pages.button.infopage.description())), LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.VIDEO, onMoreInfoRequested=lambda : showPM30IntroWindow(force=True), tooltipBody=backport.text(R.strings.personal_missions.pages.button.video.description()))))

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.campaignSelector())


@SubScopeSubLayerState.parentOf
class PersonalMissions3EntryState(LobbyState, EventsHandler, SubhangarStateGroupConfigProvider):
    STATE_ID = 'personalMissions3Entry'
    __eventsCache = dependency.descriptor(IEventsCache)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PersonalMissions3EntryState, self).__init__(flags)
        self.assemblingManager = None
        self.__cachedParams = {}
        return

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((SubhangarStateGroups.PersonalMissions,), PersonalMissions3CameraMover(callback=self.moveCamera))

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(PersonalMissions3State(flags=StateFlags.INITIAL))

    def _onEntered(self, event):
        super(PersonalMissions3EntryState, self)._onEntered(event)
        self._subscribe()
        self.assemblingManager = AssemblingManager()
        self.__cachedParams = dict(event.params)

    def _onExited(self):
        self._unsubscribe()
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
            if state == MainScreenState.ASSEMBLING.value:
                self.assemblingManager.switchCameraToFreePosition(instantly=True)
            elif operation.isFullCompleted():
                self.assemblingManager.switchCameraToFreeFarPosition(instantly=True)
            elif self.assemblingManager.isSwitchingToTopCameraNeeded():
                self.assemblingManager.startTopCameraAnimation()
        else:
            _logger.error('PersonalMissions3EntryState cachedParams is empty')

    def _getEvents(self):
        return ((self.__hangarSpace.onSpaceChanged, self.__onSpaceChanged),)

    def __onSpaceChanged(self):
        machine = self.getMachine()
        machine.getStateByCls(PersonalMissions3State).setForceLeave()
        showHangar()


@PersonalMissions3EntryState.parentOf
class PersonalMissions3State(ViewLobbyState, EventsHandler):
    STATE_ID = VIEW_ALIAS.PERSONAL_MISSIONS_3
    VIEW_KEY = ViewKey(VIEW_ALIAS.PERSONAL_MISSIONS_3)
    __appLoader = dependency.descriptor(IAppLoader)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PersonalMissions3State, self).__init__(flags=flags)
        self.__cachedParams = None
        self.__isForcedLeave = False
        return

    def _getViewLoadCtx(self, event):
        ctx = dict(event.params)
        return {'assemblingManager': self.getParent().assemblingManager,
         'state': ctx.get('state'),
         'operationID': ctx.get('operationID')}

    def serializeParams(self):
        mainView = self.getMachine().getRelatedView(self)
        return {'operationID': mainView.getOperationID(),
         'state': mainView.viewModel.getMainScreenState().value} if mainView is not None and mainView.viewStatus == ViewStatus.LOADED else self.__cachedParams

    def registerStates(self):
        self.addChildState(ProgressionState(flags=StateFlags.INITIAL))
        self.addChildState(MissionsState())
        self.addChildState(AssemblingState())
        self.addChildState(_LoadingState())

    def registerTransitions(self):
        lsm = self.getMachine()
        progression = lsm.getStateByCls(ProgressionState)
        missions = lsm.getStateByCls(MissionsState)
        assembling = lsm.getStateByCls(AssemblingState)
        self.addNavigationTransition(progression, record=True)
        self.addNavigationTransition(missions, record=True)
        self.addNavigationTransition(assembling, record=True)
        missions.addGuardTransition(missions, self.isAnimationPlayed)
        assembling.addGuardTransition(assembling, self.isAnimationPlayed)
        self.addTransition(HijackTransition(HangarState, self.isAnimationPlayed, transitionType=TransitionType.INTERNAL), self)
        missions.addTransition(HijackTransition(HangarState, self.isAnimationPlayed, transitionType=TransitionType.INTERNAL), missions)
        assembling.addTransition(HijackTransition(HangarState, self.isAnimationPlayed, transitionType=TransitionType.INTERNAL), assembling)
        progression.addTransition(HijackTransition(HangarState, self.isAnimationPlayed, transitionType=TransitionType.INTERNAL), progression)

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.dashboard())

    def setForceLeave(self):
        self.__isForcedLeave = True

    def _getEvents(self):
        assemblingManager = self.getParent().assemblingManager
        return ((self.__eventsCache.onSyncCompleted, self.__onEventsCacheSync),
         (assemblingManager.onAssemblingVideoFinished, self.__onAssemblingVideoFinished),
         (assemblingManager.onAssemblingAnimationStarted, self.__onAssemblingAnimationStarted),
         (assemblingManager.onAssemblingAnimationFinished, self.__onAssemblingAnimationFinished),
         (assemblingManager.onCameraFlightStarted, self.__onCameraFlightStarted),
         (assemblingManager.onCameraFlightFinished, self.__onCameraFlightFinished))

    def _onEntered(self, event):
        super(PersonalMissions3State, self)._onEntered(event)
        self.__isForcedLeave = False
        self.__cachedParams = event.params
        operationID = event.params.get('operationID')
        pm3Operations = getSortedPm3Operations()
        operation = pm3Operations[operationID]
        if not isIntroShown(IntroKeys.OPERATION_INTRO_VIEW.value % operation.getID()) and getOperationStatus(operation, pm3Operations) != OperationState.UNAVAILABLE:
            showPM30OperationIntroWindow(operation.getID())
        self._subscribe()

    def _onExited(self):
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(_OPAQUE_BACKGROUND_ALPHA)
        self._unsubscribe()
        super(PersonalMissions3State, self)._onExited()

    def isAnimationPlayed(self, *_):
        mainView = self.getMachine().getRelatedView(self)
        if mainView is None:
            return False
        else:
            animationPlaying = (mainView.viewModel.getAnimationState() != AnimationState.IDLE or mainView.viewModel.getCameraFlightInProgress()) and not self.__isForcedLeave
            return animationPlaying

    def __onAssemblingAnimationStarted(self):
        mainView = self.getMachine().getRelatedView(self)
        operationID = mainView.getOperationID()
        AssemblingState.goTo(operationID=operationID, state=mainView.getMainScreenState().value)

    def __onAssemblingVideoFinished(self, stageNumber):
        mainView = self.getMachine().getRelatedView(self)
        self.getParent().assemblingManager.switchCameraToStagePosition(stageNumber, callback=partial(mainView.setAnimationState, AnimationState.CONTINUE_CLAIM_DETAIL))

    def __onAssemblingAnimationFinished(self):
        mainView = self.getMachine().getRelatedView(self)
        if mainView is not None:
            mainView.setAnimationState(AnimationState.CONTINUE_CLAIM_DETAIL)
        return

    def __onEventsCacheSync(self, *_):
        mainView = self.getMachine().getRelatedView(self)
        assemblingManager = self.getParent().assemblingManager
        if mainView is not None and mainView.isCurrentOperationFullCompleted() and assemblingManager.isSwitchingToFreeFarCameraNeeded():
            assemblingManager.switchCameraToMainPosition(isOperationFullCompleted=True, callback=partial(mainView.setAnimationState, AnimationState.CONTINUE_BACK))
        return

    def __onCameraFlightStarted(self):
        mainView = self.getMachine().getRelatedView(self)
        if mainView is not None:
            mainView.setCameraFlightInProgress(True)
        return

    def __onCameraFlightFinished(self):
        mainView = self.getMachine().getRelatedView(self)
        if mainView is not None:
            mainView.setCameraFlightInProgress(False)
        return


class _PersonalMissionsChildState(LobbyState):

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_PersonalMissionsChildState, self).__init__(flags=flags)
        self._cachedParams = {}

    @property
    def assemblingManager(self):
        assemblingManager = self.getParent().getParent().assemblingManager
        if not assemblingManager:
            _logger.error('assemblingManager should be created')
        return assemblingManager

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        if not isinstance(self, _LoadingState):
            self.addNavigationTransition(lsm.getStateByCls(_LoadingState), record=True)
            lsm.getStateByCls(SubScopeSubLayerState).addNavigationTransition(self)
            self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)

    def _onEntered(self, event):
        super(_PersonalMissionsChildState, self)._onEntered(event)
        self._cachedParams = dict(event.params)

    def readyToEnter(self):
        mainView = self.getMachine().getRelatedView(self)
        return mainView and mainView.viewStatus in (ViewStatus.LOADED, ViewStatus.LOADING) and self.assemblingManager.isVehicleGOForOperationReady(self._cachedParams.get('operationID'))

    def getNavigationDescription(self):
        return LobbyStateDescription(title=self._getNavigationDescriptionTitle(), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=self.__onMoreInfoRequested, tooltipBody=backport.text(R.strings.personal_missions.pages.button.infopage.description())),))

    def _getNavigationDescriptionTitle(self):
        raise NotImplementedError

    def __onMoreInfoRequested(self):
        if self.getParent().isAnimationPlayed():
            return
        openInfoPageScreen()


class _SpecialPM3Transition(NavigationTransition):

    def getPriority(self):
        return super(_SpecialPM3Transition, self).getPriority() + 1


@PersonalMissions3State.parentOf
class _LoadingState(_PersonalMissionsChildState, EventsHandler):
    STATE_ID = 'loading'
    __appLoader = dependency.descriptor(IAppLoader)
    __uiLoader = dependency.instance(IGuiLoader)
    __eventsCache = dependency.descriptor(IEventsCache)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LoadingState, self).__init__(flags=flags)

    def getNavigationDescription(self):
        return LobbyStateDescription()

    def _getNavigationDescriptionTitle(self):
        pass

    def _getEvents(self):
        eventsTuple = super(_LoadingState, self)._getEvents()
        return eventsTuple + ((self.__uiLoader.windowsManager.onWindowStatusChanged, self.__onWindowStatusChanged),)

    def _getListeners(self):
        return ((PERSONAL_MISSIONS_3_SUB_HANGAR_IS_READY, self.__onSubHangarReady, EVENT_BUS_SCOPE.LOBBY),)

    def _onEntered(self, event):
        super(_LoadingState, self)._onEntered(event)
        app = self.__appLoader.getApp()
        app.setBackgroundAlpha(_OPAQUE_BACKGROUND_ALPHA)
        if self.readyToEnter():
            self.onLoaded()
        else:
            self._subscribe()

    def _onExited(self):
        self._cachedParams.clear()
        self._unsubscribe()
        super(_LoadingState, self)._onExited()

    def __onSubHangarReady(self, _):
        if self.readyToEnter():
            self.onLoaded()

    def onLoaded(self):
        if not self.assemblingManager.inited:
            self.__initAssemblingManager()
        self.goBack()

    def __onWindowStatusChanged(self, _, status):
        if self.readyToEnter():
            self.onLoaded()

    def __initAssemblingManager(self):
        mainView = self.getMachine().getRelatedView(self)
        operationID = mainView.getOperationID()
        operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operationID)
        self.assemblingManager.init()
        self.assemblingManager.setHangarProgressionStateOn()
        self.assemblingManager.changeVehicleGO(operationID, getCurrentOperationLastInstalledDetail(operation))


@PersonalMissions3State.parentOf
class ProgressionState(_PersonalMissionsChildState):
    STATE_ID = 'progression'
    __eventsCache = dependency.descriptor(IEventsCache)

    @classmethod
    def goTo(cls, operationID=None, category=MissionCategory.ASSAULT, state=None):
        super(ProgressionState, cls).goTo(operationID=operationID, category=category.value, state=state)

    def registerTransitions(self):
        super(ProgressionState, self).registerTransitions()
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(UserMissionsState), record=True)
        self.addTransition(_SpecialPM3Transition(transitionType=TransitionType.EXTERNAL), self)

    def _getNavigationDescriptionTitle(self):
        operationID = self._cachedParams.get('operationID')
        operation = self.__eventsCache.getPersonalMissions().getAllOperations(PM_BRANCH.V2_BRANCHES).get(operationID)
        return backport.text(R.strings.pages.titles.operation(), operationName=operation.getUserName())

    def _onEntered(self, event):
        super(ProgressionState, self)._onEntered(event)
        if not self.readyToEnter():
            _LoadingState.goTo(**self._cachedParams)
            return
        mainView = self.getMachine().getRelatedView(self)
        self.assemblingManager.activateSelectableLogic()
        currentState = mainView.getMainScreenState()
        if currentState != MainScreenState.PROGRESSION and currentState == MainScreenState.ASSEMBLING:
            self.assemblingManager.switchCameraToMainPosition(isOperationFullCompleted=mainView.isCurrentOperationFullCompleted(), callback=partial(mainView.setAnimationState, AnimationState.CONTINUE_BACK))
        mainView.setProgressionState()

    def _onExited(self):
        self.assemblingManager.deactivateSelectableLogic()
        super(ProgressionState, self)._onExited()


@PersonalMissions3State.parentOf
class MissionsState(_PersonalMissionsChildState):
    STATE_ID = 'missions'

    @classmethod
    def goTo(cls, operationID=None, category=MissionCategory.ASSAULT, state=None):
        super(MissionsState, cls).goTo(operationID=operationID, category=category.value, state=state)

    def serializeParams(self):
        view = self.getMachine().getRelatedView(self)
        if view and view.viewStatus == ViewStatus.LOADED:
            self._cachedParams['category'] = view.viewModel.missionsModel.getMissionsCategory().value
        return self._cachedParams

    def registerTransitions(self):
        super(MissionsState, self).registerTransitions()
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(UserMissionsState), record=True)

    def _getNavigationDescriptionTitle(self):
        return backport.text(R.strings.pages.titles.personal_missions())

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.missions())

    def _onEntered(self, event):
        super(MissionsState, self)._onEntered(event)
        if not self.readyToEnter():
            _LoadingState.goTo(**self._cachedParams)
            return
        mainView = self.getMachine().getRelatedView(self)
        mainView.setMissionsState()
        mainView.setMissionViewCategory(MissionCategory(self._cachedParams.get('category', MissionCategory.ASSAULT.value)))


@PersonalMissions3State.parentOf
class AssemblingState(_PersonalMissionsChildState):
    STATE_ID = 'assembling'

    @classmethod
    def goTo(cls, operationID=None, category=MissionCategory.ASSAULT, state=None):
        super(AssemblingState, cls).goTo(operationID=operationID, category=category.value, state=state)

    def _getNavigationDescriptionTitle(self):
        return backport.text(R.strings.pages.titles.assembling())

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.personal_missions.navigation.backButton.assembling())

    def _onEntered(self, event):
        super(AssemblingState, self)._onEntered(event)
        SoundGroups.g_instance.playSound2D(SoundsKeys.TO_ASSEMBLING)
        if not self.readyToEnter():
            _LoadingState.goTo(**self._cachedParams)
            return
        mainView = self.getMachine().getRelatedView(self)
        mainView.setAssemblingState()

    def _onExited(self):
        super(AssemblingState, self)._onExited()
        self._cachedParams.clear()
        self._cachedParams = None
        SoundGroups.g_instance.playSound2D(SoundsKeys.FROM_ASSEMBLING)
        return
