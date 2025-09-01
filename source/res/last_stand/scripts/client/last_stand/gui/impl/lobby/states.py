# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/impl/lobby/states.py
import time
import typing
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from gui.Scaleform.daapi.view.lobby.battle_queue.states import BattleQueueContainerState
from gui.Scaleform.daapi.view.lobby.shared.states import BrowserLobbyTopState
from gui.Scaleform.daapi.view.lobby.veh_post_progression.states import VehiclePostProgressionState
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.hangar_cameras.hangar_camera_common import CameraRelatedEvents
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.states import HangarState
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyState, SFViewLobbyState, SubScopeSubLayerState, LobbyStateFlags, SubScopeTopLayerState, TopScopeTopLayerState, LobbyStateDescription
from gui.lobby_state_machine.transitions import HijackTransition
from gui.prb_control import prbEntityProperty
from last_stand.gui.impl.lobby.hangar_ammunition_setup_view import LSHangarAmmunitionSetupView
from last_stand.gui.impl.lobby.pre_battle_queue_view import PreBattleQueueView
from last_stand.gui.scaleform.genConsts.LAST_STAND_HANGAR_ALIASES import LAST_STAND_HANGAR_ALIASES
from last_stand.gui.shared.event_dispatcher import getLoadedViewByLayoutID, showMetaIntroView, showIntroVideo
from last_stand.skeletons.ls_controller import ILSController
from skeletons.gui.app_loader import IAppLoader
from helpers import dependency
from wg_async import wg_async, wg_await, await_callback
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine

def registerStates(machine):
    machine.addState(LastStandModeState())


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
        machine.addState(LastStandAmmunitionSetupLoadout())

    def registerTransitions(self):
        from gui.Scaleform.daapi.view.lobby.battle_queue.states import CommonBattleQueueState
        machine = self.getMachine()
        parent = self.getParent()
        hangar = machine.getStateByCls(LastStandHangarState)
        parent.addNavigationTransition(hangar, record=True)
        parent.addTransition(HijackTransition(HangarState, WeakMethodProxy(self._isEventPrb)), hangar)
        ammunitionSetup = machine.getStateByCls(LastStandAmmunitionSetupLoadout)
        hangar.addNavigationTransition(ammunitionSetup)
        rewardPath = machine.getStateByCls(LastStandRewardPathState)
        hangar.addNavigationTransition(rewardPath, record=True)
        preBattleQueue = machine.getStateByCls(LastStandPreBattleQueueState)
        hangar.addNavigationTransition(preBattleQueue, record=True)
        parent.addTransition(HijackTransition(CommonBattleQueueState, WeakMethodProxy(self._isEventPrb)), preBattleQueue)
        previewVehicle = machine.getStateByCls(LastStandVehiclePreviewState)
        hangar.addNavigationTransition(previewVehicle, record=True)
        rewardPath.addNavigationTransition(previewVehicle, record=True)

    @classmethod
    def _isEventPrb(cls, event):
        return cls.lsCtrl.isEnabled() and cls.lsCtrl.isEventPrb()


@LastStandModeState.parentOf
class LastStandHangarState(SFViewLobbyState):
    STATE_ID = LAST_STAND_HANGAR_ALIASES.LS_HANGAR
    VIEW_KEY = ViewKey(LAST_STAND_HANGAR_ALIASES.LS_HANGAR)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)
        self.__cachedParams = {}

    def registerTransitions(self):
        lsm = self.getMachine()
        confirmState = lsm.getStateByCls(LastStandAmmunitionConfirmState)
        loadout = lsm.getStateByCls(LastStandAmmunitionSetupLoadout)
        self.addGuardTransition(confirmState, WeakMethodProxy(loadout.interactorConfirm))

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.headerButtons.battle.types.last_stand()))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        super(LastStandHangarState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self.__cachedParams = {}
        super(LastStandHangarState, self)._onExited()


@LastStandModeState.parentOf
class LastStandRewardPathState(SFViewLobbyState):
    STATE_ID = LAST_STAND_HANGAR_ALIASES.LS_REWARD_PATH
    VIEW_KEY = ViewKey(LAST_STAND_HANGAR_ALIASES.LS_REWARD_PATH)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandRewardPathState, self).__init__(flags=flags)
        self.__cachedParams = {}

    def getNavigationDescription(self):
        lsCtrl = dependency.instance(ILSController)
        infos = [LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showMetaIntroView, tooltipBody=backport.text(R.strings.last_stand_lobby.rewardPath.aboutTooltip()))]
        if lsCtrl.isIntroVideoEnabled():
            infos.append(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.VIDEO, onMoreInfoRequested=showIntroVideo, tooltipBody=backport.text(R.strings.last_stand_lobby.rewardPath.introTooltip())))
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.rewardPathCard.name()), infos=tuple(infos))

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


