# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/__init__.py
from adisp import adisp_process
from gui.shared.utils import functions
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext

def vehicleAmmoCheck(func):
    from CurrentVehicle import g_currentVehicle

    @adisp_process
    def wrapper(*args, **kwargs):
        res = yield functions.checkAmmoLevel((g_currentVehicle.item,))
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper


def lobbyHeaderNavigationPossibleCheck(func):

    @adisp_process
    def wrapper(*args, **kwargs):
        lobbyContext = dependency.instance(ILobbyContext)
        res = yield lobbyContext.isHeaderNavigationPossible()
        if res:
            func(*args, **kwargs)
        elif kwargs.get('callback') is not None:
            kwargs.get('callback')(False)
        return

    return wrapper


@adisp_process
def checkVehicleAmmoFull(vehicle, callback=None):
    result = yield functions.checkAmmoLevel((vehicle,))
    callback(result)
