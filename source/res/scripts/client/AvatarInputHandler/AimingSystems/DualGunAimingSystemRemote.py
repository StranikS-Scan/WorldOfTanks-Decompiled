# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/AimingSystems/DualGunAimingSystemRemote.py
import BigWorld
from AvatarInputHandler.subfilters_constants import AVATAR_SUBFILTERS
from AvatarInputHandler.AimingSystems.DualGunAimingSystem import DualGunAimingSystem

class DualGunAimingSystemRemote(DualGunAimingSystem):

    def handleMovement(self, dx, dy):
        pass

    def update(self, dt):
        super(DualGunAimingSystemRemote, self).update(dt)
        player = BigWorld.player()
        shotPoint = player.remoteCamera.shotPoint
        getVector3 = getattr(player.filter, 'getVector3', None)
        if getVector3 is not None:
            shotPoint = getVector3(AVATAR_SUBFILTERS.CAMERA_SHOT_POINT, BigWorld.serverTime())
        self.focusOnPos(shotPoint)
        super(DualGunAimingSystemRemote, self).overrideZoom(float(player.remoteCamera.zoom))
        return

    def overrideZoom(self, zoom):
        return self.getZoom()

    def enable(self, *args):
        super(DualGunAimingSystemRemote, self).enable(*args)
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None:
            vehicle.filter.enableStabilisedMatrix(True)
        return

    def disable(self):
        super(DualGunAimingSystemRemote, self).disable()
        vehicle = BigWorld.player().getVehicleAttached()
        if vehicle is not None:
            vehicle.filter.enableStabilisedMatrix(False)
        return
