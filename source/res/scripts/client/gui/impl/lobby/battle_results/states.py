# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/states.py
import logging
import math
import typing
import BigWorld
import CGF
import Math
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle
from cgf_components.pbs_components import PostBattleManager
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui import SystemMessages
from gui.ClientHangarSpace import customizationHangarCFG
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.lobby.trainings.states import TrainingRoomState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.battle_results.service import g_pbsFakeData, PostBattleResultsStateMixin
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.vehicle_hub import OverviewState
from gui.lobby_state_machine.router import SubstateRouter
from gui.lobby_state_machine.states import SFViewLobbyState, LobbyState, SubScopeSubLayerState, LobbyStateDescription, UntrackedState, LobbyStateFlags
from gui.lobby_state_machine.transitions import HijackTransition
from gui.prb_control import prbDispatcherProperty
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.system_factory import collectBattleResultStatsCtrl
from gui.shared.utils.functions import getArenaImage, getViewName
from gui.subhangar.subhangar_observer import hangarVehicleAABB, selectItemByTankSize
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroups, SubhangarStateGroupConfig, CameraMover
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.events_handler import EventsHandler
from items.components.c11n_constants import SeasonType
from shared_utils import first
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.shared.utils import IHangarSpace
_logger = logging.getLogger(__name__)
_TANK_SIZE_LOWER_BOUNDS = (float('-inf'), 5.0, 8.0)
_HIDDEN_TANK_LOCATION = Math.Vector3(0, -10000, 0)
_SHOULD_GO_BACK_AFTER_LOADING = 'shouldGoBackAfterLoading'
_TAB_STATE_ID = 'tabStateId'
_PBS_SUBHANGAR_GROUPS_BY_SIZE = (SubhangarStateGroups.PostBattleSmall, SubhangarStateGroups.PostBattleMedium, SubhangarStateGroups.PostBattleLarge)

def registerStates(lsm):
    lsm.addState(PostBattleResultsEntryState())


def registerTransitions(lsm):
    pbsEntryState = lsm.getStateByCls(PostBattleResultsEntryState)
    lsm.addNavigationTransitionFromParent(pbsEntryState, transitionType=TransitionType.EXTERNAL)
    pbsEntryState.getParent().addTransition(HijackTransition(PostBattleResultsEntryState, shouldHijackPBSEntry, transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(_LoadingStateWithRetainedCamera))
    pbsEntryState.addTransition(HijackTransition(PostBattleResultsEntryState, shouldHijackPBSEntry, transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(_LoadingStateWithRetainedCamera))


class PostBattleResultsEntryProto(LobbyState, SubhangarStateGroupConfigProvider):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleResultsEntryProto, self).__init__(flags)
        self._cachedParams = {}

    def getSubhangarStateGroupConfig(self):
        arenaUniqueID = self._cachedParams.get('arenaUniqueID', None)
        statsController = self.__battleResults.getStatsCtrl(arenaUniqueID)
        _, reusable = statsController.getResults()
        teamResultType = SubhangarStateGroups.PostBattleDefeat
        if reusable:
            teamResult = reusable.getPersonalTeamResult()
            if teamResult == PLAYER_TEAM_RESULT.WIN:
                teamResultType = SubhangarStateGroups.PostBattleVictory
        return SubhangarStateGroupConfig((teamResultType,))

    def serializeParams(self):
        return self._cachedParams

    @classmethod
    def goTo(cls, arenaUniqueID, bonusType, tabStateId=None):
        super(PostBattleResultsEntryProto, cls).goTo(arenaUniqueID=arenaUniqueID, bonusType=bonusType, tabStateId=tabStateId)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))

    def _onEntered(self, event):
        super(PostBattleResultsEntryProto, self)._onEntered(event)
        Waiting.show('loadingData')
        self._cachedParams = dict(event.params)
        if g_pbsFakeData.vehicleAndOffsets and g_pbsFakeData.vehicleName:
            fakeVehicle = g_pbsFakeData.getVehicle()
            if fakeVehicle:
                g_currentPreviewVehicle.selectVehicle(vehicleCD=fakeVehicle.intCD, vehicleStrCD=fakeVehicle.strCD)
                return
        arenaUniqueID = self._cachedParams.get('arenaUniqueID', None)
        vehicleCD, outfit = _getVehicleCDAndOutfit(self.__battleResults, arenaUniqueID)
        if vehicleCD is None:
            return
        else:
            vehicle = self.__itemsCache.items.getVehicleCopyByCD(vehicleCD)
            if vehicle is None:
                g_currentPreviewVehicle.selectVehicle()
                return
            _, reusable = self.__battleResults.getStatsCtrl(arenaUniqueID).getResults()
            mapKind = reusable.common.arenaType.getVehicleCamouflageKind()
            mapSeason = SeasonType.fromArenaKind(mapKind)
            from vehicle_systems import camouflages
            component = camouflages.getOutfitComponent(outfit, vehicle.descriptor, mapSeason)
            outfit = self.__itemsFactory.createOutfit(component=component, vehicleCD=vehicle.strCD)
            g_currentPreviewVehicle.selectVehicle(vehicleCD=vehicle.intCD, vehicleStrCD=vehicle.strCD, season=mapSeason, outfit=outfit)
            return

    def _onExited(self):
        super(PostBattleResultsEntryProto, self)._onExited()
        Waiting.hide('loadingData')
        self._cachedParams.clear()
        space = self.__hangarSpace.space
        if space is None:
            return
        else:
            g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
            g_currentPreviewVehicle.selectNoVehicle()
            space.turretAndGunAngles.reset()
            return


