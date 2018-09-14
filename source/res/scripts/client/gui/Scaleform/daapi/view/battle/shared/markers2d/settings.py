# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/markers2d/settings.py
from Math import Vector3
from gui.shared import EVENT_BUS_SCOPE
SCOPE = EVENT_BUS_SCOPE.BATTLE
MARKER_POSITION_ADJUSTMENT = Vector3(0.0, 12.0, 0.0)
MARKERS_MANAGER_SWF = 'vehicleMarkersManager.swf'
MARKERS_COLOR_SCHEME_PREFIX = 'vm_'

class DAMAGE_TYPE:
    FROM_UNKNOWN = 0
    FROM_ALLY = 1
    FROM_ENEMY = 2
    FROM_SQUAD = 3
    FROM_PLAYER = 4


EQUIPMENT_MARKER_TYPE = 'FortConsumablesMarker'
FLAG_MARKER_TYPE = 'FlagIndicatorUI'
FLAG_CAPTURE_MARKER_TYPE = 'CaptureIndicatorUI'

class FLAG_TYPE:
    ALLY = 'ally'
    ENEMY = 'enemy'
    NEUTRAL = 'neutral'
    REPAIR = 'repair'
    COOLDOWN = 'cooldown'


REPAIR_MARKER_TYPE = 'RepairPointIndicatorUI'
SAFE_ZONE_MARKER_TYPE = 'SafeZoneIndicatorUI'
RESOURCE_MARKER_TYPE = 'ResourcePointMarkerUI'

class RESOURCE_STATE:
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
