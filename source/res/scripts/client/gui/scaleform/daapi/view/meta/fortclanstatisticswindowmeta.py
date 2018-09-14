# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortClanStatisticsWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortClanStatisticsWindowMeta(AbstractWindowView):

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
