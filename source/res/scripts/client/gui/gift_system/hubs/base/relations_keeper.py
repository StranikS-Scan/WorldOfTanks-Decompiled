# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/hubs/base/relations_keeper.py
import typing
from collections import defaultdict
from gui.gift_system.constants import GiftMessageType, GifterResponseState
from gui.gift_system.hubs.subsystems import BaseMessegesDelayer
from gui.gift_system.wrappers import ifMessagesAllowed, ifMessagesEnabled
from gui.shared.utils.scheduled_notifications import Notifiable, SimpleNotifier
from helpers.time_utils import getCurrentTimestamp
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftsWebState, IncomeSysMessage, SendGiftResponse
    from helpers.server_settings import GiftEventConfig
_DEFAULT_SEND_LIMIT = 1
_ENDLESS_INTERVAL = -2

class IGiftEventKeeper(BaseMessegesDelayer):

    def isMessagesEnabled(self):
        raise NotImplementedError

    def isMessagesSuspended(self, *args, **kwargs):
        raise NotImplementedError

    def getClearingDelta(self):
        raise NotImplementedError

    def getExpirationDelta(self):
        raise NotImplementedError

    def getIncomeRelations(self, implicitCopy=True):
        raise NotImplementedError

    def getOutcomeRelations(self, implicitCopy=True):
        raise NotImplementedError

    def getSendLimit(self):
        raise NotImplementedError

    def processIncomeMessage(self, incomeData):
        raise NotImplementedError

    def processOutcomeMessage(self, outcomeData):
        raise NotImplementedError

    def processWebState(self, webState):
        raise NotImplementedError


class GiftEventBaseKeeper(IGiftEventKeeper, Notifiable):
    __slots__ = ('__clearCallback', '__outcomeRelations', '__incomeRelations', '__currentTimeInterval', '__expireTime', '__expireDelta', '__sendLimit')

    def __init__(self, eventSettings, clearCallback):
        super(GiftEventBaseKeeper, self).__init__(eventSettings)
        self._msgHandlers.update({GiftMessageType.INCOME: self._processIncomeMessage,
         GiftMessageType.OUTCOME: self._processOutcomeMessage})
        self.__clearCallback = clearCallback
        self.__sendLimit = _DEFAULT_SEND_LIMIT
        self.__incomeRelations = defaultdict(int)
        self.__outcomeRelations = defaultdict(int)
        self.__expireTime = self.__expireDelta = None
        self.__currentTimeInterval = _ENDLESS_INTERVAL
        self.addNotificator(SimpleNotifier(self.getClearingDelta, self.__updateExpiredRelations))
        return

    def destroy(self):
        self.clearNotification()
        self.__clearAllRelations()
        self.__clearCallback = None
        super(GiftEventBaseKeeper, self).destroy()
        return

    def isMessagesEnabled(self):
        return self._settings.isEnabled

    def isMessagesSuspended(self, messageData, *args, **kwargs):
        return not self.__isCurrentTimestamp(messageData.executionTime)

    def getClearingDelta(self):
        if self.__currentTimeInterval == _ENDLESS_INTERVAL:
            return 0
        nextExpireTimestamp = self.__expireTime + self.__expireDelta * (self.__currentTimeInterval + 1)
        return nextExpireTimestamp - int(getCurrentTimestamp()) + 1

    def getExpirationDelta(self):
        return self.__expireDelta

    def getIncomeRelations(self, implicitCopy=True):
        return self.__incomeRelations.copy() if implicitCopy else self.__incomeRelations

    def getOutcomeRelations(self, implicitCopy=True):
        return self.__outcomeRelations.copy() if implicitCopy else self.__outcomeRelations

    def getSendLimit(self):
        return self.__sendLimit

    @ifMessagesEnabled
    @ifMessagesAllowed(GiftMessageType.INCOME)
    def processIncomeMessage(self, incomeData):
        self._processIncomeMessage(incomeData)

    @ifMessagesEnabled
    @ifMessagesAllowed(GiftMessageType.OUTCOME)
    def processOutcomeMessage(self, outcomeData):
        self._processOutcomeMessage(outcomeData)

    @ifMessagesEnabled
    def processWebState(self, webState):
        self.__clearAllRelations()
        self.__sendLimit = webState.sendLimit
        self.__expireTime = webState.expireTime
        self.__expireDelta = webState.expireDelta
        self.__updateCurrentTimeInterval()
        self._processWebState(webState)
        self._processMessagesQueue()
        self.startNotification()

    def reset(self):
        super(GiftEventBaseKeeper, self).reset()
        self.stopNotification()
        self.__clearAllRelations()
        self._clearMessagesQueue()
        self.__expireDelta = self.__expireTime = None
        self.__currentTimeInterval = _ENDLESS_INTERVAL
        return

    def updateSettings(self, eventSettings):
        super(GiftEventBaseKeeper, self).updateSettings(eventSettings)
        if not self.isMessagesEnabled():
            self.stopNotification()
            self.__clearAllRelations()
            self._clearMessagesQueue()
            self.__expireDelta = self.__expireTime = None
            self.__currentTimeInterval = _ENDLESS_INTERVAL
        return

    @ifMessagesAllowed(GiftMessageType.INCOME, useQueue=False)
    def _processIncomeMessage(self, incomeData):
        self.__incomeRelations[incomeData.senderID] += 1

    @ifMessagesAllowed(GiftMessageType.OUTCOME, useQueue=False)
    def _processOutcomeMessage(self, outcomeData):
        if outcomeData.outCount is not None:
            self.__outcomeRelations[outcomeData.receiverID] = outcomeData.outCount
        elif outcomeData.state == GifterResponseState.WEB_SUCCESS:
            self.__outcomeRelations[outcomeData.receiverID] += 1
        return

    @ifMessagesAllowed(GiftMessageType.LIMITS, useQueue=False)
    def _processWebState(self, webState):
        packedRelations = webState.state
        for accID, outcome, income in [ packedRelations[i:i + 3] for i in xrange(0, len(packedRelations), 3) ]:
            self.__outcomeRelations[accID] = outcome
            self.__incomeRelations[accID] = income

    def __isCurrentTimestamp(self, timestamp):
        return False if self.__expireDelta is None or self.__expireTime is None else self.__getTimestampInterval(timestamp) == self.__currentTimeInterval

    def __getTimestampInterval(self, timestamp):
        return (timestamp - self.__expireTime) // self.__expireDelta if self.__expireDelta else _ENDLESS_INTERVAL

    def __updateCurrentTimeInterval(self):
        self.__currentTimeInterval = self.__getTimestampInterval(int(getCurrentTimestamp()))

    def __updateExpiredRelations(self):
        self.__clearAllRelations()
        self.__updateCurrentTimeInterval()
        self._processMessagesQueue()
        self.__clearCallback()

    def __clearAllRelations(self):
        self.__outcomeRelations.clear()
        self.__incomeRelations.clear()
