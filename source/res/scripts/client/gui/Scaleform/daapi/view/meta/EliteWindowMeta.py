# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/EliteWindowMeta.py
from gui.Scaleform.framework.entities.abstract.AbstractWindowView import AbstractWindowView

class EliteWindowMeta(AbstractWindowView):

    def as_setVehicleS(self, vehicle):
        return self.flashObject.as_setVehicle(vehicle) if self._isDAAPIInited() else None
