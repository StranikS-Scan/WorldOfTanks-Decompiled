# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/impl/lobby/states.py
from __future__ import absolute_import
import time
import typing
from WeakMethod import WeakMethodProxy
from frameworks_common.state_machine import StateFlags
from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
from gui.Scaleform.daapi.view.lobby.battle_queue.states import CommonBattleQueueState
from gui.Scaleform.daapi.view.lobby.shared.states import BrowserLobbyTopState
from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_results.service import PostBattleResultsStateMixin
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.crew.states import BarracksState
from gui.impl.lobby.hangar.base.proto_states import generateBasicLoadoutStateClasses, _LoadoutConfirmStatePrototype, _ConsumablesLoadoutStatePrototype, _LoadoutStatePrototype
from gui.impl.lobby.hangar.states import HangarState
from gui.impl.lobby.tank_setup.tank_setup_sounds import playEnterTankSetupView
from gui.impl.lobby.vehicle_hub import OverviewState, ModulesState, VehSkillTreeState, StatsState, ArmorState
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyState, SFViewLobbyState, SubScopeSubLayerState, LobbyStateFlags, SubScopeTopLayerState, TopScopeTopLayerState, LobbyStateDescription, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.prb_control import prbEntityProperty
from gui.shared.events import NavigationEvent
from halloween.gui.impl.lobby.bestiary.states import HWBestiaryState
from halloween.gui.impl.lobby.bundle_view import BundleView
from halloween.gui.impl.lobby.pre_battle_queue_view import PreBattleQueueView
from halloween.gui.scaleform.genConsts.HALLOWEEN_HANGAR_ALIASES import HALLOWEEN_HANGAR_ALIASES
from halloween.gui.shared.event_dispatcher import showIntroVideo, showMetaIntroView
from halloween.skeletons.halloween_controller import IHalloweenController
from halloween.gui.halloween_gui_constants import VIEW_ALIAS
from skeletons.gui.app_loader import IAppLoader
from helpers import dependency
from gui.impl.lobby.vehicle_hub.states import VehicleHubState
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

def registerStates(machine):
    machine.addState(HalloweenModeState())
    machine.addState(HalloweenBattleResultsState())
    machine.addState(HWBestiaryState())


def registerTransitions(machine):
    halloweenMode = machine.getStateByCls(HalloweenModeState)
    machine.addNavigationTransitionFromParent(halloweenMode)
    halloweenBestiary = machine.getStateByCls(HWBestiaryState)
    machine.addNavigationTransitionFromParent(halloweenBestiary)
    halloweenExchange = machine.getStateByCls(HalloweenExchangeScreenState)
    machine.addNavigationTransitionFromParent(halloweenExchange)


@SubScopeSubLayerState.parentOf
class HalloweenModeState(LobbyState):
    STATE_ID = 'halloween'
    halloweenCtrl = dependency.descriptor(IHalloweenController)

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(HalloweenHangarState(StateFlags.INITIAL))
        machine.addState(RewardPathState())
        machine.addState(HalloweenVehiclePreviewState())
        machine.addState(HalloweenHeroTankPreviewState())
        machine.addState(HalloweenPreBattleQueueState())
        machine.addState(HalloweenExchangeScreenState())
        machine.addState(HalloweenLoadoutState())
        machine.addState(AnomaliesState())

    def registerTransitions(self):
        machine = self.getMachine()
        parent = self.getParent()
        hangar = machine.getStateByCls(HalloweenHangarState)
        parent.addNavigationTransition(hangar, record=True)
        parent.addTransition(HijackTransition(HangarState, WeakMethodProxy(self._isEventPrb)), hangar)
        hangarRoot = machine.getStateByCls(HalloweenRootHangarState)
        hangar.addNavigationTransition(hangarRoot)
        exchangeScreen = machine.getStateByCls(HalloweenExchangeScreenState)
        hangar.addNavigationTransition(exchangeScreen)
        rewardPath = machine.getStateByCls(RewardPathState)
        rewardPath.addNavigationTransition(exchangeScreen)
        hangar.addNavigationTransition(rewardPath, record=True)
        preBattleQueue = machine.getStateByCls(HalloweenPreBattleQueueState)
        hangar.addNavigationTransition(preBattleQueue, record=True)
        parent.addTransition(HijackTransition(CommonBattleQueueState, WeakMethodProxy(self._isEventPrb)), preBattleQueue)
        bestiaryScreen = machine.getStateByCls(HWBestiaryState)
        hangar.addNavigationTransition(bestiaryScreen, record=True)
        bestiaryScreen.addNavigationTransition(hangar)
        anomaliesScreen = machine.getStateByCls(AnomaliesState)
        hangar.addNavigationTransition(anomaliesScreen)
        states = (machine.getStateByCls(OverviewState),
         machine.getStateByCls(ModulesState),
         machine.getStateByCls(VehSkillTreeState),
         machine.getStateByCls(StatsState),
         machine.getStateByCls(ArmorState),
         machine.getStateByCls(VehiclePostProgressionState),
         machine.getStateByCls(HalloweenVehiclePreviewState),
         machine.getStateByCls(BarracksState))
        self._registrationTransition(hangar, rewardPath, states)
        vehicleHub = machine.getStateByCls(VehicleHubState)
        vehicleHub.addNavigationTransition(hangar)
        vehicleHub.addNavigationTransition(rewardPath)

    def _registrationTransition(self, hangar, rewardPath, states):
        for state in states:
            hangar.addNavigationTransition(state, record=True)
            rewardPath.addNavigationTransition(state, record=True)

    @classmethod
    def _isEventPrb(cls, event):
        return cls.halloweenCtrl.isEnabled() and cls.halloweenCtrl.isEventPrb()


