# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StanceDanceBaseWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class StanceDanceBaseWidgetMeta(VehicleMechanicWidget):

    def as_setStatusS(self, isChosen, isActive):
        return self.flashObject.as_setStatus(isChosen, isActive) if self._isDAAPIInited() else None

    def as_setProgressS(self, isSwitchingState, progress):
        return self.flashObject.as_setProgress(isSwitchingState, progress) if self._isDAAPIInited() else None
