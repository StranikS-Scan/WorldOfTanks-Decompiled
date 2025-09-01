# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicle_passenger/passenger_wrappers.py
import operator
import typing
from functools import wraps
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicle_passenger.passenger_interfaces import IVehiclePassengerWatcher

def hasVehiclePassengerCtrl(ctrlName='passengerCtrl', defReturn=None, abortAction=None):

    def decorator(method):

        @wraps(method)
        def wrapper(passengerInfoWatcher, *args, **kwargs):
            passengerCtrl = passengerInfoWatcher.getVehiclePassengerCtrl()
            if passengerCtrl is not None:
                kwargs[ctrlName] = passengerCtrl
                return method(passengerInfoWatcher, *args, **kwargs)
            else:
                return operator.methodcaller(abortAction)(passengerInfoWatcher) if abortAction is not None else defReturn

        return wrapper

    return decorator
