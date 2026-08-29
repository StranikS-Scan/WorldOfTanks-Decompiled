# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/states.py
from __future__ import absolute_import
import time
import typing
from WeakMethod import WeakMethodProxy
from frameworks_common.state_machine import StateFlags
from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.battle_results.service import PostBattleResultsStateMixin
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import _LoadoutConfirmStatePrototype, generateBasicLoadoutStateClasses, _LoadoutStatePrototype, _ConsumablesLoadoutStatePrototype
import gui.impl.lobby.hangar.playlists_states as playlists
from gui.impl.lobby.crew.states import BarracksState
from gui.impl.lobby.lootbox_system.states import LootBoxMainState
from gui.impl.lobby.hangar.random.sound_manager import ALL_VEHICLES_SOUND_SPACE
from gui.impl.lobby.hangar.states import HangarState
from gui.impl.lobby.tank_setup.tank_setup_sounds import playEnterTankSetupView
from gui.impl.lobby.vehicle_hub import OverviewState, ModulesState, VehSkillTreeState, StatsState, ArmorState
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyState, SFViewLobbyState, SubScopeSubLayerState, LobbyStateFlags, TopScopeTopLayerState, LobbyStateDescription, ViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.prb_control import prbEntityProperty
from last_stand.gui.impl.lobby.pre_battle_queue_view import PreBattleQueueView
from last_stand.gui.ls_gui_constants import VIEW_ALIAS
from last_stand.gui.scaleform.genConsts.LAST_STAND_HANGAR_ALIASES import LAST_STAND_HANGAR_ALIASES
from last_stand.gui.shared.event_dispatcher import showMetaIntroView, showIntroVideo, showNarrationWindowView
from last_stand.skeletons.ls_controller import ILSController
from skeletons.gui.app_loader import IAppLoader
from helpers import dependency
from sound_gui_manager import ViewSoundExtension
from last_stand.gui.ls_account_settings import AccountSettingsKeys, getSettings, setSettings
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.shared.events import NavigationEvent

def registerStates(machine):
    machine.addState(LastStandModeState())
    machine.addState(LastStandBattleResultsState())


def registerTransitions(machine):
    lsMode = machine.getStateByCls(LastStandModeState)
    machine.addNavigationTransitionFromParent(lsMode)


@SubScopeSubLayerState.parentOf
class LastStandModeState(LobbyState):
    STATE_ID = 'lastStand'
    lsCtrl = dependency.descriptor(ILSController)

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(LastStandHangarState(StateFlags.INITIAL))
        machine.addState(LastStandRewardPathState())
        machine.addState(LastStandVehiclePreviewState())
        machine.addState(LastStandHeroTankPreviewState())
        machine.addState(LastStandPreBattleQueueState())
        machine.addState(LastStandLoadoutState())
        machine.addState(LastStandAllVehiclesState())
        machine.addState(LastStandEditPlaylistsState())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.battle_queue.states import CommonBattleQueueState
        machine = self.getMachine()
        parent = self.getParent()
        hangar = machine.getStateByCls(LastStandHangarState)
        hangarRoot = machine.getStateByCls(LastStandRootHangarState)
        parent.addNavigationTransition(hangar, record=True)
        hangar.addNavigationTransition(hangarRoot)
        parent.addTransition(HijackTransition(HangarState, WeakMethodProxy(self._isEventPrb)), hangar)
        rewardPath = machine.getStateByCls(LastStandRewardPathState)
        hangar.addNavigationTransition(rewardPath, record=True)
        allVehicle = machine.getStateByCls(LastStandAllVehiclesState)
        hangarRoot.addNavigationTransition(allVehicle)
        editPlaylistsLS = machine.getStateByCls(LastStandEditPlaylistsState)
        allVehicle.addTransition(HijackTransition(playlists.EditVehiclePlaylistsState, WeakMethodProxy(self._isEventPrb), record=True), editPlaylistsLS)
        preBattleQueue = machine.getStateByCls(LastStandPreBattleQueueState)
        hangar.addNavigationTransition(preBattleQueue, record=True)
        parent.addTransition(HijackTransition(CommonBattleQueueState, WeakMethodProxy(self._isEventPrb)), preBattleQueue)
        parent.addTransition(HijackTransition(playlists.EditVehiclePlaylistsState, WeakMethodProxy(self._isEventPrb)), editPlaylistsLS)
        states = (machine.getStateByCls(OverviewState),
         machine.getStateByCls(ModulesState),
         machine.getStateByCls(VehSkillTreeState),
         machine.getStateByCls(StatsState),
         machine.getStateByCls(ArmorState),
         machine.getStateByCls(VehiclePostProgressionState),
         machine.getStateByCls(BarracksState),
         machine.getStateByCls(LastStandVehiclePreviewState),
         machine.getStateByCls(LootBoxMainState))
        self._registrationTransition(hangar, rewardPath, states)

    def _registrationTransition(self, hangar, rewardPath, states):
        for state in states:
            hangar.addNavigationTransition(state, record=True)
            rewardPath.addNavigationTransition(state, record=True)

    @classmethod
    def _isEventPrb(cls, event):
        return cls.lsCtrl.isEnabled() and cls.lsCtrl.isEventPrb()


