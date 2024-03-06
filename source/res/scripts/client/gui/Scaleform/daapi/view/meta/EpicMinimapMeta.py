# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicMinimapMeta.py
from gui.Scaleform.daapi.view.battle.shared.minimap.component import MinimapComponent

class EpicMinimapMeta(MinimapComponent):

    def onZoomModeChanged(self, change):
        self._printOverrideError('onZoomModeChanged')

    def as_setZoomModeS(self, mode, modeText):
        return self.flashObject.as_setZoomMode(mode, modeText) if self._isDAAPIInited() else None

    def as_setMapDimensionsS(self, widthPx, heightPx):
        return self.flashObject.as_setMapDimensions(widthPx, heightPx) if self._isDAAPIInited() else None

    def as_updateSectorStateStatsS(self, data):
        return self.flashObject.as_updateSectorStateStats(data) if self._isDAAPIInited() else None

    def as_setMapShortcutKeyCodeS(self, value):
        return self.flashObject.as_setMapShortcutKeyCode(value) if self._isDAAPIInited() else None
