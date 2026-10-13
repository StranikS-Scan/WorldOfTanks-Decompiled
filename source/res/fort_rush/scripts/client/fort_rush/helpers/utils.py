# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/helpers/utils.py
from __future__ import absolute_import
import logging
import BigWorld
import typing
from helpers import dependency
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush_common.component_helpers import getVehicleRespawnComponent
from constants import IS_CLIENT
if typing.TYPE_CHECKING:
    from typing import Optional
    from RespawnFrameworkVehicleComponent import RespawnFrameworkVehicleComponent
_logger = logging.getLogger(__name__)
if IS_CLIENT:
    from gui.battle_control import avatar_getter
else:
    avatar_getter = None

def getCurrentTeam(guiSessionProvider=None):
    if guiSessionProvider is not None:
        arenaDP = guiSessionProvider.getArenaDP()
        if arenaDP is not None:
            return arenaDP.getNumberOfTeam()
    playerTeam = avatar_getter.getPlayerTeam()
    if playerTeam is None:
        playerTeam = avatar_getter.getObserverTeam()
    return playerTeam


def mapOwnerTeamToMarkerTeam(ownerTeam, playerTeam):
    if not ownerTeam:
        return 0
    elif playerTeam is None:
        return 0
    else:
        return 1 if ownerTeam == playerTeam else 2


def retrievePlayerRespawnComponent():
    vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
    if vehicle is None:
        _logger.warning('[FORT_RUSH][RESPAWN] retrievePlayerRespawnComponent: playerVehicle is None')
        return
    else:
        respawnComponent = getVehicleRespawnComponent(vehicle)
        if respawnComponent is None:
            _logger.warning('[FORT_RUSH][RESPAWN] retrievePlayerRespawnComponent: respawnComponent is None for vehicle %s', vehicle.id)
            return
        return respawnComponent


@dependency.replace_none_kwargs(ctrl=IFortRushBattleController)
def isFREventProgressionQuest(questId, ctrl=None):
    return False if questId is None else questId.startswith(ctrl.getConfig().progressionQuestPrefix)
