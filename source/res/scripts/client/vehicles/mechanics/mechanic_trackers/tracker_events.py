# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_trackers/tracker_events.py
from __future__ import absolute_import
import typing
import weakref
from future.utils import viewitems, viewvalues
from events_handler import eventHandler
from events_containers.common.containers import ClientEventsContainer, ContainersListener
from events_containers.components.life_cycle import isLifeCycleComponent, IComponentLifeCycleListenerLogic
from vehicles.entities.vehicle_events import IVehicleEventsListenerLogic
from vehicles.mechanics.mechanic_constants import TRACKABLE_VEHICLE_MECHANICS
from vehicles.mechanics.mechanic_helpers import isValidMechanicComponent, getVehicleMechanicsComponents
from vehicles.mechanics.mechanic_trackers.tracker_interfaces import IVehicleMechanicsTrackerLogic
if typing.TYPE_CHECKING:
    from events_containers.components.life_cycle import ILifeCycleComponent
    from Vehicle import Vehicle
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
    from vehicles.mechanics.mechanic_trackers.tracker_interfaces import IVehicleMechanicsTrackerListener

class _TrackableComponentCriteria(object):

    def __init__(self, trackedMechanics):
        self.__trackedMechanics = trackedMechanics

    def __call__(self, component):
        isValidType = isValidMechanicComponent(component) and isLifeCycleComponent(component)
        return isValidType and component.vehicleMechanic in self.__trackedMechanics


class VehicleMechanicsTracker(ClientEventsContainer, ContainersListener, IVehicleMechanicsTrackerLogic, IVehicleEventsListenerLogic, IComponentLifeCycleListenerLogic):

    def __init__(self, trackedMechanics):
        super(VehicleMechanicsTracker, self).__init__()
        self.__trackedMechanics = frozenset(trackedMechanics or TRACKABLE_VEHICLE_MECHANICS)
        self.__trackedComponents = {}
        self.__trackable = _TrackableComponentCriteria(self.__trackedMechanics)
        self.onMechanicComponentCatching = self._createLateEvent(self.__lateMechanicComponentHandler)
        self.onMechanicComponentsUpdate = self._createLateEvent(self.__lateMechanicComponentsUpdate)
        self.onMechanicComponentReleasing = self._createEvent()

    def __repr__(self):
        return 'VehicleMechanicsTracker(\n\t{}\n)'.format('\n\t'.join(('{}: {}'.format(str(k), self.getTrackedComponent(k)) for k in self.__trackedMechanics)))

    @property
    def trackedComponents(self):
        return {mechanic:componentRef() for mechanic, componentRef in viewitems(self.__trackedComponents)}

    def getTrackedComponent(self, mechanic):
        trackedComponentRef = self.__trackedComponents.get(mechanic)
        return trackedComponentRef() if trackedComponentRef is not None else None

    def destroy(self):
        self.__releaseMechanicComponents()
        super(VehicleMechanicsTracker, self).destroy()

    def lateSubscribe(self, listener):
        self.__lateMechanicComponentHandler(listener.onMechanicComponentCatching)
        self.__lateMechanicComponentsUpdate(listener.onMechanicComponentsUpdate)
        super(VehicleMechanicsTracker, self).lateSubscribe(listener)

    def unsubscribe(self, listener):
        self.__lateMechanicComponentHandler(listener.onMechanicComponentReleasing)
        super(VehicleMechanicsTracker, self).unsubscribe(listener)

    @eventHandler
    def onDynamicComponentCreated(self, component):
        if self.__trackable(component) and self.getTrackedComponent(component.vehicleMechanic) is None:
            self.__catchMechanicComponent(component)
            self.onMechanicComponentsUpdate(self.trackedComponents)
        return

    @eventHandler
    def onComponentDestroyed(self, component):
        self.__releaseMechanicComponent(component)
        self.onMechanicComponentsUpdate(self.trackedComponents)

    @eventHandler
    def onVehicleEntityCatching(self, vehicle):
        self.subscribeTo(vehicle.events)
        self.__catchMechanicComponents(vehicle)

    @eventHandler
    def onVehicleEntityReleasing(self, vehicle):
        self.unsubscribeFrom(vehicle.events)
        self.__releaseMechanicComponents()

    def __catchMechanicComponents(self, vehicle):
        allMechanicsComponents = getVehicleMechanicsComponents(vehicle, criteria=self.__trackable)
        for trackedMechanic in (m for m in self.__trackedMechanics if m in allMechanicsComponents):
            self.__catchMechanicComponent(allMechanicsComponents[trackedMechanic])

        self.onMechanicComponentsUpdate(self.trackedComponents)

    def __releaseMechanicComponents(self):
        trackedComponents, self.__trackedComponents = self.trackedComponents, {}
        for component in filter(None, viewvalues(trackedComponents)):
            self.__releaseMechanicComponent(component)

        self.onMechanicComponentsUpdate(self.trackedComponents)
        return

    def __catchMechanicComponent(self, mechanicComponent):
        self.__trackedComponents[mechanicComponent.vehicleMechanic] = weakref.ref(mechanicComponent)
        self.subscribeTo(mechanicComponent.lifeCycleEvents)
        self.onMechanicComponentCatching(mechanicComponent)

    def __releaseMechanicComponent(self, mechanicComponent):
        self.__trackedComponents.pop(mechanicComponent.vehicleMechanic, None)
        self.unsubscribeFrom(mechanicComponent.lifeCycleEvents)
        self.onMechanicComponentReleasing(mechanicComponent)
        return

    def __lateMechanicComponentHandler(self, handler):
        for component in viewvalues(self.trackedComponents):
            handler(component)

    def __lateMechanicComponentsUpdate(self, handler):
        if self.__trackedComponents:
            handler(self.trackedComponents)
