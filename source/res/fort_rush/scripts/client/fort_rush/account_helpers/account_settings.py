# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/account_helpers/account_settings.py
from __future__ import absolute_import
from typing import TYPE_CHECKING
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_SETTINGS
if TYPE_CHECKING:
    from typing import Any

class _AccountSettingsKeys(object):
    FORT_RUSH_KEY = 'fort_rush_keys'
    FORT_RUSH_EVENT_START_NOTIFICATION_SHOWN = 'fort_rush_event_start_notification_shown'
    FORT_RUSH_EVENT_END_NOTIFICATION_SHOWN = 'fort_rush_event_end_notification_shown'
    FORT_RUSH_PAUSE_NOTIFICATION_SHOWN = 'fort_rush_pause_notification_shown'
    FORT_RUSH_RESUME_NOTIFICATION_SHOWN = 'fort_rush_resume_notification_shown'
    FORT_RUSH_LAST_SEEN_PROGRESSION_POINTS = 'fort_rush_last_seen_progression_points'
    FORT_RUSH_SEEN_WELCOME_SCREEN = 'fort_rush_welcomeScreenSeen'
    FORT_RUSH_BANNER_SEEN = 'fort_rush_bannerSeen'
    FORT_RUSH_LAST_SELECTED_VEHICLE_INT_CD = 'fort_rush_last_selected_vehicle_int_cd'


ACCOUNT_DEFAULT_SETTINGS = {_AccountSettingsKeys.FORT_RUSH_KEY: {_AccountSettingsKeys.FORT_RUSH_EVENT_START_NOTIFICATION_SHOWN: False,
                                      _AccountSettingsKeys.FORT_RUSH_EVENT_END_NOTIFICATION_SHOWN: False,
                                      _AccountSettingsKeys.FORT_RUSH_PAUSE_NOTIFICATION_SHOWN: False,
                                      _AccountSettingsKeys.FORT_RUSH_RESUME_NOTIFICATION_SHOWN: False,
                                      _AccountSettingsKeys.FORT_RUSH_LAST_SEEN_PROGRESSION_POINTS: 0,
                                      _AccountSettingsKeys.FORT_RUSH_SEEN_WELCOME_SCREEN: False,
                                      _AccountSettingsKeys.FORT_RUSH_BANNER_SEEN: False,
                                      _AccountSettingsKeys.FORT_RUSH_LAST_SELECTED_VEHICLE_INT_CD: 0}}

def extendAccountSettings():
    AccountSettings.overrideDefaultSettings(KEY_SETTINGS, ACCOUNT_DEFAULT_SETTINGS)


def getSettings(name):
    settings = AccountSettings.getSettings(_AccountSettingsKeys.FORT_RUSH_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[_AccountSettingsKeys.FORT_RUSH_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(_AccountSettingsKeys.FORT_RUSH_KEY)
    settings[name] = value
    AccountSettings.setSettings(_AccountSettingsKeys.FORT_RUSH_KEY, settings)


def setStartEventNotificationShown(value):
    setSettings(_AccountSettingsKeys.FORT_RUSH_EVENT_START_NOTIFICATION_SHOWN, value)


def isStartEventNotificationShown():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_EVENT_START_NOTIFICATION_SHOWN)


def setEndEventNotificationShown(value):
    setSettings(_AccountSettingsKeys.FORT_RUSH_EVENT_END_NOTIFICATION_SHOWN, value)


def isEndEventNotificationShown():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_EVENT_END_NOTIFICATION_SHOWN)


def setPauseEventNotificationShown(value):
    setSettings(_AccountSettingsKeys.FORT_RUSH_PAUSE_NOTIFICATION_SHOWN, value)


def isPauseEventNotificationShown():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_PAUSE_NOTIFICATION_SHOWN)


def setResumeEventNotificationShown(value):
    setSettings(_AccountSettingsKeys.FORT_RUSH_RESUME_NOTIFICATION_SHOWN, value)


def isResumeEventNotificationShown():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_RESUME_NOTIFICATION_SHOWN)


def getLastSeenProgressionPoints():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_LAST_SEEN_PROGRESSION_POINTS)


def setLastSeenProgressionPoints(value):
    setSettings(_AccountSettingsKeys.FORT_RUSH_LAST_SEEN_PROGRESSION_POINTS, value)


def isWelcomeScreenSeen():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_SEEN_WELCOME_SCREEN)


def setWelcomeScreenSeen(seen=True):
    return setSettings(_AccountSettingsKeys.FORT_RUSH_SEEN_WELCOME_SCREEN, seen)


def isBannerSeen():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_BANNER_SEEN)


def setBannerSeen(seen=True):
    return setSettings(_AccountSettingsKeys.FORT_RUSH_BANNER_SEEN, seen)


def getLastSelectedVehicleIntCD():
    return getSettings(_AccountSettingsKeys.FORT_RUSH_LAST_SELECTED_VEHICLE_INT_CD)


def setLastSelectedVehicleIntCD(intCD):
    setSettings(_AccountSettingsKeys.FORT_RUSH_LAST_SELECTED_VEHICLE_INT_CD, intCD)
