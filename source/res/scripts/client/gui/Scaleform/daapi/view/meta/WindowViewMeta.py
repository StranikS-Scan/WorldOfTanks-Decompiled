# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/WindowViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class WindowViewMeta(WrapperViewMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends WrapperViewMeta
    null
    """

    def onWindowMinimize(self):
        """
        :return :
        """
        self._printOverrideError('onWindowMinimize')

    def onSourceLoaded(self):
        """
        :return :
        """
        self._printOverrideError('onSourceLoaded')

    def onTryClosing(self):
        """
        :return Boolean:
        """
        self._printOverrideError('onTryClosing')

    def as_getGeometryS(self):
        """
        :return Array:
        """
        return self.flashObject.as_getGeometry() if self._isDAAPIInited() else None

    def as_setGeometryS(self, x, y, width, height):
        """
        :param x:
        :param y:
        :param width:
        :param height:
        :return :
        """
        return self.flashObject.as_setGeometry(x, y, width, height) if self._isDAAPIInited() else None

    def as_isModalS(self):
        """
        :return Boolean:
        """
        return self.flashObject.as_isModal() if self._isDAAPIInited() else None
