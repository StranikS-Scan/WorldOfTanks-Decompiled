# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/ReplayAccount.py
import logging
import enum
import BigWorld
import BattleReplay
from PlayerEvents import g_playerEvents
from ReplayEvents import g_replayEvents
from helpers import dependency
from skeletons.connection_mgr import IConnectionManager
_logger = logging.getLogger(__name__)

class State(enum.IntEnum):
    PRE_START_REPLAY = 0
    STARTED_PLAYBACK = 1
    FINISHED_PLAYBACK = 2


class ReplayAccount(BigWorld.Entity):
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        self.state = State.PRE_START_REPLAY

    def onBecomePlayer(self):
        _logger.info('ReplayAccount.onBecomePlayer: state=%s', self.state)
        g_replayEvents.onReplayTerminated += self.__onReplayTerminated
        if self.state == State.PRE_START_REPLAY:
            self.__start()
        elif self.state == State.STARTED_PLAYBACK:
            self.__stop()

    def onBecomeNonPlayer(self):
        _logger.info('ReplayAccount.onBecomeNonPlayer')
        g_replayEvents.onReplayTerminated -= self.__onReplayTerminated

    def onKickedFromServer(self, reason, kickReasonType, expiryTime):
        _logger.info('ReplayAccount: onKickedFromServer: %s %d %d', reason, kickReasonType, expiryTime)
        self.connectionMgr.setKickedFromServer(reason, kickReasonType, expiryTime)

    def handleKeyEvent(self, *args, **kwargs):
        return False

    def __onReplayTerminated(self, reason):
        if reason != BigWorld.ReplayTerminatedReason.REPLAY_STOPPED_PLAYBACK:
            _logger.warning('Replay has finished abnormally, stopping')
            self.__stop()

    def __start(self):
        self.state = State.STARTED_PLAYBACK
        g_playerEvents.onServerReplayEntering()
        if not BattleReplay.g_replayCtrl.play(self.filename):
            self.__stop()

    def __stop(self):
        self.state = State.FINISHED_PLAYBACK
        g_playerEvents.onServerReplayExiting()
        self.base.stopReplay()


PlayerReplayAccount = ReplayAccount