class LoadingProto(LobbyState, EventsHandler):
    __battleResults = dependency.descriptor(IBattleResultsService)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LoadingProto, self).__init__(flags=flags | LobbyStateFlags.POST_BATTLE_RESULTS)
        self._cachedParams = {}
        self.__callbackDelayer = CallbackDelayer()

    @property
    def resultsState(self):
        raise NotImplementedError

    def _getEvents(self):
        return ((self.__hangarSpace.onVehicleChanged, self.__onSpaceOrVehicleChange), (self.__hangarSpace.onSpaceChanged, self.__onSpaceOrVehicleChange))

    def _onEntered(self, event):
        Waiting.show('loadingData')
        super(LoadingProto, self)._onEntered(event)
        self._cachedParams = dict(event.params)
        vehicleCD, _ = _getVehicleCDAndOutfit(self.__battleResults, event.params.get('arenaUniqueID'))
        incorrectVehicleLoaded = g_currentPreviewVehicle.intCD != vehicleCD
        hangarReady = self.__hangarSpace.spaceInited or self.__hangarSpace.isModelLoaded
        if not hangarReady or incorrectVehicleLoaded:
            self._subscribe()
        else:
            self.__onSpaceAvailable()
            self.__callbackDelayer.delayCallback(0.0, self.__goToWhenAABBAvailable)

    def _onExited(self):
        self._cachedParams.clear()
        self._unsubscribe()
        self.__callbackDelayer.clearCallbacks()
        Waiting.hide('loadingData')
        super(LoadingProto, self)._onExited()

    def __onSpaceOrVehicleChange(self):
        if self.__hangarSpace.spaceInited and self.__hangarSpace.isModelLoaded:
            self.__onSpaceAvailable()
            self.__callbackDelayer.delayCallback(0.0, self.__goToWhenAABBAvailable)

    def __goToWhenAABBAvailable(self):
        if not (hangarVehicleAABB() and self.__hangarSpace.spaceInited and self.__hangarSpace.isModelLoaded):
            self.__callbackDelayer.delayCallback(0.0, self.__goToWhenAABBAvailable)
        elif self._cachedParams.get(_SHOULD_GO_BACK_AFTER_LOADING, False):
            self.goBack()
        else:
            self.resultsState.goTo(**self._cachedParams)

    def __onSpaceAvailable(self):
        self.__hangarSpace.space.turretAndGunAngles.set(gunPitch=0.0, turretYaw=0.0)
        ClientSelectableCameraObject.deselectAll()
        self.__hangarSpace.space.getVehicleEntity().onSelect()
        hangarConfig = customizationHangarCFG()
        _moveTank(hangarConfig, _HIDDEN_TANK_LOCATION, (0, 0, 0))


class LoadingWithRetainedCameraProto(LoadingProto, SubhangarStateGroupConfigProvider):

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.PostBattleCommon))

    def _onEntered(self, event):
        super(LoadingWithRetainedCameraProto, self)._onEntered(event)
        Waiting.show('loadingData')

    def _onExited(self):
        super(LoadingWithRetainedCameraProto, self)._onExited()
        Waiting.hide('loadingData')


