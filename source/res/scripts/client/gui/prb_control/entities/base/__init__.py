# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/__init__.py
from adisp import process
from gui.shared.utils import functions
from helpers import dependency

def vehicleAmmoCheck(func):
    from CurrentVehicle import g_currentVehicle
    from prebattle_vehicle import IPrebattleVehicle

    @process
    def wrapper(*args, **kwargs):
        prebattleVehicle = dependency.instance(IPrebattleVehicle)
        if prebattleVehicle.isPresent():
            item = prebattleVehicle.item
        else:
            item = g_currentVehicle.item
        res = yield functions.checkAmmoLevel((item,))
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper
