# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ChargeableBurstWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class ChargeableBurstWidgetMeta(VehicleMechanicWidget):

    def as_setupS(self, penetrationCount, burstShootCount):
        return self.flashObject.as_setup(penetrationCount, burstShootCount) if self._isDAAPIInited() else None

    def as_setModeS(self, isBurstMode, isInstantly):
        return self.flashObject.as_setMode(isBurstMode, isInstantly) if self._isDAAPIInited() else None

    def as_setChargesS(self, charges, burstShotCount, isInstantly):
        return self.flashObject.as_setCharges(charges, burstShotCount, isInstantly) if self._isDAAPIInited() else None

    def as_setShellsQuantityLeftS(self, count):
        return self.flashObject.as_setShellsQuantityLeft(count) if self._isDAAPIInited() else None

    def as_updateBurstReloadingStateS(self, isReloading):
        return self.flashObject.as_updateBurstReloadingState(isReloading) if self._isDAAPIInited() else None
