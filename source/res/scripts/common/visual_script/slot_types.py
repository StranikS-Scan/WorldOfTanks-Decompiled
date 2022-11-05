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
    RESOURCE = 'Resource'
    ANGLE = 'Angle'
    COLOR = 'Color'
    ID = 'Identifier'
    ARENA = 'Arena'
    VEHICLE = 'Vehicle'
    ENTITY = 'Entity'
    PATROL_NODE = 'PatrolNode'
    PVE_SPAWN_POINT = 'PVESpawnPoint'
    SPAWN_POINT = 'SpawnPoint'
    LOOT_BASIC = 'LootBasic'
    LOOT_ADVANCED = 'LootAdvanced'
    AI_ZONE_CENTER = 'AiZoneCenter'
    MARKER_POINT = 'MarkerPoint'
    AREA_TRIGGER = 'AreaTrigger'
    VEHICLE_ATTR_FACTOR = 'VehicleAttributeFactor'
    TRIGGER_VEHICLE_AREA = 'TriggerVehicleArea'
    CONTROL_POINT = 'ControlPoint'
    POINT_OF_INTEREST_UDO = 'PointOfInterestUDO'
    SOUND = 'Sound'
    GAME_OBJECT = 'GameObject'
    UDO = 'UDO'
    E_MODULE_STATE = 'EModuleState'
    E_VEHICLE_DEVICE = 'EVehicleDevice'
    E_VEHICLE_TANKMAN = 'EVehicleTankman'
    E_ARENA_PERIOD = 'EArenaPeriod'
    E_FINISH_REASON = 'EFinishReason'


def arrayOf(slotType):
    return slotType + 'Array'
