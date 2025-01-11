# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DebugPanelMeta.py
from gui.Scaleform.framework.entities.BaseDAAPIComponent import BaseDAAPIComponent

class DebugPanelMeta(BaseDAAPIComponent):

    def as_initReplayS(self):
        return self.flashObject.as_initReplay() if self._isDAAPIInited() else None

    def as_updatePingS(self, ping):
        return self.flashObject.as_updatePing(ping) if self._isDAAPIInited() else None

    def as_updateFpsS(self, fps):
        return self.flashObject.as_updateFps(fps) if self._isDAAPIInited() else None

    def as_updatePingFPSS(self, ping, fps):
        return self.flashObject.as_updatePingFPS(ping, fps) if self._isDAAPIInited() else None

    def as_updateAllS(self, ping, fps, isLagging):
        return self.flashObject.as_updateAll(ping, fps, isLagging) if self._isDAAPIInited() else None

    def as_updateReplayS(self, ping, fps, isLagging, replayFps):
        return self.flashObject.as_updateReplay(ping, fps, isLagging, replayFps) if self._isDAAPIInited() else None
