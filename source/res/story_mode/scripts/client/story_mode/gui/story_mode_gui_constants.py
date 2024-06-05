# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/story_mode_gui_constants.py
from constants_utils import ConstInjector
from shared_utils import CONST_CONTAINER
from gui.Scaleform.daapi.settings import views
from gui.prb_control import settings
from sound_gui_manager import CommonSoundSpaceSettings

class PREBATTLE_ACTION_NAME(settings.PREBATTLE_ACTION_NAME, ConstInjector):
    _const_type = str
    STORY_MODE = 'story_mode'


class FUNCTIONAL_FLAG(settings.FUNCTIONAL_FLAG, ConstInjector):
    STORY_MODE = 2147483648L


class SELECTOR_BATTLE_TYPES(settings.SELECTOR_BATTLE_TYPES, ConstInjector):
    _const_type = str
    STORY_MODE = 'StoryMode'


class VIEW_ALIAS(views.VIEW_ALIAS, ConstInjector):
    _const_type = str
    STORY_MODE_BATTLE_PAGE = 'StoryModeBattlePage'
    ONBOARDING_BATTLE_PAGE = 'OnboardingBattlePage'
    ONBOARDING_SETTINGS_WINDOW = 'onboardingSettingsWindow'
    STORY_MODE_INTRO_VIDEO_WINDOW = 'storyModeIntroVideoWindow'
    STORY_MODE_ENTRY_POINT = 'StoryModeEntryPoint'
    STORY_MODE_WEB_VIEW_TRANSPARENT = 'StoryModeWebViewTransparent'


IS_ONBOARDING_SEAMLESS_MISSION_CHANGING_ON = True
IS_STORY_MODE_FADE_IN_OUT_ON = True
STORY_MODE_FADE_IN_DURATION = 0.4
STORY_MODE_FADE_OUT_DURATION = 0.4
SOUND_REMAPPING = 'story_mode'
POST_BATTLE_MUSIC = 'sm_lobby_pbs'
COMMON_SOUND_SPACE = 'Lobby_music_garage_story_mode'
GAMEMODE_GROUP = 'STATE_gamemode'
GAMEMODE_STATE = 'STATE_gamemode_story_mode'
GAMEMODE_DEFAULT = 'STATE_gamemode_default'
HANGAR_GROUP = 'STATE_hangar_place'
HANGAR_STATE = 'STATE_hangar_place_garage'
POST_BATTLE_MUSIC_EVENT_WIN = 'gui_reward_v1_special'
POST_BATTLE_MUSIC_EVENT_LOSE = 'reward_tank_marathon_A122_TS_5'
CONGRATULATION_MUSIC = 'gui_reward_v1_special'
STORY_MODE_SOUND_SPACE = CommonSoundSpaceSettings(name=COMMON_SOUND_SPACE, entranceStates={GAMEMODE_GROUP: GAMEMODE_STATE,
 HANGAR_GROUP: HANGAR_STATE}, exitStates={GAMEMODE_GROUP: GAMEMODE_DEFAULT}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent='', exitEvent='')

class Ambience(CONST_CONTAINER):
    ONBOARDING_START = 'sm_lobby_enter'
    ONBOARDING_STOP = 'sm_lobby_exit'
    EVENT_START = 'sm_lobby_dday_enter'
    EVENT_STOP = 'sm_lobby_dday_exit'


class Music(CONST_CONTAINER):
    ONBOARDING_START = 'ob_music_start'
    ONBOARDING_STOP = 'ob_music_stop'
    EVENT_START = 'sm_lobby_dday_music_start'
    EVENT_STOP = 'sm_lobby_dday_music_stop'


class EventLobbySoundState(CONST_CONTAINER):
    GROUP = 'STATE_sm_lobby_dday_difficulty'
    DIFFICULTY_NORMAL = 'STATE_sm_lobby_dday_difficulty_01'
    DIFFICULTY_HARD = 'STATE_sm_lobby_dday_difficulty_02'


class EventMusicState(CONST_CONTAINER):
    GROUP = 'STATE_sm_dday_music'
    DIFFICULTY_NORMAL = 'STATE_sm_dday_music_00_lobby_easy'
    DIFFICULTY_HARD = 'STATE_sm_dday_music_00_lobby_hard'
    VIDEO = 'STATE_sm_dday_music_00_lobby_video'
    LORE = 'STATE_sm_dday_music_00_lobby_hard'
