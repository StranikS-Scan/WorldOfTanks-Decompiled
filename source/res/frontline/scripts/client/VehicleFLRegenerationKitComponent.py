# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/VehicleFLRegenerationKitComponent.py
import BigWorld
from debug_utils import LOG_DEBUG
from gui.battle_control.battle_constants import VEHICLE_VIEW_STATE

class VehicleFLRegenerationKitComponent(BigWorld.DynamicScriptComponent):

    def set_regenerationKit(self, _=None):
        attachedVehicle = BigWorld.player().getVehicleAttached()
        if attachedVehicle is None:
            return
        else:
            healPointEnter = {'senderKey': 'healPoint',
             'isSourceVehicle': None,
             'isInactivation': None if not self.regenerationKit['isActive'] else self.regenerationKit['isActive'],
             'endTime': self.regenerationKit['endTime'],
             'duration': self.regenerationKit['duration']}
            if self.entity.id == attachedVehicle.id:
                self.entity.guiSessionProvider.invalidateVehicleState(VEHICLE_VIEW_STATE.HEALING, healPointEnter)
            if not self.entity.isPlayerVehicle:
                ctrl = self.entity.guiSessionProvider.shared.feedback
                if ctrl is not None:
                    ctrl.invalidateFLRegenerationKit(self.entity.id, self.regenerationKit)
            return
