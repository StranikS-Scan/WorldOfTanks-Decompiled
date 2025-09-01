# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/states.py
import typing
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.lobby_state_machine.states import SubScopeSubLayerState, SFViewLobbyState, LobbyStateDescription

def registerStates(machine):
    machine.addState(TrainingListState())
    machine.addState(TrainingRoomState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(TrainingListState))
    machine.addNavigationTransitionFromParent(machine.getStateByCls(TrainingRoomState))


@SubScopeSubLayerState.parentOf
class TrainingListState(SFViewLobbyState):
    STATE_ID = PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY
    VIEW_KEY = ViewKey(PREBATTLE_ALIASES.TRAINING_LIST_VIEW_PY)

    def getNavigationDescription(self):
        return LobbyStateDescription(backport.text(R.strings.menu.training.listTitle()))


@SubScopeSubLayerState.parentOf
class TrainingRoomState(SFViewLobbyState):
    STATE_ID = PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY
    VIEW_KEY = ViewKey(PREBATTLE_ALIASES.TRAINING_ROOM_VIEW_PY)

    def getNavigationDescription(self):
        return LobbyStateDescription(backport.text(R.strings.pages.titles.trainingRoom()))
