# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/lobby/epicBattleTraining/states.py
import typing
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.lobby_state_machine.states import SubScopeSubLayerState, SFViewLobbyState, LobbyStateDescription

def registerStates(machine):
    machine.addState(EpicTrainingListState())
    machine.addState(EpicTrainingRoomState())


def registerTransitions(machine):
    machine.addNavigationTransitionFromParent(machine.getStateByCls(EpicTrainingListState))
    machine.addNavigationTransitionFromParent(machine.getStateByCls(EpicTrainingRoomState))


@SubScopeSubLayerState.parentOf
class EpicTrainingListState(SFViewLobbyState):
    STATE_ID = PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY
    VIEW_KEY = ViewKey(PREBATTLE_ALIASES.EPICBATTLE_LIST_VIEW_PY)

    def getNavigationDescription(self):
        return LobbyStateDescription(backport.text(R.strings.menu.headerButtons.battle.types.epicTraining()))


@SubScopeSubLayerState.parentOf
class EpicTrainingRoomState(SFViewLobbyState):
    STATE_ID = PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY
    VIEW_KEY = ViewKey(PREBATTLE_ALIASES.EPIC_TRAINING_ROOM_VIEW_PY)

    def getNavigationDescription(self):
        return LobbyStateDescription(backport.text(R.strings.menu.headerButtons.battle.types.epicTraining()))
