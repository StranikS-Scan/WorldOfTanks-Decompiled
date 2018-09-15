# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/restore_contoller.py
import operator
import time
from operator import itemgetter
import BigWorld
import Event
from account_helpers.AccountSettings import AccountSettings, LAST_RESTORE_NOTIFICATION
from debug_utils import LOG_DEBUG
from gui import SystemMessages
from gui.shared.gui_items import GUI_ITEM_TYPE
from gui.shared.money import MONEY_UNDEFINED
from gui.shared.utils.requesters.ItemsRequester import REQ_CRITERIA
from gui.shared.utils.requesters.ItemsRequester import IntCDProtectionRequestCriteria
from gui.shared.utils.scheduled_notifications import Notifiable, PeriodicNotifier
from helpers import dependency
from helpers import time_utils
from skeletons.gui.game_control import IRestoreController
from skeletons.gui.shared import IItemsCache
DEFAULT_MAX_TANKMEN_BUFFER_LENGTH = 100

@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def getTankmenRestoreInfo(tankman, itemsCache=None):
    config = itemsCache.items.shop.tankmenRestoreConfig
    dismissalLength = time_utils.getTimeDeltaTilNow(tankman.dismissedAt)
    price = config.cost if dismissalLength >= config.freeDuration else MONEY_UNDEFINED
    return (price, config.billableDuration - dismissalLength)


def _hasLimitedRestore(item):
    return item.hasLimitedRestore()


def _doRestoreFilter(item):
    return item.hasRestoreCooldown() or item.hasLimitedRestore()


