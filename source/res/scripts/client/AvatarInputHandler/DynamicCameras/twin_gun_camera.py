# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/DynamicCameras/twin_gun_camera.py
import BigWorld
from BigWorld import TwinGunAimingSystem, TwinGunAimingSystemRemote
from AvatarInputHandler.DynamicCameras.SniperCamera import SniperCamera

def getCameraAsSettingsHolder(settingsDataSec):
    return TwinGunCamera(settingsDataSec)


class TwinGunCamera(SniperCamera):

    def _aimingSystemClass(self):
        return TwinGunAimingSystemRemote if BigWorld.player().isObserver() else TwinGunAimingSystem

    def _readConfigs(self, dataSec):
        super(TwinGunCamera, self)._readConfigs(dataSec)
        transitionTime = dataSec.readFloat('transitionTime', 0.3)
        TwinGunAimingSystem.setTransitionTime(transitionTime)
