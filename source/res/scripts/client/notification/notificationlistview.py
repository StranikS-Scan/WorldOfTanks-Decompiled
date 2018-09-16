# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/notification/NotificationListView.py
from debug_utils import LOG_ERROR
from gui.Scaleform.daapi.view.meta.NotificationsListMeta import NotificationsListMeta
from gui.Scaleform.locale.MESSENGER import MESSENGER
from gui.Scaleform.locale.RES_ICONS import RES_ICONS
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from messenger.formatters import TimeFormatter
from notification import NotificationMVC
from notification.BaseNotificationView import BaseNotificationView
from notification.settings import LIST_SCROLL_STEP_FACTOR, NOTIFICATION_STATE, NOTIFICATION_GROUP
from gui.shared.formatters import icons
from helpers.i18n import makeString as _ms

class NotificationListView(NotificationsListMeta, BaseNotificationView):

    def __init__(self, _):
        super(NotificationListView, self).__init__()
        self.setModel(NotificationMVC.g_instance.getModel())
        self.__currentGroup = NOTIFICATION_GROUP.INFO
        self.__countersLabels = [''] * 3

    def onClickAction(self, typeID, entityID, action):
        NotificationMVC.g_instance.handleAction(typeID, self._getNotificationID(entityID), action)

    def onGroupChange(self, groupIdx):
        self.__currentGroup = NOTIFICATION_GROUP.ALL[groupIdx]
        self.__setNotificationList()
        self.__updateCounters()

    def getMessageActualTime(self, msTime):
        return TimeFormatter.getActualMsgTimeStr(msTime)

    def _populate(self):
        super(NotificationListView, self)._populate()
        self._model.onNotificationReceived += self.__onNotificationReceived
        self._model.onNotificationUpdated += self.__onNotificationUpdated
        self._model.onNotificationRemoved += self.__onNotificationRemoved
        self.__setInitData()
        self.__setNotificationList()
        self.__updateCounters()

    def _dispose(self):
        if self._model.getDisplayState() == NOTIFICATION_STATE.LIST:
            self._model.setPopupsDisplayState()
        else:
            LOG_ERROR('Invalid state of the Notifications Model')
        self._model.onNotificationReceived -= self.__onNotificationReceived
        self._model.onNotificationUpdated -= self.__onNotificationUpdated
        self._model.onNotificationRemoved -= self.__onNotificationRemoved
        self.cleanUp()
        super(NotificationListView, self)._dispose()

    def __setInitData(self):
        if self._model.getNotifiedMessagesCount(NOTIFICATION_GROUP.INVITE) > 0:
            self.__currentGroup = NOTIFICATION_GROUP.INVITE
        else:
            self.__currentGroup = NOTIFICATION_GROUP.INFO
        self.as_setInitDataS({'scrollStepFactor': LIST_SCROLL_STEP_FACTOR,
         'btnBarSelectedIdx': NOTIFICATION_GROUP.ALL.index(self.__currentGroup),
         'tabsData': {'tabs': [self.__makeTabItemVO(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_INFORMATION_16X16, 16, 16, -4, 0), TOOLTIPS.NOTIFICATIONSVIEW_TAB_INFO), self.__makeTabItemVO(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_INVITATIONS_24X16, 24, 16, -5, 0), TOOLTIPS.NOTIFICATIONSVIEW_TAB_INVITES), self.__makeTabItemVO(icons.makeImageTag(RES_ICONS.MAPS_ICONS_LIBRARY_NOTIF_FILTERS_GIFT_16X16, 16, 16, -4, 0), TOOLTIPS.NOTIFICATIONSVIEW_TAB_OFFERS)]}})

    def __updateCounters(self):

        def formatCount(count):
            return str(count) if count > 0 else ''

        counts = [ formatCount(self._model.getNotifiedMessagesCount(group)) for group in NOTIFICATION_GROUP.ALL ]
        if self.__countersLabels != counts:
            self.__countersLabels = counts
            self.as_updateCountersS(counts)

    def __setNotificationList(self):
        messages = self.__getMessagesList()
        self.as_setMessagesListS({'messages': messages,
         'emptyListText': self.__getEmptyListMsg(len(messages) > 0),
         'btnBarSelectedIdx': NOTIFICATION_GROUP.ALL.index(self.__currentGroup)})
        self._model.resetNotifiedMessagesCount(self.__currentGroup)

    def __getMessagesList(self):
        filtered = [ item for item in self._model.collection.getListIterator() if item.getGroup() == self.__currentGroup ]
        return [ self.__getListVO(item) for item in filtered ]

    def __getEmptyListMsg(self, hasMessages):
        return _ms(MESSENGER.LISTVIEW_EMPTYLIST_TEMPLATE, listType=_ms(MESSENGER.listview_emptylist(self.__currentGroup))) if not hasMessages else ''

    def __onNotificationReceived(self, notification):
        if notification.isAlert():
            NotificationMVC.g_instance.getAlertController().showAlertMessage(notification)
        if notification.getGroup() == self.__currentGroup:
            self.as_appendMessageS(self.__getListVO(notification))
        elif notification.getGroup() == NOTIFICATION_GROUP.INVITE:
            self.__currentGroup = NOTIFICATION_GROUP.INVITE
            self.__setNotificationList()
        elif notification.isNotify():
            self._model.incrementNotifiedMessagesCount(*notification.getCounterInfo())
        self.__updateCounters()

    def __onNotificationUpdated(self, notification, isStateChanged):
        if notification.getGroup() == self.__currentGroup:
            if notification.isOrderChanged():
                self.__setNotificationList()
            else:
                self.as_updateMessageS(self.__getListVO(notification))
        elif notification.getGroup() == NOTIFICATION_GROUP.INVITE:
            self.__currentGroup = NOTIFICATION_GROUP.INVITE
            self.__setNotificationList()
        elif isStateChanged and notification.isNotify():
            self._model.incrementNotifiedMessagesCount(*notification.getCounterInfo())
        self.__updateCounters()

    def __onNotificationRemoved(self, typeID, entityID, groupID):
        if groupID == self.__currentGroup:
            self.__setNotificationList()
        else:
            self._model.decrementNotifiedMessagesCount(groupID, typeID, entityID)
        self.__updateCounters()

    def __makeTabItemVO(self, label, tooltip):
        return {'label': label,
         'tooltip': tooltip}

    def __getListVO(self, notificaton):
        flashId = self._getFlashID(notificaton.getID())
        return notificaton.getListVO(flashId)
