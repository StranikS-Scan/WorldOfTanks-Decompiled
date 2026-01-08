# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/entities/vehicle_trackers/interfaces.py
from __future__ import absolute_import
import typing
from constants import UNKNOWN_VEHICLE_ID
from events_containers.common.containers import IClientEventsContainer, IClientEventsContainerListener
if typing.TYPE_CHECKING:
    from Vehicle import Vehicle

class IVehicleEntityTrackerLogic(object):
    onVehicleEntityCatching = None
    onVehicleEntityReleasing = None

    @property
    def trackedVehicle(self):
        raise NotImplementedError

    def startTracking(self):
        raise NotImplementedError

    def stopTracking(self):
        raise NotImplementedError

    def updateTracking(self, vehicleID=UNKNOWN_VEHICLE_ID, vehicle=None):
        raise NotImplementedError


class IVehicleEntityTracker(IClientEventsContainer, IVehicleEntityTrackerLogic):
    pass


class IVehicleEntityTrackerListenerLogic(object):

    def onVehicleEntityCatching(self, vehicle):
        pass

    def onVehicleEntityReleasing(self, vehicle):
        pass


class IVehicleEntityTrackerListener(IClientEventsContainerListener, IVehicleEntityTrackerListenerLogic):
    pass
