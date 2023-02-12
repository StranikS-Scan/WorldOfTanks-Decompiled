# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/AvatarInputHandler/remote_camera_sender.py
import weakref
import BigWorld
from aih_constants import CTRL_MODES
from AvatarInputHandler.commands.input_handler_command import InputHandlerCommand
from AvatarInputHandler.control_modes import ArcadeControlMode, SniperControlMode, DualGunControlMode, StrategicControlMode, ArtyControlMode
from BigWorld import ArcadeAimingSystem, SniperAimingSystem, DualGunAimingSystem, StrategicAimingSystem, ArtyAimingSystem
from AvatarInputHandler.MapCaseMode import MapCaseControlModeBase
from system_events import g_systemEvents

class RemoteCameraSender(InputHandlerCommand):

    def __init__(self, avatarInputHandler):
        self.__aih = weakref.proxy(avatarInputHandler)
        g_systemEvents.onBeforeSend += self.__sendCameraData

    def destroy(self):
        g_systemEvents.onBeforeSend -= self.__sendCameraData

    def __sendCameraData(self):
        player = BigWorld.player()
        if player.isObserver() or not player.arena.hasObservers:
            return
        else:
            vehicle = player.getVehicleAttached()
            if vehicle is None:
                return
            ctrl = self.__aih.ctrl
            ctrlModeName = self.__aih.ctrlModeName
            aimSystem = ctrl.camera.aimingSystem
            if isinstance(ctrl, ArcadeControlMode) and isinstance(aimSystem, ArcadeAimingSystem) or isinstance(ctrl, SniperControlMode) and isinstance(aimSystem, SniperAimingSystem) or isinstance(ctrl, ArtyControlMode) and isinstance(aimSystem, ArtyAimingSystem) or isinstance(ctrl, DualGunControlMode) and isinstance(aimSystem, DualGunAimingSystem) or isinstance(ctrl, StrategicControlMode) and isinstance(aimSystem, StrategicAimingSystem) or isinstance(ctrl, MapCaseControlModeBase) and isinstance(aimSystem, ArcadeAimingSystem):
                aimingSystem = ctrl.camera.aimingSystem
                shotPoint = aimingSystem.getShotPoint()
                zoom = aimingSystem.getZoom()
                if shotPoint is not None and zoom is not None:
                    vehicle.cell.setRemoteCamera({'time': BigWorld.serverTime(),
                     'shotPoint': shotPoint,
                     'zoom': zoom,
                     'mode': CTRL_MODES.index(ctrlModeName)})
            return
