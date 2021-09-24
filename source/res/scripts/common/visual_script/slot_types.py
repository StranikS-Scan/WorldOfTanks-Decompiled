# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/visual_script/slot_types.py


class SLOT_TYPE(object):
    BOOL = 'Bool'
    STR = 'String'
    INT = 'Int'
    FLOAT = 'Float'
    VECTOR2 = 'Vector2'
    VECTOR3 = 'Vector3'
    VECTOR4 = 'Vector4'
    MATRIX4 = 'Matrix4'
    ANGLE = 'Angle'
    ID = 'Identifier'
    ARENA = 'Arena'
    VEHICLE = 'Vehicle'
    ENTITY = 'Entity'
    SCRIPT_OBJECT = 'ScriptObject'
    BSP_MODEL = 'BSPCollisionModel'
    GAME_OBJECT = 'GameObject'
    PATROL_NODE = 'PatrolNode'
    PVE_SPAWN_POINT = 'PVESpawnPoint'
    SPAWN_POINT = 'SpawnPoint'
    AI_ZONE_CENTER = 'AiZoneCenter'
    MARKER_POINT = 'MarkerPoint'
    AREA_TRIGGER = 'AreaTrigger'
    TRIGGER_VEHICLE_AREA = 'TriggerVehicleArea'
    CONTROL_POINT = 'ControlPoint'
    SOUND = 'Sound'
    E_MODULE_STATE = 'EModuleState'
    E_VEHICLE_DEVICE = 'EVehicleDevice'
    E_VEHICLE_TANKMAN = 'EVehicleTankman'
    E_ARENA_PERIOD = 'EArenaPeriod'
    E_FINISH_REASON = 'EFinishReason'


def arrayOf(slotType):
    return slotType + 'Array'
