# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceWindowPatchCutMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortIntelligenceWindowPatchCutMeta(DAAPIModule):

    def as_setDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(value)
