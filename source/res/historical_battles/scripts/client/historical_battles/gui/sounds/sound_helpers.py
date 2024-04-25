# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/historical_battles/gui/sounds/sound_helpers.py
import typing
import BigWorld
from debug_utils import LOG_WARNING
from gui.battle_control import avatar_getter
if typing.TYPE_CHECKING:
    from ArenaPhasesComponent import ArenaPhasesComponent
    from VehicleLivesComponent import VehicleLivesComponent
    from typing import Optional

def getArenaPhasesComponent():
    arenaPhasesComponent = BigWorld.player().arena.arenaInfo.dynamicComponents.get('phasesComponent')
    if not arenaPhasesComponent:
        LOG_WARNING('[May24]: ArenaPhasesComponent is missing')
        return None
    else:
        return arenaPhasesComponent


def getPlayerVehicleLivesComponent():
    playerVehicleID = avatar_getter.getPlayerVehicleID()
    vehicle = BigWorld.entities.get(playerVehicleID)
    if not vehicle:
        return None
    else:
        vehicleLivesComponent = vehicle.dynamicComponents.get('VehicleLivesComponent')
        if not vehicleLivesComponent:
            LOG_WARNING('[May24]: VehicleLivesComponent is missing')
            return None
        return vehicleLivesComponent
