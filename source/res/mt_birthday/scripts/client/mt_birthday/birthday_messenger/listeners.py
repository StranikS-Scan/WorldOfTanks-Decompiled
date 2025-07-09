# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/birthday_messenger/listeners.py
from adisp import adisp_process
import constants
from chat_shared import SYS_MESSAGE_TYPE
from constants import INVOICE_ASSET
from debug_utils import LOG_ERROR
from gui import SystemMessages
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from gui.wgcg.gold_wagon.contexts import GoldWagonFetchInfoCtx
from helpers import dependency
from lootboxes_common import makeLootboxID
from skeletons.gui.shared import IItemsCache
from skeletons.gui.web import IWebController
from messenger.proto.events import g_messengerEvents
from mt_birthday.birthday_account_settings import getSettings, setSettings
from mt_birthday.birthday_constants import BirthdayStorageKeys, BirthdayLootBoxes
from mt_birthday.birthday_messenger.decorators import BirthdayBonusMessageDecorator, BirthdayGiftCustomMessageDecorator
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from notification.listeners import ExtNotificationListener
from notification.settings import NOTIFICATION_TYPE

class BirthdayBonusLootboxListener(ExtNotificationListener):
    _TAG_IN_PRODUCT = 'birthdayBonusNotification'
    __birthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self):
        super(BirthdayBonusLootboxListener, self).__init__()
        self.__entityId = 1

    def start(self, model):
        model = super(BirthdayBonusLootboxListener, self).start(model)
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__handle
        self.__birthdayController.onLootboxSeen += self.__seenEvent
        self.__birthdayController.onEventSettingsUpdated += self.__onEventSettingsUpdated
        if not self.__birthdayController.isDisabled() and getSettings(BirthdayStorageKeys.BONUS_RECEIVED):
            self.__createMessage()
        return model

    def stop(self):
        self.__birthdayController.onEventSettingsUpdated -= self.__onEventSettingsUpdated
        self.__birthdayController.onLootboxSeen -= self.__seenEvent
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__handle
        super(BirthdayBonusLootboxListener, self).stop()

    def __handle(self, _, message):
        if message is not None and message.type == SYS_MESSAGE_TYPE.invoiceReceived.index() and message.data is not None and message.data and message.data.get('assetType', 0) == INVOICE_ASSET.PURCHASE and self._TAG_IN_PRODUCT in message.data.get('tags', []):
            self.__showMessage(message)
        return

    def __showMessage(self, message):
        model = self._model()
        lootboxID, count = self.__parseMessage(message)
        setSettings(BirthdayStorageKeys.BONUS_RECEIVED, True)
        prevNotification = model.getNotification(NOTIFICATION_TYPE.BIRTHDAY_BONUS, self.__entityId)
        if prevNotification is None:
            newNotification = BirthdayBonusMessageDecorator(self.__entityId, lootboxID, count, count, model)
            model.addNotification(newNotification)
        else:
            prevNotification.setLootBoxID(lootboxID)
            prevNotification.addCount(count)
            model.updateNotification(prevNotification.getType(), self.__entityId, prevNotification.getEntity(), True)
        return

    def __parseMessage(self, message):
        tokens = message.data.get('data', {}).get('tokens', {})
        for tokenId, tokenData in tokens.iteritems():
            if tokenId.startswith(constants.LOOTBOX_TOKEN_PREFIX):
                return (makeLootboxID(tokenId), int(tokenData['count']))

    def __seenEvent(self):
        model = self._model()
        prevNotification = model.getNotification(NOTIFICATION_TYPE.BIRTHDAY_BONUS, self.__entityId)
        if prevNotification is not None:
            prevNotification.resetCount()
            model.updateNotification(prevNotification.getType(), self.__entityId, prevNotification.getEntity(), False)
        return

    def __onEventSettingsUpdated(self):
        model = self._model()
        prevNotification = model.getNotification(NOTIFICATION_TYPE.BIRTHDAY_BONUS, self.__entityId)
        if prevNotification is not None and self.__birthdayController.isDisabled():
            model.removeNotification(NOTIFICATION_TYPE.BIRTHDAY_BONUS, self.__entityId)
        return

    def __createMessage(self):
        newNotification = BirthdayBonusMessageDecorator(self.__entityId, None, 0, 0, self._model())
        self._model().addNotification(newNotification)
        return


