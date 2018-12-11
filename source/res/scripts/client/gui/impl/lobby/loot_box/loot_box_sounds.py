# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_sounds.py
import WWISE
from shared_utils import CONST_CONTAINER

class LootBoxViewEvents(CONST_CONTAINER):
    ENTRY_VIEW_ENTER = 'gui_lootbox_logistic_center_ambience_on'
    ENTRY_VIEW_EXIT = 'gui_lootbox_logistic_center_ambience_off'
    BENGAL_FIRE_OFF = 'gui_lootbox_logistic_center_bengal_fire_off'


def playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)


class LootBoxVideos(CONST_CONTAINER):
    NEW_BOX = 0
    VEHICLE = 1
    STYLE = 2
    OPEN_BOX = 3


def onVideoStart(videoId, sourceID=''):
    eventName = _LootBoxVideoEvents.VIDEO_START.get(videoId)
    if eventName is not None:
        if videoId in (LootBoxVideos.VEHICLE, LootBoxVideos.STYLE):
            eventName = eventName.format(sourceID.replace('-', '_'))
        elif videoId == LootBoxVideos.OPEN_BOX:
            eventName = eventName.format(sourceID)
        WWISE.WW_eventGlobal(eventName)
        WWISE.WW_setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.START)
    return


def onVideoDone():
    WWISE.WW_eventGlobal(_LootBoxVideoEvents.VIDEO_DONE)
    WWISE.WW_setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.DONE)


class _LootBoxVideoEvents(CONST_CONTAINER):
    VIDEO_START = {LootBoxVideos.NEW_BOX: 'gui_lootbox_video_01_lootbox',
     LootBoxVideos.VEHICLE: 'gui_lootbox_video_03_tank_{}',
     LootBoxVideos.STYLE: 'gui_lootbox_video_04_3dstyle_{}',
     LootBoxVideos.OPEN_BOX: 'gui_lootbox_video_02_open_lootbox_{}'}
    VIDEO_DONE = 'gui_lootbox_video_stop'


class _LootBoxVideoStates(CONST_CONTAINER):
    GROUP = 'STATE_video_overlay'
    START = 'STATE_video_overlay_on'
    DONE = 'STATE_video_overlay_off'
