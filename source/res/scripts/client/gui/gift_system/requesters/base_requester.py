# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/gift_system/requesters/base_requester.py
import typing
import BigWorld
from adisp import adisp_process, adisp_async

class IGiftSystemRequester(object):

    def destroy(self):
        raise NotImplementedError

    def isProcessing(self):
        raise NotImplementedError

    def request(self, eventIds):
        raise NotImplementedError

    def stop(self):
        raise NotImplementedError


class GiftSystemBaseRequester(IGiftSystemRequester):
    __slots__ = ('__isProcessing', '__reqEventIds', '__callbackID', '__readyCallback')

    def __init__(self, readyCallback):
        self.__isProcessing = False
        self.__reqEventIds = set()
        self.__callbackID = None
        self.__readyCallback = readyCallback
        return

    def destroy(self):
        self.__readyCallback = None
        return

    def isProcessing(self):
        return self.__isProcessing

    def request(self, eventIds):
        if self.__isProcessing:
            self.__reqEventIds |= eventIds
        elif eventIds:
            self.__isProcessing = True
            self.__reqEventIds = eventIds
            self.__invoke()

    def stop(self):
        self.__isProcessing = False
        self.__reqEventIds.clear()
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        return

    def _getInvokeDelay(self):
        raise NotImplementedError

    @adisp_async
    def _doExternalRequest(self, reqEventIds, callback):
        raise NotImplementedError

    @adisp_process
    def __invoke(self):
        self.__callbackID = None
        isSuccess, result = yield self._doExternalRequest(list(self.__reqEventIds))
        if isSuccess and self.__isProcessing:
            self.__reqEventIds -= set(result.keys())
            self.__isProcessing = bool(self.__reqEventIds)
            self.__readyCallback(result)
        if self.__isProcessing:
            self.__callbackID = BigWorld.callback(self._getInvokeDelay(), self.__invoke)
        return
