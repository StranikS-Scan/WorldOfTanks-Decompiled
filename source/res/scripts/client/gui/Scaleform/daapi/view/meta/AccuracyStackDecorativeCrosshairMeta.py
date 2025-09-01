# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/AccuracyStackDecorativeCrosshairMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.vehicle_decorative_crosshair import VehicleDecorativeCrosshair

class AccuracyStackDecorativeCrosshairMeta(VehicleDecorativeCrosshair):

    def as_setInitDataS(self, maxStackCount, speedLimit):
        return self.flashObject.as_setInitData(maxStackCount, speedLimit) if self._isDAAPIInited() else None

    def as_setStacksProgresS(self, count, progress):
        return self.flashObject.as_setStacksProgres(count, progress) if self._isDAAPIInited() else None

    def as_setGainingActiveS(self, value):
        return self.flashObject.as_setGainingActive(value) if self._isDAAPIInited() else None

    def as_setSpeedLimitActiveS(self, value):
        return self.flashObject.as_setSpeedLimitActive(value) if self._isDAAPIInited() else None
