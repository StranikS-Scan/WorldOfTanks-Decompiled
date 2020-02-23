# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/video/video_sound_manager.py


class IVideoSoundManager(object):

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def pause(self):
        raise NotImplementedError

    def unpause(self):
        raise NotImplementedError


class DummySoundManager(object):

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        pass

    def unpause(self):
        pass
