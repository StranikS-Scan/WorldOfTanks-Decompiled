# Embedded file name: scripts/client/gui/prb_control/functional/decorators.py
from adisp import process
from gui.shared.utils.functions import checkAmmoLevel

def vehicleAmmoCheck(func):
    from CurrentVehicle import g_currentVehicle

    @process
    def wrapper(*args, **kwargs):
        res = yield checkAmmoLevel((g_currentVehicle.item,))
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper


def groupAmmoCheck(func):
    from gui.game_control import getFalloutCtrl

    @process
    def wrapper(*args, **kwargs):
        res = yield checkAmmoLevel(getFalloutCtrl().getSelectedVehicles())
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper
