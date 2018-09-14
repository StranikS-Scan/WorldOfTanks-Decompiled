# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/FortCombatReservesIntroMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class FortCombatReservesIntroMeta(AbstractWindowView):

    def as_setDataS(self, data):
        if self._isDAAPIInited():
            return self.flashObject.as_setData(data)
