# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gameplay/machine.py
import logging
import BattleReplay
from constants import IS_DEVELOPMENT
from frameworks.state_machine import StateMachine
from gameplay import states
_logger = logging.getLogger(__name__)
_logger.addHandler(logging.NullHandler())

class GameplayStateMachine(StateMachine):
    __slots__ = ()

    def __init__(self):
        super(GameplayStateMachine, self).__init__(start=states.StartState())

    @property
    def offline(self):
        return self.getChildByIndex(0)

    @property
    def online(self):
        return self.getChildByIndex(1)

    def configure(self):
        offline = states.OfflineState()
        offline.configure()
        online = states.OnlineState()
        online.configure(offline)
        self.addState(offline)
        self.addState(online)


class BattleReplayMachine(StateMachine):
    __slots__ = ()

    def __init__(self):
        super(BattleReplayMachine, self).__init__(start=states.StartState())

    def configure(self):
        initialization = states.BattleReplayInitState()
        initialization.configure()
        playing = states.BattleReplayPlayingState()
        playing.configure(initialization)
        self.addState(initialization)
        self.addState(playing)

    def start(self, doValidate=True):
        super(BattleReplayMachine, self).start(doValidate)
        BattleReplay.g_replayCtrl.autoStartBattleReplay()


def create():
    if BattleReplay.g_replayCtrl.getAutoStartFileName():
        return BattleReplayMachine()
    if IS_DEVELOPMENT:
        try:
            from gui.development.dev_gameplay import DevGameplayStateMachine
        except ImportError:
            _logger.exception('Development state machine is not found')
            return GameplayStateMachine()

        return DevGameplayStateMachine()
    return GameplayStateMachine()
