# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/hangar_music_stage.py


class IMusicStageCameraObjectsManager(object):

    def init(self):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError

    def addCameraDescr(self, cameraName, cameraDescr):
        raise NotImplementedError

    def removeCameraDescr(self, cameraName):
        raise NotImplementedError

    def addCameraTarget(self, cameraName, cameraTarget):
        raise NotImplementedError

    def removeCameraTarget(self, cameraName):
        raise NotImplementedError

    def switchCameraTo(self, cameraName):
        raise NotImplementedError


class IOffspringConcertManager(object):

    def setConcertEntity(self, entity):
        raise NotImplementedError

    def removeConcertEntity(self):
        raise NotImplementedError

    def concertViewStart(self, view):
        raise NotImplementedError

    def concertViewDone(self):
        raise NotImplementedError

    def onSongFinished(self, songIdx):
        raise NotImplementedError

    def onSongSwitched(self, songIdx):
        raise NotImplementedError

    @property
    def trackNames(self):
        raise NotImplementedError


class IConcertEntity(object):

    def switchToIdle(self):
        raise NotImplementedError

    def switchToSong(self, songIdx):
        raise NotImplementedError


class IConcertView(object):

    def switchToSong(self, songIdx):
        raise NotImplementedError

    def onSongFinished(self, nextSongIdx):
        raise NotImplementedError
