# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBAccountSettings.py
from account_helpers import AccountSettings
from historical_battles_common.hb_constants import AccountSettingsKeys, ACCOUNT_DEFAULT_SETTINGS

def getSettings(name):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    setting = settings.get(name)
    return setting if setting is not None else ACCOUNT_DEFAULT_SETTINGS[AccountSettingsKeys.EVENT_KEY][name]


def setSettings(name, value):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    settings[name] = value
    AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)


def getNotifications(name):
    settings = AccountSettings.getNotifications(AccountSettingsKeys.EVENT_KEY)
    return settings[name]


def setNotifications(name, value):
    settings = AccountSettings.getNotifications(AccountSettingsKeys.EVENT_KEY)
    settings[name] = value
    AccountSettings.setNotifications(AccountSettingsKeys.EVENT_KEY, settings)
