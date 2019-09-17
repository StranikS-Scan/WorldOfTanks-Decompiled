# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/hangar_music_stage/sounds.py
import WWISE
from shared_utils import CONST_CONTAINER

class TheOffspringSound(CONST_CONTAINER):
    THE_OFFSPRING_CONCERT_STATE = 'STATE_off_concert'
    THE_OFFSPRING_CONCERT_STATE_ENTER = 'STATE_off_concert_in'
    THE_OFFSPRING_CONCERT_STATE_EXIT = 'STATE_off_concert_out'
    THE_OFFSPRING_CONCERT_EVENT_ENTER = 'ev_fest_concert_enter'
    THE_OFFSPRING_CONCERT_EVENT_EXIT = 'ev_fest_concert_exit'
    THE_OFFSPRING_CONCERT_EVENT_STOP_SONG = 'ev_fest_concert_stop_song'


def setSoundState(groupName, stateName):
    if not groupName:
        return
    if not stateName:
        return
    WWISE.WW_setState(groupName, stateName)


def raiseSoundEvent(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)


def setRTPC(name, value):
    if name and value is not None:
        WWISE.WW_setRTCPGlobal(name, value)
    return
