# Embedded file name: scripts/client/gui/shared/gui_items/dossier/achievements/abstract/mixins/HasVehicleList.py
from collections import namedtuple
from gui import nationCompareByIndex

class HasVehiclesList(object):
    VehicleData = namedtuple('VehicleData', 'name nation level type icon')

    def getVehiclesData(self):
        result = []
        for vCD in self._getVehiclesDescrsList():
            from gui.shared import g_itemsCache
            vehicle = g_itemsCache.items.getItemByCD(vCD)
            result.append(self.VehicleData(vehicle.userName, vehicle.nationID, vehicle.level, vehicle.type, vehicle.iconSmall))

        return map(lambda i: i._asdict(), sorted(result, self.__sortFunc))

    def getVehiclesListTitle(self):
        return 'vehicles'

    def _getVehiclesDescrsList(self):
        raise NotImplemented

    def hasVehiclesList(self):
        return True

    @classmethod
    def __sortFunc(cls, i1, i2):
        res = i1.level - i2.level
        if res:
            return res
        return nationCompareByIndex(i1.nation, i2.nation)
