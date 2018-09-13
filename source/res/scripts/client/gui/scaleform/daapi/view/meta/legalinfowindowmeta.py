# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LegalInfoWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class LegalInfoWindowMeta(DAAPIModule):

    def getLegalInfo(self):
        self._printOverrideError('getLegalInfo')

    def onCancelClick(self):
        self._printOverrideError('onCancelClick')

    def as_setLegalInfoS(self, legalInfo):
        if self._isDAAPIInited():
            return self.flashObject.as_setLegalInfo(legalInfo)
