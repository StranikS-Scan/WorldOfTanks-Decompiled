# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/StealthRadarComponent.py
import BigWorld
from CurrentVehicle import g_currentVehicle
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class StealthRadarComponent(BigWorld.DynamicScriptComponent):
    _CALLBACK_DELAY = 0.2

    def __init__(self):
        super(StealthRadarComponent, self).__init__()
        self.__invalidateStealthRadarState()
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged += self.__onVehicleChanged

    def set_stealthRadar(self, _=None):
        self.__invalidateStealthRadarState()

    def onEnterWorld(self, *args):
        pass

    def onLeaveWorld(self):
        BigWorld.player().consistentMatrices.onVehicleMatrixBindingChanged -= self.__onVehicleChanged

    def __onVehicleChanged(self, _):
        self.__invalidateStealthRadarState()

    def __invalidateStealthRadarState(self):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None:
            return
        else:
            if self.entity.id == BigWorld.player().getObservedVehicleID() and self.stealthRadar is not None:
                self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.STEALTH_RADAR, self.stealthRadar)
            if not self.entity.isPlayerVehicle:
                ctrl = self.entity.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateStealthRadar(self.entity.id, self.stealthRadar)
            return
