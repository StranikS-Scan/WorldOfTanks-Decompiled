# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/entitlements/entitlements_requester.py
import copy
import logging
import typing
from adisp import adisp_process
from gui.wgcg.agate.contexts import AgateGetInventoryEntitlementsCtx
from helpers import dependency
from helpers.CallbackDelayer import CallbackDelayer
from skeletons.gui.web import IWebController
if typing.TYPE_CHECKING:
    from typing import List
_logger = logging.getLogger(__name__)

class EntitlementsRequester(object):

    def __init__(self):
        self.__requests = []

    def clear(self):
        for request in self.__requests:
            request.clear()

        self.__requests = []

    def requestByCodes(self, codes, retryTimes=None, callback=None):
        ctx = AgateGetInventoryEntitlementsCtx(AgateGetInventoryEntitlementsCtx.createFilterByCodes(codes))
        existingRequest = self.__findRequest(ctx)
        if existingRequest:
            existingRequest.addCallback(callback)
        else:
            request = _EntitlementsRequest(ctx, callback, retryTimes, self.__onRequestDone)
            self.__requests.append(request)
            request.send()

    def __onRequestDone(self, ctx):
        request = self.__findRequest(ctx)
        if request:
            request.clear()
            self.__requests.remove(request)

    def __findRequest(self, ctx):
        for request in self.__requests:
            if request.hasSameContext(ctx):
                return request

        return None


class _EntitlementsRequest(object):
    __DEFAULT_RETRY_TIMES = [2,
     3,
     5,
     8,
     13]
    __web = dependency.descriptor(IWebController)

    def __init__(self, ctx, callback, retryTimes, finishedCallback):
        self.__ctx = ctx
        self.__retryTimes = copy.copy(self.__DEFAULT_RETRY_TIMES) if retryTimes is None else retryTimes
        self.__callbacks = [callback]
        self.__onFinished = finishedCallback
        self.__delayer = None
        return

    def clear(self):
        self.__clear()

    def hasSameContext(self, ctx):
        return self.__ctx.getRequestType() == ctx.getRequestType() and ctx.getEntitlementsFilter() == self.__ctx.getEntitlementsFilter()

    def addCallback(self, callback):
        self.__callbacks.append(callback)

    @adisp_process
    def send(self):
        _logger.debug('Sending request entitlements request: %r, retry times left: %r', self.__ctx.getRequestType(), self.__retryTimes)
        response = yield self.__web.sendRequest(ctx=self.__ctx)
        if response.isSuccess():
            result = self.__formatResult(response.data)
            self.__sendResult(True, result)
        elif not self.__skipRetry(response):
            retryTime = self.__getNextRetryTime()
            if retryTime:
                self.__getDelayer().delayCallback(retryTime, self.send)
            else:
                self.__sendResult(False, {})
        else:
            self.__sendResult(False, {})

    def __getDelayer(self):
        if self.__delayer is None:
            self.__delayer = CallbackDelayer()
        return self.__delayer

    def __sendResult(self, isSuccess, result):
        for callback in self.__callbacks:
            callback((isSuccess, result))

        self.__onFinished(self.__ctx)

    def __skipRetry(self, response):
        return 500 <= response.code <= 511

    def __getNextRetryTime(self):
        return self.__retryTimes.pop(0) if self.__retryTimes else 0

    def __clear(self):
        self.__ctx = None
        self.__retryTimes = []
        self.__callbacks = []
        if self.__delayer:
            self.__delayer.destroy()
            self.__delayer = None
        return

    @staticmethod
    def __formatResult(result):
        balance = result.get('balance', [])
        return {entInfo['code']:entInfo for entInfo in balance}
