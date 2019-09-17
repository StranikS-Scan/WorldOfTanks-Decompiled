# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_music_stage/camera_mode.py
import BigWorld
from helpers import dependency
from skeletons.hangar_music_stage import IMusicStageCameraObjectsManager

class MusicStageCameraMode(object):
    _cameraObjMgr = dependency.descriptor(IMusicStageCameraObjectsManager)

    def __init__(self, initialCameraName, renderEnvironment):
        super(MusicStageCameraMode, self).__init__()
        self.__initialCameraName = initialCameraName
        self.__renderEnv = renderEnvironment
        self.__renderEnvSwitcher = None
        return

    def activate(self):
        self._cameraObjMgr.switchCameraTo(self.__initialCameraName)
        if self.__renderEnv:
            self.__renderEnvSwitcher = BigWorld.EnvironmentSwitcher(self.__renderEnv)
            self.__renderEnvSwitcher.enable(True)

    def deactivate(self):
        if self.__renderEnvSwitcher is not None:
            self.__renderEnvSwitcher.enable(False)
            self.__renderEnvSwitcher = None
        self._cameraObjMgr.switchCameraTo('')
        return

    def switchToCamera(self, cameraName):
        self._cameraObjMgr.switchCameraTo(cameraName)
