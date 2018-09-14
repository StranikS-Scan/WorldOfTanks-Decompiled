# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/stipple_manager.py
from functools import partial
import BigWorld
_VEHICLE_DISAPPEAR_TIME = 0.2
_VEHICLE_APPEAR_TIME = 0.2

class StippleManager:

    def __init__(self):
        self.__stippleDescs = {}
        self.__stippleToAddDescs = {}

    def showFor(self, vehicle, model):
        if not model.stipple:
            model.stipple = True
            callbackID = BigWorld.callback(0.0, partial(self.__addStippleModel, vehicle.id))
            self.__stippleToAddDescs[vehicle.id] = (model, callbackID)

    def hideIfExistFor(self, vehicle):
        desc = self.__stippleDescs.get(vehicle.id)
        if desc is not None:
            BigWorld.cancelCallback(desc[1])
            BigWorld.player().delModel(desc[0])
            desc[0].reset()
            del self.__stippleDescs[vehicle.id]
        desc = self.__stippleToAddDescs.get(vehicle.id)
        if desc is not None:
            BigWorld.cancelCallback(desc[1])
            del self.__stippleToAddDescs[vehicle.id]
        return

    def destroy(self):
        for model, callbackID in self.__stippleDescs.itervalues():
            BigWorld.cancelCallback(callbackID)
            model.reset()
            BigWorld.player().delModel(model)

        for model, callbackID in self.__stippleToAddDescs.itervalues():
            model.reset()
            BigWorld.cancelCallback(callbackID)

        self.__stippleDescs = None
        self.__stippleToAddDescs = None
        return

    def __addStippleModel(self, vehID):
        model = self.__stippleToAddDescs[vehID][0]
        if False:
            callbackID = BigWorld.callback(0.0, partial(self.__addStippleModel, vehID))
            self.__stippleToAddDescs[vehID] = (model, callbackID)
            return
        del self.__stippleToAddDescs[vehID]
        BigWorld.player().addModel(model)
        callbackID = BigWorld.callback(_VEHICLE_DISAPPEAR_TIME, partial(self.__removeStippleModel, vehID))
        self.__stippleDescs[vehID] = (model, callbackID)

    def __removeStippleModel(self, vehID):
        model = self.__stippleDescs[vehID][0]
        BigWorld.player().delModel(model)
        model.reset()
        del self.__stippleDescs[vehID]
