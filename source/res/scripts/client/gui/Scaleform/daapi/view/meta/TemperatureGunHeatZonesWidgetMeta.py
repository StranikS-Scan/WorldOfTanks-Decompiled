# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/TemperatureGunHeatZonesWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class TemperatureGunHeatZonesWidgetMeta(VehicleMechanicWidget):

    def as_setHeatZonesValuesS(self, low, medium=1):
        return self.flashObject.as_setHeatZonesValues(low, medium) if self._isDAAPIInited() else None

    def as_setTemperatureS(self, value):
        return self.flashObject.as_setTemperature(value) if self._isDAAPIInited() else None
