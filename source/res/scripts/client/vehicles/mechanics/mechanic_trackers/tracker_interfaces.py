# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_trackers/tracker_interfaces.py
from __future__ import absolute_import
import typing
from events_containers.common.containers import IClientEventsContainer, IClientEventsContainerListener
from vehicles.entities.vehicle_trackers import IVehicleEntityTrackerListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic

class IVehicleMechanicsTrackerLogic(IVehicleEntityTrackerListenerLogic):
    onMechanicComponentCatching = None
    onMechanicComponentReleasing = None
    onMechanicComponentsUpdate = None

    @property
    def trackedComponents(self):
        raise NotImplementedError

    def getTrackedComponent(self, mechanic):
        raise NotImplementedError


class IVehicleMechanicsTracker(IClientEventsContainer, IVehicleMechanicsTrackerLogic):
    pass


class IVehicleMechanicsTrackerListenerLogic(object):

    def onMechanicComponentCatching(self, component):
        pass

    def onMechanicComponentReleasing(self, component):
        pass

    def onMechanicComponentsUpdate(self, components):
        pass


class IVehicleMechanicsTrackerListener(IClientEventsContainerListener, IVehicleMechanicsTrackerListenerLogic):
    pass
