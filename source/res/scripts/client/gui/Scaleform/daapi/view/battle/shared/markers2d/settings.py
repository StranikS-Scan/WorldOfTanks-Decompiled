# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/settings.py
from Math import Vector3
from gui.shared import EVENT_BUS_SCOPE
SCOPE = EVENT_BUS_SCOPE.BATTLE
MARKER_POSITION_ADJUSTMENT = Vector3(0.0, 12.0, 0.0)
MARKERS_MANAGER_SWF = 'battleVehicleMarkersApp.swf'
MARKERS_COLOR_SCHEME_PREFIX = 'vm_'

class MARKER_SYMBOL_NAME(object):
    VEHICLE_MARKER = 'VehicleMarker'
    VEHICLE_MARKER_BOSS = 'VehicleMarkerBoss'
    EQUIPMENT_MARKER = 'FortConsumablesMarker'
    FLAG_MARKER = 'FlagIndicatorUI'
    FLAG_CAPTURE_MARKER = 'CaptureIndicatorUI'
    REPAIR_MARKER = 'RepairPointIndicatorUI'
    SAFE_ZONE_MARKER = 'SafeZoneIndicatorUI'
    RESOURCE_MARKER = 'ResourcePointMarkerUI'
    STATIC_OBJECT_MARKER = 'StaticObjectMarker'
    STATIC_ARTY_MARKER = 'StaticArtyMarkerUI'


class DAMAGE_TYPE(object):
    FROM_UNKNOWN = 0
    FROM_ALLY = 1
    FROM_ENEMY = 2
    FROM_SQUAD = 3
    FROM_PLAYER = 4


class FLAG_TYPE(object):
    ALLY = 'ally'
    ENEMY = 'enemy'
    NEUTRAL = 'neutral'
    REPAIR = 'repair'
    COOLDOWN = 'cooldown'


class RESOURCE_STATE(object):
    FREEZE = 'freeze'
    COOLDOWN = 'cooldown'
    READY = 'ready'
    OWN_MINING = 'ownMining'
    ENEMY_MINING = 'enemyMining'
    OWN_MINING_FROZEN = 'ownMiningFrozen'
    ENEMY_MINING_FROZEN = 'enemyMiningFrozen'
    CONFLICT = 'conflict'


CAPTURE_STATE_BY_TEAMS = {True: RESOURCE_STATE.OWN_MINING,
 False: RESOURCE_STATE.ENEMY_MINING}
CAPTURE_FROZEN_STATE_BY_TEAMS = {True: RESOURCE_STATE.OWN_MINING_FROZEN,
 False: RESOURCE_STATE.ENEMY_MINING_FROZEN}
