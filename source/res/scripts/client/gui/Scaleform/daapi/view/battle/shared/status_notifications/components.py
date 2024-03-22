# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/status_notifications/components.py
import logging
from gui.Scaleform.genConsts.BATTLE_NOTIFICATIONS_TIMER_TYPES import BATTLE_NOTIFICATIONS_TIMER_TYPES
_logger = logging.getLogger(__name__)

class StatusNotificationContainer(object):

    def __init__(self, orderedItemClasses, updateCallback):
        super(StatusNotificationContainer, self).__init__()
        self._items = [ itemClass(updateCallback=self.__onItemUpdated) for itemClass in orderedItemClasses ]
        self.__updateCallback = updateCallback
        for item in self._items:
            item.start()

    def destroy(self):
        self.__updateCallback = None
        while self._items:
            item = self._items.pop()
            item.destroy()

        self._items = None
        return

    def getItemsData(self):
        return [ item.getVO() for item in self._items if item.isVisible() ]

    def __onItemUpdated(self):
        self.__updateCallback(self.getItemsData())


class Comp7StatusNotificationContainer(StatusNotificationContainer):
    _COMP7_TIMER_ROLE_EFFECTS_PRIORITY = (BATTLE_NOTIFICATIONS_TIMER_TYPES.STUN, BATTLE_NOTIFICATIONS_TIMER_TYPES.COMP7_AOE_HEAL, BATTLE_NOTIFICATIONS_TIMER_TYPES.COMP7_AOE_INSPIRE)

    def getItemsData(self):
        items = [ item for item in self._items if item.isVisible() ]
        items.sort(key=self.typeIDPriority)
        return [ item.getVO() for item in items ]

    def typeIDPriority(self, item):
        typeID = item.getViewTypeID()
        if typeID == StatusNotificationsGroup.GROUP_VIEW_ITEM_ID:
            return -3
        aoeTimer = typeID in (BATTLE_NOTIFICATIONS_TIMER_TYPES.COMP7_AOE_HEAL, BATTLE_NOTIFICATIONS_TIMER_TYPES.COMP7_AOE_INSPIRE)
        if aoeTimer and item.isSourceVehicle():
            return -2
        try:
            return self._COMP7_TIMER_ROLE_EFFECTS_PRIORITY.index(typeID)
        except ValueError:
            return -1


class StatusNotificationItem(object):
    NOT_CHANGE_DEFAULT_ICON = ''

    def __init__(self, updateCallback):
        super(StatusNotificationItem, self).__init__()
        self.__updateCallback = updateCallback
        self._isPulseVisible = False
        self._vo = {'typeID': self.getViewTypeID(),
         'title': '',
         'description': '',
         'totalTime': 0.0,
         'currentTime': 0.0,
         'iconName': self.NOT_CHANGE_DEFAULT_ICON,
         'iconSmallName': self.NOT_CHANGE_DEFAULT_ICON,
         'pulseVisible': self._getIsPulseVisible()}
        self._isVisible = False

    def start(self):
        pass

    def getItemID(self):
        raise NotImplementedError

    def getViewTypeID(self):
        raise NotImplementedError

    def isVisible(self):
        return self._isVisible

    def getVO(self):
        self._vo['pulseVisible'] = self._getIsPulseVisible()
        return self._vo

    def destroy(self):
        self.__updateCallback = None
        return

    def _setVisible(self, value):
        wasVisible = self.isVisible()
        self._isVisible = value
        if wasVisible != self.isVisible():
            self._sendUpdate()

    def _sendUpdate(self):
        self.__updateCallback()

    def _getIsPulseVisible(self):
        return self._isPulseVisible


class StatusNotificationsGroup(StatusNotificationItem):
    GROUP_ITEM_ID = 'snGroup'
    GROUP_VIEW_ITEM_ID = 'snGroup'

    def __init__(self, notificationClasses, updateCallback):
        super(StatusNotificationsGroup, self).__init__(updateCallback)
        self.__items = [ nc(self.__onItemUpdated) for nc in notificationClasses ]
        self.__visibleItem = None
        return

    def start(self):
        for item in self.__items:
            item.start()

    def updateItems(self, updater):
        for item in self.__items:
            updater(item)

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

    def getVO(self):
        if self.__visibleItem is None:
            _logger.warning('Attempt to get group data when there are no visible items inside!')
            return super(StatusNotificationsGroup, self).getVO()
        else:
            return self.__visibleItem.getVO()

    def __onItemUpdated(self):
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
