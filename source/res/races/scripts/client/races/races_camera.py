# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: races/scripts/client/races/races_camera.py
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera

class RacesCamera(ArcadeCamera):

    @staticmethod
    def _getConfigsKey():
        return RacesCamera.__name__
