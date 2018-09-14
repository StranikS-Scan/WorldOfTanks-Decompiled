# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCalendarWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortCalendarWindowMeta(AbstractWindowView):

    def as_updatePreviewDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_updatePreviewData(data)
