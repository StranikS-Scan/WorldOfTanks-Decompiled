# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_NOTIFICATIONS
from story_mode.gui.impl.lobby.consts import EntryPointStates
from story_mode_common.story_mode_constants import EVENT_NAME, EXTENSION_NAME, UNDEFINED_MISSION_ID
_ENTRY_POINT_SHOWN_STATE_KEY = 'entry_point_shown'
_EVENT_ENTRY_POINT_SHOWN_STATE_KEY = 'event_entry_point_shown'
_UNLOCKED_TASKS_SHOWN_KEY = 'unlocked_tasks_shown'
_WELCOME_SCREEN_SEEN_KEY = 'welcome_screen_seen'
_NEWBIE_ADVERTISING_SCREEN_SEEN_KEY = 'newbie_advertising_screen_seen'
_NEW_MISSION_SEEN_ID_KEY = 'new_mission_seen_id'
_DEFAULT_SETTINGS = {EVENT_NAME: {_EVENT_ENTRY_POINT_SHOWN_STATE_KEY: EntryPointStates.UNKNOWN.value,
              _UNLOCKED_TASKS_SHOWN_KEY: {},
              _WELCOME_SCREEN_SEEN_KEY: False},
 EXTENSION_NAME: {_NEWBIE_ADVERTISING_SCREEN_SEEN_KEY: False,
                  _NEW_MISSION_SEEN_ID_KEY: UNDEFINED_MISSION_ID}}

def init():
    AccountSettings.overrideDefaultSettings(KEY_NOTIFICATIONS, _DEFAULT_SETTINGS)


def getEventEntryPointShownState():
    return EntryPointStates(AccountSettings.getNotifications(EVENT_NAME)[_EVENT_ENTRY_POINT_SHOWN_STATE_KEY])


def setEventEntryPointShownState(state):
    _setEventSettings(_EVENT_ENTRY_POINT_SHOWN_STATE_KEY, state.value)


def isUnlockedTaskShown(missionId, taskId):
    return taskId in AccountSettings.getNotifications(EVENT_NAME)[_UNLOCKED_TASKS_SHOWN_KEY].get(missionId, ())


def setUnlockedTaskShown(missionId, taskId):
    settings = AccountSettings.getNotifications(EVENT_NAME)
    settings[_UNLOCKED_TASKS_SHOWN_KEY].setdefault(missionId, set()).add(taskId)
    AccountSettings.setNotifications(EVENT_NAME, settings)


def isWelcomeScreenSeen():
    return AccountSettings.getNotifications(EVENT_NAME)[_WELCOME_SCREEN_SEEN_KEY]


def setWelcomeScreenSeen():
    _setEventSettings(_WELCOME_SCREEN_SEEN_KEY, True)


def isNewbieAdvertisingScreenSeen():
    return AccountSettings.getNotifications(EXTENSION_NAME)[_NEWBIE_ADVERTISING_SCREEN_SEEN_KEY]


def setNewbieAdvertisingScreenSeen():
    _setExtensionSettings(_NEWBIE_ADVERTISING_SCREEN_SEEN_KEY, True)


def getMissionNewSeenId():
    return AccountSettings.getNotifications(EXTENSION_NAME)[_NEW_MISSION_SEEN_ID_KEY]


def setMissionNewSeenId(missionId):
    _setExtensionSettings(_NEW_MISSION_SEEN_ID_KEY, missionId)


def _setEventSettings(key, value):
    settings = AccountSettings.getNotifications(EVENT_NAME)
    settings[key] = value
    AccountSettings.setNotifications(EVENT_NAME, settings)


def _setExtensionSettings(key, value):
    settings = AccountSettings.getNotifications(EXTENSION_NAME)
    settings[key] = value
    AccountSettings.setNotifications(EXTENSION_NAME, settings)
