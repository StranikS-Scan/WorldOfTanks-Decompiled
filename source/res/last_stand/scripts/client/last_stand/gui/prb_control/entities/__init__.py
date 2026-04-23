# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/prb_control/entities/__init__.py
from __future__ import absolute_import
from adisp import adisp_process
from last_stand.gui.shared import utils

def vehicleAbilitiesCheck(func):
    from CurrentVehicle import g_currentVehicle

    @adisp_process
    def wrapper(*args, **kwargs):
        res = yield utils.checkAbilities(g_currentVehicle.item)
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper


@adisp_process
def checkVehicleAbilitiesFull(vehicle, callback=None):
    result = yield utils.checkAbilities(vehicle)
    callback(result)
