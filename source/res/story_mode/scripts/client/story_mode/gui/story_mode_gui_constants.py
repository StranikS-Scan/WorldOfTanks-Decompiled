# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/story_mode_gui_constants.py
from constants_utils import ConstInjector
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
    STORY_MODE_SETTINGS_WINDOW = 'storyModeSettingsWindow'
    STORY_MODE_INTRO_VIDEO_WINDOW = 'storyModeIntroVideoWindow'


IS_ONBOARDING_SEAMLESS_MISSION_CHANGING_ON = True
IS_STORY_MODE_FADE_IN_OUT_ON = True
STORY_MODE_FADE_IN_DURATION = 0.4
STORY_MODE_FADE_OUT_DURATION = 0.4
SOUND_REMAPPING = 'story_mode'
START_ONBOARDING_MUSIC = 'ob_music_start'
STOP_ONBOARDING_MUSIC = 'ob_music_stop'
POST_BATTLE_MUSIC = 'sm_lobby_pbs'
COMMON_SOUND_SPACE = 'Lobby_music_garage_story_mode'
GAMEMODE_GROUP = 'STATE_gamemode'
GAMEMODE_STATE = 'STATE_gamemode_story_mode'
GAMEMODE_DEFAULT = 'STATE_gamemode_default'
HANGAR_GROUP = 'STATE_hangar_place'
HANGAR_STATE = 'STATE_hangar_place_garage'
ENTER_EVENT = 'sm_lobby_enter'
EXIT_EVENT = 'sm_lobby_exit'
STORY_MODE_SOUND_SPACE = CommonSoundSpaceSettings(name=COMMON_SOUND_SPACE, entranceStates={GAMEMODE_GROUP: GAMEMODE_STATE,
 HANGAR_GROUP: HANGAR_STATE}, exitStates={GAMEMODE_GROUP: GAMEMODE_DEFAULT}, persistentSounds=(), stoppableSounds=(), priorities=(), autoStart=True, enterEvent=ENTER_EVENT, exitEvent=EXIT_EVENT)
