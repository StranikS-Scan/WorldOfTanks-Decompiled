# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_event/cosmic_camera.py
from AvatarInputHandler.DynamicCameras.ArcadeCamera import ArcadeCamera

class CosmicCamera(ArcadeCamera):

    @staticmethod
    def _getConfigsKey():
        return CosmicCamera.__name__
