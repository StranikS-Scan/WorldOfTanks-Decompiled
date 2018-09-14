# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortIntelligenceNotAvailableWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortIntelligenceNotAvailableWindowMeta(AbstractWindowView):

    def as_setDataS(self, value):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(value)
