# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/BrowserWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class BrowserWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def as_configureS(self, title, showActionBtn, showCloseBtn):
        return self.flashObject.as_configure(title, showActionBtn, showCloseBtn) if self._isDAAPIInited() else None

    def as_setSizeS(self, width, height):
        return self.flashObject.as_setSize(width, height) if self._isDAAPIInited() else None
