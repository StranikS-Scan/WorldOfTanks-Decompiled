# Embedded file name: scripts/client/gui/battle_control/arena_info/settings.py
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from helpers import i18n
from shared_utils import BitmaskHelper
CONTOUR_ICON_SF_PATH = '../maps/icons/vehicle/contour/{0}.png'
CONTOUR_ICON_RES_PATH = 'gui/maps/icons/vehicle/contour/{0}.png'
UNKNOWN_CONTOUR_ICON_SF_PATH = CONTOUR_ICON_SF_PATH.format('unknown')
UNKNOWN_CONTOUR_ICON_RES_PATH = CONTOUR_ICON_RES_PATH.format('unknown')
UNKNOWN_VEHICLE_NAME = i18n.makeString('#ingame_gui:players_panel/unknown_vehicle')
UNKNOWN_VEHICLE_CLASS_NAME = 'unknown'
UNKNOWN_PLAYER_NAME = i18n.makeString('#ingame_gui:players_panel/unknown_name')
UNKNOWN_VEHICLE_LEVEL = -1
UNKNOWN_VEHICLE_CLASS_ORDER = 100
SQUAD_RANGE_TO_SHOW = xrange(2, 4)

class ARENA_LISTENER_SCOPE(object):
    LOAD = 1
    VEHICLES = 2
    TEAMS_BASES = 4
    PERIOD = 8
    RESPAWN = 16


class VEHICLE_STATUS(BitmaskHelper):
    IS_ALIVE = 1
    IS_READY = 2
    NOT_AVAILABLE = 4


class PLAYER_STATUS(BitmaskHelper):
    DEFAULT = 0
    IS_TEAM_KILLER = 1
    IS_SQUAD_MAN = 2
    IS_MUTED = 4


class INVALIDATE_OP(BitmaskHelper):
    NONE = 0
    SORTING = 1
    VEHICLE_STATUS = 2
    VEHICLE_INFO = 4
    VEHICLE_STATS = 8
    PLAYER_STATUS = 16
    PREBATTLE_CHANGED = 32


def makeContourIconSFPath(vName):
    return CONTOUR_ICON_SF_PATH.format(vName.replace(':', '-'))


def makeContourIconResPath(vName):
    return CONTOUR_ICON_RES_PATH.format(vName.replace(':', '-'))


def getOrderByVehicleClass(className = None):
    if className and className in VEHICLE_BATTLE_TYPES_ORDER_INDICES:
        result = VEHICLE_BATTLE_TYPES_ORDER_INDICES[className]
    else:
        result = UNKNOWN_VEHICLE_CLASS_ORDER
    return result


__all__ = ('CONTOUR_ICON_PATH', 'UNKNOWN_CONTOUR_ICON_PATH', 'UNKNOWN_VEHICLE_NAME', 'UNKNOWN_VEHICLE_CLASS_NAME', 'UNKNOWN_PLAYER_NAME', 'UNKNOWN_VEHICLE_LEVEL', 'UNKNOWN_VEHICLE_CLASS_ORDER', 'SQUAD_RANGE_TO_SHOW', 'VEHICLE_STATUS', 'PLAYER_STATUS', 'INVALIDATE_OP', 'makeContourIconPath', 'getOrderByVehicleClass')
