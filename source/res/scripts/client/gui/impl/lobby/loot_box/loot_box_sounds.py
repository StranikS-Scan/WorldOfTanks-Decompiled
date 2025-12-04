# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/loot_box/loot_box_sounds.py
import logging
import Windowing
import SoundGroups
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings
_logger = logging.getLogger(__name__)

class LootBoxViewEvents(CONST_CONTAINER):
    ENTRY_VIEW_ENTER = 'gui_lootbox_logistic_center_ambience_on'
    ENTRY_VIEW_EXIT = 'gui_lootbox_logistic_center_ambience_off'
    BENGAL_FIRE_OFF = 'gui_lootbox_logistic_center_bengal_fire_off'
    LOGISTIC_CENTER_SWITCH = 'gui_lootbox_logistic_center_switch'
    LOGISTIC_CENTER_NEXT = 'gui_lootbox_logistic_center_boxes_next'
    PREMIUM_MULTI_ENTER = 'gui_lootbox_reward_5_lootboxes'


class LootBoxSoundStates(CONST_CONTAINER):
    COMMON_SOUND_SPACE = 'LootBoxes'
    STATE_PLACE = 'STATE_hangar_place'
    STATE_PLACE_LOOTBOXES = 'STATE_hangar_place_lootboxes'
    STATE_PLACE_GARAGE = 'STATE_hangar_place_garage'


def playSound(eventName):
    if eventName:
        SoundGroups.g_instance.playSound2D(eventName)


class LootBoxVideos(CONST_CONTAINER):
    DELIVERY = 0
    VEHICLE = 1
    STYLE = 2
    OPEN_BOX = 3


class LootBoxVideosSpecialRewardType(CONST_CONTAINER):
    GIFT = 'gift'
    COMMON = 'common'


class LootBoxVideoStartStopHandler(object):
    __slots__ = ('__started', '__checkPauseOnStart')

    def __init__(self, checkPauseOnStart=True):
        self.__checkPauseOnStart = checkPauseOnStart
        self.__started = False

    @staticmethod
    def setVideoState(isOn):
        SoundGroups.g_instance.setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.START if isOn else _LootBoxVideoStates.DONE)

    def setIsNeedPause(self, isNeedPause):
        if not self.__started:
            return
        if isNeedPause:
            playSound(LootBoxVideoEvents.VIDEO_PAUSE)
        else:
            playSound(LootBoxVideoEvents.VIDEO_RESUME)

    def onVideoStart(self, videoId, sourceID=''):
        eventName = self.getEventName(videoId, sourceID)
        if eventName is not None:
            SoundGroups.g_instance.playSound2D(eventName)
            SoundGroups.g_instance.setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.START)
            self.__started = True
            if self.__checkPauseOnStart and not Windowing.isWindowAccessible():
                playSound(LootBoxVideoEvents.VIDEO_PAUSE)
        return

    def getEventName(self, videoId, sourceID=''):
        eventName = LootBoxVideoEvents.VIDEO_START.get(videoId)
        if eventName is not None:
            if videoId in (LootBoxVideos.VEHICLE, LootBoxVideos.STYLE):
                eventName = eventName.format(sourceID.replace('-', '_'))
            elif videoId == LootBoxVideos.OPEN_BOX:
                eventName = eventName.format(sourceID)
        return eventName

    def onVideoDone(self):
        if self.__started:
            SoundGroups.g_instance.playSound2D(LootBoxVideoEvents.VIDEO_DONE)
            SoundGroups.g_instance.setState(_LootBoxVideoStates.GROUP, _LootBoxVideoStates.DONE)
            self.__started = False


class PausedSoundManager(IVideoSoundManager):
    __slots__ = ('__isPausable', '__isOnPause')

    def __init__(self):
        self.__isPausable = self.__isOnPause = False

    def start(self):
        self.__isPausable = True

    def stop(self):
        self.__isPausable = False

    def pause(self):
        if self.__isPausable and not self.__isOnPause:
            playSound(LootBoxVideoEvents.VIDEO_PAUSE)
            self.__isOnPause = True

    def unpause(self):
        if self.__isPausable and self.__isOnPause:
            playSound(LootBoxVideoEvents.VIDEO_RESUME)
            self.__isOnPause = False


class LootBoxVideoEvents(CONST_CONTAINER):
    VIDEO_START = {LootBoxVideos.DELIVERY: 'gui_video_ny_delivery_lootbox',
     LootBoxVideos.VEHICLE: 'gui_lootbox_video_tank_{}',
     LootBoxVideos.STYLE: 'gui_lootbox_video_3dstyle_{}',
     LootBoxVideos.OPEN_BOX: 'gui_lootbox_video_open_lootbox_{}'}
    VIDEO_DONE = 'gui_lootbox_video_stop'
    VIDEO_PAUSE = 'gui_lootbox_video_pause'
    VIDEO_RESUME = 'gui_lootbox_video_resume'


class _LootBoxVideoStates(CONST_CONTAINER):
    GROUP = 'STATE_video_overlay'
    START = 'STATE_video_overlay_on'
    DONE = 'STATE_video_overlay_off'


LOOTBOXES_SOUND_SPACE = CommonSoundSpaceSettings(name=LootBoxSoundStates.COMMON_SOUND_SPACE, entranceStates={LootBoxSoundStates.STATE_PLACE: LootBoxSoundStates.STATE_PLACE_LOOTBOXES}, exitStates={LootBoxSoundStates.STATE_PLACE: LootBoxSoundStates.STATE_PLACE_GARAGE}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=LootBoxViewEvents.ENTRY_VIEW_ENTER, exitEvent=LootBoxViewEvents.ENTRY_VIEW_EXIT)
