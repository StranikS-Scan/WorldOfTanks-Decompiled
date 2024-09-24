# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/points_of_interest_shared.py
import enum
ENEMY_VEHICLE_ID = -1
INVALID_TIMESTAMP = -1
POI_EQUIPMENT_TAG = 'poiEquipment'

@enum.unique
class PoiType(enum.IntEnum):
    ARTILLERY = 1
    RECON = 2


@enum.unique
class PoiStatus(enum.IntEnum):
    ACTIVE = 1
    CAPTURING = 2
    COOLDOWN = 3


INT_2_POI_STATUS = dict([ (int(v), v) for k, v in PoiStatus.__members__.items() ])

@enum.unique
class PoiBlockReasons(enum.IntEnum):
    DAMAGE = 1
    EQUIPMENT = 2
    OVERTURNED = 3


PoiEquipmentNamesByPoiType = {PoiType.ARTILLERY: 'poi_artillery_aoe',
 PoiType.RECON: 'poi_radar'}
PoiTypesByPoiEquipmentName = {name:poiType for poiType, name in PoiEquipmentNamesByPoiType.iteritems()}
