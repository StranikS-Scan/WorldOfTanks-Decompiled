# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/account_settings.py
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_NOTIFICATIONS
from story_mode.gui.impl.lobby.consts import EntryPointStates
from story_mode_common.story_mode_constants import EVENT_NAME
_ENTRY_POINT_SHOWN_STATE_KEY = 'entry_point_shown'
_UNLOCKED_TASKS_SHOWN_KEY = 'unlocked_tasks_shown'
_WELCOME_SCREEN_SEEN_KEY = 'welcome_screen_seen'
_DEFAULT_SETTINGS = {EVENT_NAME: {_ENTRY_POINT_SHOWN_STATE_KEY: EntryPointStates.UNKNOWN.value,
              _UNLOCKED_TASKS_SHOWN_KEY: {},
              _WELCOME_SCREEN_SEEN_KEY: False}}

def init():
    AccountSettings.overrideDefaultSettings(KEY_NOTIFICATIONS, _DEFAULT_SETTINGS)


def getEntryPointShownState():
    return EntryPointStates(AccountSettings.getNotifications(EVENT_NAME)[_ENTRY_POINT_SHOWN_STATE_KEY])


def setEntryPointShownState(state):
    _setEventSettings(_ENTRY_POINT_SHOWN_STATE_KEY, state.value)


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


def _setEventSettings(key, value):
    settings = AccountSettings.getNotifications(EVENT_NAME)
    settings[key] = value
    AccountSettings.setNotifications(EVENT_NAME, settings)
