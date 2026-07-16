# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/vehicle_systems/components/vehicle_shadow_manager.py
import BigWorld
import CGF
from aih_constants import CTRL_MODE_NAME
from cgf_script.registration import registerComponent

@registerComponent
class VehicleShadowManager(object):
    domain = CGF.Domain.ClientEditor
    userVisible = False
    vseVisible = False

    def __init__(self, compound=None, playerTargetChangeEvent=None, cameraChangeModeEvent=None):
        self.__compoundModel = None
        self.__playerTargetChangeEvent = playerTargetChangeEvent
        self.__cameraChangeModeEvent = cameraChangeModeEvent
        self.__prevCameraMode = None
        if compound is not None:
            self.registerCompoundModel(compound)
        return

    def changePlayerTarget(self, isStatic):
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None and vehicle.appearance is not None:
            self.updatePlayerTarget(vehicle.appearance.compoundModel)
        else:
            self.updatePlayerTarget(None)
        return

    def changeCameraMode(self, cameraMode, currentVehicleId=None):
        vehicle = BigWorld.player().getVehicleAttached()
        self.__prevCameraMode = cameraMode
        isValidMode = cameraMode == CTRL_MODE_NAME.VIDEO or cameraMode == CTRL_MODE_NAME.DEBUG
        if isValidMode:
            self.updatePlayerTarget(None)
        elif not isValidMode and vehicle is not None and vehicle.appearance is not None:
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


class VehicleShadowSystem(CGF.System):
    ManagerActivated = CGF.ActivateReaction(CGF.ReactRw(VehicleShadowManager))
    ManagerDeactivated = CGF.DeactivateReaction(CGF.ReactRw(VehicleShadowManager))
    Reactions = CGF.Reactions(ManagerActivated, ManagerDeactivated)

    def update(self):
        for manager in self.reaction(self.ManagerActivated):
            self.__activateManager(manager)

        for manager in self.reaction(self.ManagerDeactivated):
            self.__deactivateManager(manager)

    def __activateManager(self, manager):
        manager.activate()

    def __deactivateManager(self, manager):
        manager.deactivate()
