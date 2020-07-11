# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client_common/shared_utils/vehicle_utils.py
import NetworkFilters
import BigWorld

def createWheelFilters(typeDescriptor):
    wheelsScrollFilter = None
    wheelsSteeringFilter = None
    if typeDescriptor.chassis.generalWheelsAnimatorConfig is not None:
        scrollableWheelsCount = typeDescriptor.chassis.generalWheelsAnimatorConfig.getNonTrackWheelsCount()
        wheelsScrollFilter = []
        for _ in range(scrollableWheelsCount):
            wheelsScrollFilter.append(NetworkFilters.FloatLatencyDelayingFilter())
            wheelsScrollFilter[-1].input(BigWorld.time(), 0.0)

        steerableWheelsCount = typeDescriptor.chassis.generalWheelsAnimatorConfig.getSteerableWheelsCount()
        wheelsSteeringFilter = []
        for _ in range(steerableWheelsCount):
            wheelsSteeringFilter.append(NetworkFilters.FloatLatencyDelayingFilter())
            wheelsSteeringFilter[-1].input(BigWorld.time(), 0.0)

    return (wheelsScrollFilter, wheelsSteeringFilter)
