# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/DetachmentViewMeta.py
from gui.Scaleform.framework.entities.View import View

class DetachmentViewMeta(View):

    def onEscapePress(self):
        self._printOverrideError('onEscapePress')

    def as_updateTTCDisplayPropsS(self, x, y, height, isVisible):
        return self.flashObject.as_updateTTCDisplayProps(x, y, height, isVisible) if self._isDAAPIInited() else None
