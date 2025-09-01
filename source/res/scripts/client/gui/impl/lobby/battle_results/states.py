# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/battle_results/states.py
import logging
import math
import typing
import BigWorld
import CGF
import Math
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.lobby_entry import getLobbyStateMachine
from gui.impl.lobby.vehicle_hub import OverviewState
from gui.prb_control import prbDispatcherProperty
from gui.shared.lock_overlays import lockNotificationManager
from ClientSelectableCameraObject import ClientSelectableCameraObject
from CurrentVehicle import g_currentPreviewVehicle
from WeakMethod import WeakMethodProxy
from cgf_components.pbs_components import PostBattleManager
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.ClientHangarSpace import customizationHangarCFG
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_results.service import g_pbsFakeData
from gui.battle_results.settings import PLAYER_TEAM_RESULT
from gui.impl import backport
from gui.impl.gen import R
from gui.lobby_state_machine.states import SFViewLobbyState, LobbyState, SubScopeSubLayerState, LobbyStateDescription, UntrackedState
from gui.Scaleform.daapi.view.lobby.trainings.states import TrainingRoomState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.functions import getArenaImage, getViewName
from gui.shared.view_helpers.blur_manager import ImmediateSceneBlurConfig
from gui.subhangar.subhangar_observer import hangarVehicleAABB, selectItemByTankSize
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroups, SubhangarStateGroupConfig, CameraMover
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from helpers.events_handler import EventsHandler
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IBlurController
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from skeletons.gui.shared.utils import IHangarSpace
from items.components.c11n_constants import SeasonType
_logger = logging.getLogger(__name__)
_TANK_SIZE_LOWER_BOUNDS = (float('-inf'), 5.0, 8.0)
_HIDDEN_TANK_LOCATION = Math.Vector3(0, -10000, 0)
_SHOULD_GO_BACK_AFTER_LOADING = 'shouldGoBackAfterLoading'
_PBS_SUBHANGAR_GROUPS_BY_SIZE = (SubhangarStateGroups.PostBattleSmall, SubhangarStateGroups.PostBattleMedium, SubhangarStateGroups.PostBattleLarge)

def registerStates(lsm):
    lsm.addState(PostBattleResultsEntryState())


def _shouldHijack(_):
    lsm = getLobbyStateMachine()
    return lsm.getStateByCls(PostBattleResultsState).isEntered()


