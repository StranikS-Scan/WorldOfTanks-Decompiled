# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationsModel.py
import Event
from notification.NotificationsCollection import NotificationsCollection
from notification.listeners import NotificationsListeners
from notification.settings import NOTIFICATION_STATE

class NotificationsModel(object):

    def __init__(self, storage, counter, firstEntry=True):
        self.__currentDisplayState = None
        self.__collection = NotificationsCollection()
        self.__storage = storage
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

    @property
    def storage(self):
        return self.__storage

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

    def addNotification(self, notification, saveInStorage=False, withAlert=True):
        if self.__collection.addItem(notification):
            if saveInStorage:
                self.__storage.addItem(notification)
            if withAlert:
                self.onNotificationReceived(notification)

    def updateNotification(self, typeID, entityID, entity, isStateChanged):
        if self.__collection.updateItem(typeID, entityID, entity):
            if self.hasNotificationInStorage(typeID, entityID):
                self.__storage.updateItem(typeID, entityID, entity)
            self.onNotificationUpdated(self.__collection.getItem(typeID, entityID), isStateChanged)

    def removeNotification(self, typeID, entityID):
        notification = self.getNotification(typeID, entityID)
        if notification is None:
            return
        else:
            groupID = notification.getGroup()
            if self.__collection.removeItem(typeID, entityID):
                self.onNotificationRemoved(typeID, entityID, groupID)
            if self.hasNotificationInStorage(typeID, entityID):
                self.__storage.removeItem(typeID, entityID)
            return

    def removeNotificationsByType(self, typeID):
        self.__collection.removeItemsByType(typeID)
        self.__storage.removeItemsByType(typeID)

    def hasNotification(self, typeID, entityID):
        return self.__collection.getItem(typeID, entityID) is not None

    def hasNotificationInStorage(self, typeID, entityID):
        return self.__storage.getItem(typeID, entityID) is not None

    def getNotification(self, typeID, entityID):
        return self.__collection.getItem(typeID, entityID)

    def getNotificationsFromStorage(self, typesRange=None):
        return [ item for item in self.__storage.getListIterator(typesRange) ]

    def incrementNotifiedMessagesCount(self, group, typeID, entityID):
        self.onNotifiedMessagesCountChanged(self.__counter.addNotification(group, typeID, entityID))

    def decrementNotifiedMessagesCount(self, group, typeID, entityID):
        self.onNotifiedMessagesCountChanged(self.__counter.removeNotification(group, typeID, entityID))

    def resetNotifiedMessagesCount(self, group=None):
        self.onNotifiedMessagesCountChanged(self.__counter.reset(group))

    def getNotifiedMessagesCount(self, group=None):
        return self.__counter.count(group)

    def getFirstEntry(self):
        return self.__firstEntry

    def setup(self):
        self.__collection.default()
        self.__listeners.start(self)

    def cleanUp(self):
        self.__collection.clear()
        self.__listeners.stop()
        self.__counter.resetUnreadCount()
        self.__counter = None
        self.onDisplayStateChanged.clear()
        self.onNotificationReceived.clear()
        self.onNotifiedMessagesCountChanged.clear()
        return