class PostBattleResultsProto(SFViewLobbyState, SubhangarStateGroupConfigProvider, PostBattleResultsStateMixin):
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleResultsProto, self).__init__(flags=flags | LobbyStateFlags.POST_BATTLE_RESULTS)
        self._cachedParams = {}
        self.__router = None
        return

    def serializeParams(self):
        return self._cachedParams

    def getSubhangarStateGroupConfig(self):
        _, reusable = self.__battleResults.getStatsCtrl(self._cachedParams.get('arenaUniqueID', None)).getResults()
        geometryName = reusable.common.arenaType.getGeometryName()
        mapImageName = getArenaImage(geometryName, 'screen')
        mapImageName = mapImageName.replace('img://', '')
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.PostBattleCommon), PBSSceneSetup(mapImageName))

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))

    def getViewKey(self, params=None):
        arenaUniqueID = self._cachedParams.get('arenaUniqueID', '')
        alias = super(PostBattleResultsProto, self).getViewKey().alias
        return ViewKey(alias, getViewName(alias, arenaUniqueID))

    def _getView(self):
        from skeletons.gui.app_loader import IAppLoader
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        return view.content

    def _onEntered(self, event):
        self._cachedParams = dict(event.params)
        super(PostBattleResultsProto, self)._onEntered(event)
        self.__router = SubstateRouter(self.getMachine(), self._getView(), self)
        self.__router.init()
        if self._cachedParams.get(_TAB_STATE_ID) is not None:
            stateId = self._cachedParams.pop(_TAB_STATE_ID)
            self.getMachine().getStateByID(stateId).goTo(**self._cachedParams)
        return

    def _onExited(self):
        self._cachedParams = {}
        self.__router.fini()
        self.__router = None
        super(PostBattleResultsProto, self)._onExited()
        return

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}

    def _preventNavigationOutside(self, event):
        from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
        from battle_royale.gui.impl.lobby.views.states import BattleRoyaleModeState
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is None or not prbDispatcher.getFunctionalState().isNavigationDisabled():
            return False
        else:
            targetID = event.targetStateID
            lsm = self.getMachine()
            target = lsm.getStateByID(targetID)
            parentDescendants = self.getParent().getRecursiveChildrenStates()
            battleQueueDescendants = lsm.getStateByCls(BattleQueueContainerState).getRecursiveChildrenStates()
            battleRoyaleQueueDescendants = lsm.getStateByCls(BattleRoyaleModeState).getRecursiveChildrenStates()
            eventTargetingOutside = target != self.getParent() and target not in parentDescendants and target not in battleQueueDescendants and target not in battleRoyaleQueueDescendants
            if eventTargetingOutside:
                SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')
            return eventTargetingOutside


class PostBattleTab(LobbyState, EventsHandler):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleTab, self).__init__(flags=flags | LobbyStateFlags.POST_BATTLE_RESULTS)
        self._cachedParams = None
        return

    @property
    def loadingState(self):
        raise NotImplementedError

    @property
    def entryState(self):
        raise NotImplementedError

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.store.browser.states import ShopState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(ShopState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(self.loadingState), record=True)

    def serializeParams(self):
        return self._cachedParams

    def _onEntered(self, event):
        super(PostBattleTab, self)._onEntered(event)
        self._cachedParams = self.getParent().serializeParams()
        self._cachedParams.update(event.params)
        if hangarVehicleAABB() and self.__hangarSpace.spaceInited and self.__hangarSpace.isModelLoaded:
            self._subscribe()
            return
        self._cachedParams[_SHOULD_GO_BACK_AFTER_LOADING] = True
        self.loadingState.goTo(**self._cachedParams)

    def _onExited(self):
        self._cachedParams = {}
        self._unsubscribe()
        super(PostBattleTab, self)._onExited()

    def _getEvents(self):
        return ((self.__hangarSpace.onSpaceChanged, self.__onSpaceChanged),)

    def __onSpaceChanged(self):
        self._cachedParams[_TAB_STATE_ID] = self.STATE_ID
        self.entryState.goTo(**self._cachedParams)


class OverviewTabProto(PostBattleTab):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))

    def _onEntered(self, event):
        super(OverviewTabProto, self)._onEntered(event)
        self.getMachine().getRelatedView(self).blur.disable()


class BlurredResultTab(PostBattleTab):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))

    def _onEntered(self, event):
        super(BlurredResultTab, self)._onEntered(event)
        self.getMachine().getRelatedView(self).blur.enable()


class TeamScoreTabProto(BlurredResultTab):
    pass


class MissionProgressTabProto(BlurredResultTab):
    pass


class FinancialReportTabProto(BlurredResultTab):
    pass


