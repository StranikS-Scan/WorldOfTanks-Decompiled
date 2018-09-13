# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortDisconnectViewMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortDisconnectViewMeta(DAAPIModule):

    def as_setWarningTextsS(self, warningTxt, warningDescTxt):
        if self._isDAAPIInited():
            return self.flashObject.as_setWarningTexts(warningTxt, warningDescTxt)