class BirthdayGiftLootboxListener(ExtNotificationListener):
    __birthdayController = dependency.descriptor(ITanksBirthdayController)

    def __init__(self):
        super(BirthdayGiftLootboxListener, self).__init__()
        self.__entityId = 1

    def start(self, model):
        model = super(BirthdayGiftLootboxListener, self).start(model)
        self.__birthdayController.onNewGiftsReceived += self.__handle
        self.__birthdayController.onLootboxSeen += self.__seenEvent
        self.__birthdayController.onEventSettingsUpdated += self.__onEventSettingsUpdated
        if not self.__birthdayController.isDisabled():
            self.__handle(self.__birthdayController.getUnseenGiftId(), self.__birthdayController.getNewGiftForNotification(), False)
        return model

    def stop(self):
        self.__birthdayController.onEventSettingsUpdated -= self.__onEventSettingsUpdated
        self.__birthdayController.onLootboxSeen -= self.__seenEvent
        self.__birthdayController.onNewGiftsReceived -= self.__handle
        super(BirthdayGiftLootboxListener, self).stop()

    def __handle(self, lootboxID, count, isSpecialGift):
        if isSpecialGift or not getSettings(BirthdayStorageKeys.GIFT_RECEIVED):
            return
        else:
            model = self._model()
            prevNotification = model.getNotification(NOTIFICATION_TYPE.BIRTHDAY_GIFT, self.__entityId)
            if prevNotification is None:
                newNotification = BirthdayGiftCustomMessageDecorator(self.__entityId, lootboxID, self.__birthdayController.getUnseenGiftsCount(), count, model)
                model.addNotification(newNotification)
            else:
                prevNotification.updateCount(self.__birthdayController.getUnseenGiftsCount(), count)
                model.updateNotification(prevNotification.getType(), self.__entityId, prevNotification.getEntity(), True)
            self.__birthdayController.seenGiftNotification(self.__birthdayController.getUnseenGiftsCount())
            return

    def __seenEvent(self):
        model = self._model()
        prevNotification = model.getNotification(NOTIFICATION_TYPE.BIRTHDAY_GIFT, self.__entityId)
        if prevNotification is not None:
            prevNotification.resetCount()
            model.updateNotification(prevNotification.getType(), self.__entityId, prevNotification.getEntity(), False)
            self.__birthdayController.seenGiftNotification(0)
        return

    def __onEventSettingsUpdated(self):
        model = self._model()
        prevNotification = model.getNotification(NOTIFICATION_TYPE.BIRTHDAY_GIFT, self.__entityId)
        if prevNotification is not None and self.__birthdayController.isDisabled():
            model.removeNotification(NOTIFICATION_TYPE.BIRTHDAY_GIFT, self.__entityId)
        return


class BirthdayLootboxCashBackListener(ExtNotificationListener):
    _TAG_IN_PRODUCT = 'Lootbox:GoldWagon'
    __webController = dependency.descriptor(IWebController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def start(self, model):
        model = super(BirthdayLootboxCashBackListener, self).start(model)
        g_messengerEvents.serviceChannel.onChatMessageReceived += self.__handle
        return model

    def stop(self):
        g_messengerEvents.serviceChannel.onChatMessageReceived -= self.__handle
        super(BirthdayLootboxCashBackListener, self).stop()

    def __handle(self, _, message):
        if message is not None and message.type == SYS_MESSAGE_TYPE.invoiceReceived.index() and message.data is not None and message.data and message.data.get('assetType', 0) == INVOICE_ASSET.PURCHASE and self._TAG_IN_PRODUCT in message.data.get('tags', []):
            self.__showMessage(message)
        return

    @adisp_process
    def __showMessage(self, message):
        result = yield self.__webController.sendRequest(ctx=GoldWagonFetchInfoCtx())
        if not result.isSuccess():
            return
        goldPerContainer = result.data.get('gold_per_container', 0)
        if not goldPerContainer:
            LOG_ERROR('Cannot get gold_per_container')
            return
        lootboxCount = 0
        tokens = message.data.get('data', {}).get('tokens', {})
        for token, value in tokens.iteritems():
            lootBox = self.__itemsCache.items.tokens.getLootBoxByTokenID(token)
            if lootBox and lootBox.getHistoryName() == BirthdayLootBoxes.LARGE:
                lootboxCount += value.get('count', 0)

        if not lootboxCount:
            LOG_ERROR('Cannot count Gold Wagon cashback, lootBox count is 0')
            return
        header = backport.text(R.strings.mt_birthday.notification.goldWagon.cashBack.header())
        text = backport.text(R.strings.mt_birthday.notification.goldWagon.cashBack.text(), value=goldPerContainer * lootboxCount)
        SystemMessages.pushMessage(text=text, type=SystemMessages.SM_TYPE.FinancialTransactionWithGoldHeader, priority=NotificationPriorityLevel.MEDIUM, messageData={'header': header})
