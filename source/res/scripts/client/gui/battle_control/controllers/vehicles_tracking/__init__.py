# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicles_tracking/__init__.py
from __future__ import absolute_import
import typing
from gui.battle_control.controllers.vehicles_tracking.tracking_ctrl import VehiclesTrackingController
from gui.battle_control.controllers.vehicles_tracking.tracking_interfaces import IVehiclesTrackingController
from gui.battle_control.controllers.vehicles_tracking.tracking_mixins import VehiclesTrackingWatcher
from gui.battle_control.controllers.vehicles_tracking.tracking_wrappers import hasVehiclesTrackingCtrl
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicle_passenger import IVehiclePassengerController
__all__ = ('IVehiclesTrackingController', 'VehiclesTrackingWatcher', 'hasVehiclesTrackingCtrl', 'createVehiclesTrackingController')

def createVehiclesTrackingController(vehiclePassengerCtrl):
    return VehiclesTrackingController(vehiclePassengerCtrl)
