# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_loading/state_machine/states/init_client/transitions.py
import typing
from frameworks.state_machine.transitions import StringEventTransition
from gui.game_loading.state_machine.const import GameLoadingStatesEvents
from gui.game_loading.state_machine.states.transitions import SourceToSingleTargetTransition
if typing.TYPE_CHECKING:
    from frameworks.state_machine.events import StringEvent
    from gui.game_loading.state_machine.machine import GameLoadingStateMachine
    from gui.game_loading.state_machine.states.init_client.logos_loading import LogosLoadingState
    from gui.game_loading.state_machine.states.init_client.client_loading_stub import ClientLoadingStubState

class LogosShownToClientLoadingStubTransition(SourceToSingleTargetTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(LogosShownToClientLoadingStubTransition, self).__init__(token=GameLoadingStatesEvents.LOGOS_SHOWN.value, priority=priority)

    def _apply(self, event, source, target):
        machine = target.getMachine()
        return False if machine is None else self._condition(machine)

    def _condition(self, machine):
        return machine.isGameLoadingComplete


class LogosShownToClientLoadingTransition(LogosShownToClientLoadingStubTransition):
    __slots__ = ()

    def _condition(self, machine):
        return not super(LogosShownToClientLoadingTransition, self)._condition(machine)


class ClientLoadingTransition(StringEventTransition):
    __slots__ = ()

    def __init__(self, priority=0):
        super(ClientLoadingTransition, self).__init__(token=GameLoadingStatesEvents.CLIENT_LOADING.value, priority=priority)
