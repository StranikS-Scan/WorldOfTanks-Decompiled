# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: museum_of_glory/scripts/client/museum_of_glory_account_settings.py
from account_helpers import AccountSettings
from museum_of_glory.museum_of_glory_constants import ACCOUNT_DEFAULT_SETTINGS, MUSEUM_OF_GLORY

def getMuseumOfGlorySetting(name):
    return AccountSettings.getSettings(MUSEUM_OF_GLORY).get(name, ACCOUNT_DEFAULT_SETTINGS[MUSEUM_OF_GLORY][name])


def setMuseumOfGlorySettings(name, value):
    settings = AccountSettings.getSettings(MUSEUM_OF_GLORY)
    settings[name] = value
    AccountSettings.setSettings(MUSEUM_OF_GLORY, settings)
