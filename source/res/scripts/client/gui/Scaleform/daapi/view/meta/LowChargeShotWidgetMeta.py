# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/LowChargeShotWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class LowChargeShotWidgetMeta(VehicleMechanicWidget):

    def as_setInitialTimeS(self, baseTime, lowChargeTime, almostFinishedTime, lowChargeCap, shellChangeTime):
        return self.flashObject.as_setInitialTime(baseTime, lowChargeTime, almostFinishedTime, lowChargeCap, shellChangeTime) if self._isDAAPIInited() else None

    def as_setTimeLeftS(self, timeLeft, state, isReplay):
        return self.flashObject.as_setTimeLeft(timeLeft, state, isReplay) if self._isDAAPIInited() else None
