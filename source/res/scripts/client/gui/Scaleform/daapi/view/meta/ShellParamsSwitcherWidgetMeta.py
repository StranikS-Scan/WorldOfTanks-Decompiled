# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/ShellParamsSwitcherWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class ShellParamsSwitcherWidgetMeta(VehicleMechanicWidget):

    def as_setParamsTypeS(self, type):
        return self.flashObject.as_setParamsType(type) if self._isDAAPIInited() else None
