# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/OnlyArtyCamera.py
import BigWorld
from AvatarInputHandler.DynamicCameras.ArtyCamera import ArtyCamera

def getCameraAsSettingsHolder(settingsDataSec):
    return OnlyArtyCamera(settingsDataSec)


class OnlyArtyCamera(ArtyCamera):

    @staticmethod
    def _createAimingSystem():
        from BigWorld import OnlyArtyAimingSystemRemote, OnlyArtyAimingSystem
        return OnlyArtyAimingSystemRemote(BigWorld.player().getVehicleDescriptor().shot.maxDistance) if BigWorld.player().isObserver() else OnlyArtyAimingSystem(BigWorld.player().getVehicleDescriptor().shot.maxDistance)

    def setMaxDistance(self, newMaxDist):
        self._aimingSystem.setMaxRadius(newMaxDist)
