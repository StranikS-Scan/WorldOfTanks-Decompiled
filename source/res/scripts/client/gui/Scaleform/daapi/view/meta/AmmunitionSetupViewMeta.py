# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionSetupViewMeta.py
from gui.Scaleform.daapi.view.meta.GFTutorialViewMeta import GFTutorialViewMeta

class AmmunitionSetupViewMeta(GFTutorialViewMeta):

    def onClose(self):
        self._printOverrideError('onClose')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def as_gfSizeUpdatedS(self, width, x):
        return self.flashObject.as_gfSizeUpdated(width, x) if self._isDAAPIInited() else None

    def as_showCloseAnimS(self):
        return self.flashObject.as_showCloseAnim() if self._isDAAPIInited() else None

    def as_onAnimationEndS(self):
        return self.flashObject.as_onAnimationEnd() if self._isDAAPIInited() else None
