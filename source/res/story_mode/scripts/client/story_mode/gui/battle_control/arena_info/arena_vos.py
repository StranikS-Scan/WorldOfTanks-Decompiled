# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/battle_control/arena_info/arena_vos.py
import typing
from story_mode_common.story_mode_constants import VEHICLE_BUNKER_TURRET_TAG
if typing.TYPE_CHECKING:
    from gui.battle_control.arena_info.arena_vos import VehicleTypeInfoVO

def getDisplayedClassTag(vehicleType, defaultClassTag):
    return VEHICLE_BUNKER_TURRET_TAG if VEHICLE_BUNKER_TURRET_TAG in vehicleType.tags else defaultClassTag
