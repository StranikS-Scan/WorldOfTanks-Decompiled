# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/battle_royale/status_notifications/components.py
import logging
_logger = logging.getLogger(__name__)

class BaseNotificationContainer(object):

    def __init__(self, orderedItemClasses):
        super(BaseNotificationContainer, self).__init__()
        self._items = [ itmClazz(updateCallback=self._onItemUpdated) for itmClazz in orderedItemClasses ]

    def destroy(self):
        while self._items:
            item = self._items.pop()
            item.destroy()

        self._items = None
        return

    def getItemsData(self):
        return [ item.getVO() for item in self._items if item.isVisible() ]

    def _onItemUpdated(self, itemID):
        pass


class StatusNotificationContainer(BaseNotificationContainer):

    def __init__(self, orderedItemClasses, updateCallback):
        super(StatusNotificationContainer, self).__init__(orderedItemClasses)
        self.__updateCallback = updateCallback

    def destroy(self):
        self.__updateCallback = None
        super(StatusNotificationContainer, self).destroy()
        return

    def _onItemUpdated(self, itemID):
        self.__updateCallback(self.getItemsData())


class StatusNotificationItem(object):

    def __init__(self, updateCallback):
        super(StatusNotificationItem, self).__init__()
        self.__updateCallback = updateCallback
        self._vo = {'typeID': self.getViewTypeID(),
         'title': '',
         'description': '',
         'totalTime': 0.0,
         'currentTime': 0.0}
        self._isVisible = False

    def getItemID(self):
        raise NotImplementedError

    def getViewTypeID(self):
        raise NotImplementedError

    def isVisible(self):
        return self._isVisible

    def getVO(self):
        return self._vo

    def destroy(self):
        self.__updateCallback = None
        return

    def _hide(self):
        self._setVisible(False)

    def _setVisible(self, value):
        if self._isVisible != value:
            self._isVisible = value
            self._sendUpdate()

    def _sendUpdate(self):
        self.__updateCallback(self.getItemID())


class StatusNotificationsGroup(StatusNotificationItem):
    GROUP_ITEM_ID = 'snGroup'
    GROUP_VIEW_ITEM_ID = 'snGroup'

    def __init__(self, notificationClasses, updateCallback):
        super(StatusNotificationsGroup, self).__init__(updateCallback)
        self.__items = [ nc(self.__onItemUpdated) for nc in notificationClasses ]
        self.__visibleItem = None
        return

    def getItemID(self):
        return self.GROUP_ITEM_ID

    def getViewTypeID(self):
        return self.GROUP_VIEW_ITEM_ID

    def destroy(self):
        self.__visibleItem = None
        while self.__items:
            itm = self.__items.pop()
            itm.destroy()

        super(StatusNotificationsGroup, self).destroy()
        return

    def __onItemUpdated(self, _):
        for itm in self.__items:
            if itm.isVisible():
                self._isVisible = True
                self.__visibleItem = itm
                break
        else:
            self._isVisible = False
            self.__visibleItem = None

        self._sendUpdate()
        return

    def getVO(self):
        if self.__visibleItem is None:
            _logger.warning('Attempt to get group data when there are no visible items inside!')
            return super(StatusNotificationsGroup, self).getVO()
        else:
            return self.__visibleItem.getVO()