@HalloweenModeState.parentOf
class HalloweenHangarState(SFViewLobbyState):
    STATE_ID = 'hangar'
    VIEW_KEY = ViewKey(HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_HANGAR)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(HalloweenHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)
        self.__cachedParams = {}

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(HalloweenRootHangarState(flags=StateFlags.INITIAL))

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.halloween_lobby.headerButtons.battle.types.halloween()))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        super(HalloweenHangarState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self.__cachedParams = {}
        super(HalloweenHangarState, self)._onExited()


@HalloweenHangarState.parentOf
class HalloweenRootHangarState(LobbyState):
    STATE_ID = '{root}'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(HalloweenRootHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)


@HalloweenModeState.parentOf
class RewardPathState(SFViewLobbyState):
    STATE_ID = HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_REWARD_PATH
    VIEW_KEY = ViewKey(HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_REWARD_PATH)
    halloweenCtrl = dependency.descriptor(IHalloweenController)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(RewardPathState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def getNavigationDescription(self):
        infos = []
        if self.halloweenCtrl.isInfoMetaEnabled():
            infos.append(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showMetaIntroView, tooltipBody=backport.text(R.strings.halloween_lobby.rewardPath.aboutTooltip())))
        if self.halloweenCtrl.isIntroVideoEnabled():
            infos.append(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.VIDEO, onMoreInfoRequested=showIntroVideo, tooltipBody=backport.text(R.strings.halloween_lobby.rewardPath.introTooltip())))
        return LobbyStateDescription(title=backport.text(R.strings.halloween_lobby.metaCmp.name()), infos=infos)

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.halloween_lobby.common.toRewardPath())

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        super(RewardPathState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self.__cachedParams = {}
        super(RewardPathState, self)._onExited()


@BattleQueueContainerState.parentOf
class HalloweenPreBattleQueueState(GuiImplViewLobbyState):
    STATE_ID = 'halloweenPreBattleQueue'
    VIEW_KEY = ViewKey(R.views.halloween.mono.lobby.pre_battle_queue_view())

    def __init__(self):
        super(HalloweenPreBattleQueueState, self).__init__(PreBattleQueueView, ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__startTime = None
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.halloween_lobby.preBattle.searching()))

    def serializeParams(self):
        return {'startTime': self.__startTime}

    def _getViewLoadCtx(self, event):
        return {'startTime': self.__startTime}

    def _onEntered(self, event):
        self.__startTime = event.params.get('startTime', time.time() * 1000)
        super(HalloweenPreBattleQueueState, self)._onEntered(event)

    def _onExited(self):
        self.__startTime = None
        super(HalloweenPreBattleQueueState, self)._onExited()
        return


