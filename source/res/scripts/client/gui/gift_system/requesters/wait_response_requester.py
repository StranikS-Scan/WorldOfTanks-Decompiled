# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/requesters/wait_response_requester.py
import typing
import logging
import BigWorld
from functools import partial
from adisp import adisp_async, adisp_process
from gui.clientgw.gift_system.contexts import GiftSystemWaitResponseCtx
from helpers import dependency
from helpers.time_utils import getTimestampFromISO, ONE_MINUTE
from skeletons.gui.web import IWebController
_SERVICE_AVAILABILITY = 0.5
_CLIENTGW_INAVAILABILITY = 2
_WGGG_INAVAILABILITY = ONE_MINUTE

class IGiftSystemWaitResponseRequester(object):

    def _getInvokeDelay(self):
        raise NotImplementedError

    @adisp_async
    @adisp_process
    def _doExternalRequest(self, reqEventId, spaID, metaInfo, callback):
        raise NotImplementedError


class GiftSystemWaitResponseRequester(IGiftSystemWaitResponseRequester):
    __slots__ = ('__isProcessing', '__callbackID', '__waitResponseLimit', '__responseCallback')
    __webController = dependency.descriptor(IWebController)

    def __init__(self, responseCallback):
        self.__isProcessing = False
        self.__callbackID = None
        self.__waitResponseLimit = None
        self.__responseCallback = responseCallback
        return

    def destroy(self):
        self.__responseCallback = None
        self.__waitResponseLimit = None
        return

    def isProcessing(self):
        return self.__isProcessing

    def request(self, eventId, spaID, getUpdatedAtAfter=None, getUpdatedAtBefore=None):
        isCorrectParams = getUpdatedAtAfter < getUpdatedAtBefore if getUpdatedAtBefore and getUpdatedAtAfter else True
        if not isCorrectParams:
            logging.error('Request params is not correct.')
            return
        if self.__isProcessing:
            logging.warning('Waiting response players is already requested.')
        else:
            self.__isProcessing = True
            metaInfo = {}
            if getUpdatedAtAfter:
                metaInfo.update({'updated_at_after': getUpdatedAtAfter})
            if getUpdatedAtBefore:
                metaInfo.update({'updated_at_before': getUpdatedAtBefore})
            self.__invoke(eventId, spaID, metaInfo)

    def stop(self):
        self.__isProcessing = False
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def setWaiResponseLimit(self, limit):
        self.__waitResponseLimit = limit

    def isWaitResponseLimitSet(self):
        return bool(self.__waitResponseLimit)

    @adisp_process
    def __invoke(self, eventId, spaID, metaInfo=None):
        self.__callbackID = None
        isSuccess, result = yield self._doExternalRequest(eventId, spaID, metaInfo)
        invokeDelay = self._getInvokeErrorDelay()
        if isSuccess and self.__isProcessing:
            invokeDelay = self._getInvokeDelay()
            if len(result.players) == self.__waitResponseLimit:
                metaInfo.update({'updated_at_before': getTimestampFromISO(result.firstPlayerUpdatedAt)})
            else:
                self.__isProcessing = False
        self.__responseCallback(eventId, result)
        if self.__isProcessing:
            self.__callbackID = BigWorld.callback(invokeDelay, partial(self.__invoke, eventId, spaID, metaInfo))
        return

    def _getInvokeDelay(self):
        return _SERVICE_AVAILABILITY

    def _getInvokeErrorDelay(self):
        return _WGGG_INAVAILABILITY if self.__webController.isAvailable() else _CLIENTGW_INAVAILABILITY

    @adisp_async
    @adisp_process
    def _doExternalRequest(self, reqEventId, spaID, metaInfo, callback):
        if not self.__webController.isAvailable():
            callback((False, {}))
            return
        else:
            requestCtx = GiftSystemWaitResponseCtx(reqEventId, spaID, metaInfo)
            result = yield self.__webController.sendRequest(requestCtx)
            callback((result.isSuccess(), requestCtx.getDataObj(result.data) if result.isSuccess() else None))
            return
