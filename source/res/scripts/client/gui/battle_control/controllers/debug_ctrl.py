# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/debug_ctrl.py
import BigWorld
import BattleReplay
import constants
from gui.battle_control import avatar_getter
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.view_components import IViewComponentsController
from gui.shared.utils.TimeInterval import TimeInterval
from helpers.statistics import g_statistics
_UPDATE_INTERVAL = 0.2
_LATENCY_UNAVAILABLE = (0, 0, 0, 0)

class IDebugPanel(object):

    def updateDebugInfo(self, ping, fps, isLaggingNow, fpsReplay=-1):
        raise NotImplementedError


class DebugController(IViewComponentsController):
    """Controller for the debug panel.
    
    This class starts internal update cycle and updates debug panel.
    In order to collect lagging info from near vehicles, these vehicle's ids
    should be provided from outside using special methods.
    """

    def __init__(self):
        super(DebugController, self).__init__()
        self._debugPanelUI = None
        self._timeInterval = None
        self._visibleVehicles = set()
        return

    def getControllerID(self):
        return BATTLE_CTRL_ID.DEBUG

    def startControl(self):
        self._timeInterval = TimeInterval(_UPDATE_INTERVAL, self, '_update')
        self._timeInterval.start()

    def stopControl(self):
        self._timeInterval.stop()
        self._timeInterval = None
        self._debugPanelUI = None
        self._visibleVehicles = set()
        return

    def setViewComponents(self, debugPanelUI):
        assert isinstance(debugPanelUI, IDebugPanel)
        self._debugPanelUI = debugPanelUI

    def clearViewComponents(self):
        self._debugPanelUI = None
        return

    def startVehicleVisual(self, vehicleID):
        if avatar_getter.getPlayerVehicleID() != vehicleID:
            self._visibleVehicles.add(vehicleID)

    def stopVehicleVisual(self, vehicleID):
        self._visibleVehicles.discard(vehicleID)

    def _update(self):
        replayCtrl = BattleReplay.g_replayCtrl
        if replayCtrl.isPlaying and replayCtrl.fps > 0:
            fps = BigWorld.getFPS()[1]
            fpsReplay = int(replayCtrl.fps)
            ping = replayCtrl.ping
            isLaggingNow = replayCtrl.isLaggingNow
        else:
            fpsReplay = -1
            player = BigWorld.player()
            isLaggingNow = player.filter.isLaggingNow if player is not None else False
            if not isLaggingNow:
                for vehicleID in self._visibleVehicles:
                    vehicle = BigWorld.entities[vehicleID]
                    if vehicle is not None and vehicle.isAlive():
                        try:
                            if vehicle.filter.isLagginNow:
                                isLaggingNow = True
                                break
                        except AttributeError:
                            pass

            avgLatency = BigWorld.LatencyInfo().value[3]
            if avgLatency:
                ping = min(avgLatency * 1000, 999)
                if ping < 999:
                    ping = max(1, ping - 500.0 * constants.SERVER_TICK_LENGTH)
            else:
                ping = 999
            fpsInfo = BigWorld.getFPS()
            g_statistics.update(fpsInfo, ping, isLaggingNow)
            fps = fpsInfo[1]
            if replayCtrl.isRecording:
                replayCtrl.setFpsPingLag(fps, ping, isLaggingNow)
        if self._debugPanelUI is not None:
            self._debugPanelUI.updateDebugInfo(int(ping), int(fps), isLaggingNow, fpsReplay=fpsReplay)
        return
