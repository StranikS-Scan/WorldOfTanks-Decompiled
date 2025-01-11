# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/grinch_progression/account_helpers/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_UI_FLAGS

class _AccountSettingsKeys(object):
    GRINCH_PROGRESSION_KEY = 'grinch_progression_keys'
    GRINCH_COMPLETED_QUESTS = 'grinch_completed_quests'
    GRINCH_PROGRESSION_HINT_STATE = 'grinch_progression_hint_state'
    GRINCH_PROGRESSION_CURRENT_HINT_STATE = 'grinch_progression_current_hint_state'
    GRINCH_CURRENT_VEHICLE = 'grinch_current_vehicle'


DEFAULT_UI_FLAGS = {_AccountSettingsKeys.GRINCH_PROGRESSION_KEY: {_AccountSettingsKeys.GRINCH_COMPLETED_QUESTS: set(),
                                               _AccountSettingsKeys.GRINCH_PROGRESSION_HINT_STATE: set(),
                                               _AccountSettingsKeys.GRINCH_PROGRESSION_CURRENT_HINT_STATE: None,
                                               _AccountSettingsKeys.GRINCH_CURRENT_VEHICLE: 0}}

def extendAccountSettings():
    AccountSettings.overrideDefaultSettings(KEY_UI_FLAGS, DEFAULT_UI_FLAGS)


def getCompletedQuests():
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    return settings.get(_AccountSettingsKeys.GRINCH_COMPLETED_QUESTS)


def setCompletedQuests(newSettings):
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    settings[_AccountSettingsKeys.GRINCH_COMPLETED_QUESTS] = newSettings
    AccountSettings.setUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY, settings)


def readHintState():
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    return settings.get(_AccountSettingsKeys.GRINCH_PROGRESSION_HINT_STATE)


def setHintState(value):
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    settings[_AccountSettingsKeys.GRINCH_PROGRESSION_HINT_STATE] = value
    AccountSettings.setUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY, settings)


def readCurrentHintState():
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    return settings.get(_AccountSettingsKeys.GRINCH_PROGRESSION_CURRENT_HINT_STATE)


def setCurrentHintState(value):
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    settings[_AccountSettingsKeys.GRINCH_PROGRESSION_CURRENT_HINT_STATE] = value
    AccountSettings.setUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY, settings)


def getCurrentVehicle():
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    return settings.get(_AccountSettingsKeys.GRINCH_CURRENT_VEHICLE)


def setCurrentVehicle(value):
    settings = AccountSettings.getUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY)
    settings[_AccountSettingsKeys.GRINCH_CURRENT_VEHICLE] = value
    AccountSettings.setUIFlag(_AccountSettingsKeys.GRINCH_PROGRESSION_KEY, settings)
