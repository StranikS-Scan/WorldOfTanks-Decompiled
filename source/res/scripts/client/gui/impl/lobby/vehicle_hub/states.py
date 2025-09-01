# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_hub/states.py
from __future__ import absolute_import
import logging
import math
import typing
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.sub_models.veh_skill_tree_model import VehSkillTreeModel
from gui.impl.gen.view_models.views.lobby.vehicle_hub.views.vehicle_hub_view_model import VehicleHubViewModel
from gui.impl.lobby.blueprints.states import BlueprintState
from gui.impl.lobby.vehicle_hub.camera_mover import VehicleHubCameraMover
from gui.impl.lobby.vehicle_hub.sound_constants import VH_SOUND_SPACE
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState, LobbyState, LobbyStateFlags, LobbyStateDescription
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils.module_upd_available_helper import updateViewedItems
from gui.shared.view_helpers.blur_manager import CachedBlur
from gui.subhangar.subhangar_observer import selectItemByTankSize, hangarVehicleAABB
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroups, SubhangarStateGroupConfig
from gui.veh_post_progression.models.progression import PostProgressionCompletion
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from sound_gui_manager import ViewSoundExtension
if typing.TYPE_CHECKING:
    from gui.impl.lobby.vehicle_hub.vehicle_hub_main_view import VehicleHubCtx, VehicleHubMainView
_logger = logging.getLogger(__name__)
_CAMERA_TRANSITION_DURATION = 0.8
_TANK_SIZE_LOWER_BOUNDS = (float('-inf'), 5.0, 8.0)

def registerStates(machine):
    machine.addState(VehicleHubState())


def registerTransitions(machine):
    vehicleHub = machine.getStateByCls(VehicleHubState)
    machine.addNavigationTransitionFromParent(vehicleHub)


class _VehicleHubChildState(LobbyState, SubhangarStateGroupConfigProvider):
    TAB_NAME = ''
    _SUBHANGAR_GROUPS_BY_TANK_SIZE = None
    __hangarSpace = dependency.descriptor(IHangarSpace)

    def registerTransitions(self):
        super(_VehicleHubChildState, self).registerTransitions()
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)
        from gui.Scaleform.daapi.view.lobby.vehicle_compare.states import VehicleCompareState
        lsm = self.getMachine()
        self.addNavigationTransition(lsm.getStateByCls(VehicleCompareState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(BlueprintState), record=True)
        self.addNavigationTransition(lsm.getStateByCls(_LoadingState), record=True)
        from gui.Scaleform.daapi.view.lobby.profile.states import ServiceRecordState
        self.addNavigationTransition(lsm.getStateByCls(ServiceRecordState), record=True)

    def _onEntered(self, event):
        super(_VehicleHubChildState, self)._onEntered(event)
        vhCtx = event.params.get('vhCtx')
        if not vhCtx:
            return
        incorrectVehicleLoaded = g_currentPreviewVehicle.intCD != vhCtx.intCD
        if incorrectVehicleLoaded or not hangarVehicleAABB():
            group = selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, self._SUBHANGAR_GROUPS_BY_TANK_SIZE)
            _LoadingState.goTo(group=group, **event.params)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.vehicle_hub()))

    def getSubhangarStateGroupConfig(self):
        if not self._SUBHANGAR_GROUPS_BY_TANK_SIZE:
            _logger.error('Subhangar groups cannot be none.')
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, self._SUBHANGAR_GROUPS_BY_TANK_SIZE),), self.getParent().cameraMover)


