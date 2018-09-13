# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PopOverViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class PopOverViewMeta(DAAPIModule):

    def as_setArrowDirectionS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setArrowDirection(value)

    def as_setArrowPositionS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setArrowPosition(value)