@HalloweenModeState.parentOf
class HalloweenVehiclePreviewState(SFViewLobbyState):
    STATE_ID = HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_VEHICLE_PREVIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(HalloweenVehiclePreviewState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        machine = self.getMachine()
        vehiclePostProgression = machine.getStateByCls(VehiclePostProgressionState)
        self.addNavigationTransition(vehiclePostProgression, record=True)
        heroTankPreview = machine.getStateByCls(HalloweenHeroTankPreviewState)
        self.addNavigationTransition(heroTankPreview, record=True)
        self.addNavigationTransition(machine.getStateByCls(OverviewState), record=True)
        self.addNavigationTransition(machine.getStateByCls(ModulesState), record=True)
        self.addNavigationTransition(machine.getStateByCls(StatsState), record=True)
        self.addNavigationTransition(machine.getStateByCls(ArmorState), record=True)
        self.addNavigationTransition(machine.getStateByCls(VehSkillTreeState), record=True)

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.vehicle_preview.header.title()))

    def _onEntered(self, event):
        from ClientSelectableCameraObject import ClientSelectableCameraObject
        ClientSelectableCameraObject.switchCamera()
        super(HalloweenVehiclePreviewState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self.__cachedParams = {}
        super(HalloweenVehiclePreviewState, self)._onExited()

    def _getViewLoadCtx(self, event):
        if 'ctx' in event.params:
            return super(HalloweenVehiclePreviewState, self)._getViewLoadCtx(event)
        ctx = {}
        for key, value in event.params.items():
            ctx[key] = value

        return {'ctx': ctx}


@HalloweenModeState.parentOf
class HalloweenHeroTankPreviewState(SFViewLobbyState):
    STATE_ID = HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_HERO_PREVIEW
    VIEW_KEY = ViewKey(HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_HERO_PREVIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(HalloweenHeroTankPreviewState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        machine = self.getMachine()
        vehiclePostProgression = machine.getStateByCls(VehiclePostProgressionState)
        self.addNavigationTransition(vehiclePostProgression, record=True)

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.vehicle_preview.hero.header.title()))

    def _onEntered(self, event):
        super(HalloweenHeroTankPreviewState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self._prepareExited()
        self.__cachedParams = {}
        super(HalloweenHeroTankPreviewState, self)._onExited()

    def _getViewLoadCtx(self, event):
        if 'ctx' in event.params:
            return super(HalloweenHeroTankPreviewState, self)._getViewLoadCtx(event)
        ctx = {}
        for key, value in event.params.items():
            ctx[key] = value

        return {'ctx': ctx}

    def _prepareExited(self):
        app = dependency.instance(IAppLoader).getApp()
        view = app.containerManager.getViewByKey(self.VIEW_KEY)
        if view is not None:
            view.removeListener(CameraRelatedEvents.CAMERA_ENTITY_UPDATED, view.handleSelectedEntityUpdated)
        return


@SubScopeTopLayerState.parentOf
class HalloweenExchangeScreenState(GuiImplViewLobbyState):
    STATE_ID = 'halloweenExchangeScreenState'
    VIEW_KEY = ViewKey(R.views.halloween.mono.lobby.bundles_shop())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(HalloweenExchangeScreenState, self).__init__(BundleView, ScopeTemplates.LOBBY_SUB_SCOPE, flags=flags)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.halloween_lobby.bundleView.title()))

    def registerTransitions(self):
        machine = self.getMachine()
        exchangeScreenState = machine.getStateByCls(HalloweenExchangeScreenState)
        exchangeScreenState.addNavigationTransition(machine.getStateByCls(BrowserLobbyTopState))
        exchangeScreenState.addNavigationTransition(machine.getStateByCls(BarracksState))


@TopScopeTopLayerState.parentOf
class HalloweenBattleResultsState(ViewLobbyState, PostBattleResultsStateMixin):
    STATE_ID = VIEW_ALIAS.HALLOWEEN_BATTLE_RESULTS
    VIEW_KEY = ViewKey(VIEW_ALIAS.HALLOWEEN_BATTLE_RESULTS)

    def registerTransitions(self):
        machine = self.getMachine()
        machine.addNavigationTransitionFromParent(self)


class _HalloweenLoadoutConfirmStateProto(_LoadoutConfirmStatePrototype):
    STATE_ID = 'halloweenLoadoutConfirmLeave'


class _HalloweenLoadoutStateCls(_LoadoutStatePrototype):
    STATE_ID = 'loadout'

    def _onEntered(self, event):
        playEnterTankSetupView()


class _HalloweenConsumableLoadoutState(_ConsumablesLoadoutStatePrototype):
    STATE_ID = 'hw_consumables'

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.halloween_lobby.hangarAmmunitionSetup.header()))


HalloweenLoadoutState, _, _, _, _, _, HalloweenConsumablesLoadoutState = generateBasicLoadoutStateClasses(HalloweenHangarState, R.invalid, consumablesStatePrototypeCls=_HalloweenConsumableLoadoutState, loadoutStatePrototypeCls=_HalloweenLoadoutStateCls, confirmStatePrototypeCls=_HalloweenLoadoutConfirmStateProto)

@HalloweenModeState.parentOf
class AnomaliesState(SFViewLobbyState):
    STATE_ID = HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_ANOMALIES
    VIEW_KEY = ViewKey(HALLOWEEN_HANGAR_ALIASES.HALLOWEEN_ANOMALIES)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.halloween_lobby.anomaliesView.header()))
