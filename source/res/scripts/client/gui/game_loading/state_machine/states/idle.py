# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/idle.py
from frameworks.state_machine import StateFlags
import game_loading_bindings
from gui.game_loading import loggers
from gui.game_loading.state_machine.states.base import BaseState
from gui.game_loading.state_machine.const import GameLoadingStates, LOADING_VIEW_FADE_OUT_DURATION
_logger = loggers.getStatesLogger()

class IdleState(BaseState):
    __slots__ = ()

    def __init__(self, flags=StateFlags.UNDEFINED):
        super(IdleState, self).__init__(stateID=GameLoadingStates.IDLE.value, flags=flags)

    def _onEntered(self, event):
        super(IdleState, self)._onEntered(event)
        if game_loading_bindings.isViewOpened():
            _logger.debug('[%s] closing GF view.', self)
            game_loading_bindings.destroyLoadingView(LOADING_VIEW_FADE_OUT_DURATION)
        _logger.debug('[%s] entered.', self)