@SubScopeSubLayerState.parentOf
class VehicleHubState(SFViewLobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = VIEW_ALIAS.VEHICLE_HUB
    VIEW_KEY = ViewKey(VIEW_ALIAS.VEHICLE_HUB)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __itemsCache = dependency.descriptor(IItemsCache)
    __soundExtension = ViewSoundExtension(VH_SOUND_SPACE)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(VehicleHubState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)
        self.__cameraMover = None
        return

    @property
    def cameraMover(self):
        return self.__cameraMover

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((SubhangarStateGroups.VehicleHub,))

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(EntryState(LobbyStateFlags.INITIAL))
        lsm.addState(_LoadingState())
        lsm.addState(OverviewState())
        lsm.addState(ModulesState())
        lsm.addState(VehSkillTreeState())
        lsm.addState(StatsState())
        lsm.addState(ArmorState())

    def registerTransitions(self):
        lsm = self.getMachine()
        loadingState = lsm.getStateByCls(_LoadingState)
        for state in self.getChildrenStates():
            if state is not loadingState:
                self.getParent().addNavigationTransition(state)
                self.addNavigationTransition(state)

    @classmethod
    def goTo(cls, vhCtx):
        super(VehicleHubState, cls).goTo(vhCtx=vhCtx)

    def serializeParams(self):
        view = self.getMachine().getRelatedView(self)
        return {} if not view else {'vhCtx': view.vehicleCtx}

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params.get('vhCtx')}

    def _onEntered(self, event):
        super(VehicleHubState, self)._onEntered(event)
        self.__soundExtension.initSoundManager()
        self.__soundExtension.startSoundSpace()
        self.__setupTankTransformation()
        self.__cameraMover = VehicleHubCameraMover(_CAMERA_TRANSITION_DURATION)

    def __setupTankTransformation(self):
        from gui.ClientHangarSpace import customizationHangarCFG
        cfg = customizationHangarCFG()
        isForwardPipeline = BigWorld.getGraphicsSetting('RENDER_PIPELINE') == 1
        targetPos = cfg['v_start_pos']
        yaw = math.radians(cfg['v_start_angles'][0])
        pitch = math.radians(cfg['v_start_angles'][1])
        roll = math.radians(cfg['v_start_angles'][2])
        shadowYOffset = cfg['shadow_forward_y_offset'] if isForwardPipeline else cfg['shadow_deferred_y_offset']
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.CHANGE_VEHICLE_MODEL_TRANSFORM, ctx={'targetPos': targetPos,
         'rotateYPR': (yaw, pitch, roll),
         'shadowYOffset': shadowYOffset}), scope=EVENT_BUS_SCOPE.LOBBY)

    def _onExited(self):
        self.__cameraMover = None
        self.getMachine().getRelatedView(self).stateExited()
        super(VehicleHubState, self)._onExited()
        self.__soundExtension.destroySoundManager()
        g_currentPreviewVehicle.selectNoVehicle()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__hangarSpace.spaceInited:
            self.__hangarSpace.space.turretAndGunAngles.reset()
        return


@VehicleHubState.parentOf
class EntryState(LobbyState):
    STATE_ID = 'entry'


@VehicleHubState.parentOf
class _LoadingState(LobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = 'loading'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_LoadingState, self).__init__(flags)
        self.__callbackDelayer = CallbackDelayer()
        self.__cachedParams = {}

    def _onEntered(self, event):
        super(_LoadingState, self)._onEntered(event)
        self.__callbackDelayer.delayCallback(0.0, WeakMethodProxy(self.__navigateBackWhenAABBAvailable))
        self.__cachedParams = event.params

    def _onExited(self):
        super(_LoadingState, self)._onExited()
        self.__callbackDelayer.clearCallbacks()
        self.__cachedParams = {}

    def __navigateBackWhenAABBAvailable(self):
        if hangarVehicleAABB():
            self.goBack()
            return None
        else:
            return 0

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((self.__cachedParams.get('group'),), self.getParent().cameraMover)


@VehicleHubState.parentOf
class OverviewState(_VehicleHubChildState):
    STATE_ID = VehicleHubViewModel.OVERVIEW
    TAB_NAME = VehicleHubViewModel.OVERVIEW
    _SUBHANGAR_GROUPS_BY_TANK_SIZE = (SubhangarStateGroups.VehicleHubOverviewSmallTank, SubhangarStateGroups.VehicleHubOverviewMediumTank, SubhangarStateGroups.VehicleHubOverviewLargeTank)


@VehicleHubState.parentOf
class ModulesState(_VehicleHubChildState):
    STATE_ID = VehicleHubViewModel.MODULES
    TAB_NAME = VehicleHubViewModel.MODULES
    _SUBHANGAR_GROUPS_BY_TANK_SIZE = (SubhangarStateGroups.VehicleHubModulesSmallTank, SubhangarStateGroups.VehicleHubModulesMediumTank, SubhangarStateGroups.VehicleHubModulesLargeTank)

    def registerTransitions(self):
        super(ModulesState, self).registerTransitions()
        from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
        vehiclePostProgression = self.getMachine().getStateByCls(VehiclePostProgressionState)
        self.addNavigationTransition(vehiclePostProgression, record=True)

    def _onEntered(self, event):
        super(ModulesState, self)._onEntered(event)
        vhCtx = event.params.get('vhCtx')
        if not vhCtx:
            return
        updateViewedItems(vhCtx.intCD)


