# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCalendarWindowMeta.py
from gui.Scaleform.framework.entities.DAAPIModule import DAAPIModule

class FortCalendarWindowMeta(DAAPIModule):

    def as_updatePreviewDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updatePreviewData(data)