def registerTransitions(lsm):
    pbsEntryState = lsm.getStateByCls(PostBattleResultsEntryState)
    lsm.addNavigationTransitionFromParent(pbsEntryState, transitionType=TransitionType.EXTERNAL)
    pbsEntryState.getParent().addTransition(HijackTransition(PostBattleResultsEntryState, _shouldHijack, transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(_LoadingStateWithRetainedCamera))
    pbsEntryState.addTransition(HijackTransition(PostBattleResultsEntryState, _shouldHijack, transitionType=TransitionType.EXTERNAL), lsm.getStateByCls(_LoadingStateWithRetainedCamera))


@SubScopeSubLayerState.parentOf
class PostBattleResultsEntryState(LobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = 'postBattleResultsEntry'
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __battleResults = dependency.descriptor(IBattleResultsService)
    __itemsCache = dependency.descriptor(IItemsCache)
    __itemsFactory = dependency.descriptor(IGuiItemsFactory)
    __c11nService = dependency.descriptor(ICustomizationService)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleResultsEntryState, self).__init__(flags)
        self.__cachedParams = {}

    def getSubhangarStateGroupConfig(self):
        arenaUniqueID = self.__cachedParams.get('arenaUniqueID', None)
        statsController = self.__battleResults.getPresenter(arenaUniqueID)
        teamResultType = SubhangarStateGroups.PostBattleDefeat
        _, reusable = statsController.getResults()
        if reusable:
            teamResult = reusable.getPersonalTeamResult()
            if teamResult == PLAYER_TEAM_RESULT.WIN:
                teamResultType = SubhangarStateGroups.PostBattleVictory
        return SubhangarStateGroupConfig((teamResultType,))

    def registerTransitions(self):
        lsm = self.getMachine()
        lsm.getStateByCls(TrainingRoomState).addNavigationTransition(self, record=True)
        self.addNavigationTransition(lsm.getStateByCls(OverviewState), record=True)
        myDescendants = set(self.getRecursiveChildrenStates())
        for state in self.getParent().getRecursiveChildrenStates():
            if state in myDescendants or state == self or isinstance(state, UntrackedState):
                continue
            if not state.getChildrenStates():
                state.addNavigationTransition(self, record=True)

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(_LoadingState(flags=StateFlags.INITIAL))
        lsm.addState(_LoadingStateWithRetainedCamera())
        lsm.addState(PostBattleResultsState())

    def serializeParams(self):
        return self.__cachedParams

    @classmethod
    def goTo(cls, arenaUniqueID, bonusType):
        super(PostBattleResultsEntryState, cls).goTo(arenaUniqueID=arenaUniqueID, bonusType=bonusType)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))

    def _onEntered(self, event):
        super(PostBattleResultsEntryState, self)._onEntered(event)
        Waiting.show('loadingData')
        self.__cachedParams = dict(event.params)
        if g_pbsFakeData.vehicleAndOffsets and g_pbsFakeData.vehicleName:
            fakeVehicle = g_pbsFakeData.getVehicle()
            if fakeVehicle:
                g_currentPreviewVehicle.selectVehicle(vehicleCD=fakeVehicle.intCD, vehicleStrCD=fakeVehicle.strCD)
                return
        arenaUniqueID = self.__cachedParams.get('arenaUniqueID', None)
        vehicleCD, outfit = _getVehicleCDAndOutfit(self.__battleResults, arenaUniqueID)
        vehicle = self.__itemsCache.items.getVehicleCopyByCD(vehicleCD)
        if vehicle is None:
            g_currentPreviewVehicle.selectVehicle()
            return
        else:
            _, reusable = self.__battleResults.getPresenter(arenaUniqueID).getResults()
            mapKind = reusable.common.arenaType.getVehicleCamouflageKind()
            mapSeason = SeasonType.fromArenaKind(mapKind)
            from vehicle_systems import camouflages
            component = camouflages.getOutfitComponent(outfit, vehicle.descriptor, mapSeason)
            outfit = self.__itemsFactory.createOutfit(component=component, vehicleCD=vehicle.strCD)
            g_currentPreviewVehicle.selectVehicle(vehicleCD=vehicle.intCD, vehicleStrCD=vehicle.strCD, season=mapSeason, outfit=outfit)
            return

    def _onExited(self):
        super(PostBattleResultsEntryState, self)._onExited()
        Waiting.hide('loadingData')
        self.__cachedParams.clear()
        space = self.__hangarSpace.space
        if space is None:
            return
        else:
            g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
            g_currentPreviewVehicle.selectNoVehicle()
            space.turretAndGunAngles.reset()
            return


