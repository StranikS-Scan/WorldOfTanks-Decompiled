# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationsModel.py
import Event
from notification.NotificationsCollection import NotificationsCollection
from notification.listeners import NotificationsListeners
from notification.settings import NOTIFICATION_STATE

class NotificationsModel(object):

    def __init__(self, counter, firstEntry=True):
        self.__currentDisplayState = None
        self.__collection = NotificationsCollection()
        self.__listeners = NotificationsListeners()
        self.__counter = counter
        self.__firstEntry = firstEntry
        self.onDisplayStateChanged = Event.Event()
        self.onNotificationReceived = Event.Event()
        self.onNotificationUpdated = Event.Event()
        self.onNotificationRemoved = Event.Event()
        self.onNotifiedMessagesCountChanged = Event.Event()
        self.__setDisplayState(NOTIFICATION_STATE.POPUPS, {})
        return

    @property
    def collection(self):
        return self.__collection

    def setListDisplayState(self, data=None):
        self.__setDisplayState(NOTIFICATION_STATE.LIST, data)

    def setPopupsDisplayState(self, data=None):
        self.__setDisplayState(NOTIFICATION_STATE.POPUPS, data)

    def __setDisplayState(self, newState, data):
        if newState != self.__currentDisplayState:
            oldState = self.__currentDisplayState
            self.__currentDisplayState = newState
            self.onDisplayStateChanged(oldState, newState, data)

    def getDisplayState(self):
        return self.__currentDisplayState

    def addNotification(self, notification):
        if self.__collection.addItem(notification):
            overloaded = self.__collection.getOverloaded(notification)
            if overloaded:
                for item in overloaded:
                    self.__removeNotification(item)

            self.onNotificationReceived(notification)

    def updateNotification(self, typeID, entityID, entity, isStateChanged):
        if self.__collection.updateItem(typeID, entityID, entity):
            self.onNotificationUpdated(self.__collection.getItem(typeID, entityID), isStateChanged)

    def removeNotification(self, typeID, entityID):
        notification = self.getNotification(typeID, entityID)
        if notification is None:
            return
        else:
            self.__removeNotification(notification)
            return

    def removeNotificationsByType(self, typeID):
        self.__collection.removeItemsByType(typeID)

    def hasNotification(self, typeID, entityID):
        return self.__collection.getItem(typeID, entityID) is not None

    def getNotification(self, typeID, entityID):
        return self.__collection.getItem(typeID, entityID)

    def __removeNotification(self, notification):
        typeID, entityID = notification.getType(), notification.getID()
        groupID = notification.getGroup()
        countOnce = notification.isShouldCountOnlyOnce()
        if self.__collection.removeItem(typeID, entityID):
            self.onNotificationRemoved(typeID, entityID, groupID, countOnce)

    def incrementNotifiedMessagesCount(self, group, typeID, entityID, countOnlyOnce):
        self.onNotifiedMessagesCountChanged(self.__counter.addNotification(group, typeID, entityID, countOnlyOnce))

    def decrementNotifiedMessagesCount(self, group, typeID, entityID, countOnlyOnce):
        self.onNotifiedMessagesCountChanged(self.__counter.removeNotification(group, typeID, entityID, countOnlyOnce))

    def resetNotifiedMessagesCount(self, group=None):
        self.onNotifiedMessagesCountChanged(self.__counter.reset(group))

    def getNotifiedMessagesCount(self, group=None):
        return self.__counter.count(group)

    def getFirstEntry(self):
        return self.__firstEntry

    def setup(self):
        self.__collection.default()
        self.__collection.onNotificationRemoved += self.__onNotificationRemoved
        self.__listeners.start(self)

    def cleanUp(self):
        self.__collection.onNotificationRemoved -= self.__onNotificationRemoved
        self.__collection.clear()
        self.__listeners.stop()
        self.__counter.resetUnreadCount()
        self.__counter = None
        self.onDisplayStateChanged.clear()
        self.onNotificationReceived.clear()
        self.onNotifiedMessagesCountChanged.clear()
        return

    def __onNotificationRemoved(self, typeID, entityID, groupID, countOnce):
        self.onNotificationRemoved(typeID, entityID, groupID, countOnce)
