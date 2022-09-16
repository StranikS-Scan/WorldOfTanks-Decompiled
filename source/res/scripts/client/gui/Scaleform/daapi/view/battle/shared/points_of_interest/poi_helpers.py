# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/points_of_interest/poi_helpers.py
import typing
import BigWorld
from items import vehicles
from points_of_interest_shared import PoiEquipmentNamesByPoiType, PoiTypesByPoiEquipmentName
if typing.TYPE_CHECKING:
    from items.artefacts import Equipment
    from points_of_interest.components import PoiStateComponent

def getPoiCooldownProgress(poiState):
    status = poiState.status
    duration = status.endTime - status.startTime
    progress = (BigWorld.serverTime() - status.startTime) / duration * 100
    return progress


def getPoiEquipmentByType(poiType):
    cache = vehicles.g_cache
    name = PoiEquipmentNamesByPoiType[poiType]
    equipmentID = cache.equipmentIDs().get(name)
    return cache.equipments()[equipmentID] if equipmentID is not None else None


def getPoiTypeByEquipment(equipment):
    return PoiTypesByPoiEquipmentName.get(equipment.name, None)