def generatePostBattleStateClasses(parentStateCls, entryStateProto=PostBattleResultsEntryProto, loadingProto=LoadingProto, loadingWithRetainedCameraProto=LoadingWithRetainedCameraProto, resultsProto=PostBattleResultsProto, overviewProto=OverviewTabProto, teamScoreProto=TeamScoreTabProto, missionProgressProto=MissionProgressTabProto, financialReportProto=FinancialReportTabProto):

    @parentStateCls.parentOf
    class GeneratedEntryState(entryStateProto):
        STATE_ID = entryStateProto.STATE_ID or 'postBattleResultsEntry'

        def registerTransitions(self):
            lsm = self.getMachine()
            lsm.getStateByCls(TrainingRoomState).addNavigationTransition(self, record=True)
            self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
            myDescendants = set(self.getRecursiveChildrenStates())
            for state in self.getParent().getRecursiveChildrenStates():
                stateFlags = state.getFlags()
                if state in myDescendants or state == self or stateFlags & LobbyStateFlags.POST_BATTLE_RESULTS or isinstance(state, UntrackedState):
                    continue
                if not state.getChildrenStates() and not stateFlags & LobbyStateFlags.HANGAR:
                    state.addNavigationTransition(self, record=True)

        def registerStates(self):
            lsm = self.getMachine()
            lsm.addState(GeneratedLoadingState(flags=StateFlags.INITIAL))
            lsm.addState(GeneratedLoadingWithRetainedCamera())
            lsm.addState(GeneratedResultsState())

    @GeneratedEntryState.parentOf
    class GeneratedLoadingState(loadingProto):
        STATE_ID = loadingProto.STATE_ID or 'loading'

        @property
        def resultsState(self):
            return GeneratedResultsState

        def registerTransitions(self):
            lsm = self.getMachine()
            self.addNavigationTransition(lsm.getStateByCls(GeneratedResultsState))

    @GeneratedEntryState.parentOf
    class GeneratedLoadingWithRetainedCamera(loadingWithRetainedCameraProto):
        STATE_ID = loadingWithRetainedCameraProto.STATE_ID or 'loadingWithRetainedCamera'

        @property
        def resultsState(self):
            return GeneratedResultsState

        def registerTransitions(self):
            lsm = self.getMachine()
            self.addNavigationTransition(lsm.getStateByCls(GeneratedResultsState))

    @GeneratedEntryState.parentOf
    class GeneratedResultsState(resultsProto):
        STATE_ID = resultsProto.STATE_ID or VIEW_ALIAS.POST_BATTLE_RESULTS
        VIEW_KEY = resultsProto.VIEW_KEY or ViewKey(VIEW_ALIAS.POST_BATTLE_RESULTS)

        def registerStates(self):
            lsm = self.getMachine()
            lsm.addState(GeneratedOverviewTab(StateFlags.INITIAL))
            lsm.addState(GeneratedTeamScoreTab())
            lsm.addState(GeneratedMissionProgressTab())
            lsm.addState(GeneratedFinancialReportTab())

        def registerTransitions(self):
            lsm = self.getMachine()
            for child in self.getChildrenStates():
                lsm.addNavigationTransitionFromParent(child)
                child.addGuardTransition(child, self._preventNavigationOutside)

    @GeneratedResultsState.parentOf
    class GeneratedOverviewTab(overviewProto):
        STATE_ID = overviewProto.STATE_ID or 'overview'

        @property
        def loadingState(self):
            return GeneratedLoadingState

        @property
        def entryState(self):
            return GeneratedEntryState

    @GeneratedResultsState.parentOf
    class GeneratedTeamScoreTab(teamScoreProto):
        STATE_ID = teamScoreProto.STATE_ID or 'teamScore'

        @property
        def loadingState(self):
            return GeneratedLoadingState

        @property
        def entryState(self):
            return GeneratedEntryState

        def registerTransitions(self):
            super(GeneratedTeamScoreTab, self).registerTransitions()
            lsm = self.getMachine()
            self.addNavigationTransition(lsm.getStateByCls(GeneratedLoadingState), record=True)

    @GeneratedResultsState.parentOf
    class GeneratedMissionProgressTab(missionProgressProto):
        STATE_ID = missionProgressProto.STATE_ID or 'missionProgress'

        @property
        def loadingState(self):
            return GeneratedLoadingState

        @property
        def entryState(self):
            return GeneratedEntryState

        def registerTransitions(self):
            from gui.Scaleform.daapi.view.lobby.user_missions.states import UserMissionsState
            from gui.Scaleform.daapi.view.lobby.missions.regular.states import MissionsState as CommonMissionState
            from gui.Scaleform.daapi.view.lobby.profile.states import ServiceRecordState
            from gui.impl.lobby.personal_missions_30.state import MissionsState as PM3MissionsState
            from gui.impl.lobby.battle_pass.states import STATES
            from gui.impl.lobby.vehicle_hub import ModulesState
            from gui.impl.lobby.vehicle_hub.states import VehicleHubState
            super(GeneratedMissionProgressTab, self).registerTransitions()
            lsm = self.getMachine()
            self.addNavigationTransition(lsm.getStateByCls(PM3MissionsState), record=True)
            self.addNavigationTransition(lsm.getStateByCls(UserMissionsState), record=True)
            self.addNavigationTransition(lsm.getStateByCls(CommonMissionState), record=True)
            self.addNavigationTransition(lsm.getStateByCls(ServiceRecordState), record=True)
            self.addNavigationTransition(lsm.getStateByCls(ModulesState), record=True)
            lsm.getStateByCls(VehicleHubState).addNavigationTransition(self)
            for state in STATES.values():
                self.addNavigationTransition(lsm.getStateByCls(state), record=True)

    @GeneratedResultsState.parentOf
    class GeneratedFinancialReportTab(financialReportProto):
        STATE_ID = financialReportProto.STATE_ID or 'financialReport'

        @property
        def loadingState(self):
            return GeneratedLoadingState

        @property
        def entryState(self):
            return GeneratedEntryState

    return (GeneratedEntryState,
     GeneratedLoadingState,
     GeneratedLoadingWithRetainedCamera,
     GeneratedResultsState,
     GeneratedOverviewTab,
     GeneratedTeamScoreTab,
     GeneratedMissionProgressTab,
     GeneratedFinancialReportTab)


