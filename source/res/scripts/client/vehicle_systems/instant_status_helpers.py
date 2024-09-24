# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/instant_status_helpers.py
import InstantStatuses
from constants import IS_CLIENT

def invokeInstantStatusForVehicle(vehicle, instantStatusType):
    instantStatus = vehicle.appearance.findComponentByType(instantStatusType)
    if instantStatus is None:
        vehicle.appearance.createComponent(instantStatusType)
    else:
        instantStatus.addNextDone()
    return


def invokeShotsDoneStatus(vehicle):
    invokeInstantStatusForVehicle(vehicle, InstantStatuses.ShotsDoneComponent)
    if IS_CLIENT:
        vehicle.onDiscreteShotDone()
