# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicles/components/component_wrappers.py
from __future__ import absolute_import
import typing
from functools import wraps
import BigWorld
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
