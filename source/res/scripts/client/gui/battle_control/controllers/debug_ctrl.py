# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/debug_ctrl.py
import BigWorld
import BattleReplay
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from gui.shared.utils.TimeInterval import TimeInterval
from helpers import dependency
from skeletons.helpers.statistics import IStatisticsCollector
_UPDATE_INTERVAL = 0.2

class IDebugPanel(object):

    def updateDebugInfo(self, ping, fps, isLaggingNow):
        raise NotImplementedError

    def updateReplayDebugInfo(self, ping, fps, isLaggingNow, fpsReplay):
        raise NotImplementedError


class DebugController(IViewComponentsController):
    statsCollector = dependency.descriptor(IStatisticsCollector)

    def __init__(self):
        super(DebugController, self).__init__()
        self._debugPanelUI = None
        self._timeInterval = None
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.DEBUG

    def startControl(self):
        replayCtrl = BattleReplay.g_replayCtrl
        self._timeInterval = TimeInterval(_UPDATE_INTERVAL, self, '_updateReplay' if replayCtrl.isPlaying else '_update')
        self._timeInterval.start()

    def stopControl(self):
        self._timeInterval.stop()
        self._timeInterval = None
        self.clearViewComponents()
        return

    def setViewComponents(self, debugPanelUI):
        self._debugPanelUI = debugPanelUI
        if BattleReplay.g_replayCtrl.isPlaying:
            self._debugPanelUI.as_initReplayS()

    def clearViewComponents(self):
        self._debugPanelUI = None
        return

    def _update(self):
        isLaggingNow = BigWorld.statLagDetected()
        ping = BigWorld.statPing()
        fps = BigWorld.getFPS()[1]
        self.statsCollector.update()
        try:
            ping = int(ping)
            fps = int(fps)
        except (ValueError, OverflowError):
            return

        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isRecording:
            replayCtrl.setFpsPingLag(fps, ping, isLaggingNow)
        if self._debugPanelUI is not None:
            self._debugPanelUI.updateDebugInfo(ping, fps, isLaggingNow)
        return

    def _updateReplay(self):
        if self._debugPanelUI is None:
            return
        else:
            replayCtrl = BattleReplay.g_replayCtrl
            fps = BigWorld.getFPS()[1]
            fpsReplay = replayCtrl.fps
            ping = replayCtrl.ping
            isLaggingNow = replayCtrl.isLaggingNow
            self._debugPanelUI.updateReplayDebugInfo(ping, fps, isLaggingNow, fpsReplay)
            return
