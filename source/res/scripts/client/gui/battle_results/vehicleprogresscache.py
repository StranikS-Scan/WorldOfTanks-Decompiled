# Embedded file name: scripts/client/gui/battle_results/VehicleProgressCache.py


class VehicleProgressCache(object):

    def __init__(self):
        self.__cache = None
        return

    def init(self):
        if self.__cache is None:
            self.__cache = {}
        return

    def fini(self):
        if self.__cache is not None:
            self.__cache.clear()
            self.__cache = None
        return

    def clear(self):
        if self.__cache is not None:
            self.__cache.clear()
        return

    def getVehicleProgressList(self, arenaUniqueID):
        return self.__cache.get(arenaUniqueID, None)

    def saveVehicleProgress(self, arenaUniqueID, vehicleProgressList):
        self.__cache[arenaUniqueID] = vehicleProgressList


g_vehicleProgressCache = VehicleProgressCache()
