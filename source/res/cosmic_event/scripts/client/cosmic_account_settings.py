# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: cosmic_event/scripts/client/cosmic_account_settings.py
from typing import TYPE_CHECKING
from account_helpers import AccountSettings
from cosmic_event_common.cosmic_constants import COSMIC_KEY, ACCOUNT_DEFAULT_SETTINGS, EVENT_STARTED_NOTIFICATION_VIEWED, LAST_PROGRESSION_VISITED_LEVEL, COSMIC_MODE_SELECTOR_BATTLE_PASS_SHOWN, SELECTED_VEHICLE_ID, COSMIC_LOBBY_FIRST_ENTER_SOUND_PLAYED, COSMIC_INTRO_VIDEO_VIEWED
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


def setLastVisitedProgressionLevel(level):
    setSettings(LAST_PROGRESSION_VISITED_LEVEL, level)


def getLastVisitedProgressionLevel():
    return getSettings(LAST_PROGRESSION_VISITED_LEVEL)


def setLastSelectedVehicleID(id):
    setSettings(SELECTED_VEHICLE_ID, id)


def getLastSelectedVehicleID():
    return getSettings(SELECTED_VEHICLE_ID)


def isCosmicBattlePassShown():
    return getSettings(COSMIC_MODE_SELECTOR_BATTLE_PASS_SHOWN)


def setCosmicBattlePassShown(status):
    return setSettings(COSMIC_MODE_SELECTOR_BATTLE_PASS_SHOWN, status)


def isLobbyFirstEnterSoundPlayed():
    return getSettings(COSMIC_LOBBY_FIRST_ENTER_SOUND_PLAYED)


def setLobbyFirstEnterSoundPlayed(status):
    return setSettings(COSMIC_LOBBY_FIRST_ENTER_SOUND_PLAYED, status)


def isIntroVideoViewed():
    return getSettings(COSMIC_INTRO_VIDEO_VIEWED)


def setIntroVideoViewed(status):
    return setSettings(COSMIC_INTRO_VIDEO_VIEWED, status)
