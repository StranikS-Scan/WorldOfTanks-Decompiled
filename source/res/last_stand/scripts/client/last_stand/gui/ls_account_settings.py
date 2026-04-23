# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: last_stand/scripts/client/last_stand/gui/ls_account_settings.py
from __future__ import absolute_import
from copy import deepcopy
from future.utils import viewitems
from account_helpers import AccountSettings
from last_stand.gui.ls_gui_constants import DifficultyLevel, AmmoPanelSwitchPreset

class AccountSettingsKeys(object):
    EVENT_KEY = 'ls26.1_keys'
    SELECTED_LEVEL = 'selected_level'
    UNLOCK_LEVELS = 'unlock_levels'
    AWARD_UNLOCK_LEVELS = 'award_unlock_level'
    META_INTRO_VIEW_SHOWED = 'meta_into_view_showed'
    FAVORITES_VEHICLE = 'favorites'
    AMMO_PANEL_PRESET = 'ammo_preset'
    SOUND = 'sound'
    CHAT_FIRST_SEEN = 'chat_first_seen'
    STORY_POINT_VOICEOVER_MUTED = 'story_point_voiceover_muted'
    PROMO_SCREEN_SHOWED = 'promo_screen_showed'
    CAROUSEL_FILTER_DEF = 'carousel_filter_def'
    IS_EVENT_NEW = 'ls_event_is_new'
    IS_BANNER_FIRST_APPEARANCE_SEEN = 'bannerFirstAppearanceSeen'


ACCOUNT_DEFAULT_SETTINGS = {AccountSettingsKeys.EVENT_KEY: {AccountSettingsKeys.SELECTED_LEVEL: DifficultyLevel.EASY.value,
                                 AccountSettingsKeys.UNLOCK_LEVELS: {},
                                 AccountSettingsKeys.AWARD_UNLOCK_LEVELS: [],
                                 AccountSettingsKeys.META_INTRO_VIEW_SHOWED: False,
                                 AccountSettingsKeys.FAVORITES_VEHICLE: 0,
                                 AccountSettingsKeys.SOUND: {},
                                 AccountSettingsKeys.AMMO_PANEL_PRESET: AmmoPanelSwitchPreset.PRESET_1,
                                 AccountSettingsKeys.CHAT_FIRST_SEEN: False,
                                 AccountSettingsKeys.STORY_POINT_VOICEOVER_MUTED: False,
                                 AccountSettingsKeys.PROMO_SCREEN_SHOWED: False,
                                 AccountSettingsKeys.CAROUSEL_FILTER_DEF: {},
                                 AccountSettingsKeys.IS_EVENT_NEW: True,
                                 AccountSettingsKeys.IS_BANNER_FIRST_APPEARANCE_SEEN: False}}

def getSettings(name):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    value = settings.get(name, None)
    if value is None:
        value = deepcopy(AccountSettings.getSettingsDefault(AccountSettingsKeys.EVENT_KEY)[name])
    return value


def setSettings(name, value):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    settings[name] = value
    AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)


def isSoundPlayed(name, difficultyLevel):
    soundsSettings = getSettings(AccountSettingsKeys.SOUND)
    soundsByDifficultyLevel = soundsSettings.get(difficultyLevel.value)
    return name in soundsByDifficultyLevel if soundsByDifficultyLevel else False


def setSoundPlayed(name, difficultyLevel):
    soundsSettings = getSettings(AccountSettingsKeys.SOUND)
    soundsByDifficultyLevel = soundsSettings.setdefault(difficultyLevel.value, set())
    soundsByDifficultyLevel.add(name)
    setSettings(AccountSettingsKeys.SOUND, soundsSettings)


def setAwardUnlockedLevel(level):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    unlockedLevels = settings[AccountSettingsKeys.AWARD_UNLOCK_LEVELS]
    if level.value not in unlockedLevels:
        unlockedLevels.append(level.value)
        settings[AccountSettingsKeys.AWARD_UNLOCK_LEVELS] = unlockedLevels
        AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)


def setNewStatusUnlockLevel(level, status):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    unlockedLevels = settings[AccountSettingsKeys.UNLOCK_LEVELS]
    unlockedLevels[level.value] = {'isNew': status}
    settings[AccountSettingsKeys.UNLOCK_LEVELS] = unlockedLevels
    AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)


def getFirstNewStatusUnlockLevel():
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    for level, status in viewitems(settings[AccountSettingsKeys.UNLOCK_LEVELS]):
        if status.get('isNew', False):
            return level

    return None


def clearNewStatusUnlockLevel(level):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    unlockedLevels = settings[AccountSettingsKeys.UNLOCK_LEVELS]
    unlockedLevels.pop(level.value, None)
    settings[AccountSettingsKeys.UNLOCK_LEVELS] = unlockedLevels
    AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)
    return
