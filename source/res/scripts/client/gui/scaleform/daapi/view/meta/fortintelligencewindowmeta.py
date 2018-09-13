# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortIntelligenceWindowMeta(DAAPIModule):

    def as_setDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(value)
