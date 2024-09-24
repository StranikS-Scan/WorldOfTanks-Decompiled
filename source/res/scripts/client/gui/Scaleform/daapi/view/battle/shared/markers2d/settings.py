# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/settings.py
from enum import IntEnum
from Math import Vector3
from gui.shared import EVENT_BUS_SCOPE
SCOPE = EVENT_BUS_SCOPE.BATTLE
MARKER_POSITION_ADJUSTMENT = Vector3(0.0, 12.0, 0.0)
MARKERS_COLOR_SCHEME_PREFIX = 'vm_'

class MARKER_SYMBOL_NAME(object):
    VEHICLE_MARKER = 'VehicleMarker'
    TARGET_MARKER = 'TargetMarker'
    EQUIPMENT_MARKER = 'FortConsumablesMarker'
    LOCATION_MARKER = 'LocationMarkerUI'
    ATTENTION_MARKER = 'AttentionMarkerUI'
    SHOOTING_MARKER = 'AimMarkerUI'
    NAVIGATION_MARKER = 'NavigationMarkerUI'
    FLAG_MARKER = 'FlagMarkerUI'
    SAFE_ZONE_MARKER = 'SafeZoneIndicatorUI'
    STATIC_OBJECT_MARKER = 'StaticObjectMarker'
    TARGET_POINT_MARKER = 'TargetPointMarkerUI'
    STATIC_ARTY_MARKER = 'StaticArtyMarkerUI'
    SECTOR_BASE_TYPE = 'SectorBaseMarkerUI'
    HEADQUARTER_TYPE = 'HeadquarterMarkerUI'
    STEP_REPAIR_MARKER_TYPE = 'ResupplyMarkerUI'
    WAYPOINT_MARKER = 'SectorWaypointMarkerUI'
    SECTOR_WARNING_MARKER = 'SectorWarningMarkerUI'


class DamageType(object):
    FROM_OTHER = 0
    FROM_SQUAD = 1
    FROM_PLAYER = 2


class CommonMarkerType(IntEnum):
    NORMAL = 0
    BASE = 1
    FRONTLINE_BASE = 2
    FRONTLINE_WAYPOINT = 3
    FRONTLINE_HEADQUARTER = 4
    FRONTLINE_WARNING = 5
    LOCATION = 6
    VEHICLE = 7
    TARGET_POINT = 8
