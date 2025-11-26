# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/impl/lobby/states.py
import typing
from WeakMethod import WeakMethodProxy
from frameworks.state_machine import StateFlags
from frameworks.state_machine.transitions import TransitionType
from frontline.constants.aliases import FrontlineHangarAliases
from frontline.gui.impl.gen.view_models.views.lobby.views.frontline_const import FrontlineConst
from frontline.gui.impl.gen.view_models.views.lobby.views.info_page_scroll_to_section import InfoPageScrollToSection
from frontline.gui.impl.lobby.progression_screen_view import ProgressionScreenView
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import _LoadoutConfirmStatePrototype, generateBasicLoadoutStateClasses
from gui.impl.lobby.hangar.states import HangarState
from gui.lobby_state_machine.states import GuiImplViewLobbyState, LobbyState, LobbyStateDescription, LobbyStateFlags, SFViewLobbyState, SubScopeSubLayerState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.shared.event_dispatcher import showFrontlineInfoWindow
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IEpicBattleMetaGameController
from skeletons.gui.game_control import ILoadoutController
from frontline.gui.frontline_helpers import becomeNonPlayerState
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from frontline.gui.impl.lobby.hangar_view import FrontlineHangar

def registerStates(machine):
    machine.addState(FrontlineModeState())


def registerTransitions(machine):
    frontlineMode = machine.getStateByCls(FrontlineModeState)
    machine.addNavigationTransitionFromParent(frontlineMode)


class FrontlineStateIDs(object):
    FRONTLINE = 'frontline'
    HANGAR = 'hangar'
    ROOT = '{root}'
    LOADOUT_CONFIRM_LEAVE = 'frontline/loadoutConfirmLeave'
    ALL_VEHICLES = 'allVehicles'
    PROGRESSION_SCREEN = 'frontlineProgressionScreen'
    BATTLE_ABILITIES = FrontlineConst.BATTLE_ABILITIES


@SubScopeSubLayerState.parentOf
class FrontlineModeState(LobbyState):
    STATE_ID = FrontlineStateIDs.FRONTLINE
    __epicController = dependency.descriptor(IEpicBattleMetaGameController)

    def registerStates(self):
        lsm = self.getMachine()
        lsm.addState(FrontlineHangarState(StateFlags.INITIAL))
        lsm.addState(FrontlineLoadoutState())
        lsm.addState(FrontlineAllVehiclesState())
        lsm.addState(ProgressionScreenState())

    def registerTransitions(self):
        lsm = self.getMachine()
        parent = self.getParent()
        frontlineHangar = lsm.getStateByCls(FrontlineRootHangarState)
        parent.addNavigationTransition(frontlineHangar)
        parent.addTransition(HijackTransition(HangarState, WeakMethodProxy(self._hijackTransitionCondition)), frontlineHangar)
        for cls in (FrontlineAllVehiclesState, ProgressionScreenState):
            state = lsm.getStateByCls(cls)
            frontlineHangar.addNavigationTransition(state)

        parent.addNavigationTransition(lsm.getStateByCls(ProgressionScreenState))

    def _hijackTransitionCondition(self, _):
        return self.__epicController.isEnabled() and self.__epicController.isEpicPrbActive()


@FrontlineModeState.parentOf
class FrontlineHangarState(SFViewLobbyState):
    STATE_ID = FrontlineStateIDs.HANGAR
    VIEW_KEY = ViewKey(FrontlineHangarAliases.FRONTLINE_LOBBY_HANGAR)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FrontlineHangarState, self).__init__(flags | LobbyStateFlags.HANGAR)
        self.__hangarObserver = None
        return

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(FrontlineRootHangarState(flags=StateFlags.INITIAL))

    def __getView(self):
        app = self.__appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        return view.getParentWindow().content


@FrontlineHangarState.parentOf
class FrontlineRootHangarState(LobbyState):
    STATE_ID = FrontlineStateIDs.ROOT

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(FrontlineRootHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)

    def _onEntered(self, event):
        super(FrontlineRootHangarState, self)._onEntered(event)
        lsm = self.getMachine()
        lsm.getRelatedView(self).blur.disable()


class _FlLoadoutConfirmStatePrototype(_LoadoutConfirmStatePrototype):
    STATE_ID = FrontlineStateIDs.LOADOUT_CONFIRM_LEAVE


@FrontlineHangarState.parentOf
class FrontlineAllVehiclesState(LobbyState):
    STATE_ID = FrontlineStateIDs.ALL_VEHICLES

    def _onEntered(self, event):
        super(FrontlineAllVehiclesState, self)._onEntered(event)
        lsm = self.getMachine()
        lsm.getRelatedView(self).blur.enable()

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.allVehicles()))


@FrontlineModeState.parentOf
class ProgressionScreenState(GuiImplViewLobbyState):
    STATE_ID = FrontlineStateIDs.PROGRESSION_SCREEN
    VIEW_KEY = ViewKey(R.views.frontline.mono.lobby.progression_screen())

    def __init__(self):
        super(ProgressionScreenState, self).__init__(ProgressionScreenView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fl_progression_screen.title()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, tooltipHeader=backport.text(R.strings.fl_tooltips.infoButton.header()), tooltipBody=backport.text(R.strings.fl_tooltips.infoButton.body()), onMoreInfoRequested=self.__openInfoView),))

    def __openInfoView(self):
        showFrontlineInfoWindow()


FrontlineLoadoutStateBase, _, FrontlineLoadoutSectionState, FrontlineShellsLoadoutState, _, _, _ = generateBasicLoadoutStateClasses(FrontlineHangarState, R.invalid, confirmStatePrototypeCls=_FlLoadoutConfirmStatePrototype)

class _BattleAbilitiesLoadoutStatePrototype(LobbyState):

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.fl_battle_abilities_setup.header.title()), infos=(LobbyStateDescription.Info(tooltipHeader=backport.text(R.strings.fl_tooltips.infoButton.header()), tooltipBody=backport.text(R.strings.fl_tooltips.infoButton.body()), onMoreInfoRequested=self.__openInfoView),))

    @staticmethod
    def __openInfoView(*_):
        showFrontlineInfoWindow(autoscrollSection=InfoPageScrollToSection.BATTLE_SCENARIOS)


@FrontlineLoadoutStateBase.parentOf
class FrontlineBattleAbilitiesLoadoutState(FrontlineLoadoutSectionState, _BattleAbilitiesLoadoutStatePrototype):
    STATE_ID = _BattleAbilitiesLoadoutStatePrototype.STATE_ID or FrontlineStateIDs.BATTLE_ABILITIES


class FrontlineLoadoutState(FrontlineLoadoutStateBase):
    __loadoutController = dependency.descriptor(ILoadoutController)

    def registerStates(self):
        super(FrontlineLoadoutState, self).registerStates()
        lsm = self.getMachine()
        lsm.addState(FrontlineBattleAbilitiesLoadoutState())

    def _onExited(self):
        if not becomeNonPlayerState():
            super(FrontlineLoadoutState, self)._onExited()

    def registerTransitions(self):
        super(FrontlineLoadoutState, self).registerTransitions()
        lsm = self.getMachine()
        lsm.addNavigationTransitionFromParent(self)
        generatedClasses = [lsm.getStateByCls(FrontlineBattleAbilitiesLoadoutState)]
        parent = self.getParent()
        for state in generatedClasses:
            parent.addNavigationTransition(state)
            lsm.addNavigationTransitionFromParent(state, transitionType=TransitionType.EXTERNAL)
            state.addNavigationTransition(state, transitionType=TransitionType.EXTERNAL)
