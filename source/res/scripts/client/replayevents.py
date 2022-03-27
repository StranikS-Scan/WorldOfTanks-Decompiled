# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/ReplayEvents.py
import Event

class _ReplayEvents(object):

    @property
    def isPlaying(self):
        return self.__isPlaying

    @property
    def isRecording(self):
        return self.__isRecording

    def __init__(self):
        self.onTimeWarpStart = Event.Event()
        self.onTimeWarpFinish = Event.Event()
        self.onPause = Event.Event()
        self.onMuteSound = Event.Event()
        self.onWatcherNotify = Event.Event()
        self.onReplayTerminated = Event.Event()
        self.__isPlaying = False
        self.__isRecording = False

    def onRecording(self):
        self.__isRecording = True

    def onPlaying(self):
        self.__isPlaying = True


g_replayEvents = _ReplayEvents()
