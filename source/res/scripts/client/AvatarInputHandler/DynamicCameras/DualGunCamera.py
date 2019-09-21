# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/DualGunCamera.py
import BigWorld
from AvatarInputHandler.AimingSystems.DualGunAimingSystem import DualGunAimingSystem
from AvatarInputHandler.AimingSystems.DualGunAimingSystemRemote import DualGunAimingSystemRemote
from AvatarInputHandler.DynamicCameras.SniperCamera import SniperCamera

def getCameraAsSettingsHolder(settingsDataSec):
    return DualGunCamera(settingsDataSec)


class DualGunCamera(SniperCamera):

    def _aimingSystemClass(self):
        return DualGunAimingSystemRemote if BigWorld.player().isObserver() else DualGunAimingSystem

    def _readCfg(self, dataSec):
        super(DualGunCamera, self)._readCfg(dataSec)
        transitionTime = dataSec.readFloat('transitionTime', 0.3)
        DualGunAimingSystem.setTransitionTime(transitionTime)
        transitionDelay = dataSec.readFloat('transitionDelay', 0.0)
        DualGunAimingSystem.setTransitionDelay(transitionDelay)
