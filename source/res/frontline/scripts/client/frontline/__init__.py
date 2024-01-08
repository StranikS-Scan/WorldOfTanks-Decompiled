# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/__init__.py
import BigWorld
from helpers import isPlayerAvatar

def invalidateVehicleMarkerState(entity, vehData, markerData, state, stateCallBack):
    attachedVehicle = BigWorld.player().getVehicleAttached()
    if attachedVehicle is None:
        return
    else:
        if entity.id == BigWorld.player().getObservedVehicleID() and vehData is not None:
            entity.guiSessionProvider.invalidateVehicleState(state, vehData)
        if not entity.isPlayerVehicle:
            ctrl = entity.guiSessionProvider.shared.feedback
            if ctrl is not None:
                call = getattr(ctrl, stateCallBack)
                call(entity.id, markerData)
        return


def isAvatarReady():
    return isPlayerAvatar() and BigWorld.player().userSeesWorld()
