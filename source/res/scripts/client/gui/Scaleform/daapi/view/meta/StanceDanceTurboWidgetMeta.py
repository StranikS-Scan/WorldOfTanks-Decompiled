# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StanceDanceTurboWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class StanceDanceTurboWidgetMeta(VehicleMechanicWidget):

    def as_setProgressS(self, isSwitchingState, progress):
        return self.flashObject.as_setProgress(isSwitchingState, progress) if self._isDAAPIInited() else None

    def as_setSpeedS(self, currentSpeed, isActive):
        return self.flashObject.as_setSpeed(currentSpeed, isActive) if self._isDAAPIInited() else None

    def as_setParamsS(self, maxSpeed, maxActiveSpeed, maxTurboSpeed, gainSpeed):
        return self.flashObject.as_setParams(maxSpeed, maxActiveSpeed, maxTurboSpeed, gainSpeed) if self._isDAAPIInited() else None

    def as_switchTimerS(self, value):
        return self.flashObject.as_switchTimer(value) if self._isDAAPIInited() else None

    def as_keysVisibleS(self, value):
        return self.flashObject.as_keysVisible(value) if self._isDAAPIInited() else None
