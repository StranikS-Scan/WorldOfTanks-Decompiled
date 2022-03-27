# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/ReplayConnectionHandler.py
import os
import BigWorld
import BattleReplay
from PlayerEvents import g_playerEvents
from debug_utils import LOG_DEBUG, LOG_ERROR

class State:
    PRE_START_REPLAY = 0
    STARTED_PLAYBACK = 1
    FINISHED_PLAYBACK = 2


class ReplayConnectionHandler(BigWorld.Entity):

    def __init__(self):
        print 'ReplayConnectionHandler.__init__: self=id=%d' % self.id
        self.state = State.PRE_START_REPLAY

    def __del__(self):
        print 'ReplayConnectionHandler.__del__: self=id=%d' % self.id

    def onBecomePlayer(self):
        LOG_DEBUG('ReplayConnectionHandler.onBecomePlayer: self.id=%d, self.state=%s' % (self.id, self.state))
        if self.state == State.PRE_START_REPLAY:
            g_playerEvents.onServerReplayEntering()
            filename = BattleReplay.getDemandedToWatchFileName()
            if filename is None or not os.path.isfile(filename):
                LOG_ERROR('ReplayConnectionHandler.onBecomePlayer: replay file %s is not accessible' % str(filename))
                g_playerEvents.onServerReplayExiting()
                self.base.stopReplay()
                return
            LOG_DEBUG("BattleReplay.onBecomePlayer: filename='%s'" % filename)

            def _fn():
                self.state = State.STARTED_PLAYBACK
                BattleReplay.g_replayCtrl.play(filename)

            BigWorld.callback(1.0, _fn)
        elif self.state == State.STARTED_PLAYBACK:
            self.state = State.FINISHED_PLAYBACK
            print 'invoking g_playerEvents.onServerReplayExiting... : %s' % repr(g_playerEvents.onServerReplayExiting)
            g_playerEvents.onServerReplayExiting()
            print '...finished invoking g_playerEvents.onServerReplayExiting'
            self.base.stopReplay()
        return

    def onBecomeNonPlayer(self):
        LOG_DEBUG('ReplayConnectionHandler.onBecomeNonPlayer: self.id=%d' % self.id)

    def stopReplay(self):
        LOG_DEBUG('ReplayConnectionHandler.stopReplay')
        if BattleReplay.isPlaying():
            BattleReplay.g_replayCtrl.stop()

    def handleKeyEvent(self, *args, **kwargs):
        return False


PlayerReplayConnectionHandler = ReplayConnectionHandler
