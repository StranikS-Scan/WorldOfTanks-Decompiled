# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_wrappers.py
import operator
import typing
from functools import wraps
import BigWorld
import BattleReplay
if typing.TYPE_CHECKING:
    from Avatar import PlayerAvatar

def ifAppearanceReady(method):

    @wraps(method)
    def wrapper(vehicleComponent, *args, **kwargs):
        if vehicleComponent.isAppearanceReady():
            method(vehicleComponent, *args, **kwargs)

    return wrapper


def ifPlayerVehicle(method):

    @wraps(method)
    def wrapper(vehicleComponent, *args, **kwargs):
        player = BigWorld.player()
        if vehicleComponent.isPlayerVehicle(player):
            method(vehicleComponent, player, *args, **kwargs)

    return wrapper


def ifObservedVehicle(method):

    @wraps(method)
    def wrapper(vehicleComponent, *args, **kwargs):
        player = BigWorld.player()
        vehicle = None if player is None else player.getVehicleAttached()
        if vehicleComponent.isObservedVehicle(player, vehicle):
            method(vehicleComponent, player, vehicle, *args, **kwargs)
        return

    return wrapper


def checkStateStatus(states=(), defReturn=None, abortAction=None):

    def decorator(method):

        @wraps(method)
        def wrapper(controller, *args, **kwargs):
            stateStatus = controller.stateStatus
            if stateStatus is not None and stateStatus.state in states:
                return method(controller, stateStatus, *args, **kwargs)
            else:
                return operator.methodcaller(abortAction)(controller) if abortAction is not None else defReturn

        return wrapper

    return decorator


def skipOnRewind(defReturn=None):

    def decorator(method):

        @wraps(method)
        def wrapper(*args, **kwargs):
            return method(*args, **kwargs) if not (BattleReplay.isPlaying() and BattleReplay.g_replayCtrl.isTimeWarpInProgress) else defReturn

        return wrapper

    return decorator
