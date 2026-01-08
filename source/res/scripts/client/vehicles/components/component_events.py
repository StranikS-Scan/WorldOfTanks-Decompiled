# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_events.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import ClientEventsContainerCGFIntegration
if typing.TYPE_CHECKING:
    from events_containers.common.containers.interfaces import IClientEventsContainer

class VehicleComponentEventsCGFIntegration(ClientEventsContainerCGFIntegration):

    def __init__(self, events, component):
        self._spaceID = component.entity.spaceID
        self._vehicleID = component.entity.id
        self._slotName = component.getVehicleSlotName()
        super(VehicleComponentEventsCGFIntegration, self).__init__(events)

    def _attachToEventsContainer(self, events):
        self.lateSubscribeTo(events)
