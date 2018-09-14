# Embedded file name: scripts/client/notification/NotificationsModel.py
import Event
from notification.NotificationsCollection import NotificationsCollection
from notification.NotificationsCounter import NotificationsCounter
from notification.listeners import NotificationsListeners
from notification.settings import NOTIFICATION_STATE

class NotificationsModel:

    def __init__(self):
        self.__layoutSettings = {'paddingRight': 0,
         'paddingBottom': 0}
        self.__currentDisplayState = None
        self.__collection = NotificationsCollection()
        self.__listeners = NotificationsListeners()
        self.__counter = NotificationsCounter()
        self.onLayoutSettingsChanged = Event.Event()
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

    def setListDisplayState(self, data = None):
        self.__setDisplayState(NOTIFICATION_STATE.LIST, data)

    def setPopupsDisplayState(self, data = None):
        self.__setDisplayState(NOTIFICATION_STATE.POPUPS, data)

    def __setDisplayState(self, newState, data):
        if newState != self.__currentDisplayState:
            oldState = self.__currentDisplayState
            self.__currentDisplayState = newState
            self.onDisplayStateChanged(oldState, newState, data)
            if newState == NOTIFICATION_STATE.LIST:
                self.resetNotifiedMessagesCount()

    def getDisplayState(self):
        return self.__currentDisplayState

    def addNotification(self, notification):
        if self.__collection.addItem(notification):
            self.onNotificationReceived(notification)

    def updateNotification(self, typeID, entityID, entity, isStateChanged):
        if self.__collection.updateItem(typeID, entityID, entity):
            self.onNotificationUpdated(self.__collection.getItem(typeID, entityID), isStateChanged)

    def removeNotification(self, typeID, entityID):
        if self.__collection.removeItem(typeID, entityID):
            self.onNotificationRemoved(typeID, entityID)

    def removeNotificationsByType(self, typeID):
        self.__collection.removeItemsByType(typeID)

    def hasNotification(self, typeID, entityID):
        return self.__collection.getItem(typeID, entityID) is not None

    def getNotification(self, typeID, entityID):
        return self.__collection.getItem(typeID, entityID)

    def setLayoutSettings(self, paddingRight, paddingBottom):
        self.__layoutSettings = {'paddingRight': paddingRight,
         'paddingBottom': paddingBottom}
        self.onLayoutSettingsChanged(self.__layoutSettings)

    def getLayoutSettings(self):
        return self.__layoutSettings

    def incrementNotifiedMessagesCount(self):
        self.onNotifiedMessagesCountChanged(self.__counter.increment())

    def resetNotifiedMessagesCount(self):
        self.onNotifiedMessagesCountChanged(self.__counter.reset())

    def decrementNotifiedMessagesCount(self):
        self.onNotifiedMessagesCountChanged(self.__counter.decrement())

    def getNotifiedMessagesCount(self):
        return self.__counter.count()

    def setup(self):
        self.__collection.default()
        self.__listeners.start(self)

    def cleanUp(self):
        self.__collection.clear()
        self.__listeners.stop()
        self.__counter.reset()
        self.onLayoutSettingsChanged.clear()
        self.onDisplayStateChanged.clear()
        self.onNotificationReceived.clear()
        self.onNotifiedMessagesCountChanged.clear()
