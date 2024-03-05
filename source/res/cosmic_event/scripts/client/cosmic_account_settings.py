# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_account_settings.py
from typing import TYPE_CHECKING
from account_helpers import AccountSettings
from cosmic_event_common.cosmic_constants import COSMIC_KEY, ACCOUNT_DEFAULT_SETTINGS, EVENT_STARTED_NOTIFICATION_VIEWED
if TYPE_CHECKING:
    from typing import Any

def getSettings(name):
    settings = AccountSettings.getSettings(COSMIC_KEY)
    return settings.get(name, ACCOUNT_DEFAULT_SETTINGS[COSMIC_KEY].get(name))


def setSettings(name, value):
    settings = AccountSettings.getSettings(COSMIC_KEY)
    settings[name] = value
    AccountSettings.setSettings(COSMIC_KEY, settings)


def isEventStartedNotificationViewed():
    return getSettings(EVENT_STARTED_NOTIFICATION_VIEWED)


def setEventStartedNotificationViewed(status):
    return setSettings(EVENT_STARTED_NOTIFICATION_VIEWED, status)
