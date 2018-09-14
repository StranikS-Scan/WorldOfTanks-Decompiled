# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReportBugMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ReportBugMeta(DAAPIModule):

    def reportBug(self):
        self._printOverrideError('reportBug')

    def as_setHyperLinkS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setHyperLink(value)
