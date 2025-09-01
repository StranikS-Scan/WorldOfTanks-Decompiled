# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/RocketAcceleratorIndicatorMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class RocketAcceleratorIndicatorMeta(VehicleMechanicWidget):

    def as_setCountS(self, count):
        return self.flashObject.as_setCount(count) if self._isDAAPIInited() else None

    def as_setProgressS(self, progress):
        return self.flashObject.as_setProgress(progress) if self._isDAAPIInited() else None

    def as_updateLayoutS(self, x, y):
        return self.flashObject.as_updateLayout(x, y) if self._isDAAPIInited() else None
