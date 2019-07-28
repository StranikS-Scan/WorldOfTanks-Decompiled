# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/skeletons/gui/event_hangar_sound_controller.py


class IEventHangarSoundController(object):

    def init(self):
        raise NotImplementedError

    def start(self):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError

    def reset(self, forcedSoundId=None):
        raise NotImplementedError

    def fini(self):
        raise NotImplementedError
