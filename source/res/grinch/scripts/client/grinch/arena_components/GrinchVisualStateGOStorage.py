# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/arena_components/GrinchVisualStateGOStorage.py
from arena_component_system.client_arena_component_system import ClientArenaComponent

class GrinchVisualStateGOStorage(ClientArenaComponent):

    def __init__(self, componentSystem):
        super(GrinchVisualStateGOStorage, self).__init__(componentSystem)
        self.__storedGOs = {}

    def destroy(self):
        for vehicleDict in self.__storedGOs.itervalues():
            vehicleDict.clear()

        self.__storedGOs.clear()
        super(GrinchVisualStateGOStorage, self).destroy()

    def storeGO(self, vehicleGameObjectId, componentName, go):
        if vehicleGameObjectId not in self.__storedGOs:
            self.__storedGOs[vehicleGameObjectId] = {}
        self.__storedGOs[vehicleGameObjectId][componentName] = go

    def retrieveGO(self, vehicleGameObjectId, componentName):
        vehicleComponents = self.__storedGOs.get(vehicleGameObjectId, None)
        return vehicleComponents.pop(componentName, None) if vehicleComponents else None
