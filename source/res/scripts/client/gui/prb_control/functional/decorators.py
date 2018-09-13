# Embedded file name: scripts/client/gui/prb_control/functional/decorators.py
from adisp import process
from gui.shared.utils.functions import checkAmmoLevel

def vehicleAmmoCheck(func):

    @process
    def wrapper(*args, **kwargs):
        res = yield checkAmmoLevel()
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper
