# Embedded file name: scripts/client/notification/NotificationVisibilityController.py
from gui.clubs.task_scheduler import TaskScheduler, Task
from notification.BaseMessagesController import BaseMessagesController
from helpers import time_utils

class NotificationVisibilityController(BaseMessagesController):

    def __init__(self, model):
        super(NotificationVisibilityController, self).__init__(model)
        self.__visibilitySch = TaskScheduler()
        self.__visibilitySch.start()
        self.__notificationTypes = set()
        self._model.onNotificationUpdated += self.__onNotificationUpdated
        self._model.onNotificationRemoved += self.__onNotificationRemoved
        self._model.onNotificationReceived += self.__onNotificationReceived

    def cleanUp(self):
        self._model.onNotificationUpdated -= self.__onNotificationUpdated
        self._model.onNotificationRemoved -= self.__onNotificationRemoved
        self._model.onNotificationReceived -= self.__onNotificationReceived
        self.__notificationTypes = set()
        self.__visibilitySch.cancelAllTasks()
        super(NotificationVisibilityController, self).cleanUp()

    def registerNotifications(self, typeIDs):
        self.__notificationTypes.update(typeIDs)

    def __onNotificationReceived(self, notification):
        self._processNotification(notification)

    def __onNotificationUpdated(self, notification, _):
        self._processNotification(notification)

    def __onNotificationRemoved(self, typeID, entityID):
        self.__visibilitySch.cancelTask((typeID, entityID))

    def _processNotification(self, notification):
        typeID = notification.getType()
        if typeID in self.__notificationTypes:
            vt = notification.getVisibilityTime()
            if vt is not None:
                if time_utils.isFuture(vt):
                    self.__visibilitySch.scheduleTask(Task((typeID, notification.getID()), vt, self.__onInviteVisibilityChanged, None))
                else:
                    self._model.removeNotification(typeID, notification.getID())
        return

    def __onInviteVisibilityChanged(self, key, extra):
        typeID, entityID = key
        self._model.removeNotification(typeID, entityID)
