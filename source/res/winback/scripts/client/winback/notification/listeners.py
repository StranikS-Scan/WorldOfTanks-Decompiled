# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: winback/scripts/client/winback/notification/listeners.py
from helpers import dependency
from notification.listeners import BaseReminderListener
from notification.settings import NOTIFICATION_TYPE
from skeletons.gui.game_control import IWinbackController
from skeletons.gui.shared import IItemsCache
from winback.notification.decorators import WinbackSelectableRewardReminderDecorator

class WinbackSelectableRewardReminder(BaseReminderListener):
    __winbackController = dependency.descriptor(IWinbackController)
    __itemsCache = dependency.descriptor(IItemsCache)
    __ENTITY_ID = 0

    def __init__(self):
        super(WinbackSelectableRewardReminder, self).__init__(NOTIFICATION_TYPE.WINBACK_SELECTABLE_REWARD_AVAILABLE, self.__ENTITY_ID)

    def start(self, model):
        result = super(WinbackSelectableRewardReminder, self).start(model)
        if result:
            self.__addListeners()
            self.__tryNotify()
        return result

    def stop(self):
        self.__removeListeners()
        super(WinbackSelectableRewardReminder, self).stop()

    def _createDecorator(self, _):
        return WinbackSelectableRewardReminderDecorator(self._getNotificationId())

    def __addListeners(self):
        self.__itemsCache.onSyncCompleted += self.__tryNotify
        self.__winbackController.onStateUpdated += self.__tryNotify

    def __removeListeners(self):
        self.__itemsCache.onSyncCompleted -= self.__tryNotify
        self.__winbackController.onStateUpdated -= self.__tryNotify

    def __tryNotify(self, *_):
        isAdding = self.__winbackController.hasWinbackOfferGiftToken() and self.__winbackController.isFinished()
        self._notifyOrRemove(isAdding)