PostBattleResultsEntryState, _LoadingState, _LoadingStateWithRetainedCamera, PostBattleResultsState, _OverviewTab, _TeamScoreTab, _MissionProgressTab, _FinancialReportTab = generatePostBattleStateClasses(SubScopeSubLayerState)

class PBSSceneSetup(CameraMover):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, mapImageName):
        self.__mapImageName = mapImageName

    def moveCamera(self, cameraManager, cameraName):
        super(PBSSceneSetup, self).moveCamera(cameraManager, cameraName)
        hangarConfig = customizationHangarCFG()
        _moveTank(hangarConfig, hangarConfig['v_start_pos'], tuple((math.radians(angle) for angle in hangarConfig['v_start_angles'])))
        spaceID = self.__hangarSpace.spaceID
        pbsManager = CGF.getManager(spaceID, PostBattleManager)
        if pbsManager and self.__mapImageName:
            pbsManager.applyArenaImage(self.__mapImageName)
        Waiting.hide('loadingData')

    def moveCameraFailed(self):
        Waiting.hide('loadingData')


def shouldHijackPBSEntry(event, targetStateClass=PostBattleResultsState):
    lsm = getLobbyStateMachine()
    pbsState = lsm.getStateByCls(targetStateClass)
    if event.params.get('bonusType') is None:
        return False
    else:
        oldState = first(lsm.getNonEmptyEnteredStates())
        newBattleCtrl = collectBattleResultStatsCtrl(event.params.get('bonusType'))
        oldBattleCtrl = collectBattleResultStatsCtrl(getattr(oldState, '_cachedParams', {}).get('bonusType'))
        return pbsState.isEntered() and newBattleCtrl is not None and oldBattleCtrl is not None and newBattleCtrl.representativeArenaBonusType() == oldBattleCtrl.representativeArenaBonusType()


def _getVehicleCDAndOutfit(battleResultsService, arenaUniqueID):
    statsController = battleResultsService.getStatsCtrl(arenaUniqueID)
    if statsController is not None:
        battleResults, reusable = statsController.getResults()
        for vehicleCD, vehicle in reusable.personal.getVehicleCDsIterator(battleResults['personal']):
            return (vehicleCD, vehicle['outfit'])

    return (None, None)


def _moveTank(hangarConfig, position, yawPitchRoll):
    isForwardPipeline = BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 1
    shadowOffsetKey = 'shadow_forward_y_offset' if isForwardPipeline else 'shadow_deferred_y_offset'
    shadowYOffset = hangarConfig[shadowOffsetKey]
    g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.CHANGE_VEHICLE_MODEL_TRANSFORM, ctx={'targetPos': position,
     'rotateYPR': yawPitchRoll,
     'shadowYOffset': shadowYOffset}), scope=EVENT_BUS_SCOPE.LOBBY)
