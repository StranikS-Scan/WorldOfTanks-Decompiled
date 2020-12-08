# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_sounds.py
import logging
import WWISE
import Windowing
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager
from gui.ranked_battles.ranked_helpers.sound_manager import Sounds
from shared_utils import CONST_CONTAINER
_logger = logging.getLogger(__name__)

class LootBoxViewEvents(CONST_CONTAINER):
    ENTRY_VIEW_ENTER = 'gui_lootbox_logistic_center_ambience_on'
    ENTRY_VIEW_EXIT = 'gui_lootbox_logistic_center_ambience_off'
    BENGAL_FIRE_OFF = 'gui_lootbox_logistic_center_bengal_fire_off'
    LOGISTIC_CENTER_SWITCH = 'gui_lootbox_logistic_center_switch'
    LOGISTIC_CENTER_NEXT = 'gui_lootbox_logistic_center_boxes_next'


def playSound(eventName):
    if eventName:
        WWISE.WW_eventGlobal(eventName)


def setOverlayHangarGeneral(onState):
    if onState:
        WWISE.WW_setState(Sounds.OVERLAY_HANGAR_GENERAL, Sounds.OVERLAY_HANGAR_GENERAL_ON)
    else:
        WWISE.WW_setState(Sounds.OVERLAY_HANGAR_GENERAL, Sounds.OVERLAY_HANGAR_GENERAL_OFF)


class LootBoxVideos(CONST_CONTAINER):
    DELIVERY = 0
    VEHICLE = 1
    STYLE = 2
    OPEN_BOX = 3
    START = 4


class LootBoxVideosSpecialRewardType(CONST_CONTAINER):
    GIFT = 'gift'
    COMMON = 'common'


class LootBoxVideoStartStopHandler(object):
    __slots__ = ('__started',)

    def __init__(self):
        self.__started = False

    def onVideoStart(self, videoId, sourceID=''):
        eventName = LootBoxVideoEvents.VIDEO_START.get(videoId)
        if eventName is not None:
            if videoId in (LootBoxVideos.VEHICLE, LootBoxVideos.STYLE):
                eventName = eventName.format(sourceID.replace('-', '_'))
            elif videoId == LootBoxVideos.OPEN_BOX:
                eventName = eventName.format(sourceID)
            WWISE.WW_eventGlobal(eventName)
            WWISE.WW_setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.START)
            self.__started = True
            if not Windowing.isWindowAccessible():
                playSound(LootBoxVideoEvents.VIDEO_PAUSE)
        return

    @staticmethod
    def setVideoState(isOn):
        WWISE.WW_setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.START if isOn else _LootBoxVideoStates.DONE)

    def onVideoDone(self):
        if self.__started:
            WWISE.WW_eventGlobal(LootBoxVideoEvents.VIDEO_DONE)
            WWISE.WW_setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.DONE)
            self.__started = False

    def setIsNeedPause(self, isNeedPause):
        if isNeedPause:
            playSound(LootBoxVideoEvents.VIDEO_PAUSE)
        else:
            playSound(LootBoxVideoEvents.VIDEO_RESUME)


class PausedSoundManager(IVideoSoundManager):

    def start(self):
        pass

    def stop(self):
        pass

    def pause(self):
        playSound(LootBoxVideoEvents.VIDEO_PAUSE)

    def unpause(self):
        playSound(LootBoxVideoEvents.VIDEO_RESUME)


class LootBoxVideoEvents(CONST_CONTAINER):
    VIDEO_START = {LootBoxVideos.DELIVERY: 'gui_lootbox_video_2020_lootbox_delivery',
     LootBoxVideos.VEHICLE: 'gui_lootbox_video_2020_tank_{}',
     LootBoxVideos.STYLE: 'gui_lootbox_video_2020_3dstyle_{}',
     LootBoxVideos.OPEN_BOX: 'gui_lootbox_video_2020_open_lootbox_{}',
     LootBoxVideos.START: 'gui_lootbox_video_2020_lootbox_start'}
    VIDEO_DONE = 'gui_lootbox_video_stop'
    VIDEO_PAUSE = 'gui_lootbox_video_pause'
    VIDEO_RESUME = 'gui_lootbox_video_resume'


class _LootBoxVideoStates(CONST_CONTAINER):
    GROUP = 'STATE_video_overlay'
    START = 'STATE_video_overlay_on'
    DONE = 'STATE_video_overlay_off'
