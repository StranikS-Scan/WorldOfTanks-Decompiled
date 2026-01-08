# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/entities/vehicle_events/__init__.py
from __future__ import absolute_import
import typing
from events_containers.common.container_wrappers import activateEventsContainer
from vehicles.entities.vehicle_events.interfaces import IVehicleEvents, IVehicleEventsListener, IVehicleEventsListenerLogic
from vehicles.entities.vehicle_events.events import VehicleEvents
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle
__all__ = ('IVehicleEvents', 'IVehicleEventsListener', 'IVehicleEventsListenerLogic', 'VehicleEvents', 'createVehicleEvents')

@activateEventsContainer()
def createVehicleEvents(vehicle, **_):
    return VehicleEvents(vehicle)
