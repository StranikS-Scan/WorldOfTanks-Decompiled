# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationPopUpViewer.py
from gui.Scaleform.daapi.view.meta.NotificationPopUpViewerMeta import NotificationPopUpViewerMeta
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from messenger import g_settings
from messenger.formatters import TimeFormatter
from notification import NotificationMVC
from notification.BaseNotificationView import BaseNotificationView
from notification.settings import NOTIFICATION_STATE, NOTIFICATION_GROUP, NOTIFICATION_TYPE
from skeletons.connection_mgr import IConnectionManager

class NotificationPopUpViewer(NotificationPopUpViewerMeta, BaseNotificationView):
    """
    WARNING! This class uses ids mapping! It means that all ids coming outside should be maped with special method
    from base class.
    """
    connectionMgr = dependency.descriptor(IConnectionManager)

    def __init__(self):
        mvc = NotificationMVC.g_instance
        mvc.initialize()
        settings = g_settings.lobby.serviceChannel
        self.__maxAvailableItemsCount = settings.stackLength
        self.__messagesPadding = settings.padding
        self.__noDisplayingPopups = True
        self.__pendingMessagesQueue = []
        super(NotificationPopUpViewer, self).__init__()
        self.setModel(mvc.getModel())

    def onClickAction(self, typeID, entityID, action):
        NotificationMVC.g_instance.handleAction(typeID, self._getNotificationID(entityID), action)

    def onMessageHidden(self, byTimeout, wasNotified, typeID, entityID):
        if self._model.getDisplayState() == NOTIFICATION_STATE.POPUPS and typeID != NOTIFICATION_TYPE.GIFT:
            if not byTimeout and wasNotified:
                notification = self._model.getNotification(typeID, self._getNotificationID(entityID))
                self._model.decrementNotifiedMessagesCount(*notification.getCounterInfo())

    def setListClear(self):
        self.__noDisplayingPopups = True
        if self._model is not None and self._model.getDisplayState() == NOTIFICATION_STATE.POPUPS:
            if self.__pendingMessagesQueue:
                self.__showAlertMessage(self.__pendingMessagesQueue.pop(0))
        return

    def getMessageActualTime(self, msTime):
        return TimeFormatter.getActualMsgTimeStr(msTime)

    def _populate(self):
        super(NotificationPopUpViewer, self)._populate()
        self._model.onNotificationReceived += self.__onNotificationReceived
        self._model.onNotificationUpdated += self.__onNotificationUpdated
        self._model.onNotificationRemoved += self.__onNotificationRemoved
        self._model.onDisplayStateChanged += self.__displayStateChangeHandler
        mvcInstance = NotificationMVC.g_instance
        mvcInstance.getAlertController().onAllAlertsClosed += self.__allAlertsMessageCloseHandler
        self.as_initInfoS(self.__maxAvailableItemsCount, self.__messagesPadding)
        self._model.setup()

    def _dispose(self):
        self.__pendingMessagesQueue = []
        self._model.onNotificationReceived -= self.__onNotificationReceived
        self._model.onNotificationUpdated -= self.__onNotificationUpdated
        self._model.onNotificationRemoved -= self.__onNotificationRemoved
        self._model.onDisplayStateChanged -= self.__displayStateChangeHandler
        mvcInstance = NotificationMVC.g_instance
        mvcInstance.getAlertController().onAllAlertsClosed -= self.__allAlertsMessageCloseHandler
        self.cleanUp()
        mvcInstance.cleanUp(resetCounter=self.connectionMgr.isDisconnected())
        super(NotificationPopUpViewer, self)._dispose()

    def __onNotificationReceived(self, notification):
        if self._model.getDisplayState() == NOTIFICATION_STATE.POPUPS:
            if notification.isNotify() and (notification.getGroup() != NOTIFICATION_GROUP.INFO or notification.getPriorityLevel() == NotificationPriorityLevel.LOW):
                self._model.incrementNotifiedMessagesCount(*notification.getCounterInfo())
            if NotificationMVC.g_instance.getAlertController().isAlertShowing():
                self.__pendingMessagesQueue.append(notification)
            elif self.__pendingMessagesQueue:
                self.__pendingMessagesQueue.append(notification)
            elif notification.isAlert():
                if self.__noDisplayingPopups:
                    self.__showAlertMessage(notification)
                else:
                    self.__pendingMessagesQueue.append(notification)
            else:
                self.__sendMessageForDisplay(notification)

    def __onNotificationUpdated(self, notification, isStateChanged):
        flashID = self._getFlashID(notification.getID())
        if self.as_hasPopUpIndexS(notification.getType(), flashID):
            self.as_updateMessageS(self.__getPopUpVO(notification))
        elif isStateChanged:
            self.__onNotificationReceived(notification)

    def __onNotificationRemoved(self, typeID, entityID, groupID):
        self._model.decrementNotifiedMessagesCount(groupID, typeID, entityID)
        self.as_removeMessageS(typeID, self._getFlashID(entityID))

    def __sendMessageForDisplay(self, notification):
        if notification.getPriorityLevel() != NotificationPriorityLevel.LOW:
            self.as_appendMessageS(self.__getPopUpVO(notification))
            self.__noDisplayingPopups = False

    def __showAlertMessage(self, notification):
        NotificationMVC.g_instance.getAlertController().showAlertMessage(notification)

    def __allAlertsMessageCloseHandler(self):
        if self.__pendingMessagesQueue:
            needToShowFromQueueMessages = []
            while self.__pendingMessagesQueue:
                notification = self.__pendingMessagesQueue.pop(0)
                isAlert = notification.isAlert()
                if isAlert:
                    self.__showAlertMessage(notification)
                    return
                needToShowFromQueueMessages.append(notification)

            while needToShowFromQueueMessages:
                notification = needToShowFromQueueMessages.pop(0)
                if len(needToShowFromQueueMessages) < self.__maxAvailableItemsCount:
                    self.__sendMessageForDisplay(notification)

    def __displayStateChangeHandler(self, oldState, newState, data):
        if newState == NOTIFICATION_STATE.LIST:
            self.as_removeAllMessagesS()
            self.__pendingMessagesQueue = []

    def __getPopUpVO(self, notificaton):
        flashId = self._getFlashID(notificaton.getID())
        return notificaton.getPopUpVO(flashId)
