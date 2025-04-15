# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/gui/story_mode_gui_constants.py
from constants_utils import ConstInjector
from gui.Scaleform.daapi.settings import views
from gui.prb_control import settings

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
    STORY_MODE_EVENT_ENTRY_POINT = 'StoryModeEventEntryPoint'
    STORY_MODE_NEWBIE_ENTRY_POINT = 'StoryModeNewbieEntryPoint'
    STORY_MODE_WEB_VIEW_TRANSPARENT = 'StoryModeWebViewTransparent'
    STORY_MODE_OUTRO_VIDEO_WINDOW = 'storyModeOutroVideoWindow'


IS_ONBOARDING_SEAMLESS_MISSION_CHANGING_ON = True
IS_STORY_MODE_FADE_IN_OUT_ON = True
STORY_MODE_FADE_IN_DURATION = 0.4
STORY_MODE_FADE_OUT_DURATION = 0.4
BONUS_ORDER = ['dossier',
 'vehicles',
 'slots',
 'bpcoin',
 'battlePassPoints',
 'crystal',
 'freeXP',
 'credits',
 'premium_plus',
 'items',
 'customizations']
INFO_PAGE_STORY_MODE = 'infoPageStoryMode'
INFO_PAGE_STORY_MODE_EVENT = 'infoPageStoryMode_event'
ABILITY_ON_COOLDOWN_ACTIVATION_ERROR_KEY = 'ability_on_cooldown'
