# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/trainings/states.py
import typing
from gui.Scaleform.framework.entities.View import ViewKey
from gui.Scaleform.genConsts.PREBATTLE_ALIASES import PREBATTLE_ALIASES
from gui.impl import backport
from gui.impl.gen.resources import R
from gui.lobby_state_machine.states import SubScopeSubLayerState, SFViewLobbyState, LobbyStateDescription
from gui.prb_control import prbEntityProperty
from gui.prb_control.entities.base.legacy.ctx import SetPlayerStateCtx
from gui.prb_control.entities.training.legacy.entity import TrainingEntity

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

    @prbEntityProperty
    def prbEntity(self):
        return None

    def _onEntered(self, event):
        super(TrainingRoomState, self)._onEntered(event)
        if isinstance(self.prbEntity, TrainingEntity):
            self.prbEntity.setPlayerState(SetPlayerStateCtx(True, waitingID='prebattle/player_ready'))

    def _onExited(self):
        super(TrainingRoomState, self)._onExited()
        if isinstance(self.prbEntity, TrainingEntity):
            self.prbEntity.setPlayerState(SetPlayerStateCtx(False, waitingID='prebattle/player_not_ready'))

    def getNavigationDescription(self):
        return LobbyStateDescription(backport.text(R.strings.pages.titles.trainingRoom()))
