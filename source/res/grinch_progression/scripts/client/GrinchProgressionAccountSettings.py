# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch_progression/scripts/client/GrinchProgressionAccountSettings.py
from account_helpers import AccountSettings
_GRINCH_PROGRESSION_KEY = 'grinch_progression_key'
PREVIOUS_POINTS_COUNT = 'previous_points_count'
IS_FIRST_ENTRY = 'is_first_entry'
ACCOUNT_DEFAULT_SETTINGS = {_GRINCH_PROGRESSION_KEY: {PREVIOUS_POINTS_COUNT: 0,
                           IS_FIRST_ENTRY: True}}

def getSettings(name):
    settings = AccountSettings.getSettings(_GRINCH_PROGRESSION_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[_GRINCH_PROGRESSION_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(_GRINCH_PROGRESSION_KEY)
    settings[name] = value
    AccountSettings.setSettings(_GRINCH_PROGRESSION_KEY, settings)
