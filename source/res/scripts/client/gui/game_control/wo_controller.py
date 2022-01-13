# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/wo_controller.py
import logging
import random
from functools import partial
import typing
import BigWorld
from account_helpers.AccountSettings import AccountSettings, VIEWED_WO_NOTIFICATIONS
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import event_dispatcher
from helpers import dependency
from helpers.time_utils import ONE_HOUR
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.game_control import IWOController, IHeroTankController
from skeletons.gui.server_events import IEventsCache
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from wo2022.wo_constants import WO_EVENT_DISABLED, WO_OFFER_REMINDER_QUEST_PREFIX, WO_GOTO_AUCTION_ACTION
if typing.TYPE_CHECKING:
    from typing import List
    from gui.server_events.event_items import Quest
_logger = logging.getLogger(__name__)
_LOAD_BALANCE_RANGE = 300
_MIN_DECISION_MAKING_TIME = 60
_REMINDER_DELAY = ONE_HOUR

class WONotificationType(object):
    ANNOUNCE = 1
    REMINDER = 2


class WOController(IWOController):
    _heroTankCtrl = dependency.descriptor(IHeroTankController)
    _systemMessages = dependency.descriptor(ISystemMessages)
    __eventsCache = dependency.descriptor(IEventsCache)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self):
        super(WOController, self).__init__()
        self.__callbacks = {}

    def onLobbyStarted(self, ctx):
        super(WOController, self).onLobbyStarted(ctx)
        self.__eventsCache.onSyncCompleted += self.__onEventsSyncCompleted

    def onConnected(self):
        super(WOController, self).onConnected()
        self._heroTankCtrl.onHeroTankChanged += self._onHeroTankChanged

    def onAvatarBecomePlayer(self):
        super(WOController, self).onAvatarBecomePlayer()
        self._clearCallbacks()
        self.__eventsCache.onSyncCompleted -= self.__onEventsSyncCompleted

    def onDisconnected(self):
        super(WOController, self).onDisconnected()
        self._clearCallbacks()
        self._heroTankCtrl.onHeroTankChanged -= self._onHeroTankChanged
        self.__eventsCache.onSyncCompleted -= self.__onEventsSyncCompleted

    def isAuctionActive(self):
        currentAction = self._heroTankCtrl.getCurrentVehicleAction()
        return currentAction == 'auction' and self.__isAccountEligible()

    def goToAuction(self):
        if not self.isAuctionActive():
            return
        shopUrl = self._heroTankCtrl.getCurrentShopUrl()
        event_dispatcher.showShop(shopUrl)

    def _onHeroTankChanged(self):
        if self.isAuctionActive():
            if self.__checkReminder() is False:
                self._scheduleNotification(WONotificationType.ANNOUNCE, self.__getNextAnnounceDelay())

    def _scheduleNotification(self, notificationType, delay):
        intCD = self._heroTankCtrl.getCurrentTankCD()
        settingsKey = self.__getSettingsKey(notificationType, intCD)
        if settingsKey not in self.__getViewedNotifications() and not self.__hasCallback(settingsKey):
            self.__createCallback(settingsKey, delay, partial(self._pushNotification, notificationType, intCD))
            _logger.info('Schedule notification for %s seconds, type=%s, vehicle=%s, callbackID=%s', delay, notificationType, intCD, settingsKey)

    def _clearCallbacks(self):
        for callbackID in self.__callbacks.values():
            BigWorld.cancelCallback(callbackID)

        self.__callbacks.clear()

    def _pushNotification(self, notificationType, intCD):
        self.__clearCallback(self.__getSettingsKey(notificationType, intCD))
        _logger.info('Show notification type=%s, vehicle=%s', notificationType, intCD)
        if not self.__isAccountEligible():
            return
        else:
            vehicle = self.__itemsCache.items.getItemByCD(intCD)
            if vehicle.isInInventory:
                return
            offerResId = R.strings.wo2022.notifications.currentOffer if notificationType == WONotificationType.ANNOUNCE else R.strings.wo2022.notifications.offerReminder
            self._systemMessages.proto.serviceChannel.pushClientMessage(message=None, msgType=SCH_CLIENT_MSG_TYPE.WO_NOTIFICATION, auxData=[{'header': backport.text(offerResId.header(), vehicleName=vehicle.userName),
              'body': backport.text(offerResId.description()),
              'buttonLabel': backport.text(offerResId.buttonAction()),
              'action': WO_GOTO_AUCTION_ACTION,
              'vehicleName': vehicle.name,
              'intCD': intCD}])
            self.__markNotificationViewed(self.__getSettingsKey(notificationType, intCD))
            return

    def __isAccountEligible(self):
        return WO_EVENT_DISABLED not in self.__eventsCache.questsProgress.getTokensData()

    def __onEventsSyncCompleted(self):
        self.__checkReminder()

    def __checkReminder(self):
        self.__clearCallback(WONotificationType.REMINDER)
        if not self.isAuctionActive():
            return False
        timeTillOfferEnd = self.__getClosestStartTime(self.__reminderQuestsPredicate)
        if timeTillOfferEnd > 0:
            if _MIN_DECISION_MAKING_TIME < timeTillOfferEnd < _REMINDER_DELAY:
                self.__clearCallback(self.__getSettingsKey(WONotificationType.ANNOUNCE, self._heroTankCtrl.getCurrentTankCD()))
                self._scheduleNotification(WONotificationType.REMINDER, self.__getNextReminderDelay(timeTillOfferEnd))
                return True
            if timeTillOfferEnd > _REMINDER_DELAY:
                self.__createCallback(WONotificationType.REMINDER, timeTillOfferEnd - _REMINDER_DELAY, self.__checkReminder)
        return False

    def __getClosestStartTime(self, predicate):
        quests = self.__eventsCache.getHiddenQuests(predicate)
        if quests:
            closestQuest = min(quests.values(), key=lambda item: item.getStartTimeLeft())
            return closestQuest.getStartTimeLeft()

    @staticmethod
    def __getViewedNotifications():
        return AccountSettings.getNotifications(VIEWED_WO_NOTIFICATIONS)

    def __markNotificationViewed(self, settingsKey):
        viewedNotifications = self.__getViewedNotifications()
        if settingsKey not in viewedNotifications:
            viewedNotifications.append(settingsKey)
            AccountSettings.setNotifications(VIEWED_WO_NOTIFICATIONS, viewedNotifications)

    @staticmethod
    def __reminderQuestsPredicate(quest):
        return quest.getStartTimeLeft() > 0 and quest.getID().startswith(WO_OFFER_REMINDER_QUEST_PREFIX)

    @staticmethod
    def __getNextAnnounceDelay():
        return random.random() * _LOAD_BALANCE_RANGE

    @staticmethod
    def __getNextReminderDelay(timeLeft):
        elapsedTime = _REMINDER_DELAY - timeLeft
        return 0 if elapsedTime > _LOAD_BALANCE_RANGE else random.random() * (_LOAD_BALANCE_RANGE - elapsedTime)

    @staticmethod
    def __getSettingsKey(notificationType, intCD):
        return 'n_{type}_{cd}'.format(type=notificationType, cd=intCD)

    def __createCallback(self, key, delay, callback):
        self.__clearCallback(key)
        self.__callbacks[key] = BigWorld.callback(delay, callback)

    def __hasCallback(self, key):
        return key in self.__callbacks

    def __clearCallback(self, key):
        callbackID = self.__callbacks.get(key)
        if callbackID:
            _logger.info('Clear callback id=%s', key)
            BigWorld.cancelCallback(callbackID)
            del self.__callbacks[key]
