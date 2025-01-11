# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/sounds_helper/video_handler.py
import WWISE
import Windowing
from gui.impl.new_year.sounds import GuestCVideoStates, GuestCVideoEvents

class VideoStartStopHandler(object):
    _videoStates = None
    _videoSoundEvents = None
    __slots__ = ('__started', '__checkPauseOnStart')

    def __init__(self, checkPauseOnStart=True):
        self.__checkPauseOnStart = checkPauseOnStart
        self.__started = False

    def setIsNeedPause(self, isNeedPause):
        if not self.__started:
            return
        if isNeedPause:
            WWISE.WW_eventGlobal(self._videoSoundEvents.VIDEO_PAUSE)
        else:
            WWISE.WW_eventGlobal(self._videoSoundEvents.VIDEO_RESUME)

    def onVideoStartEvent(self, eventName):
        WWISE.WW_eventGlobal(eventName)
        WWISE.WW_setState(self._videoStates.GROUP, self._videoStates.START)
        self.__started = True
        if self.__checkPauseOnStart and not Windowing.isWindowAccessible():
            WWISE.WW_eventGlobal(self._videoSoundEvents.VIDEO_PAUSE)

    def onVideoDone(self):
        if self.__started:
            WWISE.WW_eventGlobal(self._videoSoundEvents.VIDEO_DONE)
            WWISE.WW_setState(self._videoStates.GROUP, self._videoStates.DONE)
            self.__started = False


class GuestVideoStartStopHandler(VideoStartStopHandler):
    _videoStates = GuestCVideoStates
    _videoSoundEvents = GuestCVideoEvents
