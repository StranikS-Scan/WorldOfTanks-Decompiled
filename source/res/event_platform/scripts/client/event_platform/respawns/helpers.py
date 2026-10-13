# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/client/event_platform/respawns/helpers.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
import CGF
from event_platform.respawns.respawns import RespawnPolicySystem
if TYPE_CHECKING:
    from typing import Any, Optional, Type

def getRespawnPolicyComponent(spaceID, vehicleId, componentType):
    system = CGF.getSystem(spaceID, RespawnPolicySystem)
    if system is None:
        return
    else:
        policyGO = system.findPolicyGameObject(vehicleId)
        return policyGO.findRead(componentType) if policyGO is not None else None
