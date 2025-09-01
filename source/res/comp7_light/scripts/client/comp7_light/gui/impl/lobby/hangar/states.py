# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: comp7_light/scripts/client/comp7_light/gui/impl/lobby/hangar/states.py
import logging
import typing
from WeakMethod import WeakMethodProxy
from comp7_light.gui.Scaleform.genConsts.COMP7_LIGHT_HANGAR_ALIASES import COMP7_LIGHT_HANGAR_ALIASES
from comp7_light.gui.impl.lobby.comp7_light_intro_screen import Comp7LightIntroScreen
from comp7_light.gui.impl.lobby.comp7_light_no_vehicles_screen import Comp7LightNoVehiclesScreen
from comp7_light.gui.impl.lobby.progression_main_view import ProgressionMainView
from comp7_light.gui.shared.event_dispatcher import showComp7LightInfoPage
from frameworks.state_machine import StateFlags
from gui.Scaleform.framework import ScopeTemplates
from gui.Scaleform.framework.entities.View import ViewKey
from gui.impl import backport
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import generateBasicLoadoutStateClasses, _LoadoutConfirmStatePrototype
from gui.impl.lobby.hangar.states import HangarState
from gui.lobby_state_machine.states import LobbyState, LobbyStateFlags, SubScopeSubLayerState, SFViewLobbyState, GuiImplViewLobbyState, LobbyStateDescription
from gui.lobby_state_machine.transitions import HijackTransition
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IComp7LightController
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from comp7_light.gui.impl.lobby.hangar.comp7_light_hangar import Comp7LightHangar
_logger = logging.getLogger(__name__)

def registerStates(machine):
    machine.addState(Comp7LightModeState())


def registerTransitions(machine):
    comp7LightMode = machine.getStateByCls(Comp7LightModeState)
    machine.addNavigationTransitionFromParent(comp7LightMode)


@SubScopeSubLayerState.parentOf
class Comp7LightModeState(LobbyState):
    STATE_ID = 'comp7Light'
    __comp7LightController = dependency.descriptor(IComp7LightController)

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(Comp7LightHangarState(StateFlags.INITIAL))
        machine.addState(Comp7LightProgressionState())
        machine.addState(Comp7LightAllVehiclesState())
        machine.addState(Comp7LightLoadoutState())
        machine.addState(Comp7LightNoVehiclesState())
        machine.addState(Comp7LightIntroState())
        machine.addState(Comp7LightPrimeTimeState())

    def registerTransitions(self):
        lsm = self.getMachine()
        parent = self.getParent()
        comp7LightHangar = lsm.getStateByCls(Comp7LightRootHangarState)
        parent.addNavigationTransition(comp7LightHangar)
        parent.addTransition(HijackTransition(HangarState, WeakMethodProxy(self._hijackTransitionCondition)), comp7LightHangar)
        for cls in (Comp7LightProgressionState,
         Comp7LightAllVehiclesState,
         Comp7LightNoVehiclesState,
         Comp7LightIntroState,
         Comp7LightPrimeTimeState):
            state = lsm.getStateByCls(cls)
            comp7LightHangar.addNavigationTransition(state)

    def _hijackTransitionCondition(self, _):
        return self.__comp7LightController.isEnabled() and self.__comp7LightController.isModePrbActive()


@Comp7LightModeState.parentOf
class Comp7LightHangarState(SFViewLobbyState):
    STATE_ID = 'hangar'
    VIEW_KEY = ViewKey(COMP7_LIGHT_HANGAR_ALIASES.COMP7_LIGHT_LOBBY_HANGAR)
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(Comp7LightHangarState, self).__init__(flags | LobbyStateFlags.HANGAR)

    def registerStates(self):
        machine = self.getMachine()
        machine.addState(Comp7LightRootHangarState(flags=StateFlags.INITIAL))

    def __getView(self):
        app = self.__appLoader.getApp()
        view = app.containerManager.getViewByKey(self.getViewKey())
        return view.getParentWindow().content


@Comp7LightHangarState.parentOf
class Comp7LightRootHangarState(LobbyState):
    STATE_ID = '{root}'

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(Comp7LightRootHangarState, self).__init__(flags=flags | LobbyStateFlags.HANGAR)


@Comp7LightHangarState.parentOf
class Comp7LightAllVehiclesState(LobbyState):
    STATE_ID = 'allVehicles'

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.allVehicles()))


@Comp7LightModeState.parentOf
class Comp7LightNoVehiclesState(GuiImplViewLobbyState):
    STATE_ID = 'noVehicles'
    VIEW_KEY = ViewKey(R.views.comp7_light.mono.lobby.no_vehicles_screen())

    def __init__(self):
        super(Comp7LightNoVehiclesState, self).__init__(Comp7LightNoVehiclesScreen, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7_light.noVehicles()))


@Comp7LightModeState.parentOf
class Comp7LightIntroState(GuiImplViewLobbyState):
    STATE_ID = 'intro'
    VIEW_KEY = ViewKey(R.views.comp7_light.mono.lobby.intro_screen())

    def __init__(self):
        super(Comp7LightIntroState, self).__init__(Comp7LightIntroScreen, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7_light.intro()))


@Comp7LightModeState.parentOf
class Comp7LightProgressionState(GuiImplViewLobbyState):
    STATE_ID = 'progression'
    VIEW_KEY = ViewKey(R.views.comp7_light.mono.lobby.progression_main_view())

    def __init__(self):
        super(Comp7LightProgressionState, self).__init__(ProgressionMainView, ScopeTemplates.LOBBY_SUB_SCOPE)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7_light.progression()), infos=(LobbyStateDescription.Info(type=LobbyStateDescription.Info.Type.INFO, onMoreInfoRequested=showComp7LightInfoPage, tooltipHeader=backport.text(R.strings.comp7_light.tooltip.infoPageButton.header())),))


@Comp7LightModeState.parentOf
class Comp7LightPrimeTimeState(SFViewLobbyState):
    STATE_ID = 'primeTime'
    VIEW_KEY = ViewKey(COMP7_LIGHT_HANGAR_ALIASES.COMP7_LIGHT_PRIME_TIME_ALIAS)

    def getNavigationDescription(self):
        return LobbyStateDescription(title=backport.text(R.strings.pages.titles.comp7_light.primeTime()))


class _Comp7LightLoadoutConfirmStatePrototype(_LoadoutConfirmStatePrototype):
    STATE_ID = 'comp7Light/loadoutConfirmLeave'


Comp7LightLoadoutState, _, _, Comp7LightShellsLoadoutState, Comp7LightEquipmentLoadoutState, _, _ = generateBasicLoadoutStateClasses(Comp7LightHangarState, R.invalid, confirmStatePrototypeCls=_Comp7LightLoadoutConfirmStatePrototype)
