# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/OverheatDecorativeCrosshairMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.decorative_crosshairs.vehicle_decorative_crosshair import VehicleDecorativeCrosshair

class OverheatDecorativeCrosshairMeta(VehicleDecorativeCrosshair):

    def as_setStacksProgresS(self, progress, level):
        return self.flashObject.as_setStacksProgres(progress, level) if self._isDAAPIInited() else None

    def as_setHeatProgresS(self, progress):
        return self.flashObject.as_setHeatProgres(progress) if self._isDAAPIInited() else None

    def as_updateStateS(self, state):
        return self.flashObject.as_updateState(state) if self._isDAAPIInited() else None

    def as_setInitDataS(self, speedLimit, maxLevel, heatingTime, coolingTime, isSpeedChanged):
        return self.flashObject.as_setInitData(speedLimit, maxLevel, heatingTime, coolingTime, isSpeedChanged) if self._isDAAPIInited() else None

    def as_setDamageDataS(self, baseDamage, maxDamage):
        return self.flashObject.as_setDamageData(baseDamage, maxDamage) if self._isDAAPIInited() else None
