# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WindowViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class WindowViewMeta(WrapperViewMeta):

    def onWindowMinimize(self):
        self._printOverrideError('onWindowMinimize')

    def onSourceLoaded(self):
        self._printOverrideError('onSourceLoaded')

    def onTryClosing(self):
        self._printOverrideError('onTryClosing')

    def as_getGeometryS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_getGeometry()

    def as_setGeometryS(self, x, y, width, height):
        if self._isDAAPIInited():
            return self.flashObject.as_setGeometry(x, y, width, height)

    def as_isModalS(self):
        if self._isDAAPIInited():
            return self.flashObject.as_isModal()