class RestoreController(IRestoreController, Notifiable):
    itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        """
        RestoreController send event onRestoreChangeNotify on restore left time change
        """
        super(RestoreController, self).__init__()
        self.__eventManager = Event.EventManager()
        self.__restoreNotifyTimeCallback = None
        self.__vehiclesForUpdate = []
        self.__tankmenList = []
        self.__tankmanLiveTime = None
        self.__maxTankmenBufferLength = DEFAULT_MAX_TANKMEN_BUFFER_LENGTH
        self.__checkForNotify = False
        self.__waitNextUpdate = False
        self.onRestoreChangeNotify = Event.Event(self.__eventManager)
        self.onTankmenBufferUpdated = Event.Event(self.__eventManager)
        LOG_DEBUG('PATCH FOR WOTD-91767 IS APPLIED')
        return

    def init(self):
        self.itemsCache.onSyncCompleted += self._update
        self.addNotificator(PeriodicNotifier(self.__getClosestTankmanUpdateTime, self.__updateTankmenList))

    def onLobbyInited(self, _):
        self.__tankmanLiveTime = self.itemsCache.items.shop.tankmenRestoreConfig.billableDuration
        if self.__restoreNotifyTimeCallback is None and not self.__waitNextUpdate:
            self.__startRestoreTimeNotifyCallback()
        self.__checkLimitedRestoreNotification()
        return

    def onAvatarBecomePlayer(self):
        self._stop()

    def onConnected(self):
        self.__checkForNotify = False

    def onDisconnected(self):
        self._stop()

    def fini(self):
        self._stop()
        self.clearNotification()
        self.itemsCache.onSyncCompleted -= self._update
        super(RestoreController, self).fini()

    def getMaxTankmenBufferLength(self):
        return self.__maxTankmenBufferLength

    def getDismissedTankmen(self):
        return self.__tankmenList

    def getTankmenBeingDeleted(self, newTankmenCount=1):
        """
          returns tankmen which will be deleted from buffer in case it will be overflowed (maximum
          buffer size is exceeded) after insertion in it specified number of tankmen
        :param newTankmenCount: number of tankmen being added to buffer
        :return: list of tankmen which will be deleted from buffer
        """
        result = []
        tankmenCountToDelete = len(self.__tankmenList) + newTankmenCount - self.__maxTankmenBufferLength
        if tankmenCountToDelete > 0:
            result = self.__tankmenList[-1 * tankmenCountToDelete:]
        return result

    def getTankmenDeletedBySelling(self, vehicle):
        """
        returns tankmen which would be deleted from buffer and added to it after
        vehicle sell operation:
        :param vehicle: vehicle being sold
        :return:
               - list of tankmen which will be added to buffer
               - list of tankmen which will be deleted from buffer in case if buffer is overflowed
        """
        newTankmen = [ tankman for _, tankman in vehicle.crew if tankman is not None and tankman.isRestorable() ]
        return (newTankmen, self.getTankmenBeingDeleted(len(newTankmen)))

    def _stop(self):
        self.__clearRestoreTimeNotifyCallback()
        self.__vehiclesForUpdate = None
        self.__eventManager.clear()
        self.stopNotification()
        self.__tankmenList = []
        return

    def _update(self, _, invalidItems):
        restoreConfig = self.itemsCache.items.shop.tankmenRestoreConfig
        self.__maxTankmenBufferLength = restoreConfig.limit
        self.__tankmanLiveTime = restoreConfig.billableDuration
        if invalidItems == {} or any([ tmanID < 0 for tmanID in invalidItems.get(GUI_ITEM_TYPE.TANKMAN, []) ]):
            self.__updateTankmenList()
        self.__clearRestoreTimeNotifyCallback()
        self.__startRestoreTimeNotifyCallback()

    def __startRestoreTimeNotifyCallback(self):
        self.__vehiclesForUpdate = []
        criteria = IntCDProtectionRequestCriteria(_doRestoreFilter, self.itemsCache.items.recycleBin.getVehiclesIntCDs())
        restoreVehicles = self.itemsCache.items.getVehicles(criteria).values()
        notificationList = []
        for vehicle in restoreVehicles:
            if vehicle.hasRestoreCooldown():
                delta = vehicle.restoreInfo.getRestoreCooldownTimeLeft()
            else:
                delta = vehicle.restoreInfo.getRestoreTimeLeft()
            if delta > 0:
                if delta > time_utils.ONE_DAY:
                    period = time_utils.ONE_DAY
                elif delta > time_utils.ONE_HOUR:
                    period = time_utils.ONE_HOUR
                else:
                    period = delta
                notificationList.append((vehicle.intCD, delta % period or period))

        if notificationList:
            _, nextRestoreNotification = min(notificationList, key=itemgetter(1))
            for vehCD, timeDelta in notificationList:
                if timeDelta == nextRestoreNotification:
                    self.__vehiclesForUpdate.append(vehCD)

            nextRestoreNotification = max(nextRestoreNotification, 0)
        else:
            self.__waitNextUpdate = True
            return
        self.__waitNextUpdate = False
        self.__restoreNotifyTimeCallback = BigWorld.callback(nextRestoreNotification, self.__notifyRestoreTime)

    def __notifyRestoreTime(self):
        self.__restoreNotifyTimeCallback = None
        self.onRestoreChangeNotify(self.__vehiclesForUpdate)
        self.__startRestoreTimeNotifyCallback()
        return

    def __clearRestoreTimeNotifyCallback(self):
        if self.__restoreNotifyTimeCallback is not None:
            BigWorld.cancelCallback(self.__restoreNotifyTimeCallback)
            self.__restoreNotifyTimeCallback = None
        return

    def __updateTankmenList(self):
        tankmen = self.itemsCache.items.getTankmen(REQ_CRITERIA.TANKMAN.DISMISSED).values()
        self.__tankmenList = sorted(tankmen, key=operator.attrgetter('dismissedAt'), reverse=True)
        self.startNotification()
        self.onTankmenBufferUpdated()

    def __getClosestTankmanUpdateTime(self):
        if self.__tankmenList:
            timeOfClosestDeletion = self.__tankmenList[-1].dismissedAt + self.__tankmanLiveTime
            return time_utils.getTimeDeltaFromNow(timeOfClosestDeletion) + 1

    def __checkLimitedRestoreNotification(self):
        criteria = IntCDProtectionRequestCriteria(_hasLimitedRestore, self.itemsCache.items.recycleBin.getVehiclesIntCDs())
        vehicles = self.itemsCache.items.getVehicles(criteria).values()
        lastRestoreNotification = AccountSettings.getSettings(LAST_RESTORE_NOTIFICATION)
        if lastRestoreNotification is None:
            showMessage = True
        else:
            showMessage = time_utils.getTimeDeltaTilNow(lastRestoreNotification) >= time_utils.ONE_DAY
        if vehicles and showMessage and not self.__checkForNotify:
            AccountSettings.setSettings(LAST_RESTORE_NOTIFICATION, time.time())
            SystemMessages.pushI18nMessage('#system_messages:restoreController/hasLimitedRestoreVehicles', type=SystemMessages.SM_TYPE.Warning)
        self.__checkForNotify = True
        return
