# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/gui_items/processors/offers.py
import cPickle
import logging
from functools import partial
import BigWorld
from AccountCommands import RES_SUCCESS, RES_FAILURE
from gui import SystemMessages
from gui.Scaleform.Waiting import Waiting
from gui.shared.gui_items.processors import Processor, makeI18nError, makeSuccess
from gui.shared.gui_items.processors.plugins import MessageConfirmator
from helpers import dependency
from messenger.formatters.service_channel import QuestAchievesFormatter
from messenger.m_constants import SCH_CLIENT_MSG_TYPE
from skeletons.gui.system_messages import ISystemMessages
_logger = logging.getLogger(__name__)

class ReceiveOfferGiftProcessor(Processor):

    def __init__(self, offerID, giftID, cdnTitle='', skipConfirm=False):
        self.__offerID = offerID
        self.__giftID = giftID
        plugins = [ReceiveGiftConfirmator(offerID, giftID, cdnTitle, isEnabled=not skipConfirm)]
        super(ReceiveOfferGiftProcessor, self).__init__(plugins)

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('loadContent')
        defaultKey = 'offers/server_error'
        return makeI18nError('/'.join((defaultKey, errStr)), defaultKey)

    def _successHandler(self, code, ctx=None):
        Waiting.hide('loadContent')
        msg = QuestAchievesFormatter.formatQuestAchieves(ctx or {}, False)
        if msg is not None:
            SystemMessages.pushMessage(msg, type=SystemMessages.SM_TYPE.OfferGiftBonuses)
        return super(ReceiveOfferGiftProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to receive offer gift. offerID=%s, giftID=%s', self.__offerID, self.__giftID)
        Waiting.show('loadContent')
        BigWorld.player().receiveOfferGift(self.__offerID, self.__giftID, lambda requestID, resultID, errStr, ext=None: self._response(resultID, callback, ctx=ext, errStr=errStr))
        return


class ReceiveGiftConfirmator(MessageConfirmator):

    def __init__(self, offerID, giftID, cdnTitle='', isEnabled=True):
        super(ReceiveGiftConfirmator, self).__init__(None, isEnabled=isEnabled)
        self._offerID = offerID
        self._giftID = giftID
        self._cdnTitle = cdnTitle
        return

    def _gfMakeMeta(self):
        from gui.shared import event_dispatcher
        return partial(event_dispatcher.showOfferGiftDialog, self._offerID, self._giftID, self._cdnTitle)


class ReceiveMultipleOfferGiftsProcessor(Processor):
    ERROR_DEFAULT_KEY = 'offers/server_error'
    ERROR_CODE_MULTI_ERROR = 'MULTI_ERROR'

    def __init__(self, chosenGifts):
        self.__chosenGifts = chosenGifts
        super(ReceiveMultipleOfferGiftsProcessor, self).__init__()

    def _errorHandler(self, code, errStr='', ctx=None):
        Waiting.hide('loadContent')
        return makeI18nError('/'.join((self.ERROR_DEFAULT_KEY, errStr)), self.ERROR_DEFAULT_KEY)

    def _successHandler(self, code, ctx=None):
        Waiting.hide('loadContent')
        successData = ctx.get(RES_SUCCESS)
        if successData:
            msg = QuestAchievesFormatter.formatQuestAchieves(successData, False)
            SystemMessages.pushMessage(msg, type=SystemMessages.SM_TYPE.OfferGiftBonuses)
        failureData = ctx.get(RES_FAILURE)
        if failureData:
            msg = self._errorHandler(code, self.ERROR_CODE_MULTI_ERROR, ctx=failureData)
            SystemMessages.pushMessage(msg.userMsg, msg.sysMsgType)
        return super(ReceiveMultipleOfferGiftsProcessor, self)._successHandler(code, ctx)

    def _request(self, callback):
        _logger.debug('Make server request to receive offers gifts. Choices: %s', self.__chosenGifts)
        Waiting.show('loadContent')
        choices = cPickle.dumps(self.__chosenGifts)
        BigWorld.player().receiveMultipleOfferGifts(choices, lambda requestID, resultID, errStr, ext=None: self._response(resultID, callback, ctx=ext, errStr=errStr))
        return


class BattleMattersOfferProcessor(ReceiveOfferGiftProcessor):
    __systemMessages = dependency.descriptor(ISystemMessages)

    def _successHandler(self, code, ctx=None):
        Waiting.hide('loadContent')
        self.__systemMessages.proto.serviceChannel.pushClientMessage(ctx, SCH_CLIENT_MSG_TYPE.BATTLE_MATTERS_TOKEN_AWARD)
        return makeSuccess(auxData=ctx)
