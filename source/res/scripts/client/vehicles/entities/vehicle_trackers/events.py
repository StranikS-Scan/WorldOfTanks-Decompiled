# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/entities/vehicle_trackers/events.py
from __future__ import absolute_import
import typing
import weakref
import BigWorld
from constants import UNKNOWN_VEHICLE_ID
from events_handler import eventHandler
from events_containers.common.containers import ClientEventsContainer, ContainersListener
from PlayerEvents import g_playerEvents
from vehicles.entities.vehicle_events import IVehicleEventsListenerLogic
from vehicles.entities.vehicle_trackers.interfaces import IVehicleEntityTrackerLogic
if typing.TYPE_CHECKING:
    from vehicles.entities.vehicle_trackers.interfaces import IVehicleEntityTrackerListener
    from Vehicle import Vehicle

class VehicleEntityTracker(ClientEventsContainer, ContainersListener, IVehicleEntityTrackerLogic, IVehicleEventsListenerLogic):

    def __init__(self, vehicleID):
        super(VehicleEntityTracker, self).__init__()
        self.__vehicleID = vehicleID
        self.__isTracking = False
        self.__vehicleRef = None
        self.onVehicleEntityCatching = self._createLateEvent(self.__lateVehicleEntityHandler)
        self.onVehicleEntityReleasing = self._createEvent()
        return

    def __repr__(self):
        return 'VehicleEntityTracker({}, {})'.format(self.__vehicleID, self.trackedVehicle)

    @property
    def trackedVehicle(self):
        return self.__vehicleRef() if self.__vehicleRef is not None else None

    def destroy(self):
        self.stopTracking()
        self.__vehicleID = UNKNOWN_VEHICLE_ID
        super(VehicleEntityTracker, self).destroy()

    def lateSubscribe(self, listener):
        self.__lateVehicleEntityHandler(listener.onVehicleEntityCatching)
        super(VehicleEntityTracker, self).lateSubscribe(listener)

    def unsubscribe(self, listener):
        self.__lateVehicleEntityHandler(listener.onVehicleEntityReleasing)
        super(VehicleEntityTracker, self).unsubscribe(listener)

    def startTracking(self):
        self.__isTracking = True
        self.subscribeTo(g_playerEvents)
        self.__invalidateVehicleEntity()

    def stopTracking(self):
        self.__releaseVehicleEntity()
        self.unsubscribeFrom(g_playerEvents)
        self.__isTracking = False

    def updateTracking(self, vehicleID=UNKNOWN_VEHICLE_ID, vehicle=None):
        self.__vehicleID = vehicle.id if vehicle is not None else vehicleID
        if self.__isTracking:
            self.__invalidateVehicleEntity(vehicle)
        return

    @eventHandler
    def onVehicleEntityCreated(self, vehicle):
        if self.trackedVehicle is None and vehicle.id == self.__vehicleID:
            self.__catchVehicleEntity(vehicle)
        return

    @eventHandler
    def onVehicleDestroyed(self):
        self.__releaseVehicleEntity()

    def __invalidateVehicleEntity(self, vehicle=None):
        vehicle = vehicle or BigWorld.entity(self.__vehicleID)
        if vehicle is not self.trackedVehicle:
            self.__releaseVehicleEntity()
            self.__catchVehicleEntity(vehicle)

    def __catchVehicleEntity(self, vehicle):
        if vehicle is not None:
            self.__vehicleRef = weakref.ref(vehicle)
            self.subscribeTo(vehicle.events)
            self.onVehicleEntityCatching(vehicle)
        return

    def __releaseVehicleEntity(self):
        trackedVehicle = self.trackedVehicle
        if trackedVehicle is not None:
            self.__vehicleRef = None
            self.unsubscribeFrom(trackedVehicle.events)
            self.onVehicleEntityReleasing(trackedVehicle)
        return

    def __lateVehicleEntityHandler(self, handler):
        if self.trackedVehicle is not None:
            handler(self.trackedVehicle)
        return
