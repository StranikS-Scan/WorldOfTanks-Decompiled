# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationsModel.py
import Event
from notification.NotificationsCollection import NotificationsCollection
from notification.listeners import NotificationsListeners
from notification.settings import NOTIFICATION_STATE

class NotificationsModel:

    def __init__(self, counter):
        self.__layoutSettings = {'paddingRight': 0,
         'paddingBottom': 0}
        self.__currentDisplayState = None
        self.__collection = NotificationsCollection()
        self.__listeners = NotificationsListeners()
        self.__counter = counter
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
            self.onNotificationReceived(notification)

    def updateNotification(self, typeID, entityID, entity, isStateChanged):
        if self.__collection.updateItem(typeID, entityID, entity):
            self.onNotificationUpdated(self.__collection.getItem(typeID, entityID), isStateChanged)

    def removeNotification(self, typeID, entityID):
        groupID = self.getNotification(typeID, entityID).getGroup()
        if self.__collection.removeItem(typeID, entityID):
            self.onNotificationRemoved(typeID, entityID, groupID)

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

    def incrementNotifiedMessagesCount(self, group, typeID, entityID):
        self.onNotifiedMessagesCountChanged(self.__counter.addNotification(group, typeID, entityID))

    def decrementNotifiedMessagesCount(self, group, typeID, entityID):
        self.onNotifiedMessagesCountChanged(self.__counter.removeNotification(group, typeID, entityID))

    def resetNotifiedMessagesCount(self, group=None):
        self.onNotifiedMessagesCountChanged(self.__counter.reset(group))

    def getNotifiedMessagesCount(self, group=None):
        return self.__counter.count(group)

    def setup(self):
        self.__collection.default()
        self.__listeners.start(self)

    def cleanUp(self):
        self.__collection.clear()
        self.__listeners.stop()
        self.__counter.resetUnreadCount()
        self.__counter = None
        self.onLayoutSettingsChanged.clear()
        self.onDisplayStateChanged.clear()
        self.onNotificationReceived.clear()
        self.onNotifiedMessagesCountChanged.clear()
        return
