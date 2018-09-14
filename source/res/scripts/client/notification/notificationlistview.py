# Embedded file name: scripts/client/notification/NotificationListView.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.NotificationsListMeta import NotificationsListMeta
from messenger.formatters import TimeFormatter
from notification.NotificationLayoutView import NotificationLayoutView
from notification import NotificationMVC
from notification.settings import LIST_SCROLL_STEP_FACTOR, NOTIFICATION_STATE

class NotificationListView(NotificationsListMeta, NotificationLayoutView):

    def __init__(self, _):
        super(NotificationListView, self).__init__()
        self.setModel(NotificationMVC.g_instance.getModel())

    def onClickAction(self, typeID, entityID, action):
        NotificationMVC.g_instance.handleAction(typeID, entityID, action)

    def destroy(self):
        if self._model.getDisplayState() == NOTIFICATION_STATE.LIST:
            self._model.setPopupsDisplayState()
        else:
            LOG_ERROR('Invalid state of the Notifications Model')
        super(NotificationListView, self).destroy()

    def getMessageActualTime(self, msTime):
        return TimeFormatter.getActualMsgTimeStr(msTime)

    def _populate(self):
        super(NotificationListView, self)._populate()
        self._model.onNotificationReceived += self.__onNotificationReceived
        self._model.onNotificationUpdated += self.__onNotificationUpdated
        self._model.onNotificationRemoved += self.__onNotificationRemoved
        self.as_setInitDataS({'scrollStepFactor': LIST_SCROLL_STEP_FACTOR})
        self.__setNotificationList()
        self._onLayoutSettingsChanged({})

    def _dispose(self):
        self._model.onNotificationReceived -= self.__onNotificationReceived
        self._model.onNotificationUpdated -= self.__onNotificationUpdated
        self._model.onNotificationRemoved -= self.__onNotificationRemoved
        self.__closeCallBack = None
        self.cleanUp()
        super(NotificationListView, self)._dispose()
        return

    def _onLayoutSettingsChanged(self, settings):
        pass

    def __setNotificationList(self):
        self.as_setMessagesListS(map(lambda item: item.getListVO(), self._model.collection.getListIterator()))

    def __onNotificationReceived(self, notification):
        if notification.isAlert():
            NotificationMVC.g_instance.getAlertController().showAlertMessage(notification)
        self.as_appendMessageS(notification.getListVO())

    def __onNotificationUpdated(self, notification, _):
        if notification.isOrderChanged():
            self.__setNotificationList()
        else:
            self.as_updateMessageS(notification.getListVO())

    def __onNotificationRemoved(self, typeID, entityID):
        self.__setNotificationList()
