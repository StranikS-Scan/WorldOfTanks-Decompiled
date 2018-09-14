# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PromoPremiumIgrWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class PromoPremiumIgrWindowMeta(AbstractWindowView):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends AbstractWindowView
    """

    def as_setTitleS(self, value):
        return self.flashObject.as_setTitle(value) if self._isDAAPIInited() else None

    def as_setTextS(self, value):
        return self.flashObject.as_setText(value) if self._isDAAPIInited() else None

    def as_setWindowTitleS(self, value):
        return self.flashObject.as_setWindowTitle(value) if self._isDAAPIInited() else None

    def as_setApplyButtonLabelS(self, value):
        return self.flashObject.as_setApplyButtonLabel(value) if self._isDAAPIInited() else None
