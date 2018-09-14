# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PopOverViewMeta.py
from gui.Scaleform.daapi.view.meta.WrapperViewMeta import WrapperViewMeta

class PopOverViewMeta(WrapperViewMeta):
    """
    DO NOT MODIFY!
    Generated with yaml.
    __author__ = 'yaml_processor'
    @extends WrapperViewMeta
    """

    def as_setArrowDirectionS(self, value):
        return self.flashObject.as_setArrowDirection(value) if self._isDAAPIInited() else None

    def as_setArrowPositionS(self, value):
        return self.flashObject.as_setArrowPosition(value) if self._isDAAPIInited() else None
