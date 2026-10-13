# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: event_platform/scripts/common/event_platform_common/respawns/helpers.py
from __future__ import absolute_import
VEHICLE_RESPAWN_COMPONENT = 'VehicleRespawnComponent'

def getVehicleRespawnComponent(vehicle):
    return vehicle.dynamicComponents.get(VEHICLE_RESPAWN_COMPONENT)
