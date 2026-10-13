# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: open_bundle/scripts/client/open_bundle/helpers/account_settings.py
from __future__ import absolute_import
from account_helpers import AccountSettings
from account_helpers.AccountSettings import OPEN_BUNDLE_ENTRY_POINT_SHOWN, OPEN_BUNDLE_INTRO_SHOWN, OPEN_BUNDLE_NOTIFICATIONS, OPEN_BUNDLE_REMINDER_SHOWN, OPEN_BUNDLE_START_SHOWN

def getNotificationSettings():
    defaults = AccountSettings.getNotificationDefault(OPEN_BUNDLE_NOTIFICATIONS)
    settings = AccountSettings.getNotifications(OPEN_BUNDLE_NOTIFICATIONS, defaults)
    return settings


def getIntroSettings():
    return AccountSettings.getSettings(OPEN_BUNDLE_INTRO_SHOWN)


def getEntryPointSettings():
    return AccountSettings.getSettings(OPEN_BUNDLE_ENTRY_POINT_SHOWN)


def isNotificationShown(sectionName, bundleID):
    return bundleID in getNotificationSettings().get(sectionName, set())


def setIsNotificationShown(sectionName, bundleID):
    settings = getNotificationSettings()
    settings[sectionName].add(bundleID)
    AccountSettings.setNotifications(OPEN_BUNDLE_NOTIFICATIONS, settings)


def isStartNotificationShown(bundleID):
    return isNotificationShown(OPEN_BUNDLE_START_SHOWN, bundleID)


def isReminderNotificationShown(bundleID):
    return isNotificationShown(OPEN_BUNDLE_REMINDER_SHOWN, bundleID)


def setStartNotificationShown(bundleID):
    return setIsNotificationShown(OPEN_BUNDLE_START_SHOWN, bundleID)


def setReminderNotificationShown(bundleID):
    return setIsNotificationShown(OPEN_BUNDLE_REMINDER_SHOWN, bundleID)


def isIntroShown(bundleID):
    return bundleID in getIntroSettings()


def setIntroShown(bundleID):
    settings = getIntroSettings()
    if not isIntroShown(bundleID):
        settings.add(bundleID)
        AccountSettings.setSettings(OPEN_BUNDLE_INTRO_SHOWN, settings)


def isEntryPointShown(bundleID):
    return bundleID in getEntryPointSettings()


def setEntryPointShown(bundleID):
    if not bundleID or isEntryPointShown(bundleID):
        return
    settings = getEntryPointSettings()
    settings.add(bundleID)
    AccountSettings.setSettings(OPEN_BUNDLE_ENTRY_POINT_SHOWN, settings)
