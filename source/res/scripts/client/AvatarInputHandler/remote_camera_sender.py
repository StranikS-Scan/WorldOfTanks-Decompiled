# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/remote_camera_sender.py
import weakref
import BigWorld
from debug_utils import LOG_DEBUG_DEV
from aih_constants import CTRL_MODES
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from AvatarInputHandler.control_modes import ArcadeControlMode, SniperControlMode, DualGunControlMode
from AvatarInputHandler.control_modes import StrategicControlMode, ArtyControlMode
from AvatarInputHandler.AimingSystems.ArcadeAimingSystem import ArcadeAimingSystem
from AvatarInputHandler.AimingSystems.SniperAimingSystem import SniperAimingSystem
from AvatarInputHandler.AimingSystems.DualGunAimingSystem import DualGunAimingSystem
from AvatarInputHandler.AimingSystems.StrategicAimingSystem import StrategicAimingSystem
from AvatarInputHandler.AimingSystems.ArtyAimingSystem import ArtyAimingSystem

class RemoteCameraSender(InputHandlerCommand):

    def __init__(self, avatarInputHandler):
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__aih.onCameraChanged += self.__onCameraChanged
        from game import g_onBeforeSendEvent
        if g_onBeforeSendEvent is not None:
            g_onBeforeSendEvent += self.sendCameraData
        return

    def destroy(self):
        self.__aih.onCameraChanged -= self.__onCameraChanged
        from game import g_onBeforeSendEvent
        if g_onBeforeSendEvent is not None:
            g_onBeforeSendEvent -= self.sendCameraData
        return

    def sendCameraData(self):
        player = BigWorld.player()
        if player.isObserver() or not hasattr(player, 'numOfObservers') or player.numOfObservers == 0:
            return
        else:
            vehicle = player.getVehicleAttached()
            if vehicle is None:
                return
            ctrl = self.__aih.ctrl
            if isinstance(ctrl, ArcadeControlMode) and isinstance(ctrl.camera.aimingSystem, ArcadeAimingSystem) or isinstance(ctrl, SniperControlMode) and isinstance(ctrl.camera.aimingSystem, SniperAimingSystem) or isinstance(ctrl, ArtyControlMode) and isinstance(ctrl.camera.aimingSystem, ArtyAimingSystem) or isinstance(ctrl, DualGunControlMode) and isinstance(ctrl.camera.aimingSystem, DualGunAimingSystem) or isinstance(ctrl, StrategicControlMode) and isinstance(ctrl.camera.aimingSystem, StrategicAimingSystem):
                aimingSystem = ctrl.camera.aimingSystem
                shotPoint = aimingSystem.getShotPoint()
                zoom = aimingSystem.getZoom()
                if shotPoint is not None and zoom is not None:
                    vehicle.cell.setRemoteCamera({'time': BigWorld.serverTime(),
                     'shotPoint': shotPoint,
                     'zoom': zoom})
            return

    def __onCameraChanged(self, cameraName, currentVehicleId=None):
        player = BigWorld.player()
        if player.isObserver():
            return
        else:
            vehicle = player.vehicle if player.vehicle is not None else player.getVehicleAttached()
            if vehicle is None:
                return
            controlMode = CTRL_MODES.index(cameraName)
            LOG_DEBUG_DEV('RemoteCameraSender.__onCameraChanged(): switching to control mode', cameraName, controlMode)
            vehicle.cell.switchObserverFPVControlMode(controlMode)
            return
