# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/DualGunCamera.py
import BigWorld
from BigWorld import DualGunAimingSystem, DualGunAimingSystemRemote
from AvatarInputHandler.DynamicCameras.SniperCamera import SniperCamera

def getCameraAsSettingsHolder(settingsDataSec):
    return DualGunCamera(settingsDataSec)


class DualGunCamera(SniperCamera):

    def _aimingSystemClass(self):
        return DualGunAimingSystemRemote if BigWorld.player().isObserver() else DualGunAimingSystem

    def _readConfigs(self, dataSec):
        super(DualGunCamera, self)._readConfigs(dataSec)
        transitionTime = dataSec.readFloat('transitionTime', 0.3)
        DualGunAimingSystem.setTransitionTime(transitionTime)
