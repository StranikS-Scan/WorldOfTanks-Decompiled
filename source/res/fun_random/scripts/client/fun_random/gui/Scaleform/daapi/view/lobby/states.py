# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fun_random/scripts/client/fun_random/gui/Scaleform/daapi/view/lobby/states.py
from __future__ import absolute_import
from gui.lobby_state_machine.states import SFViewLobbyState, SubScopeSubLayerState
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.FUNRANDOM_ALIASES import FUNRANDOM_ALIASES

def registerStates(machine):
    machine.addState(FunRandomPrimeTimeState())


def registerTransitions(machine):
    funRandomPrimeTime = machine.getStateByCls(FunRandomPrimeTimeState)
    machine.addNavigationTransitionFromParent(funRandomPrimeTime)


@SubScopeSubLayerState.parentOf
class FunRandomPrimeTimeState(SFViewLobbyState):
    STATE_ID = 'funRandomPrimeTime'
    VIEW_KEY = ViewKey(FUNRANDOM_ALIASES.FUN_RANDOM_PRIME_TIME)
