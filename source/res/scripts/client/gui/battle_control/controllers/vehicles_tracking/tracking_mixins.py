# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicles_tracking/tracking_mixins.py
from __future__ import absolute_import
import typing
from gui.battle_control.controllers.vehicles_tracking.tracking_interfaces import IVehiclesTrackingWatcher
from gui.battle_control.controllers.vehicles_tracking.tracking_wrappers import hasVehiclesTrackingCtrl
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicles_tracking.tracking_interfaces import IVehiclesTrackingController
    from vehicles.mechanics.mechanic_constants import VehicleMechanic
    from vehicles.mechanics.mechanic_trackers import IVehicleMechanicsTrackerListener

class VehiclesTrackingWatcher(IVehiclesTrackingWatcher):

    @classmethod
    def getVehiclesTrackingCtrl(cls):
        return dependency.instance(IBattleSessionProvider).shared.vehiclesTracking

    @classmethod
    @hasVehiclesTrackingCtrl()
    def startCurrentVehicleMechanicsTracking(cls, mechanics, listener, vehiclesTrackingCtrl=None):
        vehiclesTrackingCtrl.vehicleMechanicTrackers.startCurrentMechanicsTracking(mechanics, listener)

    @classmethod
    @hasVehiclesTrackingCtrl()
    def stopCurrentVehicleMechanicsTracking(cls, mechanics, listener, vehiclesTrackingCtrl=None):
        vehiclesTrackingCtrl.vehicleMechanicTrackers.stopCurrentMechanicsTracking(mechanics, listener)

    @classmethod
    @hasVehiclesTrackingCtrl()
    def startVehicleMechanicsTracking(cls, vehicleID, mechanics, listener, vehiclesTrackingCtrl=None):
        vehiclesTrackingCtrl.vehicleMechanicTrackers.startMechanicsTracking(vehicleID, mechanics, listener)

    @classmethod
    @hasVehiclesTrackingCtrl()
    def stopVehicleMechanicsTracking(cls, vehicleID, mechanics, listener, vehiclesTrackingCtrl=None):
        vehiclesTrackingCtrl.vehicleMechanicTrackers.stopMechanicsTracking(vehicleID, mechanics, listener)
