# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/new_year/ny_messenger.py
import logging
import typing
from collections import defaultdict
from gui import SystemMessages
from gui.gift_system.constants import GiftMessageType, GifterResponseState
from gui.gift_system.hubs.base.messenger import GiftEventBaseMessenger
from gui.impl import backport
from gui.impl.gen import R
from gui.shared import g_eventBus
from gui.shared.events import GiftSystemOperationEvent
from gui.shared.gui_items.loot_box import NewYearLootBoxes, NewYearCategories
from gui.shared.formatters import text_styles
from helpers import dependency
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.shared import IItemsCache
from skeletons.gui.system_messages import ISystemMessages
from skeletons.new_year import INewYearController
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftsHistoryData, IncomeSysMessage, SendGiftResponse
_logger = logging.getLogger(__name__)

class GiftEventNYMessenger(GiftEventBaseMessenger):
    __slots__ = ()
    __itemsCache = dependency.descriptor(IItemsCache)
    __nyController = dependency.descriptor(INewYearController)
    __systemMessages = dependency.descriptor(ISystemMessages)

    def isMessagesEnabled(self):
        return self.__nyController.isEnabled()

    def _pushHistoryMessage(self, history):
        for boxID, boxCount in ((bID, bCount) for bID, bCount in history.aggregated.iteritems() if bCount > 0):
            self.__pushBoxesSystemMessage(boxID, boxCount)

    def _pushIncomeMessage(self, incomeData):
        self.__pushBoxesSystemMessage(incomeData.giftItemID, 1)

    def _pushIncomeMessages(self, incomeDataList):
        aggregate = defaultdict(int)
        for incomeData in incomeDataList:
            aggregate[incomeData.giftItemID] += 1

        for boxID, boxCount in aggregate.iteritems():
            self.__pushBoxesSystemMessage(boxID, boxCount)

    def _pushOutcomeMessage(self, outcomeData):
        if outcomeData.state == GifterResponseState.WEB_FAILURE:
            errorText = backport.text(R.strings.ny.giftSystem.notification.error.defaultSending())
            SystemMessages.pushMessage(errorText, type=SystemMessages.SM_TYPE.GiftSystemError)
        else:
            ctx = {'eventID': self._settings.eventID,
             'userID': outcomeData.receiverID}
            g_eventBus.handleEvent(GiftSystemOperationEvent(GiftSystemOperationEvent.GIFT_SENT, ctx=ctx))

    def _processMessagesQueue(self):
        incomeMessages = []
        for mType, mData in self._msgQueue:
            if mType not in self._msgHandlers:
                continue
            if mType == GiftMessageType.INCOME:
                incomeMessages.append(mData)
                continue
            self._msgHandlers[mType](mData)

        if incomeMessages:
            self._pushIncomeMessages(incomeMessages)
        self._clearMessagesQueue()

    def __pushBoxSystemMessage(self, header, body, count, category=''):
        auxData = {'header': header,
         'body': body,
         'category': category,
         'count': count}
        self.__systemMessages.proto.serviceChannel.pushClientMessage(message=None, msgType=SCH_CLIENT_MSG_TYPE.NEW_NY_LOOT_BOXES, auxData=[auxData])
        return

    def __pushBoxesSystemMessage(self, boxID, boxCount):
        lootBox = self.__itemsCache.items.tokens.getLootBoxByID(boxID)
        if lootBox is None or lootBox.getType() not in (NewYearLootBoxes.COMMON, NewYearLootBoxes.SPECIAL):
            return
        else:
            if lootBox.getType() == NewYearLootBoxes.COMMON:
                if self._settings.isDisabled:
                    self.__pushNYCommonBoxMessage(boxCount)
                else:
                    self.__pushGiftCommonBoxMessage(boxCount)
            elif not self._settings.isDisabled:
                self.__pushSurpriseBoxMessage(boxCount)
            return

    def __pushGiftCommonBoxMessage(self, boxCount):
        header = backport.text(R.strings.ny.notification.lootBox.header.newYear_usual())
        body = backport.text(R.strings.ny.notification.lootBox.body.newYear_usual())
        self.__pushBoxSystemMessage(header, body, boxCount)

    def __pushNYCommonBoxMessage(self, boxCount):
        header = backport.text(R.strings.ny.notification.lootBox.header.small())
        body = backport.text(R.strings.ny.notification.lootBox.body.default())
        self.__pushBoxSystemMessage(header, body, boxCount)

    def __pushSurpriseBoxMessage(self, boxCount):
        header = backport.text(R.strings.ny.notification.lootBox.header.newYear_special())
        body = text_styles.neutral(backport.text(R.strings.ny.notification.lootBox.body.newYear_special()))
        self.__pushBoxSystemMessage(header, body, boxCount, NewYearCategories.SPECIAL)
