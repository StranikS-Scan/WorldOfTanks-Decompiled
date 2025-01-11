# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/account_helpers/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS

class _AccountSettingsKeys(object):
    GRINCH_KEY = 'grinch_keys'
    GRINCH_CURRENT_VEHICLE = 'grinch_current_vehicle'
    GRINCH_CHAPTERS_START_NOTIFICATION_SHOWN = 'grinch_chapters_start_notification_shown'
    GRINCH_CHAPTERS_END_NOTIFICATION_SHOWN = 'grinch_chapters_end_notification_shown'
    GRINCH_FINISHED_NOTIFICATION_SHOWN = 'grinch_finished_notification_shown'


ACCOUNT_DEFAULT_SETTINGS = {_AccountSettingsKeys.GRINCH_KEY: {_AccountSettingsKeys.GRINCH_CURRENT_VEHICLE: 0,
                                   _AccountSettingsKeys.GRINCH_CHAPTERS_START_NOTIFICATION_SHOWN: set(),
                                   _AccountSettingsKeys.GRINCH_CHAPTERS_END_NOTIFICATION_SHOWN: set(),
                                   _AccountSettingsKeys.GRINCH_FINISHED_NOTIFICATION_SHOWN: False}}

def extendAccountSettings():
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)


def getSettings(name):
    settings = AccountSettings.getSettings(_AccountSettingsKeys.GRINCH_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[_AccountSettingsKeys.GRINCH_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(_AccountSettingsKeys.GRINCH_KEY)
    settings[name] = value
    AccountSettings.setSettings(_AccountSettingsKeys.GRINCH_KEY, settings)


def saveCurrentGrinchVehicle(vehID):
    setSettings(_AccountSettingsKeys.GRINCH_CURRENT_VEHICLE, vehID)


def readCurrentGrinchVehicle():
    return getSettings(_AccountSettingsKeys.GRINCH_CURRENT_VEHICLE)


def setStartChapterNotificationShown(chapterID):
    settings = getSettings(_AccountSettingsKeys.GRINCH_CHAPTERS_START_NOTIFICATION_SHOWN)
    settings.add(chapterID)
    setSettings(_AccountSettingsKeys.GRINCH_CHAPTERS_START_NOTIFICATION_SHOWN, settings)


def isStartChapterNotifationShown(chapterID):
    settings = getSettings(_AccountSettingsKeys.GRINCH_CHAPTERS_START_NOTIFICATION_SHOWN)
    return chapterID in settings


def setEndedChapterNotificationShown(chapterID):
    settings = getSettings(_AccountSettingsKeys.GRINCH_CHAPTERS_END_NOTIFICATION_SHOWN)
    settings.add(chapterID)
    setSettings(_AccountSettingsKeys.GRINCH_CHAPTERS_END_NOTIFICATION_SHOWN, settings)


def isEndedChapterNotifationShown(chapterID):
    settings = getSettings(_AccountSettingsKeys.GRINCH_CHAPTERS_END_NOTIFICATION_SHOWN)
    return chapterID in settings


def setFinishedNotificationShown():
    setSettings(_AccountSettingsKeys.GRINCH_FINISHED_NOTIFICATION_SHOWN, True)


def isFinishedNotifationShown():
    return getSettings(_AccountSettingsKeys.GRINCH_FINISHED_NOTIFICATION_SHOWN)