@PostBattleResultsEntryState.parentOf
class _LoadingState(LobbyState, EventsHandler):
    STATE_ID = 'loading'
    __battleResults = dependency.descriptor(IBattleResultsService)
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LoadingState, self).__init__(flags=flags)
        self.__cachedParams = {}
        self.__callbackDelayer = CallbackDelayer()

    def registerTransitions(self):
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(PostBattleResultsState))

    def _getEvents(self):
        return ((self.__hangarSpace.onVehicleChanged, self.__onSpaceOrVehicleChange), (self.__hangarSpace.onSpaceChanged, self.__onSpaceOrVehicleChange))

    def _onEntered(self, event):
        lockNotificationManager(True, source=self.STATE_ID)
        Waiting.show('loadingData')
        super(_LoadingState, self)._onEntered(event)
        self.__cachedParams = dict(event.params)
        vehicleCD, _ = _getVehicleCDAndOutfit(self.__battleResults, event.params.get('arenaUniqueID'))
        incorrectVehicleLoaded = g_currentPreviewVehicle.intCD != vehicleCD
        hangarReady = self.__hangarSpace.spaceInited or self.__hangarSpace.isModelLoaded
        if not hangarReady or incorrectVehicleLoaded:
            self._subscribe()
        else:
            self.__onSpaceAvailable()
            self.__callbackDelayer.delayCallback(0.0, WeakMethodProxy(self.__goToWhenAABBAvailable))

    def _onExited(self):
        self.__cachedParams.clear()
        self._unsubscribe()
        self.__callbackDelayer.clearCallbacks()
        Waiting.hide('loadingData')
        lockNotificationManager(False, source=self.STATE_ID, releasePostponed=True)
        super(_LoadingState, self)._onExited()

    def __onSpaceOrVehicleChange(self):
        if self.__hangarSpace.spaceInited and self.__hangarSpace.isModelLoaded:
            self.__onSpaceAvailable()
            self.__callbackDelayer.delayCallback(0.0, WeakMethodProxy(self.__goToWhenAABBAvailable))

    def __goToWhenAABBAvailable(self):
        if not hangarVehicleAABB():
            return 0.0
        else:
            if self.__cachedParams.get(_SHOULD_GO_BACK_AFTER_LOADING, False):
                self.goBack()
            else:
                PostBattleResultsState.goTo(**self.__cachedParams)
            return None

    def __onSpaceAvailable(self):
        self.__hangarSpace.space.turretAndGunAngles.set(gunPitch=0.0, turretYaw=0.0)
        ClientSelectableCameraObject.deselectAll()
        self.__hangarSpace.space.getVehicleEntity().onSelect()
        hangarConfig = customizationHangarCFG()
        _moveTank(hangarConfig, _HIDDEN_TANK_LOCATION, (0, 0, 0))


@PostBattleResultsEntryState.parentOf
class _LoadingStateWithRetainedCamera(_LoadingState, SubhangarStateGroupConfigProvider):
    STATE_ID = 'loadingWithRetainedCamera'

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.PostBattleCommon))

    def _onEntered(self, event):
        super(_LoadingStateWithRetainedCamera, self)._onEntered(event)
        Waiting.show('loadingData')

    def _onExited(self):
        super(_LoadingStateWithRetainedCamera, self)._onExited()
        Waiting.hide('loadingData')


@PostBattleResultsEntryState.parentOf
class PostBattleResultsState(SFViewLobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = VIEW_ALIAS.POST_BATTLE_RESULTS
    VIEW_KEY = ViewKey(VIEW_ALIAS.POST_BATTLE_RESULTS)
    _POST_BATTLE_BLUR_SETTINGS_KEY = 'maximum'
    __blurCtrl = dependency.descriptor(IBlurController)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __battleResults = dependency.descriptor(IBattleResultsService)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleResultsState, self).__init__(flags=flags)
        self.__blur = None
        self.__cachedParams = {}
        return

    def getSubhangarStateGroupConfig(self):
        _, reusable = self.__battleResults.getPresenter(self.__cachedParams.get('arenaUniqueID', None)).getResults()
        geometryName = reusable.common.arenaType.getGeometryName()
        mapImageName = getArenaImage(geometryName, 'screen')
        mapImageName = mapImageName.replace('img://', '')
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, _PBS_SUBHANGAR_GROUPS_BY_SIZE), SubhangarStateGroups.PostBattleCommon), _PBSSceneSetup(mapImageName))

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(_OverviewTab(StateFlags.INITIAL))
        lsm.addState(_TeamScoreTab())
        lsm.addState(_MissionProgressTab())
        lsm.addState(_FinancialReportTab())

    def registerTransitions(self):
        lsm = self.getMachine()
        for child in self.getChildrenStates():
            lsm.addNavigationTransitionFromParent(child)
            child.addGuardTransition(child, self.__preventNavigationOutside)

    @prbDispatcherProperty
    def prbDispatcher(self):
        pass

    def __preventNavigationOutside(self, event):
        from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
        prbDispatcher = self.prbDispatcher
        if prbDispatcher is None or not prbDispatcher.getFunctionalState().isNavigationDisabled():
            return False
        else:
            targetID = event.targetStateID
            lsm = self.getMachine()
            target = lsm.getStateByID(targetID)
            parentDescendants = self.getParent().getRecursiveChildrenStates()
            battleQueueDescendants = lsm.getStateByCls(BattleQueueContainerState).getRecursiveChildrenStates()
            eventTargetingOutside = target != self.getParent() and target not in parentDescendants and target not in battleQueueDescendants
            if eventTargetingOutside:
                SystemMessages.pushI18nMessage('#system_messages:queue/isInQueue', type=SystemMessages.SM_TYPE.Error, priority='high')
            return eventTargetingOutside

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))

    @property
    def blur(self):
        return self.__blur

    def getViewKey(self, params=None):
        arenaUniqueID = self.__cachedParams.get('arenaUniqueID', '')
        alias = super(PostBattleResultsState, self).getViewKey().alias
        return ViewKey(alias, getViewName(alias, arenaUniqueID))

    def _getView(self):
        from skeletons.gui.app_loader import IAppLoader
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        return view.content

    def _onEntered(self, event):
        lockNotificationManager(True, source=self.STATE_ID)
        self.__cachedParams = dict(event.params)
        super(PostBattleResultsState, self)._onEntered(event)
        lockNotificationManager(False, source=self.STATE_ID, releasePostponed=True)
        self.__blur = self.__blurCtrl.createBlur((ImmediateSceneBlurConfig(spaceID=self.__hangarSpace.spaceID, settings=self.__blurCtrl.getSettingsByAlias(self._POST_BATTLE_BLUR_SETTINGS_KEY)),))

    def _onExited(self):
        self.__blur.disable()
        self.__blur.fini()
        self.__blur = None
        self.__cachedParams = {}
        super(PostBattleResultsState, self)._onExited()
        return

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}


