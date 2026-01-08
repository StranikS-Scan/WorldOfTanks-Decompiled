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

    @property
    def isTimeWarp(self):
        return self.__isTimeWarp

    @property
    def isLastWarpRewind(self):
        return self.__isLastWarpRewind

    def __init__(self):
        self.onTimeWarpStart = Event.Event()
        self.onTimeWarpFinish = Event.Event()
        self.onPause = Event.Event()
        self.onMuteSound = Event.Event()
        self.onPlaybackSpeedChanged = Event.Event()
        self.onWatcherNotify = Event.Event()
        self.onReplayTerminated = Event.Event()
        self.__isPlaying = False
        self.__isRecording = False
        self.__isTimeWarp = False
        self.__isLastWarpRewind = False

    def onRecording(self):
        self.__isRecording = True

    def onPlaying(self):
        self.__isPlaying = True

    def callOnTimeWarpStart(self, isRewind):
        self.__isTimeWarp = True
        self.__isLastWarpRewind = isRewind
        self.onTimeWarpStart()

    def callOnTimeWarpFinish(self):
        self.onTimeWarpFinish()
        self.__isTimeWarp = False


g_replayEvents = _ReplayEvents()
