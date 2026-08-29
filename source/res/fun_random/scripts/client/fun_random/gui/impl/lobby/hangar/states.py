# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/states.py
from __future__ import absolute_import
import typing
from frameworks_common.state_machine.transitions import TransitionType
from fun_random.gui.feature.util.fun_mixins import FunSubModesWatcher
from fun_random.gui.feature.util.fun_wrappers import hasDesiredSubMode
from fun_random_common.fun_constants import FunSubModeImpl
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import generateBasicHangarStateClasses, generateBasicLoadoutStateClasses, _LoadoutStatePrototype, _LoadoutConfirmStatePrototype, _ShellsLoadoutStatePrototype, _EquipmentLoadoutStatePrototype, _InstructionsLoadoutStatePrototype, _ConsumablesLoadoutStatePrototype
from gui.impl.lobby.hangar.states import HangarState
from gui.lobby_state_machine.states import SubScopeSubLayerState, SFViewLobbyState
from gui.lobby_state_machine.transitions import HijackTransition
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES
from helpers import dependency
from skeletons.gui.game_control import IFunRandomController
from WeakMethod import WeakMethodProxy
if typing.TYPE_CHECKING:
    from gui.lobby_state_machine.lobby_state_machine import LobbyStateMachine
    from gui.shared.events import NavigationEvent

def registerStates(machine):
    machine.addState(FunRandomHangarState())
    machine.addState(FunRandomLoadoutState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(FunRandomHangarState), transitionType=TransitionType.EXTERNAL)


class _HangarStateProto(SFViewLobbyState):
    STATE_ID = 'funRandomHangar'
    VIEW_KEY = ViewKey(FUNRANDOM_ALIASES.FUN_RANDOM_HANGAR)
    __funRandomController = dependency.descriptor(IFunRandomController)

    def registerTransitions(self):
        hijackCondition = WeakMethodProxy(self.__hijackTransitionCondition)
        hijackTransition = HijackTransition(HangarState, hijackCondition, transitionType=TransitionType.EXTERNAL)
        self.getParent().addTransition(hijackTransition, self)

    def __hijackTransitionCondition(self, _):
        return self.__funRandomController.isFunRandomPrbActive()


class _FunRandomLoadoutStateProto(_LoadoutStatePrototype, FunSubModesWatcher):

    def __init__(self):
        super(_FunRandomLoadoutStateProto, self).__init__()
        self.__desiredSubImpl = FunSubModeImpl.UNDEFINED

    def _onEntered(self, event):
        super(_FunRandomLoadoutStateProto, self)._onEntered(event)
        self.startSubSettingsListening(self.__invalidateSubMode, desiredOnly=True)
        self.startSubSelectionListening(self.__invalidateSubMode)
        self.__invalidateSubMode()

    def _onExited(self):
        self.stopSubSelectionListening(self.__invalidateSubMode)
        self.stopSubSettingsListening(self.__invalidateSubMode, desiredOnly=True)
        super(_FunRandomLoadoutStateProto, self)._onExited()
        self.__desiredSubImpl = FunSubModeImpl.UNDEFINED

    @hasDesiredSubMode()
    def __invalidateSubMode(self, *_):
        self.__desiredSubImpl, previousSubImpl = self.getDesiredSubMode().getSubModeImpl(), self.__desiredSubImpl
        if previousSubImpl not in (FunSubModeImpl.UNDEFINED, self.__desiredSubImpl):
            SubScopeSubLayerState.goTo(forcedRollback=True)


class _FunRandomLoadoutConfirmStateProto(_LoadoutConfirmStatePrototype):
    STATE_ID = 'funRandomLoadoutConfirmLeave'


class _FunRandomShellsLoadoutStatePrototype(_ShellsLoadoutStatePrototype, FunSubModesWatcher):

    @hasDesiredSubMode(defReturn=False)
    def isStateReachable(self, event):
        return self.getDesiredSubMode().getConfigurationModel().common.regularShells


class _FunRandomEquipmentLoadoutStatePrototype(_EquipmentLoadoutStatePrototype, FunSubModesWatcher):

    @hasDesiredSubMode(defReturn=False)
    def isStateReachable(self, event):
        return self.getDesiredSubMode().getConfigurationModel().common.regularDevices


class _FunRandomInstructionsLoadoutStatePrototype(_InstructionsLoadoutStatePrototype, FunSubModesWatcher):

    @hasDesiredSubMode(defReturn=False)
    def isStateReachable(self, event):
        return self.getDesiredSubMode().getConfigurationModel().common.regularBoosters


class _FunRandomConsumablesLoadoutStatePrototype(_ConsumablesLoadoutStatePrototype, FunSubModesWatcher):

    @hasDesiredSubMode(defReturn=False)
    def isStateReachable(self, event):
        return self.getDesiredSubMode().getConfigurationModel().common.regularConsumables


FunRandomHangarState, DefaultFunRandomHangarState, _, _ = generateBasicHangarStateClasses(SubScopeSubLayerState, R.invalid, hangarPrototypeCls=_HangarStateProto)
FunRandomLoadoutState, _, _, FunRandomShellsLoadoutState, _, _, _ = generateBasicLoadoutStateClasses(FunRandomHangarState, R.invalid, loadoutStatePrototypeCls=_FunRandomLoadoutStateProto, confirmStatePrototypeCls=_FunRandomLoadoutConfirmStateProto, shellsStatePrototypeCls=_FunRandomShellsLoadoutStatePrototype, equipmentStatePrototypeCls=_FunRandomEquipmentLoadoutStatePrototype, instructionsStatePrototypeCls=_FunRandomInstructionsLoadoutStatePrototype, consumablesStatePrototypeCls=_FunRandomConsumablesLoadoutStatePrototype)
