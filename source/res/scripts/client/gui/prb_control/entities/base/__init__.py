# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/__init__.py
from adisp import process
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