@SubScopeTopLayerState.parentOf
class LastStandAmmunitionSetupLoadout(LobbyState):
    STATE_ID = 'lastStandAmmunitionSetupLoadout'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandAmmunitionSetupLoadout, self).__init__(flags)
        self.__transitionWithoutBuying = False

    def registerStates(self):
        self.addChildState(LastStandHangarAmmunitionSetupState(flags=StateFlags.INITIAL))
        machine = self.getMachine()
        machine.addState(LastStandAmmunitionConfirmState())

    def registerTransitions(self):
        machine = self.getMachine()
        ammunitionSetup = machine.getStateByCls(LastStandHangarAmmunitionSetupState)
        confirmState = machine.getStateByCls(LastStandAmmunitionConfirmState)
        browser = machine.getStateByCls(BrowserLobbyTopState)
        ammunitionSetup.addNavigationTransition(browser, record=True)
        ammunitionSetup.addNavigationTransition(confirmState)
        self.addGuardTransition(confirmState, WeakMethodProxy(self.interactorConfirm))

    def interactorConfirm(self, event):
        browserStateID = self.getMachine().getStateByCls(BrowserLobbyTopState).getStateID()
        self.__transitionWithoutBuying = event.targetStateID == browserStateID
        if self.__transitionWithoutBuying:
            return False
        else:
            targetingSelf = event.targetStateID == self.getStateID()
            view = getLoadedViewByLayoutID(R.views.last_stand.mono.lobby.ammunition_setup())
            if not view:
                return False
            interactor = view.tankSetup.currentInteractor if view and view.tankSetup else None
            return False if not interactor else not targetingSelf and interactor and interactor.hasChanged()

    def _onEntered(self, event):
        super(LastStandAmmunitionSetupLoadout, self)._onEntered(event)
        self.__transitionWithoutBuying = False

    @wg_async
    def _onExited(self):
        if not self.__transitionWithoutBuying:
            view = getLoadedViewByLayoutID(R.views.last_stand.mono.lobby.ammunition_setup())
            interactor = view.tankSetup.currentInteractor if view and view.tankSetup else None
            if interactor:
                yield await_callback(interactor.applyQuit)(skipApplyAutoRenewal=False)
        self.__transitionWithoutBuying = False
        super(LastStandAmmunitionSetupLoadout, self)._onExited()
        return


@LastStandAmmunitionSetupLoadout.parentOf
class LastStandHangarAmmunitionSetupState(GuiImplViewLobbyState):
    STATE_ID = 'lastStandAmmunitionSetup'
    VIEW_KEY = ViewKey(R.views.last_stand.mono.lobby.ammunition_setup())

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(LastStandHangarAmmunitionSetupState, self).__init__(LSHangarAmmunitionSetupView, ScopeTemplates.LOBBY_SUB_SCOPE, flags=flags)
        self.__cachedParams = {}

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.hangarAmmunitionSetup.navigation()))

    def serializeParams(self):
        return self.__cachedParams

    def _onEntered(self, event):
        super(LastStandHangarAmmunitionSetupState, self)._onEntered(event)
        self.__cachedParams = event.params

    def _onExited(self):
        self.__cachedParams = {}
        super(LastStandHangarAmmunitionSetupState, self)._onExited()


@TopScopeTopLayerState.parentOf
class LastStandAmmunitionConfirmState(LobbyState):
    STATE_ID = 'lastStandAmmunitionConfirmState'

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.last_stand_lobby.hangarAmmunitionSetup.navigation()))

    @wg_async
    def _onEntered(self, event):
        redirected = event.targetStateID != self.getStateID()
        if not redirected:
            TopScopeTopLayerState.goTo()
            return
        view = getLoadedViewByLayoutID(R.views.last_stand.mono.lobby.ammunition_setup())
        if not view:
            TopScopeTopLayerState.goTo()
            return
        result = yield wg_await(view.tankSetup.canQuit())
        if result:
            view._closeWindow()
            self.getMachine().post(event)
        else:
            TopScopeTopLayerState.goTo()


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
