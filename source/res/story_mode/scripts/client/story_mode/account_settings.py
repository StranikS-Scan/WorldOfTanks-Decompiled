# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: story_mode/scripts/client/story_mode/account_settings.py
import typing
from account_helpers import AccountSettings
from account_helpers.AccountSettings import KEY_NOTIFICATIONS
from story_mode_common.configs.story_mode_settings import settingsSchema
from story_mode_common.story_mode_constants import EXTENSION_NAME, MissionId
_ENTRY_POINT_ANIMATION_SEEN_ID_KEY = 'entry_point_animation_seen_id'
_EVENT_ENTRY_POINT_SHOWN_KEY = 'event_entry_point_shown'
_EVENT_VISITED_KEY = 'event_visited'
_UNLOCKED_TASKS_SHOWN_KEY = 'unlocked_tasks_shown'
_WELCOME_SCREEN_SEEN_KEY = 'welcome_screen_seen'
_NEWBIE_ADVERTISING_SCREEN_SEEN_KEY = 'newbie_advertising_screen_seen'
_NEW_MISSION_SEEN_ID_KEY = 'new_mission_seen_id'
_DEFAULT_EVENT_NAME = 'story_mode_event'
_DEFAULT_SETTINGS = {EXTENSION_NAME: {_NEWBIE_ADVERTISING_SCREEN_SEEN_KEY: False,
                  _NEW_MISSION_SEEN_ID_KEY: MissionId.UNDEFINED,
                  _ENTRY_POINT_ANIMATION_SEEN_ID_KEY: MissionId.UNDEFINED}}
_DEFAULT_EVENT_SETTINGS = {_EVENT_ENTRY_POINT_SHOWN_KEY: False,
 _EVENT_VISITED_KEY: False,
 _UNLOCKED_TASKS_SHOWN_KEY: {},
 _WELCOME_SCREEN_SEEN_KEY: False}

def init():
    AccountSettings.overrideDefaultSettings(KEY_NOTIFICATIONS, _DEFAULT_SETTINGS)


def getEventEntryPointShown():
    return _getEventSettings()[_EVENT_ENTRY_POINT_SHOWN_KEY]


def setEventEntryPointShown():
    _setEventSettings(_EVENT_ENTRY_POINT_SHOWN_KEY, True)


def getEventVisited():
    return _getEventSettings()[_EVENT_VISITED_KEY]


def setEventVisited():
    _setEventSettings(_EVENT_VISITED_KEY, True)


def getNewbieEntryPointAnimationSeenId():
    return AccountSettings.getNotifications(EXTENSION_NAME).get(_ENTRY_POINT_ANIMATION_SEEN_ID_KEY, MissionId.UNDEFINED)


def setNewbieEntryPointAnimationSeenId(missionId):
    _setExtensionSettings(_ENTRY_POINT_ANIMATION_SEEN_ID_KEY, missionId)


def isUnlockedTaskShown(missionId, taskId):
    return taskId in _getEventSettings()[_UNLOCKED_TASKS_SHOWN_KEY].get(missionId, ())


def setUnlockedTaskShown(missionId, taskId):
    eventName = _getEventName()
    settings = _getEventSettings()
    settings[_UNLOCKED_TASKS_SHOWN_KEY].setdefault(missionId, set()).add(taskId)
    AccountSettings.setNotifications(eventName, settings)


def isWelcomeScreenSeen():
    return _getEventSettings()[_WELCOME_SCREEN_SEEN_KEY]


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


def _getEventName():
    settings = settingsSchema.getModel()
    return settings.eventName if settings is not None else None


def _getEventSettings():
    eventName = _getEventName()
    return _DEFAULT_EVENT_SETTINGS.copy() if eventName is None else AccountSettings.getNotifications(eventName, default=_DEFAULT_EVENT_SETTINGS.copy())


def _setEventSettings(key, value):
    eventName = _getEventName()
    if eventName is None:
        return
    else:
        settings = _getEventSettings()
        settings[key] = value
        AccountSettings.setNotifications(eventName, settings, force=True)
        return


def _setExtensionSettings(key, value):
    settings = AccountSettings.getNotifications(EXTENSION_NAME)
    settings[key] = value
    AccountSettings.setNotifications(EXTENSION_NAME, settings)
