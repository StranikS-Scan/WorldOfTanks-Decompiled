# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/instant_status_helpers.py


def invokeInstantStatusForVehicle(vehicle, instantStatusType):
    instantStatus = vehicle.appearance.findComponentByType(instantStatusType)
    if instantStatus is None:
        vehicle.appearance.createComponent(instantStatusType)
    else:
        instantStatus.addNextDone()
    return
