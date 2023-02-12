# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/debug_panel.py
from gui.Scaleform.daapi.view.meta.DebugPanelMeta import DebugPanelMeta
from gui.battle_control.controllers.debug_ctrl import IDebugPanel

class DebugPanel(DebugPanelMeta, IDebugPanel):

    def __init__(self):
        super(DebugPanel, self).__init__()
        self._fps = 0
        self._ping = 0
        self._isLaggingNow = False

    def updateDebugInfo(self, ping, fps, isLaggingNow, fpsReplay):
        if fpsReplay > 0:
            fps = '{0}({1})'.format(fpsReplay, fps)
        else:
            fps = str(fps)
        if self._isLaggingNow != isLaggingNow:
            self.as_updatePingFPSLagInfoS(ping, fps, isLaggingNow)
        else:
            self.as_updatePingFPSInfoS(ping, fps)
        self._ping, self._fps, self._isLaggingNow = ping, fps, isLaggingNow
