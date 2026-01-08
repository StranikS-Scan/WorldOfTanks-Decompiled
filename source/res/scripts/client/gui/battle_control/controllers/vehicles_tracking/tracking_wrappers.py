# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/vehicles_tracking/tracking_wrappers.py
from __future__ import absolute_import
import operator
import typing
from functools import wraps
if typing.TYPE_CHECKING:
    from gui.battle_control.controllers.vehicles_tracking.tracking_interfaces import IVehiclesTrackingWatcher

def hasVehiclesTrackingCtrl(ctrlName='vehiclesTrackingCtrl', defReturn=None, abortAction=None):

    def decorator(method):

        @wraps(method)
        def wrapper(vehiclesTrackingWatcher, *args, **kwargs):
            trackingCtrl = vehiclesTrackingWatcher.getVehiclesTrackingCtrl()
            if trackingCtrl is not None:
                kwargs[ctrlName] = trackingCtrl
                return method(vehiclesTrackingWatcher, *args, **kwargs)
            else:
                return operator.methodcaller(abortAction)(vehiclesTrackingWatcher) if abortAction is not None else defReturn

        return wrapper

    return decorator
