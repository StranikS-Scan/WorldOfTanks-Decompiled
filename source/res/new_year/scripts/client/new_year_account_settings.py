# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year_account_settings.py
from account_helpers import AccountSettings
from new_year.ny_constants import ACCOUNT_DEFAULT_SETTINGS, NEW_YEAR, NY_SHOW_NAVIGATION_BUBBLE, NY_CAN_BUY_ZONE, NY_QUESTS_UPDATED_AT, NY_IS_FIRST_MACHINE_TOKEN

def getNYSetting(name):
    return AccountSettings.getSettings(NEW_YEAR).get(name, ACCOUNT_DEFAULT_SETTINGS[NEW_YEAR][name])


def setNYSettings(name, value):
    settings = AccountSettings.getSettings(NEW_YEAR)
    settings[name] = value
    AccountSettings.setSettings(NEW_YEAR, settings)


def getQuestsUpdatedAt():
    return getNYSetting(NY_QUESTS_UPDATED_AT)


def setQuestsUpdatedAt(value):
    setNYSettings(NY_QUESTS_UPDATED_AT, value)


def getShowBubbleNavigation(widgetNavigationName):
    return getNYSetting(NY_SHOW_NAVIGATION_BUBBLE).get(widgetNavigationName)


def setShowBubbleNavigation(widgetNavigationName, value):
    settings = getNYSetting(NY_SHOW_NAVIGATION_BUBBLE)
    settings[widgetNavigationName] = value
    setNYSettings(NY_SHOW_NAVIGATION_BUBBLE, settings)


def getCanBuyCustomizationZone(customizationZone):
    return getNYSetting(NY_CAN_BUY_ZONE).get(customizationZone)


def setCanBuyCustomizationZone(customizationZone, value):
    settings = getNYSetting(NY_CAN_BUY_ZONE)
    settings[customizationZone] = value
    setNYSettings(NY_CAN_BUY_ZONE, settings)


def getIsFirstMachineToken():
    return getNYSetting(NY_IS_FIRST_MACHINE_TOKEN)


def setIsFirstMachineToken(value):
    setNYSettings(NY_IS_FIRST_MACHINE_TOKEN, value)
