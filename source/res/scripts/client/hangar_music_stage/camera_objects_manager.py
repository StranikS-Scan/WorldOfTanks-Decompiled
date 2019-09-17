# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_music_stage/camera_objects_manager.py
from skeletons.hangar_music_stage import IMusicStageCameraObjectsManager
from music_stage_camera import MusicStageCamera

class MusicStageCameraObjectsManager(IMusicStageCameraObjectsManager):

    def __init__(self):
        super(MusicStageCameraObjectsManager, self).__init__()
        self.__cameraObjects = None
        self.__cameraTargets = None
        self.__cam = None
        return

    def init(self):
        self.__cameraObjects = {}
        self.__cameraTargets = {}
        self.__cam = MusicStageCamera()
        self.__cam.init()

    def fini(self):
        self.__cam.destroy()
        self.__cameraObjects.clear()
        self.__cameraTargets.clear()

    def addCameraDescr(self, cameraName, cameraDescr):
        self.__cameraObjects[cameraName] = cameraDescr

    def removeCameraDescr(self, cameraName):
        if cameraName in self.__cameraObjects:
            del self.__cameraObjects[cameraName]

    def addCameraTarget(self, cameraName, cameraTarget):
        self.__cameraTargets[cameraName] = cameraTarget

    def removeCameraTarget(self, cameraName):
        if cameraName in self.__cameraTargets:
            del self.__cameraTargets[cameraName]

    def switchCameraTo(self, cameraName):
        self.__cam.deactivate()
        if not cameraName:
            return
        else:
            cameraDescr = self.__getCameraDescr(cameraName)
            if cameraDescr is None:
                return
            cameraTarget = self.__getCameraTarget(cameraName)
            if cameraTarget is None:
                return
            self.__cam.activate(cameraTarget, cameraDescr)
            return

    def __getCameraDescr(self, cameraName):
        return None if cameraName not in self.__cameraObjects else self.__cameraObjects[cameraName]

    def __getCameraTarget(self, cameraName):
        return None if cameraName not in self.__cameraTargets else self.__cameraTargets[cameraName]
