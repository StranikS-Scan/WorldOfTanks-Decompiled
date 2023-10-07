# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/HWAccountSettings.py
from copy import deepcopy
from account_helpers import AccountSettings
from halloween.hw_constants import AccountSettingsKeys

def getSettings(name):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    return settings.get(name, deepcopy(AccountSettings.getSettingsDefault(AccountSettingsKeys.EVENT_KEY)[name]))


def setSettings(name, value):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    settings[name] = value
    AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)
