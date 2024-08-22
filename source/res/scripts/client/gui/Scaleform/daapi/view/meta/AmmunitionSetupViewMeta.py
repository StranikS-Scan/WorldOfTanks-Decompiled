# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AmmunitionSetupViewMeta.py
from gui.Scaleform.framework.entities.View import View

class AmmunitionSetupViewMeta(View):

    def onClose(self):
        self._printOverrideError('onClose')

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def as_gfSizeUpdatedS(self, x, width, bottomMargin):
        return self.flashObject.as_gfSizeUpdated(x, width, bottomMargin) if self._isDAAPIInited() else None

    def as_showCloseAnimS(self):
        return self.flashObject.as_showCloseAnim() if self._isDAAPIInited() else None

    def as_onAnimationEndS(self):
        return self.flashObject.as_onAnimationEnd() if self._isDAAPIInited() else None

    def as_toggleParamsS(self, isVisible):
        return self.flashObject.as_toggleParams(isVisible) if self._isDAAPIInited() else None
