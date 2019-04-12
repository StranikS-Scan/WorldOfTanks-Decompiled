# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/marathon/marathon_reward_sounds.py
import WWISE
from shared_utils import CONST_CONTAINER

class MarathonVideos(CONST_CONTAINER):
    VEHICLE = 1


def playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)


def onVideoStart(videoId, sourceID=''):
    eventName = _MarathonVideoEvents.VIDEO_START.get(videoId)
    if eventName is not None:
        if videoId in (MarathonVideos.VEHICLE,):
            eventName = eventName.format(sourceID.replace('-', '_'))
        WWISE.WW_eventGlobal(eventName)
        WWISE.WW_setState(_MarathonVideoStates.GROUP, _MarathonVideoStates.START)
    return


def onVideoDone():
    WWISE.WW_eventGlobal(_MarathonVideoEvents.VIDEO_DONE)
    WWISE.WW_setState(_MarathonVideoStates.GROUP, _MarathonVideoStates.DONE)


class _MarathonVideoEvents(CONST_CONTAINER):
    VIDEO_START = {MarathonVideos.VEHICLE: 'gui_marathon_video_tank_{}'}
    VIDEO_DONE = 'gui_marathon_video_stop'


class _MarathonVideoStates(CONST_CONTAINER):
    GROUP = 'STATE_video_overlay'
    START = 'STATE_video_overlay_on'
    DONE = 'STATE_video_overlay_off'
