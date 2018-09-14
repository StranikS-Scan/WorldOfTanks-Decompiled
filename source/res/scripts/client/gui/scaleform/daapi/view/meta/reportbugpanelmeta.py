# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ReportBugPanelMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class ReportBugPanelMeta(DAAPIModule):

    def reportBug(self):
        self._printOverrideError('reportBug')

    def as_setHyperLinkS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setHyperLink(value)
