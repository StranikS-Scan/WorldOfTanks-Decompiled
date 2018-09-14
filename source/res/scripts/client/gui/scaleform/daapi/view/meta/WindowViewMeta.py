# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WindowViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class WindowViewMeta(WrapperViewMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends WrapperViewMeta
    """

    def onWindowMinimize(self):
        self._printOverrideError('onWindowMinimize')

    def onSourceLoaded(self):
        self._printOverrideError('onSourceLoaded')

    def onTryClosing(self):
        self._printOverrideError('onTryClosing')

    def as_getGeometryS(self):
        return self.flashObject.as_getGeometry() if self._isDAAPIInited() else None

    def as_setGeometryS(self, x, y, width, height):
        return self.flashObject.as_setGeometry(x, y, width, height) if self._isDAAPIInited() else None

    def as_isModalS(self):
        return self.flashObject.as_isModal() if self._isDAAPIInited() else None
