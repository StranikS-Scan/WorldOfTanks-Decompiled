# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationsCollection.py
import Event
from debug_utils import LOG_ERROR, LOG_WARNING
from notification.decorators import SearchCriteria, _NotificationDecorator
from notification.settings import NOTIFICATION_TYPE, ITEMS_MAX_LENGTHS

class NotificationsCollection(object):

    def __init__(self):
        super(NotificationsCollection, self).__init__()
        self.__received = {}
        self.onNotificationRemoved = Event.Event()

    def clear(self):
        self.onNotificationRemoved.clear()
        for typeID in NOTIFICATION_TYPE.RANGE:
            if typeID not in self.__received:
                continue
            notifications = self.__received[typeID]
            while notifications:
                notifications.pop().clear()

    def default(self):
        self.clear()
        for typeID in NOTIFICATION_TYPE.RANGE:
            self.__received[typeID] = []

    def addItem(self, item):
        result = True
        typeID, itemID = item.getType(), item.getID()
        if typeID in self.__received:
            notifications = self.__received[typeID]
            if item not in notifications:
                notifications.append(item)
                if len(notifications) > ITEMS_MAX_LENGTHS[typeID]:
                    self.__removeNotification(notifications.pop(0))
            else:
                result = False
                LOG_WARNING('Notification already exists', typeID, itemID, item)
        else:
            result = False
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def removeItem(self, typeID, itemID):
        result = True
        if typeID in self.__received:
            notifications = self.__received[typeID]
            criteria = SearchCriteria(typeID, itemID)
            if criteria in notifications:
                index = notifications.index(criteria)
                removed = notifications.pop(index)
                removed.clear()
            else:
                result = False
                LOG_WARNING('Notification not found', typeID, itemID)
        else:
            result = False
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def removeItemsByType(self, typeID):
        result = True
        if typeID in self.__received:
            notifications = self.__received[typeID]
            while notifications:
                self.__removeNotification(notifications.pop())

        else:
            result = False
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def updateItem(self, typeID, itemID, entity):
        result = False
        if typeID in self.__received:
            notifications = self.__received[typeID]
            criteria = SearchCriteria(typeID, itemID)
            if criteria in notifications:
                result = True
                notifications[notifications.index(criteria)].update(entity)
        else:
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def getItem(self, typeID, itemID):
        result = None
        if typeID in self.__received:
            notifications = self.__received[typeID]
            criteria = SearchCriteria(typeID, itemID)
            if criteria in notifications:
                result = notifications[notifications.index(criteria)]
        else:
            LOG_ERROR('Type of notification not found', typeID)
        return result

    def getListIterator(self, typesRange=None):
        notifications = []
        typesRange = typesRange or NOTIFICATION_TYPE.RANGE
        for typeID in typesRange:
            notifications.extend(self.__received[typeID])

        for item in sorted(notifications, key=lambda x: (x.isPinned(), x.getOrder())):
            yield item

    def __removeNotification(self, notification):
        typeID, entityID = notification.getType(), notification.getID()
        groupID, countOnce = notification.getGroup(), notification.isShouldCountOnlyOnce()
        notification.clear()
        self.onNotificationRemoved(typeID, entityID, groupID, countOnce)
