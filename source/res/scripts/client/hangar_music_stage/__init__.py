# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_music_stage/__init__.py
from skeletons.hangar_music_stage import IMusicStageCameraObjectsManager, IOffspringConcertManager

def getHangarMusicStageServicesConfig(manager):
    from camera_objects_manager import MusicStageCameraObjectsManager
    cameraObjMgr = MusicStageCameraObjectsManager()
    cameraObjMgr.init()
    manager.addInstance(IMusicStageCameraObjectsManager, cameraObjMgr, finalizer='fini')
    from offspring_concert_manager import OffspringConcertManager
    concertMgr = OffspringConcertManager()
    manager.addInstance(IOffspringConcertManager, concertMgr, finalizer='fini')
