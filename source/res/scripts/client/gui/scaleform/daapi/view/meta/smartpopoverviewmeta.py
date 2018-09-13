# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SmartPopOverViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class SmartPopOverViewMeta(DAAPIModule):

    def as_setPositionKeyPointS(self, valX, valY):
        if self._isDAAPIInited():
            return self.flashObject.as_setPositionKeyPoint(valX, valY)
