# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationsStorage.py
from collections import defaultdict
import typing
from debug_utils import LOG_ERROR, LOG_WARNING
from notification.decorators import _NotificationDecorator
from notification.settings import NOTIFICATION_TYPE, ITEMS_MAX_LENGTHS, SavedNotificationData
if typing.TYPE_CHECKING:
    from typing import Dict, List

class NotificationsStorage(object):

    def __init__(self):
        super(NotificationsStorage, self).__init__()
        self.__received = defaultdict(list)

    def clear(self):
        for typeID in NOTIFICATION_TYPE.RANGE:
            if typeID not in self.__received:
                continue
            notifications = self.__received[typeID]
            while notifications:
                notifications.pop()

    def addItem(self, item):
        result = True
        typeID, entityID = item.getType(), item.getID()
        if typeID in NOTIFICATION_TYPE.RANGE:
            notifications = self.__received[typeID]
            notificationToSave = SavedNotificationData(entityID, item.getSavedData(), item.getPriorityLevel())
            if notificationToSave not in notifications:
                notifications.append(notificationToSave)
                if len(notifications) > ITEMS_MAX_LENGTHS[typeID]:
                    notifications.pop(0)
            else:
                result = False
                LOG_WARNING('Notification already exists', typeID, entityID, item)
        else:
            result = False
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def removeItem(self, typeID, entityID):
        result = True
        if typeID in NOTIFICATION_TYPE.RANGE:
            notifications = self.__received[typeID]
            indexList = list((i for i, v in enumerate(notifications) if v.entityID == entityID))
            if indexList:
                notifications.pop(indexList[0])
            else:
                result = False
                LOG_WARNING('Notification not found', typeID, entityID)
        else:
            result = False
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def removeItemsByType(self, typeID):
        result = True
        if typeID in NOTIFICATION_TYPE.RANGE:
            notifications = self.__received[typeID]
            while notifications:
                notifications.pop()

        else:
            result = False
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def updateItem(self, typeID, entityID, entity):
        result = False
        if typeID in NOTIFICATION_TYPE.RANGE:
            notifications = self.__received[typeID]
            indexList = list((i for i, v in enumerate(notifications) if v.entityID == entityID))
            if indexList:
                result = True
                prev = notifications.pop(indexList[0])
                notificationToSave = SavedNotificationData(entityID, entity.get('savedData'), prev.priorityLevel)
                notifications.append(notificationToSave)
        else:
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def getItem(self, typeID, entityID):
        result = None
        if typeID in NOTIFICATION_TYPE.RANGE:
            notifications = self.__received[typeID]
            indexList = list((i for i, v in enumerate(notifications) if v.entityID == entityID))
            if indexList:
                result = notifications[indexList[0]]
        else:
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def getListIterator(self, typesRange=None):
        notifications = []
        typesRange = typesRange or NOTIFICATION_TYPE.RANGE
        for typeID in typesRange:
            notifications.extend(self.__received[typeID])

        for item in notifications:
            yield item
