# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/scaleform/daapi/view/meta/LSMinimapMeta.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent

class LSMinimapMeta(ClassicMinimapComponent):

    def as_setZoomModeS(self, mode):
        return self.flashObject.as_setZoomMode(mode) if self._isDAAPIInited() else None

    def as_setMapDimensionsS(self, widthPx, heightPx):
        return self.flashObject.as_setMapDimensions(widthPx, heightPx) if self._isDAAPIInited() else None
