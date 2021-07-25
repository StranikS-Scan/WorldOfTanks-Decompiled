# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/data_providers.py
from gui.shared.utils import sortByFields
from helpers import dependency
import nations
from skeletons.gui.shared import IItemsCache
from gui.Scaleform.framework.entities.DAAPIDataProvider import SortableDAAPIDataProvider
from gui.shared.gui_items.Vehicle import VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED

def _getNationID(intCD):
    itemsCache = dependency.instance(IItemsCache)
    return nations.NAMES[itemsCache.items.getItemByCD(intCD).nationID]


class SimplifiedVehiclesDataProvider(SortableDAAPIDataProvider):
    itemsCache = dependency.descriptor(IItemsCache)
    __sortMapping = {'type': lambda v: VEHICLE_TABLE_TYPES_ORDER_INDICES_REVERSED[v.getType().replace('_', '-')],
     'level': lambda v: v.getLevel(),
     'name': lambda v: v.getName(),
     'hangar': lambda v: v.getIsLearnedForDetachment() << 3 | v.getVehicleSlotPriority() << 1 | v.getIsInHangar()}

    def __init__(self):
        super(SimplifiedVehiclesDataProvider, self).__init__()
        self.__vehiclesList = None
        return

    @property
    def sortedCollection(self):
        return sortByFields(self._sort, self.__vehiclesList, self.__sortingMethod)

    @property
    def collection(self):
        return self.__vehiclesList

    def emptyItem(self):
        return None

    def buildList(self, vehicleVOs):
        self.__vehiclesList = vehicleVOs

    def clear(self):
        self.__vehiclesList = []

    def fini(self):
        self.clear()
        self.destroy()

    def __sortingMethod(self, item, field):
        valueGetter = self.__sortMapping[field]
        return valueGetter(item)
