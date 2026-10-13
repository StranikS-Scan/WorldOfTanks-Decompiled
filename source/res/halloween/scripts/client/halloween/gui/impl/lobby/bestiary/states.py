# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/bestiary/states.py
from __future__ import absolute_import
import math
import typing
import BigWorld
from CurrentVehicle import g_currentPreviewVehicle
from WeakMethod import WeakMethodProxy
from frameworks_common.state_machine import StateFlags
from frameworks_common.state_machine.transitions import TransitionType
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.vehicle_hub.camera_mover import VehicleHubCameraMover
from gui.impl.lobby.vehicle_hub.sound_constants import VH_SOUND_SPACE
from gui.lobby_state_machine.events import _BackNavigationGeneratedNavigationEvent
from gui.lobby_state_machine.states import SubScopeSubLayerState, SFViewLobbyState, LobbyStateFlags, LobbyState, LobbyStateDescription
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events
from gui.shared.events import NavigationEvent
from gui.subhangar.subhangar_observer import selectItemByTankSize, hangarVehicleAABB
from gui.subhangar.subhangar_state_groups import SubhangarStateGroupConfigProvider, SubhangarStateGroups, SubhangarStateGroupConfig
from halloween.gui.impl.lobby.hw_helpers.bestiary_helper import getOutfit, getLastSelectedEnemy
from halloween.gui.scaleform.genConsts.HALLOWEEN_HANGAR_ALIASES import HALLOWEEN_HANGAR_ALIASES
from halloween.skeletons.halloween_bestiary_controller import IHalloweenBestiaryController
from halloween_common.configs.halloween_bestiary import EnemyModel
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.shared import IItemsCache
from skeletons.gui.shared.utils import IHangarSpace
from sound_gui_manager import ViewSoundExtension
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
_CAMERA_TRANSITION_DURATION = 0.8
_TANK_SIZE_LOWER_BOUNDS = (float('-inf'), 5.0, 8.0)

@SubScopeSubLayerState.parentOf
class HWBestiaryState(SFViewLobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_BESTIARY
    VIEW_KEY = ViewKey(HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_BESTIARY)
    __hangarSpace = dependency.descriptor(IHangarSpace)
    __soundExtension = ViewSoundExtension(VH_SOUND_SPACE)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(HWBestiaryState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)
        self.__cameraMover = None
        return

    @property
    def cameraMover(self):
        return self.__cameraMover

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((SubhangarStateGroups.VehicleHub,))

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(HWBestiaryEntryState(LobbyStateFlags.INITIAL))
        lsm.addState(_HWBestiaryLoadingState())
        lsm.addState(HWBestiaryOverviewState())

    def registerTransitions(self):
        lsm = self.getMachine()
        loadingState = lsm.getStateByCls(_HWBestiaryLoadingState)
        for state in self.getChildrenStates():
            if state is not loadingState:
                self.getParent().addNavigationTransition(state)
                self.addNavigationTransition(state)

    @classmethod
    def goTo(cls, vehIntCD=None):
        super(HWBestiaryState, cls).goTo(vehIntCD=vehIntCD)

    def _getViewLoadCtx(self, event):
        return {'ctx': event.params}

    def _onEntered(self, event):
        super(HWBestiaryState, self)._onEntered(event)
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
        super(HWBestiaryState, self)._onExited()
        self.__soundExtension.destroySoundManager()
        g_currentPreviewVehicle.selectNoVehicle()
        g_eventBus.handleEvent(events.HangarCustomizationEvent(events.HangarCustomizationEvent.RESET_VEHICLE_MODEL_TRANSFORM), scope=EVENT_BUS_SCOPE.LOBBY)
        if self.__hangarSpace.spaceInited:
            self.__hangarSpace.space.turretAndGunAngles.reset()
        return


@HWBestiaryState.parentOf
class HWBestiaryEntryState(LobbyState):
    STATE_ID = 'hwBestiaryEntry'


@HWBestiaryState.parentOf
class HWBestiaryOverviewState(LobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = 'hwBestiaryOverview'
    _SUBHANGAR_GROUPS_BY_TANK_SIZE = (SubhangarStateGroups.VehicleHubOverviewSmallTank, SubhangarStateGroups.VehicleHubOverviewMediumTank, SubhangarStateGroups.VehicleHubOverviewLargeTank)
    hwBestiaryCtrl = dependency.descriptor(IHalloweenBestiaryController)

    def registerTransitions(self):
        super(HWBestiaryOverviewState, self).registerTransitions()
        self.addNavigationTransition(self, transitionType=TransitionType.EXTERNAL)
        lsm = self.getMachine()
        loadingState = lsm.getStateByCls(_HWBestiaryLoadingState)
        self.addTransition(loadingState.makeTransition(TransitionType.INTERNAL, True), loadingState)

    def _onEntered(self, event):
        super(HWBestiaryOverviewState, self)._onEntered(event)
        if isinstance(event, _BackNavigationGeneratedNavigationEvent):
            return
        intCD = event.params.get('vehIntCD') or self.hwBestiaryCtrl.getFirstNewEnemy() or getLastSelectedEnemy()
        if g_currentPreviewVehicle.intCD != intCD or not hangarVehicleAABB():
            _HWBestiaryLoadingState.goTo(group=selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, self._SUBHANGAR_GROUPS_BY_TANK_SIZE), enemy=self.hwBestiaryCtrl.getEnemyByIntCD(intCD), intCD=int(intCD))

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.halloween_lobby.bestiaryView.title()))

    def getSubhangarStateGroupConfig(self):
        return SubhangarStateGroupConfig((selectItemByTankSize(_TANK_SIZE_LOWER_BOUNDS, self._SUBHANGAR_GROUPS_BY_TANK_SIZE),), self.getParent().cameraMover)


@HWBestiaryState.parentOf
class _HWBestiaryLoadingState(LobbyState, SubhangarStateGroupConfigProvider):
    STATE_ID = 'hwBestiaryLoading'
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(_HWBestiaryLoadingState, self).__init__(flags)
        self.__callbackDelayer = CallbackDelayer()
        self.__cachedParams = {}

    def _onEntered(self, event):
        super(_HWBestiaryLoadingState, self)._onEntered(event)
        self.__cachedParams = event.params
        enemy = self.__cachedParams.get('enemy')
        intCD = self.__cachedParams.get('intCD')
        outfit = getOutfit(enemy.style, intCD) if enemy.style else None
        vehicle = self.itemsCache.items.getItemByCD(intCD)
        g_currentPreviewVehicle.selectVehicle(vehicleCD=intCD, vehicleStrCD=vehicle.strCD, outfit=outfit)
        self.__callbackDelayer.delayCallback(0.0, WeakMethodProxy(self.__navigateBackWhenAABBAvailable))
        return

    def _onExited(self):
        super(_HWBestiaryLoadingState, self)._onExited()
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
