# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortOrderInfoWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortOrderInfoWindowMeta(DAAPIModule):

    def as_setWindowDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setWindowData(data)

    def as_setDynPropertiesS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setDynProperties(data)
