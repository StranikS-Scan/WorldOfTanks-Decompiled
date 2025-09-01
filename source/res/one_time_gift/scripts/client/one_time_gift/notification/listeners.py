# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: one_time_gift/scripts/client/one_time_gift/notification/listeners.py
import uuid
from PlayerEvents import g_playerEvents
from account_helpers import AccountSettings
from account_helpers.AccountSettings import OTG_BATTLES_PLAYED_BEFORE_START, OTG_REWARD_AVAILABLE_NOTIFICATION_SHOWN
from gui.impl.lobby.gf_notifications.cache import getCache
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from notification.listeners import BaseReminderListener
from notification.settings import NOTIFICATION_TYPE, NotificationData
from skeletons.gui.shared import IItemsCache
from one_time_gift.gui.impl.lobby import OTG_REWARD_AVAILABLE_NOTIFICATION
from one_time_gift.gui.shared.lock_overlays import areNotificationsLockedByOTG
from one_time_gift.notification.decorators import RewardAvailableDecorator
from one_time_gift.skeletons.gui.game_control import IOneTimeGiftController

class RewardAvailableListener(BaseReminderListener):
    __oneTimeGiftController = dependency.descriptor(IOneTimeGiftController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __ENTITY_ID = 0

    def __init__(self):
        super(RewardAvailableListener, self).__init__(NOTIFICATION_TYPE.OTG_REWARD_AVAILABLE, self.__ENTITY_ID)

    def start(self, model):
        result = super(RewardAvailableListener, self).start(model)
        if result:
            self.__oneTimeGiftController.onSettingsChanged += self.__tryNotify
            self.__oneTimeGiftController.onEntryPointUpdated += self.__tryNotify
            self.__oneTimeGiftController.onPlayerOTGStatusChanged += self.__tryNotify
            g_playerEvents.onDossiersResync += self.__tryNotify
            self.__tryNotify()
        return result

    def stop(self):
        g_playerEvents.onDossiersResync -= self.__tryNotify
        self.__oneTimeGiftController.onPlayerOTGStatusChanged -= self.__tryNotify
        self.__oneTimeGiftController.onEntryPointUpdated -= self.__tryNotify
        self.__oneTimeGiftController.onSettingsChanged -= self.__tryNotify
        super(RewardAvailableListener, self).stop()

    def _createNotificationData(self, priority, **ctx):
        gfDataID = str(uuid.uuid4())
        getCache().setPayload(gfDataID, {})
        data = {'gfDataID': gfDataID}
        return NotificationData(self._getNotificationId(), data, priority, None)

    def _createDecorator(self, data):
        return RewardAvailableDecorator(data.entityID, data.savedData, self._model(), OTG_REWARD_AVAILABLE_NOTIFICATION, data.priorityLevel)

    def __tryNotify(self, *args, **kwargs):
        if not self.__oneTimeGiftController.isEntryPointEnabled:
            self._notifyOrRemove(isAdding=False)
            return
        if areNotificationsLockedByOTG():
            return
        battlesCount = self.__itemsCache.items.getAccountDossier().getRandomStats().getBattlesCount()
        battlesBeforeEventStart = AccountSettings.getUIFlag(OTG_BATTLES_PLAYED_BEFORE_START)
        if not self.__oneTimeGiftController.isEntryPointShown:
            priority = NotificationPriorityLevel.HIGH
            self.__oneTimeGiftController.markEntryPointShown()
        elif battlesCount - battlesBeforeEventStart >= self.__oneTimeGiftController.getRemindBattlesAmount() and not AccountSettings.getUIFlag(OTG_REWARD_AVAILABLE_NOTIFICATION_SHOWN):
            priority = NotificationPriorityLevel.HIGH
            AccountSettings.setUIFlag(OTG_REWARD_AVAILABLE_NOTIFICATION_SHOWN, True)
            self._notifyOrRemove(isAdding=False)
        else:
            priority = NotificationPriorityLevel.LOW
        self._notifyOrRemove(isAdding=True, priority=priority)