@VehicleHubState.parentOf
class VehSkillTreeState(_VehicleHubChildState):
    STATE_ID = VehicleHubViewModel.VEH_SKILL_TREE
    TAB_NAME = VehicleHubViewModel.VEH_SKILL_TREE
    _SUBHANGAR_GROUPS_BY_TANK_SIZE = (SubhangarStateGroups.VehicleHubUpgradesSmallTank, SubhangarStateGroups.VehicleHubUpgradesMediumTank, SubhangarStateGroups.VehicleHubUpgradesLargeTank)

    def registerStates(self):
        self.addChildState(VehSkillTreeInitialState(LobbyStateFlags.INITIAL))
        self.addChildState(VehSkillTreeProgressionState())
        self.addChildState(VehSkillTreePrestigeState())

    def registerTransitions(self):
        super(VehSkillTreeState, self).registerTransitions()
        for state in self.getChildrenStates():
            self.getParent().addNavigationTransition(state)
            self.addNavigationTransition(state)


class _VehSkillTreeSubStateBase(LobbyState):

    def getNavigationDescription(self):
        from gui.shared.event_dispatcher import showVehSkillTreeIntro
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.vehicle_hub()), infos=(LobbyStateDescription.Info(tooltipBody=backport.text(R.strings.veh_skill_tree.intro.button.tooltip()), onMoreInfoRequested=showVehSkillTreeIntro),))


@VehSkillTreeState.parentOf
class VehSkillTreeInitialState(_VehSkillTreeSubStateBase):
    STATE_ID = VehSkillTreeModel.INITIAL
    __itemsCache = dependency.descriptor(IItemsCache)

    def _onEntered(self, event):
        super(VehSkillTreeInitialState, self)._onEntered(event)
        view = self.getMachine().getRelatedView(self)
        vhCtx = view.vehicleCtx
        vehicle = self.__itemsCache.items.getItemByCD(vhCtx.intCD)
        if vehicle is not None and vehicle.postProgression.isVehSkillTree():
            if vehicle.postProgression.getCompletion() == PostProgressionCompletion.FULL:
                VehSkillTreePrestigeState.goTo(vhCtx=vhCtx)
            else:
                VehSkillTreeProgressionState.goTo(vhCtx=vhCtx)
        else:
            _logger.error("Vehicle created from intCD:%d can't be None.", vhCtx.intCD)
        return


@VehSkillTreeState.parentOf
class VehSkillTreeProgressionState(_VehSkillTreeSubStateBase):
    STATE_ID = VehSkillTreeModel.TREE
    SUB_TAB_NAME = VehSkillTreeModel.TREE

    def registerTransitions(self):
        super(VehSkillTreeProgressionState, self).registerTransitions()
        machine = self.getMachine()
        subScopeSubLayerState = machine.getStateByCls(SubScopeSubLayerState)
        subScopeSubLayerState.addNavigationTransition(self)


@VehSkillTreeState.parentOf
class VehSkillTreePrestigeState(_VehSkillTreeSubStateBase):
    STATE_ID = VehSkillTreeModel.PRESTIGE
    SUB_TAB_NAME = VehSkillTreeModel.PRESTIGE

    def registerTransitions(self):
        super(VehSkillTreePrestigeState, self).registerTransitions()
        machine = self.getMachine()
        subScopeSubLayerState = machine.getStateByCls(SubScopeSubLayerState)
        subScopeSubLayerState.addNavigationTransition(self)


@VehicleHubState.parentOf
class StatsState(_VehicleHubChildState):
    STATE_ID = VehicleHubViewModel.STATS
    TAB_NAME = VehicleHubViewModel.STATS
    _SUBHANGAR_GROUPS_BY_TANK_SIZE = (SubhangarStateGroups.VehicleHubStatsSmallTank, SubhangarStateGroups.VehicleHubStatsMediumTank, SubhangarStateGroups.VehicleHubStatsLargeTank)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(StatsState, self).__init__(flags=flags)
        self.__blur = None
        return

    def _onEntered(self, event):
        super(StatsState, self)._onEntered(event)
        self.__blur = CachedBlur(enabled=True)

    def _onExited(self):
        super(StatsState, self)._onExited()
        self.__blur.disable()
        self.__blur.fini()
        self.__blur = None
        return


@VehicleHubState.parentOf
class ArmorState(_VehicleHubChildState):
    STATE_ID = VehicleHubViewModel.ARMOR
    TAB_NAME = VehicleHubViewModel.ARMOR
    _SUBHANGAR_GROUPS_BY_TANK_SIZE = (SubhangarStateGroups.VehicleHubArmorSmallTank, SubhangarStateGroups.VehicleHubArmorMediumTank, SubhangarStateGroups.VehicleHubArmorLargeTank)
