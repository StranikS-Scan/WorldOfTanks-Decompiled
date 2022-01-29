# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/gift_system/hubs/lunar_ny_messenger.py
import logging
import typing
from gui import SystemMessages
from gui.gift_system.constants import GiftMessageType, GifterResponseState
from gui.gift_system.hubs.base.messenger import GiftEventBaseMessenger
from gui.impl import backport
from gui.impl.gen import R
from gui.shared.notifications import NotificationPriorityLevel
from gui.shared.view_helpers import UsersInfoHelper
from helpers import dependency
from lunar_ny import ILunarNYController
from lunar_ny.lunar_ny_constants import ENVELOPE_ENTITLEMENT_CODE_TO_TYPE
if typing.TYPE_CHECKING:
    from gui.gift_system.wrappers import GiftsHistoryData, IncomeSysMessage, SendGiftResponse
_logger = logging.getLogger(__name__)

class GiftLunarNYMessenger(GiftEventBaseMessenger):
    __lunarNyController = dependency.descriptor(ILunarNYController)
    __slots__ = ('__userInfoHelper',)

    def __init__(self, eventSettings, isMessagesAllowed):
        super(GiftLunarNYMessenger, self).__init__(eventSettings, isMessagesAllowed)
        self.__userInfoHelper = UsersInfoHelper()

    def __repr__(self):
        return 'GiftLunarNYMessenger id={}'.format(self._settings.eventID)

    def _pushHistoryMessage(self, history):
        giftIDs = set()
        senderIDs = set()
        sumCount = 0
        for giftID, sendersInfo in history.aggregated.iteritems():
            giftIDs.add(giftID)
            for senderID, count in sendersInfo.iteritems():
                senderIDs.add(senderID)
                sumCount += count

        if sumCount > 0:
            self.__pushReceivedEnvelopesMsg(senderIDs=senderIDs, count=sumCount, giftIDs=giftIDs)

    def _pushIncomeMessage(self, incomeData):
        self.__pushReceivedEnvelopesMsg(senderIDs={incomeData.senderID}, count=1, giftIDs={incomeData.giftItemID})

    def _pushOutcomeMessage(self, outcomeData):
        isSuccess = outcomeData is not None and outcomeData.state == GifterResponseState.WEB_SUCCESS
        receiverID = outcomeData.receiverID if isSuccess else None
        sendEnvelope = R.strings.lunar_ny.systemMessage.sendEnvelope
        if isSuccess:
            envelopeType = ENVELOPE_ENTITLEMENT_CODE_TO_TYPE[outcomeData.entitlementCode]
            envelopeTypeStr = backport.text(sendEnvelope.dyn(envelopeType.name)())
            if receiverID == -1:
                msg = backport.text(sendEnvelope.toRandomUser(), envelopeType=envelopeTypeStr)
            else:
                msg = backport.text(sendEnvelope.toFriend(), envelopeType=envelopeTypeStr, nickName=self.__userInfoHelper.getUserName(receiverID, withEmptyName=True))
            msgType = SystemMessages.SM_TYPE.MessageHeader
            msgData = {'header': backport.text(sendEnvelope.header())}
        else:
            msg = backport.text(sendEnvelope.error())
            msgType = SystemMessages.SM_TYPE.ErrorSimple
            msgData = None
        SystemMessages.pushMessage(msg, msgType, NotificationPriorityLevel.MEDIUM, messageData=msgData)
        return

    def _processMessagesQueue(self):
        giftIDs = set()
        senderIDs = set()
        sumCount = 0
        for mType, mData in self._msgQueue:
            if mType == GiftMessageType.INCOME:
                senderIDs.add(mData.senderID)
                sumCount += 1
                giftIDs.add(mData.giftItemID)
            if mType == GiftMessageType.HISTORY:
                for giftID, sendersInfo in mData.aggregated.iteritems():
                    giftIDs.add(giftID)
                    for senderID, count in sendersInfo.iteritems():
                        senderIDs.add(senderID)
                        sumCount += count

            if mType in self._msgHandlers:
                self._msgHandlers[mType](mData)

        if sumCount > 0:
            self.__pushReceivedEnvelopesMsg(senderIDs=senderIDs, count=sumCount, giftIDs=giftIDs)
        self._clearMessagesQueue()

    def __pushReceivedEnvelopesMsg(self, senderIDs, count, giftIDs):
        if self.__lunarNyController.isActive():
            self.__lunarNyController.receivedEnvelopes.pushNewReceivedEnvelopes(senderIDs, count, giftIDs)
