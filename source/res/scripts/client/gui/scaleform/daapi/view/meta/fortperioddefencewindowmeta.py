# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortPeriodDefenceWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortPeriodDefenceWindowMeta(DAAPIModule):

    def onApply(self, data):
        self._printOverrideError('onApply')

    def onCancel(self):
        self._printOverrideError('onCancel')

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)

    def as_setTextDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setTextData(data)
