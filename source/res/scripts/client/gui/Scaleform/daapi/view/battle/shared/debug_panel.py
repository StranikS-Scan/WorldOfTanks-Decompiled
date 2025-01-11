# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/debug_panel.py
from gui.Scaleform.daapi.view.meta.DebugPanelMeta import DebugPanelMeta
from gui.battle_control.controllers.debug_ctrl import IDebugPanel
_REPLAY_WITHOUT_CHANGE = -1

class DebugPanel(DebugPanelMeta, IDebugPanel):

    def __init__(self):
        super(DebugPanel, self).__init__()
        self._fps = 0
        self._fpsReplay = 0
        self._ping = 0
        self._isLaggingNow = False

    def updateDebugInfo(self, ping, fps, isLaggingNow):
        fpsChanged = self._fps != fps
        pingChanged = self._ping != ping
        laggingChanged = self._isLaggingNow != isLaggingNow
        if not fpsChanged and not pingChanged and not laggingChanged:
            return
        if fpsChanged and not pingChanged and not laggingChanged:
            self.as_updateFpsS(fps)
        elif fpsChanged and pingChanged and not laggingChanged:
            self.as_updatePingFPSS(ping, fps)
        elif not fpsChanged and pingChanged and not laggingChanged:
            self.as_updatePingS(ping)
        else:
            self.as_updateAllS(ping, fps, isLaggingNow)
        self._ping, self._fps, self._isLaggingNow = ping, fps, isLaggingNow

    def updateReplayDebugInfo(self, ping, fps, isLaggingNow, fpsReplay):
        if self._ping != ping or self._fpsReplay != fpsReplay or self._fps != fps or self._isLaggingNow != isLaggingNow:
            if self._ping != ping:
                self._ping = ping
            else:
                ping = _REPLAY_WITHOUT_CHANGE
            if self._fps != fps or self._fpsReplay != fpsReplay:
                self._fps, self._fpsReplay = fps, fpsReplay
            else:
                fps = _REPLAY_WITHOUT_CHANGE
                fpsReplay = _REPLAY_WITHOUT_CHANGE
            self.as_updateReplayS(ping, fps, isLaggingNow, fpsReplay)
            self._isLaggingNow = isLaggingNow
