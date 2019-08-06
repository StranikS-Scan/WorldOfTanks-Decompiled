# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/festivity/festival/sounds.py
import WWISE
from shared_utils import CONST_CONTAINER

class FestivalSoundEvents(CONST_CONTAINER):
    FESTIVAL_TUTORIAL_VIDEO_GROUP = 'STATE_video_overlay'
    FESTIVAL_TUTORIAL_VIDEO_STATE_ENTER = 'STATE_video_overlay_on'
    FESTIVAL_TUTORIAL_VIDEO_STATE_EXIT = 'STATE_video_overlay_off'
    FESTIVAL_TUTORIAL_VIDEO_EVENT_NAME = 'ev_fest_hangar_token_video'


def setSoundState(groupName, stateName, eventName=None):
    playSound(eventName=eventName)
    WWISE.WW_setState(groupName, stateName)


def playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)
