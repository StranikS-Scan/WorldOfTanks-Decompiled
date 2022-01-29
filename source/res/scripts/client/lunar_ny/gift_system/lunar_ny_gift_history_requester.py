# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/lunar_ny/gift_system/lunar_ny_gift_history_requester.py
import logging
from collections import namedtuple, OrderedDict
import AccountCommands
import BigWorld
from account_helpers import isLongDisconnectedFromCenter
from adisp import async, process
from constants import REQUEST_COOLDOWN
_logger = logging.getLogger(__name__)
RequestResult = namedtuple('RequestResult', ('success', 'data'))
GIFT_HISTORY_REQUEST_COOLDOWN = REQUEST_COOLDOWN.GIFTS_HISTORY_LOAD * 2
COUNT_GIFT_HISTORY_REQUEST_COOLDOWN = REQUEST_COOLDOWN.GIFTS_HISTORY_PAGE * 2

class BaseGiftHistoryRequester(object):
    __slots__ = ('__isProcessing', '__callbackID', '__callback')

    def __init__(self):
        self.__isProcessing = False
        self.__callbackID = None
        self.__callback = None
        return

    def request(self, callback=None, **kwargs):
        if self.__isProcessing:
            _logger.warning('GiftHistoryRequester warning! History request in process')
            if callback is not None:
                callback(RequestResult(False, None))
        elif isLongDisconnectedFromCenter():
            if callback is not None:
                callback(RequestResult(False, None))
        else:
            self.__isProcessing = True
            self.__callback = callback
            self.__invoke()
        return

    def stop(self):
        if self.__callbackID is not None:
            BigWorld.cancelCallback(self.__callbackID)
            self.__callbackID = None
        self.__isProcessing = False
        if self.__callback is not None:
            callback = self.__callback
            self.__callback = None
            callback(RequestResult(False, None))
        return

    @async
    def _doExternalRequest(self, callback):
        raise NotImplementedError

    def _getInvokeDelay(self):
        raise NotImplementedError

    def _responseData(self, result):
        pass

    @process
    def __invoke(self):
        self.__callbackID = None
        code, ext = yield self._doExternalRequest()
        if code == AccountCommands.RES_COOLDOWN:
            self.__callbackID = BigWorld.callback(self._getInvokeDelay(), self.__invoke)
        else:
            self._responseData(RequestResult(code >= 0, ext))
            self.__isProcessing = False
            if self.__callback is not None:
                callback = self.__callback
                self.__callback = None
                callback(RequestResult(code >= 0, ext))
        return


class CountGiftHistoryRequester(BaseGiftHistoryRequester):
    __slots__ = ('__eventID', '__cache')

    def __init__(self):
        super(CountGiftHistoryRequester, self).__init__()
        self.__eventID = None
        self.__cache = {}
        return

    def request(self, callback=None, eventID=0, **kwargs):
        if eventID in self.__cache:
            if callback is not None:
                callback(self.__cache[eventID])
        else:
            self.__eventID = eventID
            super(CountGiftHistoryRequester, self).request(callback)
        return

    def stop(self):
        super(CountGiftHistoryRequester, self).stop()
        self.__eventID = None
        self.__cache.clear()
        return

    @async
    def _doExternalRequest(self, callback):
        _logger.debug('Make server request to get count of gift history by eventID: %d', self.__eventID)
        BigWorld.player().giftSystem.requestGetCountGiftHistory(self.__eventID, callback)

    def _getInvokeDelay(self):
        return COUNT_GIFT_HISTORY_REQUEST_COOLDOWN

    def _responseData(self, result):
        if result.success:
            self.__cache[self.__eventID] = result
        self.__eventID = None
        return


class GiftHistoryRequester(BaseGiftHistoryRequester):
    __slots__ = ('__lootboxID', '__pageNum', '__column', '__order', '__cache')
    _CACHE_MAX_SIZE = 5

    def __init__(self):
        super(GiftHistoryRequester, self).__init__()
        self.__lootboxID = None
        self.__pageNum = None
        self.__column = None
        self.__order = None
        self.__cache = OrderedDict()
        return

    def request(self, callback=None, lootboxID=0, pageNum=0, column=0, order=0, **kwargs):
        cacheKey = (lootboxID,
         pageNum,
         column,
         order)
        if cacheKey in self.__cache:
            if callback is not None:
                callback(self.__cache[cacheKey])
        else:
            self.__lootboxID = lootboxID
            self.__pageNum = pageNum
            self.__column = column
            self.__order = order
            super(GiftHistoryRequester, self).request(callback)
        return

    def stop(self):
        super(GiftHistoryRequester, self).stop()
        self.__lootboxID = None
        self.__pageNum = None
        self.__column = None
        self.__order = None
        self.__cache.clear()
        return

    @async
    def _doExternalRequest(self, callback):
        _logger.debug('Make server request to get gift history by lootboxID: %d, pageNum: %d, column: %d, order: %d', self.__lootboxID, self.__pageNum, self.__column, self.__order)
        BigWorld.player().giftSystem.requestSelectGiftHistory(self.__lootboxID, self.__pageNum, self.__column, self.__order, callback)

    def _getInvokeDelay(self):
        return GIFT_HISTORY_REQUEST_COOLDOWN

    def _responseData(self, result):
        if result.success:
            cacheKey = (self.__lootboxID,
             self.__pageNum,
             self.__column,
             self.__order)
            self.__cache[cacheKey] = result
            if len(self.__cache) > self._CACHE_MAX_SIZE:
                self.__cache.popitem(last=False)
        self.__lootboxID = None
        self.__pageNum = None
        self.__column = None
        self.__order = None
        return
