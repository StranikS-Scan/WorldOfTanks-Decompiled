# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/arena_info/settings.py
from gui.shared.gui_items.Vehicle import VEHICLE_BATTLE_TYPES_ORDER_INDICES
from helpers import i18n
from shared_utils import BitmaskHelper
__all__ = ('CONTOUR_ICON_PATH', 'UNKNOWN_CONTOUR_ICON_PATH', 'UNKNOWN_VEHICLE_NAME', 'UNKNOWN_VEHICLE_CLASS_NAME', 'UNKNOWN_PLAYER_NAME', 'UNKNOWN_VEHICLE_LEVEL', 'UNKNOWN_VEHICLE_CLASS_ORDER', 'SQUAD_RANGE_TO_SHOW', 'VEHICLE_STATUS', 'PLAYER_STATUS', 'INVALIDATE_OP', 'makeContourIconPath', 'getOrderByVehicleClass')
CONTOUR_ICON_SF_PATH = '../maps/icons/vehicle/contour/{0}.png'
CONTOUR_ICON_RES_PATH = 'gui/maps/icons/vehicle/contour/{0}.png'
SMALL_MAP_IMAGE_SF_PATH = '../maps/icons/map/battleLoading/%s.png'
SCREEN_MAP_IMAGE_RES_PATH = 'gui/maps/icons/map/screen/%s.dds'
UNKNOWN_CONTOUR_ICON_NAME = 'unknown'
UNKNOWN_CONTOUR_ICON_SF_PATH = CONTOUR_ICON_SF_PATH.format(UNKNOWN_CONTOUR_ICON_NAME)
UNKNOWN_CONTOUR_ICON_RES_PATH = CONTOUR_ICON_RES_PATH.format(UNKNOWN_CONTOUR_ICON_NAME)
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
    INVITATIONS = 32
    POSITIONS = 64
    CONTACTS = 128


class VEHICLE_STATUS(BitmaskHelper):
    DEFAULT = 0
    IS_ALIVE = 1
    IS_READY = 2
    NOT_AVAILABLE = 4
    STOP_RESPAWN = 8


class PLAYER_STATUS(BitmaskHelper):
    DEFAULT = 0
    IS_TEAM_KILLER = 1
    IS_SQUAD_MAN = 2
    IS_SQUAD_PERSONAL = 4
    IS_PLAYER_SELECTED = 8
    IS_VOIP_DISABLED = 16
    IS_ACTION_DISABLED = 32


class INVITATION_DELIVERY_STATUS(BitmaskHelper):
    NONE = 0
    FORBIDDEN_BY_RECEIVER = 1
    FORBIDDEN_BY_SENDER = 2
    RECEIVED_FROM = 4
    RECEIVED_INACTIVE = 8
    SENT_TO = 16
    SENT_INACTIVE = 32


class PERSONAL_STATUS(BitmaskHelper):
    DEFAULT = 0
    CAN_SEND_INVITE_TO_ALLY = 1
    CAN_SEND_INVITE_TO_ENEMY = 2
    SQUAD_RESTRICTIONS = 4
    IS_VEHICLE_LEVEL_SHOWN = 8
    IS_VEHICLE_COUNTER_SHOWN = 16
    IS_COLOR_BLIND = 32
    SHOW_ALLY_INVITES = 64
    SHOW_ENEMY_INVITES = 128


class INVALIDATE_OP(BitmaskHelper):
    NONE = 0
    SORTING = 1
    VEHICLE_STATUS = 2
    VEHICLE_INFO = 4
    VEHICLE_STATS = 8
    VEHICLE_ISTATS = 16
    PLAYER_STATUS = 32
    PREBATTLE_CHANGED = 64
    INVITATION_DELIVERY_STATUS = 128


def makeVehicleIconName(vName):
    return vName.replace(':', '-')


def makeContourIconSFPath(vName):
    return CONTOUR_ICON_SF_PATH.format(makeVehicleIconName(vName))


def makeContourIconResPath(vName):
    return CONTOUR_ICON_RES_PATH.format(makeVehicleIconName(vName))


def getOrderByVehicleClass(className=None):
    if className and className in VEHICLE_BATTLE_TYPES_ORDER_INDICES:
        result = VEHICLE_BATTLE_TYPES_ORDER_INDICES[className]
    else:
        result = UNKNOWN_VEHICLE_CLASS_ORDER
    return result