@LastStandModeState.parentOf
class LastStandHangarState(SFViewLobbyState):
    STATE_ID = 'hangar'
    VIEW_KEY = ViewKey(LAST_STAND_HANGAR_ALIASES.LS_HANGAR)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)
        self.__cachedParams = {}

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(LastStandRootHangarState(flags=StateFlags.INITIAL))

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.headerButtons.battle.types.last_stand()))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        super(LastStandHangarState, self)._onEntered(event)
        self.__cachedParams = event.params
        if getSettings(AccountSettingsKeys.IS_EVENT_NEW):
            showIntroVideo()
            showNarrationWindowView()
            setSettings(AccountSettingsKeys.IS_EVENT_NEW, False)

    def _onExited(self):
        self.__cachedParams = {}
        super(LastStandHangarState, self)._onExited()


@LastStandHangarState.parentOf
class LastStandRootHangarState(LobbyState):
    STATE_ID = '{root}'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandRootHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)


@LastStandHangarState.parentOf
class LastStandAllVehiclesState(LobbyState):
    STATE_ID = 'allVehicles'
    __soundExtension = ViewSoundExtension(ALL_VEHICLES_SOUND_SPACE)

    def _onEntered(self, event):
        super(LastStandAllVehiclesState, self)._onEntered(event)
        self.__soundExtension.initSoundManager()
        self.__soundExtension.startSoundSpace()

    def _onExited(self):
        self.__soundExtension.destroySoundManager()
        super(LastStandAllVehiclesState, self)._onExited()

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.allVehicles()))


LastStandEditPlaylistsState = playlists.generateVehiclePlayListClasses(parentStateCls=LastStandHangarState, parentAllVehicleStateCls=LastStandAllVehiclesState)

@LastStandModeState.parentOf
class LastStandRewardPathState(SFViewLobbyState):
    STATE_ID = LAST_STAND_HANGAR_ALIASES.LS_REWARD_PATH
    VIEW_KEY = ViewKey(LAST_STAND_HANGAR_ALIASES.LS_REWARD_PATH)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandRewardPathState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def getNavigationDescription(self):
        lsCtrl = dependency.instance(ILSController)
        infos = []
        if lsCtrl.isMetaInfoEnabled():
            infos.append(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showMetaIntroView, tooltipBody=backport.text(R.strings.last_stand_lobby.rewardPath.aboutTooltip())))
        if lsCtrl.isIntroVideoEnabled():
            infos.append(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.VIDEO, onMoreInfoRequested=showIntroVideo, tooltipBody=backport.text(R.strings.last_stand_lobby.rewardPath.introTooltip())))
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.rewardPath.title()), infos=tuple(infos))

    def getBackNavigationDescription(self, params):
        return backport.text(R.strings.last_stand_lobby.common.toRewardPath())

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        super(LastStandRewardPathState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self.__cachedParams = {}
        super(LastStandRewardPathState, self)._onExited()

    def _getViewLoadCtx(self, event):
        if 'ctx' in event.params:
            return super(LastStandRewardPathState, self)._getViewLoadCtx(event)
        ctx = {}
        for key, value in event.params.items():
            ctx[key] = value

        return {'ctx': ctx}


@BattleQueueContainerState.parentOf
class LastStandPreBattleQueueState(GuiImplViewLobbyState):
    STATE_ID = 'lastStandPreBattleQueue'
    VIEW_KEY = ViewKey(R.views.last_stand.mono.lobby.prebattle_queue_view())

    def __init__(self):
        super(LastStandPreBattleQueueState, self).__init__(PreBattleQueueView, ScopeTemplates.LOBBY_SUB_SCOPE)
        self.__startTime = None
        return

    @prbEntityProperty
    def prbEntity(self):
        return None

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.preBattle.searching()))

    def serializeParams(self):
        return {'startTime': self.__startTime}

    def _getViewLoadCtx(self, event):
        return {'startTime': self.__startTime}

    def _onEntered(self, event):
        self.__startTime = event.params.get('startTime', time.time() * 1000)
        super(LastStandPreBattleQueueState, self)._onEntered(event)

    def _onExited(self):
        self.__startTime = None
        super(LastStandPreBattleQueueState, self)._onExited()
        return


