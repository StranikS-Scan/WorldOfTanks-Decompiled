# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/races_control_mode.py
from AvatarInputHandler.control_modes import ArcadeControlMode
from races_camera import RacesCamera

class RacesControlMode(ArcadeControlMode):

    def _setupCamera(self, dataSection):
        self._cam = RacesCamera(dataSection['camera'], defaultOffset=self._defaultOffset)
