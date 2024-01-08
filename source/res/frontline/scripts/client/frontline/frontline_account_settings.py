# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/frontline_account_settings.py
from account_helpers import AccountSettings
from frontline_common.constants import AccountSettingsKeys, ACCOUNT_DEFAULT_SETTINGS

def getSettings(name):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[AccountSettingsKeys.EVENT_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(AccountSettingsKeys.EVENT_KEY)
    settings[name] = value
    AccountSettings.setSettings(AccountSettingsKeys.EVENT_KEY, settings)


def getSkillPointsShown(seasonId):
    data = getSettings(AccountSettingsKeys.SKILL_POINTS_SHOWN)
    return data.get(seasonId, None)


def setSkillPointsShown(seasonId, pointsAmount):
    return setSettings(AccountSettingsKeys.SKILL_POINTS_SHOWN, {seasonId: pointsAmount})


def isWelcomeScreenViewed(seasonId):
    data = getSettings(AccountSettingsKeys.WELCOME_SCREEN_VIEWED)
    return data.get(seasonId, False)


def setWelcomeScreenViewed(seasonId):
    return setSettings(AccountSettingsKeys.WELCOME_SCREEN_VIEWED, {seasonId: True})
