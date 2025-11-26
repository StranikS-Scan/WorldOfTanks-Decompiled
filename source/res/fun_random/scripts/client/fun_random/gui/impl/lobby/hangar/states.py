# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/impl/lobby/hangar/states.py
from __future__ import absolute_import
import typing
from frameworks.state_machine.transitions import TransitionType
from gui.impl.gen import R
from gui.impl.lobby.hangar.base.proto_states import generateBasicHangarStateClasses, generateBasicLoadoutStateClasses, _LoadoutConfirmStatePrototype
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


class _LoadoutConfirmStateProto(_LoadoutConfirmStatePrototype):
    STATE_ID = 'funRandomLoadoutConfirmLeave'


FunRandomHangarState, _, _ = generateBasicHangarStateClasses(SubScopeSubLayerState, R.invalid, hangarPrototypeCls=_HangarStateProto)
FunRandomLoadoutState, _, _, FunRandomShellsLoadoutState, _, _, _ = generateBasicLoadoutStateClasses(FunRandomHangarState, R.invalid, confirmStatePrototypeCls=_LoadoutConfirmStateProto)
