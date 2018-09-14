# Embedded file name: scripts/client/gui/prb_control/functional/decorators.py
from adisp import process
from constants import QUEUE_TYPE
from gui.prb_control.storage import prequeue_storage_getter
from gui.shared.utils import functions

def vehicleAmmoCheck(func):
    from CurrentVehicle import g_currentVehicle

    @process
    def wrapper(*args, **kwargs):
        res = yield functions.checkAmmoLevel((g_currentVehicle.item,))
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper


class falloutQueueAmmoCheck(object):

    @prequeue_storage_getter(QUEUE_TYPE.EVENT_BATTLES)
    def storage(self):
        return None

    def __call__(self, func):

        @process
        def wrapper(*args, **kwargs):
            vehicles = self.storage.getSelectedVehicles()
            res = yield functions.checkAmmoLevel(vehicles)
            if res:
                func(*args, **kwargs)
            elif kwargs.get('callback') is not None:
                kwargs.get('callback')(False)
            return

        return wrapper
