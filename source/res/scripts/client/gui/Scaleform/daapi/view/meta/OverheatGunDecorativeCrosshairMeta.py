# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/OverheatGunDecorativeCrosshairMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.vehicle_decorative_crosshair import VehicleDecorativeCrosshair

class OverheatGunDecorativeCrosshairMeta(VehicleDecorativeCrosshair):

    def as_setProgressS(self, progress):
        return self.flashObject.as_setProgress(progress) if self._isDAAPIInited() else None

    def as_setSectionS(self, section):
        return self.flashObject.as_setSection(section) if self._isDAAPIInited() else None
