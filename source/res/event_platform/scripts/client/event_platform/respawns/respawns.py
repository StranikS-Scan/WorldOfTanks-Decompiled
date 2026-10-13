# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/respawns/respawns.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
import CGF
from RespawnPolicyVehicleLinkComponent import RespawnPolicyVehicleLinkComponent
if TYPE_CHECKING:
    from typing import Optional

class RespawnPolicySystem(CGF.System):
    PolicyIterate = CGF.IterateReaction(CGF.GameObject, CGF.Ro(RespawnPolicyVehicleLinkComponent))
    Reactions = CGF.Reactions(PolicyIterate)

    def update(self):
        pass

    def findPolicyGameObject(self, vehicleId):
        for policyGO, link in self.reaction(self.PolicyIterate):
            if link.vehicleId == vehicleId:
                return policyGO

        return None
