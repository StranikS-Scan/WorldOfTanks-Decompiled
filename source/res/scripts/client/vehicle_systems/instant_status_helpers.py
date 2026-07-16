# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/instant_status_helpers.py
import CGF
import InstantStatuses

def invokeInstantStatusForVehicle(vehicle, instantStatusType):
    gameObject = vehicle.appearance.gameObject
    instantStatus = gameObject.findWrite(instantStatusType)
    if not instantStatus:
        queue = CGF.CommandQueue(gameObject.spaceID)
        queue.createComponent(gameObject, instantStatusType)
    else:
        instantStatus.addNextDone()


def invokeShotsDoneStatus(vehicle):
    invokeInstantStatusForVehicle(vehicle, InstantStatuses.ShotsDoneComponent)
