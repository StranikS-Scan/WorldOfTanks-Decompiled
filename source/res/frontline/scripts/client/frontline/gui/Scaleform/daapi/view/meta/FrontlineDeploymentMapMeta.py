# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/Scaleform/daapi/view/meta/FrontlineDeploymentMapMeta.py
from frontline.gui.Scaleform.daapi.view.meta.FrontlineMinimapMeta import FrontlineMinimapMeta

class FrontlineDeploymentMapMeta(FrontlineMinimapMeta):

    def as_setMapDimensionsS(self, widthPx, heightPx):
        return self.flashObject.as_setMapDimensions(widthPx, heightPx) if self._isDAAPIInited() else None
