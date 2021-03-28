# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_shadow_manager.py
import BigWorld
from aih_constants import CTRL_MODE_NAME
from cgf_obsolete_script.py_component import Component

class VehicleShadowManager(Component):

    def __init__(self, compound=None, playerTargetChangeEvent=None, cameraChangeModeEvent=None):
        super(VehicleShadowManager, self).__init__()
        self.__compoundModel = None
        self.__playerTargetChangeEvent = playerTargetChangeEvent
        self.__cameraChangeModeEvent = cameraChangeModeEvent
        self.__prevCameraMode = None
        if compound is not None:
            self.registerCompoundModel(compound)
        return

    def changePlayerTarget(self, isStatic):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None:
            self.updatePlayerTarget(vehicle.appearance.compoundModel)
        else:
            self.updatePlayerTarget(None)
        return

    def changeCameraMode(self, cameraMode, currentVehicleId=None):
        vehicle = BigWorld.player().getVehicleAttached()
        self.__prevCameraMode = cameraMode
        isValidMode = cameraMode == CTRL_MODE_NAME.VIDEO or cameraMode == CTRL_MODE_NAME.CAT
        if isValidMode:
            self.updatePlayerTarget(None)
        elif not isValidMode and vehicle is not None:
            self.updatePlayerTarget(vehicle.appearance.compoundModel)
        return

    def activate(self):
        if self.__playerTargetChangeEvent:
            self.__playerTargetChangeEvent += self.changePlayerTarget
        if self.__cameraChangeModeEvent:
            self.__cameraChangeModeEvent += self.changeCameraMode

    def deactivate(self):
        if self.__playerTargetChangeEvent:
            self.__playerTargetChangeEvent -= self.changePlayerTarget
        if self.__cameraChangeModeEvent:
            self.__cameraChangeModeEvent -= self.changeCameraMode
        if self.__compoundModel is not None:
            BigWorld.resetPlayerTargetFrom(self.__compoundModel)
        return

    def updatePlayerTarget(self, compoundModel):
        BigWorld.setPlayerTargetTo(compoundModel)

    def registerCompoundModel(self, compoundModel):
        self.__compoundModel = compoundModel
        BigWorld.registerShadowCaster(compoundModel)

    def unregisterCompoundModel(self, compoundModel):
        BigWorld.unregisterShadowCaster(compoundModel)

    def reattachCompoundModel(self, vehicle, oldCompoundModel, newCompoundModel):
        self.unregisterCompoundModel(oldCompoundModel)
        self.registerCompoundModel(newCompoundModel)
        if BigWorld.player().getVehicleAttached() is vehicle:
            self.updatePlayerTarget(newCompoundModel)

    def destroy(self):
        pass
