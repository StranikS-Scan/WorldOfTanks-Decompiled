# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/FlameArtyCamera.py
import BigWorld
from AvatarInputHandler.DynamicCameras.ArtyCamera import ArtyCamera

def getCameraAsSettingsHolder(settingsDataSec):
    return FlameArtyCamera(settingsDataSec)


class FlameArtyCamera(ArtyCamera):

    @staticmethod
    def _createAimingSystem():
        from BigWorld import FlameArtyAimingSystemRemote, FlameArtyAimingSystem
        return FlameArtyAimingSystemRemote(BigWorld.player().getVehicleDescriptor().shot.maxDistance) if BigWorld.player().isObserver() else FlameArtyAimingSystem(BigWorld.player().getVehicleDescriptor().shot.maxDistance)

    def setMaxDistance(self, newMaxDist):
        self._aimingSystem.setMaxRadius(newMaxDist)
