# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/meta/StanceDanceWidgetMeta.py
from gui.Scaleform.daapi.view.battle.shared.vehicle_mechanics.mechanic_widgets.vehicle_mechanic_widget import VehicleMechanicWidget

class StanceDanceWidgetMeta(VehicleMechanicWidget):

    def as_setStatusS(self, isFightState, isTurboState, isActiveFightState, isActiveTurboState):
        return self.flashObject.as_setStatus(isFightState, isTurboState, isActiveFightState, isActiveTurboState) if self._isDAAPIInited() else None

    def as_setProgressS(self, isSwitchingState, progressFight, progressTurbo):
        return self.flashObject.as_setProgress(isSwitchingState, progressFight, progressTurbo) if self._isDAAPIInited() else None
