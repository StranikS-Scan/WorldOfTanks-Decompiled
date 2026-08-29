# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/SightPointerWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class SightPointerWidgetMeta(VehicleMechanicWidget):

    def as_setProgressS(self, progress, timeLeft):
        return self.flashObject.as_setProgress(progress, timeLeft) if self._isDAAPIInited() else None

    def as_setTankIconStateS(self, state):
        return self.flashObject.as_setTankIconState(state) if self._isDAAPIInited() else None

    def as_triggerHighlightLampS(self):
        return self.flashObject.as_triggerHighlightLamp() if self._isDAAPIInited() else None
