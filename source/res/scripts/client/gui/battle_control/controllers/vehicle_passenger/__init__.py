# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicle_passenger/__init__.py
import typing
from gui.battle_control.controllers.vehicle_passenger.passenger_ctrl import VehiclePassengerController
from gui.battle_control.controllers.vehicle_passenger.passenger_interfaces import IVehiclePassengerController
from gui.battle_control.controllers.vehicle_passenger.passenger_mixins import VehiclePassengerInfoWatcher
from gui.battle_control.controllers.vehicle_passenger.passenger_wrappers import hasVehiclePassengerCtrl
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicle_state_ctrl import VehicleStateController
__all__ = ('IVehiclePassengerController', 'VehiclePassengerInfoWatcher', 'hasVehiclePassengerCtrl', 'createVehiclePassengerController')

def createVehiclePassengerController(vehStateCtrl):
    return VehiclePassengerController(vehStateCtrl)
