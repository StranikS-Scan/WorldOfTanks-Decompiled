# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/PropellantGunWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class PropellantGunWidgetMeta(VehicleMechanicWidget):

    def as_setChargeValuesS(self, chargeProgress, chargeDamage):
        return self.flashObject.as_setChargeValues(chargeProgress, chargeDamage) if self._isDAAPIInited() else None

    def as_setupThresholdS(self, chargeThreshold):
        return self.flashObject.as_setupThreshold(chargeThreshold) if self._isDAAPIInited() else None

    def as_showHotKeysS(self, isShow=True):
        return self.flashObject.as_showHotKeys(isShow) if self._isDAAPIInited() else None

    def as_activateHotKeyS(self, command):
        return self.flashObject.as_activateHotKey(command) if self._isDAAPIInited() else None
