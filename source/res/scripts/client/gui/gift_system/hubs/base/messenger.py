# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/base/messenger.py
import typing
from gui.gift_system.constants import GiftMessageType
from gui.gift_system.hubs.subsystems import BaseMessegesDelayer
from gui.gift_system.wrappers import ifMessagesEnabled, ifMessagesAllowed
if typing.TYPE_CHECKING:
    from helpers.server_settings import GiftEventConfig
    from gui.gift_system.wrappers import GiftsHistoryData, IncomeSysMessage, SendGiftResponse

class IGiftEventMessenger(BaseMessegesDelayer):

    def isMessagesEnabled(self):
        raise NotImplementedError

    def isMessagesSuspended(self, *args, **kwargs):
        raise NotImplementedError

    def setMessagesAllowed(self, isMessagesAllowed):
        raise NotImplementedError

    def pushHistoryMessage(self, history):
        raise NotImplementedError

    def pushIncomeMessage(self, incomeData):
        raise NotImplementedError

    def pushOutcomeMessage(self, outcomeData):
        raise NotImplementedError


class GiftEventBaseMessenger(IGiftEventMessenger):
    __slots__ = ('__isMessagesAllowed',)

    def __init__(self, eventSettings, isMessagesAllowed):
        super(GiftEventBaseMessenger, self).__init__(eventSettings)
        self._msgHandlers.update({GiftMessageType.HISTORY: self._pushHistoryMessage,
         GiftMessageType.INCOME: self._pushIncomeMessage,
         GiftMessageType.OUTCOME: self._pushOutcomeMessage})
        self.__isMessagesAllowed = isMessagesAllowed

    def isMessagesEnabled(self):
        return not self._settings.isDisabled

    def isMessagesSuspended(self, *args, **kwargs):
        return not self.__isMessagesAllowed

    def setMessagesAllowed(self, isMessagesAllowed):
        self.__isMessagesAllowed = isMessagesAllowed
        if not self.isMessagesSuspended():
            self._processMessagesQueue()

    @ifMessagesEnabled
    @ifMessagesAllowed(GiftMessageType.HISTORY)
    def pushHistoryMessage(self, history):
        self._pushHistoryMessage(history)

    @ifMessagesEnabled
    @ifMessagesAllowed(GiftMessageType.INCOME)
    def pushIncomeMessage(self, incomeData):
        self._pushIncomeMessage(incomeData)

    @ifMessagesEnabled
    @ifMessagesAllowed(GiftMessageType.OUTCOME)
    def pushOutcomeMessage(self, outcomeData):
        self._pushOutcomeMessage(outcomeData)

    def updateSettings(self, eventSettings):
        super(GiftEventBaseMessenger, self).updateSettings(eventSettings)
        if not self.isMessagesEnabled():
            self._clearMessagesQueue()

    def _pushHistoryMessage(self, history):
        pass

    def _pushIncomeMessage(self, incomeData):
        pass

    def _pushOutcomeMessage(self, outcomeData):
        pass
