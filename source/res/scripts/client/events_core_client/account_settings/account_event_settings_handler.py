# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/events_core_client/account_settings/account_event_settings_handler.py
import typing
from account_helpers import AccountSettings
from helpers import time_utils
if typing.TYPE_CHECKING:
    from typing import Dict, Any
    from events_core_client.skeletons.event_controller import IEventController

class AccountEventSettingsHandler(object):

    def __init__(self, eventKey, expiryTimeKey, eventController):
        self._eventKey = eventKey
        self._expiryTimeKey = expiryTimeKey
        self._eventController = eventController

    @property
    def settings(self):
        return AccountSettings.getSettings(self._eventKey)

    @property
    def notifications(self):
        return AccountSettings.getNotifications(self._eventKey)

    def setSetting(self, name, value):
        settings = self.settings
        settings[name] = value
        AccountSettings.setSettings(self._eventKey, settings)

    def setNotification(self, name, value):
        notifications = self.notifications
        notifications[name] = value
        AccountSettings.setNotifications(self._eventKey, notifications)

    def migrateAccount(self):
        expiryDate = self.settings.get(self._expiryTimeKey)
        currentTime = time_utils.getServerUTCTime()
        if expiryDate and expiryDate < currentTime:
            self.__reset()
        finishDate = self._eventController.getEventFinishTime()
        if self._eventController.isEnabled() and finishDate > currentTime and not expiryDate:
            self.setSetting(self._expiryTimeKey, finishDate)

    @property
    def _defaultSettings(self):
        return AccountSettings.getSettingsDefault(self._eventKey)

    @property
    def _defaultNotifications(self):
        return AccountSettings.getNotificationsDefault(self._eventKey)

    def __reset(self):
        AccountSettings.setSettings(self._eventKey, self._defaultSettings)
        AccountSettings.setNotifications(self._eventKey, self._defaultNotifications)
