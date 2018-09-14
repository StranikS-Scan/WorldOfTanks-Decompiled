# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/mixins/HasVehicleList.py
from collections import namedtuple
from gui import nationCompareByIndex
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class HasVehiclesList(object):
    VehicleData = namedtuple('VehicleData', 'name nation level type icon')
    itemsCache = dependency.descriptor(IItemsCache)

    def getVehiclesData(self):
        result = []
        for vCD in self._getVehiclesDescrsList():
            vehicle = self.itemsCache.items.getItemByCD(vCD)
            result.append(self.VehicleData(vehicle.userName, vehicle.nationID, vehicle.level, vehicle.type, vehicle.iconSmall))

        return map(lambda i: i._asdict(), sorted(result, self.__sortFunc))

    def getVehiclesListTitle(self):
        pass

    def _getVehiclesDescrsList(self):
        raise NotImplemented

    def hasVehiclesList(self):
        return True

    @classmethod
    def __sortFunc(cls, i1, i2):
        res = i1.level - i2.level
        return res if res else nationCompareByIndex(i1.nation, i2.nation)
