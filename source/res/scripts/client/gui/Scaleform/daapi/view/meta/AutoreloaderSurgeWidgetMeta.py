# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AutoreloaderSurgeWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class AutoreloaderSurgeWidgetMeta(VehicleMechanicWidget):

    def as_setStagesProgressS(self, progress):
        return self.flashObject.as_setStagesProgress(progress) if self._isDAAPIInited() else None

    def as_setAvailableS(self, value):
        return self.flashObject.as_setAvailable(value) if self._isDAAPIInited() else None

    def as_setChargeCountS(self, value):
        return self.flashObject.as_setChargeCount(value) if self._isDAAPIInited() else None

    def as_setSectorCountS(self, count):
        return self.flashObject.as_setSectorCount(count) if self._isDAAPIInited() else None

    def as_setBoostedChargeS(self, value):
        return self.flashObject.as_setBoostedCharge(value) if self._isDAAPIInited() else None
