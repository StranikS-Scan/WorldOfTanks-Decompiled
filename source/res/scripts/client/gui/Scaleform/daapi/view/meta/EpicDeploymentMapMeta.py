# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EpicDeploymentMapMeta.py
from gui.Scaleform.daapi.view.meta.EpicMinimapMeta import EpicMinimapMeta

class EpicDeploymentMapMeta(EpicMinimapMeta):

    def as_setMapDimensionsS(self, widthPx, heightPx):
        return self.flashObject.as_setMapDimensions(widthPx, heightPx) if self._isDAAPIInited() else None
