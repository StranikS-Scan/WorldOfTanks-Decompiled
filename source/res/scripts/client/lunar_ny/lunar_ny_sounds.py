# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/lunar_ny_sounds.py
import WWISE
from shared_utils import CONST_CONTAINER
from sound_gui_manager import CommonSoundSpaceSettings
from gui.impl.lobby.video.video_sound_manager import IVideoSoundManager

class LunarNYSoundEvents(CONST_CONTAINER):
    SEND_SCREEN_ENTER = 'lny_2022_env_send_screen_enter'
    SEND_SCREEN_EXIT = 'lny_2022_env_send_screen_exit'
    ALBUM_ENTER = 'lny_2022_hangar_charms_album_enter'
    ALBUM_EXIT = 'lny_2022_hangar_charms_album_exit'
    STORAGE_ENV_ENTER = 'lny_2022_env_vault_enter'
    STORAGE_ENV_EXIT = 'lny_2022_env_vault_exit'
    NEW_ENVELOPES_RECEIVED = 'lny_2022_hangar_notify'
    LUNAR_NY_MAIN_ENTER = 'lny_2022_main_enter'
    LUNAR_NY_MAIN_EXIT = 'lny_2022_main_exit'
    VIDEO_START = 'lny_2022_hangar_intro_start'
    VIDEO_STOP = 'lny_2022_hangar_intro_stop'
    VIDEO_PAUSE = 'lny_2022_hangar_intro_pause'
    VIDEO_RESUME = 'lny_2022_hangar_intro_resume'


class LunarNYSoundStates(CONST_CONTAINER):
    SEND_ENV = 'STATE_ext_lny_hangar_2022_place_env_send'
    ALBUM = 'STATE_ext_lny_hangar_2022_place_charms_album'
    STORAGE_ENV = 'STATE_ext_lny_hangar_2022_place_env_vault'
    INFO = 'STATE_ext_lny_hangar_2022_place_infopage'
    NOT_IN_VIEW = 'STATE_ext_lny_hangar_2022_place_hangar'
    VIDEO_ON = 'STATE_video_overlay_on'
    VIDEO_OFF = 'STATE_video_overlay_off'


class LunarNYSoundStateGroups(CONST_CONTAINER):
    PLACE_GROUP = 'STATE_ext_lny_hangar_2022_place'
    VIDEO_GROUP = 'STATE_video_overlay'


class LunarNYSoundSpaces(CONST_CONTAINER):
    MAIN = 'lunar_ny_main'
    SEND_ENVELOPES = 'lunar_ny_send_envelopes'
    ALBUM = 'lunar_ny_album'
    STORAGE = 'lunar_ny_storage_env'
    INFO = 'lunar_ny_info'


LUNAR_NY_SEND_ENVELOPES_SOUND_SPACE = CommonSoundSpaceSettings(name=LunarNYSoundSpaces.SEND_ENVELOPES, entranceStates={LunarNYSoundStateGroups.PLACE_GROUP: LunarNYSoundStates.SEND_ENV}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=LunarNYSoundEvents.SEND_SCREEN_ENTER, exitEvent=LunarNYSoundEvents.SEND_SCREEN_EXIT, parentSpace='')
LUNAR_NY_ALBUM_SOUND_SPACE = CommonSoundSpaceSettings(name=LunarNYSoundSpaces.ALBUM, entranceStates={LunarNYSoundStateGroups.PLACE_GROUP: LunarNYSoundStates.ALBUM}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=LunarNYSoundEvents.ALBUM_ENTER, exitEvent=LunarNYSoundEvents.ALBUM_EXIT, parentSpace='')
LUNAR_NY_STORAGE_ENV_SOUND_SPACE = CommonSoundSpaceSettings(name=LunarNYSoundSpaces.STORAGE, entranceStates={LunarNYSoundStateGroups.PLACE_GROUP: LunarNYSoundStates.STORAGE_ENV}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=LunarNYSoundEvents.STORAGE_ENV_ENTER, exitEvent=LunarNYSoundEvents.STORAGE_ENV_EXIT, parentSpace='')
LUNAR_NY_INFO_SOUND_SPACE = CommonSoundSpaceSettings(name=LunarNYSoundSpaces.INFO, entranceStates={LunarNYSoundStateGroups.PLACE_GROUP: LunarNYSoundStates.INFO}, exitStates={}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='', parentSpace='')
LUNAR_NY_MAIN_SOUND_SPACE = CommonSoundSpaceSettings(name=LunarNYSoundSpaces.MAIN, entranceStates={}, exitStates={LunarNYSoundStateGroups.PLACE_GROUP: LunarNYSoundStates.NOT_IN_VIEW}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=LunarNYSoundEvents.LUNAR_NY_MAIN_ENTER, exitEvent=LunarNYSoundEvents.LUNAR_NY_MAIN_EXIT, parentSpace='')

class LunarNYVideoStartStopHandler(object):
    __slots__ = ('__started',)

    def __init__(self):
        self.__started = False

    def onVideoStart(self):
        WWISE.WW_eventGlobal(LunarNYSoundEvents.VIDEO_START)
        WWISE.WW_setState(LunarNYSoundStateGroups.VIDEO_GROUP, LunarNYSoundStates.VIDEO_ON)
        self.__started = True

    def onVideoDone(self):
        if self.__started:
            WWISE.WW_eventGlobal(LunarNYSoundEvents.VIDEO_STOP)
            WWISE.WW_setState(LunarNYSoundStateGroups.VIDEO_GROUP, LunarNYSoundStates.VIDEO_OFF)
            self.__started = False

    def __playSound(self, eventName):
        if eventName:
            WWISE.WW_eventGlobal(eventName)


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
            self.__playSound(LunarNYSoundEvents.VIDEO_PAUSE)
            self.__isOnPause = True

    def unpause(self):
        if self.__isPausable and self.__isOnPause:
            self.__playSound(LunarNYSoundEvents.VIDEO_RESUME)
            self.__isOnPause = False

    def __playSound(self, eventName):
        if eventName:
            WWISE.WW_eventGlobal(eventName)
