# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PveMinimapMeta.py
from gui.Scaleform.daapi.view.battle.classic.minimap import ClassicMinimapComponent

class PveMinimapMeta(ClassicMinimapComponent):

    def as_setShorcutLabelS(self, label):
        return self.flashObject.as_setShorcutLabel(label) if self._isDAAPIInited() else None

    def as_showGridS(self, show):
        return self.flashObject.as_showGrid(show) if self._isDAAPIInited() else None

    def as_setGridS(self, rows, columns):
        return self.flashObject.as_setGrid(rows, columns) if self._isDAAPIInited() else None
