# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/VehicleCorrodingShotComponent.py
import BigWorld
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE
from script_component.DynamicScriptComponent import DynamicScriptComponent

class VehicleCorrodingShotComponent(DynamicScriptComponent):

    def _onAvatarReady(self):
        self.set_finishTime()

    def set_finishTime(self, _=None):
        elapsedTime = self.finishTime - BigWorld.serverTime() if self.finishTime else 0.0
        self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.CORRODING_SHOT, elapsedTime)
