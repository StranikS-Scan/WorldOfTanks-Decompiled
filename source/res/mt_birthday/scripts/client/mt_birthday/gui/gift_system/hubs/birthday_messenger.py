# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/gift_system/hubs/birthday_messenger.py
from gui import SystemMessages
from gui.gift_system.hubs.base.messenger import GiftEventBaseMessenger
from gui.gift_system.constants import GifterResponseState
from gui.gift_system.wrappers import SendGiftResponse, IncomeSysMessage
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from mt_birthday.birthday_constants import BIRTHDAY_2025_STAMP_CODE_SPECIAL
from mt_birthday.skeletons.mt_birthday_controller import ITanksBirthdayController
from mt_birthday.birthday_constants import BirthdayLootBoxes

class GiftEventBirthdayMessenger(GiftEventBaseMessenger):
    __birthdayController = dependency.descriptor(ITanksBirthdayController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, *args, **kwargs):
        super(GiftEventBirthdayMessenger, self).__init__(*args, **kwargs)
        self.__birthdayController.userInfoHelper.onNamesReceived += self.__onNamesReceived
        self.__errorPlayers = {}
        self.__parcelSenders = {}

    def _pushIncomeMessage(self, incomeData):
        name = self.__birthdayController.userInfoHelper.getUserName(incomeData.senderID, withEmptyName=True)
        if not name:
            self.__parcelSenders[incomeData.senderID] = incomeData.giftItemID
            self.__birthdayController.userInfoHelper.syncUsersInfo()
        else:
            self.__pushBoxesSystemMessage(incomeData.giftItemID, name)
        self.__birthdayController.pushNewGiftReceived(incomeData.giftItemID, 1)

    def __pushBoxesSystemMessage(self, boxID, playerName, boxCount=1):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
        if lootBox is None or lootBox.getType() not in (BirthdayLootBoxes.SMALL, BirthdayLootBoxes.LARGE):
            return
        else:
            lootBoxName = lootBox.getUserName()
            text = backport.text(R.strings.mt_birthday.notification.lootBox.body(), player=playerName, lootBoxName=lootBoxName, count=boxCount)
            header = backport.text(R.strings.mt_birthday.notification.lootBox.header())
            messageType = SystemMessages.SM_TYPE.InformationHeader
            self.__pushSystemMessage(text, messageType, header, NotificationPriorityLevel.LOW)
            return

    def __clearPlayers(self):
        self.__errorPlayers = {}

    def destroy(self):
        self.__birthdayController.userInfoHelper.onNamesReceived -= self.__onNamesReceived
        self.__clearPlayers()
        self.__parcelSenders = None
        super(GiftEventBirthdayMessenger, self).destroy()
        return

    def __onNamesReceived(self, receivedNames):
        for spaId in self.__errorPlayers:
            name = receivedNames.get(spaId)
            if name:
                self.__errorPlayers[spaId] = name

        self.__preprocessPartialSending()
        for spaId, lootBoxID in list(self.__parcelSenders.items()):
            name = receivedNames.get(spaId)
            if name:
                self.__pushBoxesSystemMessage(lootBoxID, name)
                self.__parcelSenders.pop(spaId)

    def __preprocessPartialSending(self):
        if self.__errorPlayers and all(self.__errorPlayers.values()):
            self.__pushPartialSendingMessage()
            self.__clearPlayers()

    def __pushPartialSendingMessage(self):
        text = backport.text(R.strings.mt_birthday.notification.error.partialSending.body(), players=', '.join(self.__errorPlayers.values()))
        messageType = SystemMessages.SM_TYPE.InformationHeader
        header = backport.text(R.strings.mt_birthday.notification.error.partialSending.header())
        self.__pushSystemMessage(text, messageType, header)

    def __pushErrorDefaultSending(self):
        text = backport.text(R.strings.mt_birthday.notification.error.defaultSending.body())
        header = backport.text(R.strings.mt_birthday.notification.error.defaultSending.header())
        messageType = SystemMessages.SM_TYPE.ErrorHeader
        self.__pushSystemMessage(text, messageType, header)

    def __pushSuccessSending(self, outcomeData):
        if outcomeData.entitlementCode == BIRTHDAY_2025_STAMP_CODE_SPECIAL:
            text = backport.text(R.strings.mt_birthday.notification.successSending.special.body(), parcelCount=len(outcomeData.receiverIDs))
        else:
            text = backport.text(R.strings.mt_birthday.notification.successSending.body(), parcelCount=len(outcomeData.receiverIDs), posStampCount=len(outcomeData.receiverIDs))
        header = backport.text(R.strings.mt_birthday.notification.successSending.header())
        messageType = SystemMessages.SM_TYPE.InformationHeader
        self.__pushSystemMessage(text, messageType, header)

    def _pushOutcomeMessage(self, outcomeData):
        if outcomeData.declinedReceivers:
            for spaId in outcomeData.declinedReceivers:
                name = self.__birthdayController.userInfoHelper.getUserName(spaId, withEmptyName=True)
                if not name:
                    self.__errorPlayers[spaId] = None
                    self.__birthdayController.userInfoHelper.syncUsersInfo()
                self.__errorPlayers[spaId] = name

            self.__preprocessPartialSending()
        elif outcomeData.state == GifterResponseState.WEB_FAILURE:
            self.__pushErrorDefaultSending()
        else:
            self.__pushSuccessSending(outcomeData)
        return

    def _pushHistoryMessage(self, history):
        for giftID, count in history.aggregated.iteritems():
            self.__birthdayController.pushNewGiftReceived(giftID, count)

    def __pushSystemMessage(self, text, messageType, header, priority=NotificationPriorityLevel.MEDIUM):
        SystemMessages.pushMessage(text=text, type=messageType, priority=priority, messageData={'header': header})
