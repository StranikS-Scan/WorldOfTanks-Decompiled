# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/fallout/__init__.py
from adisp import process
from constants import QUEUE_TYPE
from gui.prb_control.storages import prequeue_storage_getter
from gui.shared.utils import functions

class falloutQueueAmmoCheck(object):

    @prequeue_storage_getter(QUEUE_TYPE.FALLOUT)
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
