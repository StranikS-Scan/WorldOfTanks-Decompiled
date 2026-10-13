# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/common/fort_rush_common/component_helpers.py
from __future__ import absolute_import
import typing
import BigWorld
from constants import IS_CLIENT
from fort_rush_common.fort_rush_constants import CAPTURE_POINT_INVADER_COMPONENT, FORT_RUSH_HIGHLIGHTER, SCORE_COMPONENT, VEHICLE_RESPAWN_COMPONENT
if typing.TYPE_CHECKING:
    import weakref
    from typing import Union
    from Arena import Arena
    from Vehicle import Vehicle
    from CapturePointInvaderComponent import CapturePointInvaderComponent
    from FortRushHighlighter import FortRushHighlighter
    from FortRushScoreComponent import FortRushScoreComponent
    from RespawnFrameworkVehicleComponent import RespawnFrameworkVehicleComponent

def _getArenaInfo(arena=None):
    if arena is not None:
        return arena.arenaInfo
    elif not IS_CLIENT:
        return
    from helpers import isPlayerAvatar
    player = BigWorld.player()
    if not player or not isPlayerAvatar():
        return
    else:
        return None if not player.arena or not player.arena.arenaInfo else player.arena.arenaInfo


def getScoreComponent(arena=None):
    arenaInfo = _getArenaInfo(arena)
    return None if arenaInfo is None else arenaInfo.dynamicComponents.get(SCORE_COMPONENT)


def getVehicleRespawnComponent(vehicle=None):
    return None if vehicle is None else vehicle.dynamicComponents.get(VEHICLE_RESPAWN_COMPONENT)


def getHighlighter(vehicle):
    return vehicle.dynamicComponents.get(FORT_RUSH_HIGHLIGHTER)


def getInvaderComponent(vehicle=None):
    if vehicle is None:
        return
    else:
        return None if vehicle.isDestroyed else vehicle.dynamicComponents.get(CAPTURE_POINT_INVADER_COMPONENT)
