# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/mechanics/mechanic_trackers/__init__.py
from __future__ import absolute_import
import typing
from vehicles.mechanics.mechanic_trackers.tracker_events import VehicleMechanicsTracker
from vehicles.mechanics.mechanic_trackers.tracker_interfaces import IVehicleMechanicsTracker, IVehicleMechanicsTrackerListener, IVehicleMechanicsTrackerListenerLogic
if typing.TYPE_CHECKING:
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
__all__ = ('IVehicleMechanicsTracker', 'IVehicleMechanicsTrackerListener', 'IVehicleMechanicsTrackerListenerLogic', 'createVehicleMechanicsTracker')

def createVehicleMechanicsTracker(trackedMechanics):
    return VehicleMechanicsTracker(trackedMechanics)
