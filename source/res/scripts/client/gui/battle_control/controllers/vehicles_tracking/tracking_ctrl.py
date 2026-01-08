# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicles_tracking/tracking_ctrl.py
from __future__ import absolute_import
import weakref
import typing
from future.utils import viewvalues, viewitems
from constants import UNKNOWN_VEHICLE_ID
from gui.battle_control.battle_constants import BATTLE_CTRL_ID
from gui.battle_control.controllers.vehicles_tracking.tracking_interfaces import IVehicleTrackers, IVehicleMechanicTrackers, IVehiclesTrackingController
from vehicles.entities.vehicle_trackers import createVehicleEntityTracker
from vehicles.mechanics.mechanic_trackers import createVehicleMechanicsTracker
if typing.TYPE_CHECKING:
    from events_containers.common.containers import IClientEventsContainerListener
    from gui.battle_control.controllers.vehicle_passenger import IVehiclePassengerController
    from Vehicle import Vehicle
    from vehicles.entities.vehicle_trackers import IVehicleEntityTrackerListener
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
    from vehicles.mechanics.mechanic_trackers import IVehicleMechanicsTrackerListener
_CURR_VEH_KEY = -1

class _TrackersCollection(object):

    def __init__(self):
        self._trackers = {}

    def destroy(self):
        for tracker in viewvalues(self._trackers):
            tracker.destroy()

        self._trackers.clear()

    def _addTracking(self, listener, trackerKey, trackerFactory, trackerArgs=()):
        createdTracker = None
        tracker = self._trackers.get(trackerKey)
        if tracker is None:
            self._trackers[trackerKey] = createdTracker = tracker = trackerFactory(*trackerArgs)
        listener.lateSubscribeTo(tracker)
        return createdTracker

    def _removeTracking(self, listener, trackerKey):
        tracker = self._trackers.get(trackerKey)
        if tracker is None:
            return
        else:
            tracker.unsubscribe(listener)
            if tracker.hasListeners:
                return
            self._trackers.pop(trackerKey).destroy()
            return tracker


class _VehicleTrackers(_TrackersCollection, IVehicleTrackers):

    def __init__(self):
        super(_VehicleTrackers, self).__init__()
        self.__currentVehicleID = UNKNOWN_VEHICLE_ID

    def __repr__(self):
        return 'VehicleTrackers:\n{}'.format('\n'.join(('{}: {}'.format(k, v) for k, v in sorted(viewitems(self._trackers), key=lambda item: item[0]))))

    def destroy(self):
        self.__currentVehicleID = UNKNOWN_VEHICLE_ID
        super(_VehicleTrackers, self).destroy()

    def startCurrentVehicleTracking(self, listener):
        created = self._addTracking(listener, _CURR_VEH_KEY, createVehicleEntityTracker, (self.__currentVehicleID,))
        if created is not None:
            created.startTracking()
        return

    def stopCurrentVehicleTracking(self, listener):
        self._removeTracking(listener, _CURR_VEH_KEY)

    def startVehicleTracking(self, vehicleID, listener):
        created = self._addTracking(listener, vehicleID, createVehicleEntityTracker, (vehicleID,))
        if created is not None:
            created.startTracking()
        return

    def stopVehicleTracking(self, vehicleID, listener):
        self._removeTracking(listener, vehicleID)

    def updateCurrentVehicle(self, vehicleID=UNKNOWN_VEHICLE_ID, vehicle=None):
        currentVehicleTracker = self._trackers.get(_CURR_VEH_KEY)
        if currentVehicleTracker is not None:
            currentVehicleTracker.updateTracking(vehicleID, vehicle)
        self.__currentVehicleID = vehicle.id if vehicle is not None else vehicleID
        return


class _VehicleMechanicTrackers(_TrackersCollection, IVehicleMechanicTrackers):

    def __init__(self, vehicleTrackers):
        super(_VehicleMechanicTrackers, self).__init__()
        self.__vehicleTrackers = vehicleTrackers

    def __repr__(self):
        return 'VehicleMechanicTrackers:\n{}'.format('\n'.join(('{}: {}'.format(k[0], v) for k, v in sorted(viewitems(self._trackers), key=lambda item: item[0][0]))))

    def destroy(self):
        self.__vehicleTrackers = None
        super(_VehicleMechanicTrackers, self).destroy()
        return

    def startCurrentMechanicsTracking(self, mechanics, listener):
        created = self._addTracking(listener, (_CURR_VEH_KEY, mechanics), createVehicleMechanicsTracker, (mechanics,))
        if created is not None:
            self.__vehicleTrackers.startCurrentVehicleTracking(created)
        return

    def stopCurrentMechanicsTracking(self, mechanics, listener):
        destroyed = self._removeTracking(listener, (_CURR_VEH_KEY, mechanics))
        if destroyed is not None:
            self.__vehicleTrackers.stopCurrentVehicleTracking(destroyed)
        return

    def startMechanicsTracking(self, vehicleID, mechanics, listener):
        created = self._addTracking(listener, (vehicleID, mechanics), createVehicleMechanicsTracker, (mechanics,))
        if created is not None:
            self.__vehicleTrackers.startVehicleTracking(vehicleID, created)
        return

    def stopMechanicsTracking(self, vehicleID, mechanics, listener):
        destroyed = self._removeTracking(listener, (vehicleID, mechanics))
        if destroyed is not None:
            self.__vehicleTrackers.stopVehicleTracking(vehicleID, destroyed)
        return


class VehiclesTrackingController(IVehiclesTrackingController):

    def __init__(self, vehiclePassengerCtrl):
        self.__vehiclePassengerCtrl = weakref.proxy(vehiclePassengerCtrl)
        self.__vehicleTrackers = _VehicleTrackers()
        self.__vehicleMechanicTrackers = _VehicleMechanicTrackers(self.__vehicleTrackers)

    def __repr__(self):
        return 'VehiclesTrackingController:\nEntities - {}\nComponents - {}'.format(self.vehicleTrackers, self.vehicleMechanicTrackers)

    @property
    def vehicleTrackers(self):
        return self.__vehicleTrackers

    @property
    def vehicleMechanicTrackers(self):
        return self.__vehicleMechanicTrackers

    def getControllerID(self):
        return BATTLE_CTRL_ID.VEHICLES_TRACKING_CTRL

    def startControl(self, *args):
        self.__vehiclePassengerCtrl.onVehiclePassengerUpdate += self.__onVehiclePassengerUpdate
        self.__vehicleTrackers.updateCurrentVehicle(vehicleID=self.__vehiclePassengerCtrl.currentVehicleID)

    def stopControl(self):
        self.__vehicleMechanicTrackers.destroy()
        self.__vehicleTrackers.destroy()
        self.__vehiclePassengerCtrl = None
        return

    def __onVehiclePassengerUpdate(self, vehicle):
        self.__vehicleTrackers.updateCurrentVehicle(vehicle=vehicle)
