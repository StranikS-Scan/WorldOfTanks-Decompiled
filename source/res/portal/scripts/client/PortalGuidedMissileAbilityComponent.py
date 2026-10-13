# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/client/PortalGuidedMissileAbilityComponent.py
import BigWorld
from script_component.DynamicScriptComponent import DynamicScriptComponent

class PortalGuidedMissileAbilityComponent(DynamicScriptComponent):

    def onCeilingBlocked(self):
        self.__showError('guidedMissileCeilingBlocked')

    def onTeleportBlocked(self):
        self.__showError('guidedMissileTeleportBlocked')

    def __showError(self, key):
        player = BigWorld.player()
        if player is None:
            return
        else:
            vehicle = player.getVehicleAttached()
            if vehicle is not None and vehicle.id == self.entity.id:
                player.showVehicleError(key)
            return
