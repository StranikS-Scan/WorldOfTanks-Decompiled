# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StationaryReloadWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class StationaryReloadWidgetMeta(VehicleMechanicWidget):

    def as_setConditionS(self, condition):
        return self.flashObject.as_setCondition(condition) if self._isDAAPIInited() else None