@LastStandModeState.parentOf
class LastStandVehiclePreviewState(SFViewLobbyState):
    STATE_ID = LAST_STAND_HANGAR_ALIASES.LS_VEHICLE_PREVIEW
    VIEW_KEY = ViewKey(LAST_STAND_HANGAR_ALIASES.LS_VEHICLE_PREVIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandVehiclePreviewState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def registerTransitions(self):
        machine = self.getMachine()
        vehiclePostProgression = machine.getStateByCls(VehiclePostProgressionState)
        self.addNavigationTransition(vehiclePostProgression, record=True)
        heroTankPreview = machine.getStateByCls(LastStandHeroTankPreviewState)
        self.addNavigationTransition(heroTankPreview, record=True)

    def serializeParams(self):
        return self.__cachedParams

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.vehicle_preview.header.title()))

    def _onEntered(self, event):
        from ClientSelectableCameraObject import ClientSelectableCameraObject
        ClientSelectableCameraObject.switchCamera()
        super(LastStandVehiclePreviewState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self.__cachedParams = {}
        super(LastStandVehiclePreviewState, self)._onExited()

    def _getViewLoadCtx(self, event):
        if 'ctx' in event.params:
            return super(LastStandVehiclePreviewState, self)._getViewLoadCtx(event)
        ctx = {}
        for key, value in event.params.items():
            ctx[key] = value

        return {'ctx': ctx}


@LastStandModeState.parentOf
class LastStandHeroTankPreviewState(SFViewLobbyState):
    STATE_ID = LAST_STAND_HANGAR_ALIASES.LS_HERO_PREVIEW
    VIEW_KEY = ViewKey(LAST_STAND_HANGAR_ALIASES.LS_HERO_PREVIEW)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandHeroTankPreviewState, self).__init__(flags=flags)
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
        super(LastStandHeroTankPreviewState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self._prepareExited()
        self.__cachedParams = {}
        super(LastStandHeroTankPreviewState, self)._onExited()

    def _getViewLoadCtx(self, event):
        if 'ctx' in event.params:
            return super(LastStandHeroTankPreviewState, self)._getViewLoadCtx(event)
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


@TopScopeTopLayerState.parentOf
class LastStandBattleResultsState(ViewLobbyState, PostBattleResultsStateMixin):
    STATE_ID = VIEW_ALIAS.LS_BATTLE_RESULTS
    VIEW_KEY = ViewKey(VIEW_ALIAS.LS_BATTLE_RESULTS)

    def registerTransitions(self):
        machine = self.getMachine()
        machine.addNavigationTransitionFromParent(self)


class _LastStandLoadoutConfirmStateProto(_LoadoutConfirmStatePrototype):
    STATE_ID = 'lastStandLoadoutConfirmLeave'


class _LastStandLoadoutStateCls(_LoadoutStatePrototype):
    STATE_ID = 'loadout'
    lsCtrl = dependency.descriptor(ILSController)

    def _onEntered(self, event):
        playEnterTankSetupView()

    def _onExited(self):
        if not self.lsCtrl.isAvailable():
            LobbyState._onExited(self)
        else:
            super(_LastStandLoadoutStateCls, self)._onExited()


class _LastStandConsumableLoadoutState(_ConsumablesLoadoutStatePrototype):
    STATE_ID = 'ls_consumables'

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.hangarAmmunitionSetup.header()))


LastStandLoadoutState, _, _, _, _, _, LastStandConsumableLoadoutState = generateBasicLoadoutStateClasses(LastStandHangarState, R.invalid, consumablesStatePrototypeCls=_LastStandConsumableLoadoutState, loadoutStatePrototypeCls=_LastStandLoadoutStateCls, confirmStatePrototypeCls=_LastStandLoadoutConfirmStateProto)