class PostBattleTab(LobbyState):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(PostBattleTab, self).__init__(flags=flags)
        self.__cachedParams = None
        return

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        super(PostBattleTab, self)._onEntered(event)
        self.__cachedParams = event.params
        if hangarVehicleAABB() and self.__hangarSpace.spaceInited and self.__hangarSpace.isModelLoaded:
            return
        self.__cachedParams[_SHOULD_GO_BACK_AFTER_LOADING] = True
        _LoadingState.goTo(**self.__cachedParams)


@PostBattleResultsState.parentOf
class _OverviewTab(PostBattleTab):
    STATE_ID = 'overview'

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))


class _BlurredResultTab(PostBattleTab):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.battle_results()))

    def _onEntered(self, event):
        super(_BlurredResultTab, self)._onEntered(event)
        self.getParent().blur.enable()

    def _onExited(self):
        super(_BlurredResultTab, self)._onExited()
        self.getParent().blur.disable()


@PostBattleResultsState.parentOf
class _TeamScoreTab(_BlurredResultTab):
    STATE_ID = 'teamScore'


@PostBattleResultsState.parentOf
class _MissionProgressTab(_BlurredResultTab):
    STATE_ID = 'missionProgress'


@PostBattleResultsState.parentOf
class _FinancialReportTab(_BlurredResultTab):
    STATE_ID = 'financialReport'


class _PBSSceneSetup(CameraMover):
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def __init__(self, mapImageName):
        self.__mapImageName = mapImageName

    def moveCamera(self, cameraManager, cameraName):
        super(_PBSSceneSetup, self).moveCamera(cameraManager, cameraName)
        hangarConfig = customizationHangarCFG()
        _moveTank(hangarConfig, hangarConfig['v_start_pos'], tuple((math.radians(angle) for angle in hangarConfig['v_start_angles'])))
        spaceID = self.__hangarSpace.spaceID
        pbsManager = CGF.getManager(spaceID, PostBattleManager)
        if pbsManager and self.__mapImageName:
            pbsManager.applyArenaImage(self.__mapImageName)
        Waiting.hide('loadingData')


def _getVehicleCDAndOutfit(battleResultsService, arenaUniqueID):
    statsController = battleResultsService.getPresenter(arenaUniqueID)
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
