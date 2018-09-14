# Embedded file name: scripts/client/AvatarInputHandler/FalloutDeathMode.py
import weakref
import GUI
import aims
import SoundGroups
import BigWorld
import Math
from control_modes import IControlMode, dumpStateEmpty, _ARCADE_CAM_PIVOT_POS
from DynamicCameras.ArcadeCamera import ArcadeCamera
from mathUtils import clamp

class FalloutDeathMode(IControlMode):
    curVehicleID = property(lambda self: self.__curVehicleID)

    def __init__(self, dataSection, avatarInputHandler):
        self.__aih = weakref.proxy(avatarInputHandler)
        self.__aim = aims.createAim('postmortem')
        self.__cam = ArcadeCamera(dataSection['camera'], self.__aim)
        self.__isEnabled = False
        self.__curVehicleID = None
        return

    def create(self):
        self.__aim.create()
        self.__cam.create(_ARCADE_CAM_PIVOT_POS, None, True)
        return

    def destroy(self):
        self.disable()
        self.__aim.destroy()
        self.__cam.destroy()
        self.__cam = None
        return

    def dumpState(self):
        return dumpStateEmpty()

    def getAim(self):
        return self.__aim

    def enable(self, **args):
        SoundGroups.g_instance.changePlayMode(0)
        self.__cam.enable(None, False, args.get('postmortemParams'))
        self.__aim.enable()
        player = BigWorld.player()
        self.__curVehicleID = player.playerVehicleID
        self.__isEnabled = True
        return

    def disable(self):
        self.__isEnabled = False
        self.__aim.disable()
        self.__cam.disable()

    def handleMouseEvent(self, dx, dy, dz):
        raise self.__isEnabled or AssertionError
        GUI.mcursor().position = self.__aim.offset()
        self.__cam.update(dx, dy, clamp(-1.0, 1.0, dz))
        return True
