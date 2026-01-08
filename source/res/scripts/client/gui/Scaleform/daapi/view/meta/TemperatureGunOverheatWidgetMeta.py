# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TemperatureGunOverheatWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class TemperatureGunOverheatWidgetMeta(VehicleMechanicWidget):

    def as_setupThresholdsS(self, warning, overheat):
        return self.flashObject.as_setupThresholds(warning, overheat) if self._isDAAPIInited() else None

    def as_setTemperatureS(self, value):
        return self.flashObject.as_setTemperature(value) if self._isDAAPIInited() else None
