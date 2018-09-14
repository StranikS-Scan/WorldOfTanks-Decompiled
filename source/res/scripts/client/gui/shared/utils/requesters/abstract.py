# Embedded file name: scripts/client/gui/shared/utils/requesters/abstract.py
import BigWorld
from helpers import isPlayerAccount
from gui.shared.utils import code2str
from adisp import async, process
from debug_utils import LOG_ERROR
from gui.Scaleform.Waiting import Waiting
from gui.shared.utils.decorators import ReprInjector

class AbstractRequester(object):
    """
    Abstract requester for server data caches. Contains cache
    member dict, common request and response methods.
    """

    def __init__(self):
        self.__synced = False
        self.__cache = dict()

    def _response(self, resID, value, callback):
        """
        Common server response method. Must be called ANYWAY after
        server operation will complete.
        
        @param resID: request result id
        @param value: requested value
        @param callback: function to be called after operation will complete
        """
        self.__synced = resID >= 0
        if resID < 0:
            LOG_ERROR('[class %s] There is error while getting data from cache: %s[%d]' % (self.__class__.__name__, code2str(resID), resID))
            return callback(dict())
        callback(dict(value))

    @async
    def _requestCache(self, callback = None):
        """
        Empty request method. Just call response without
        any data requesting.
        """
        self._response(0, {}, callback)

    @async
    @process
    def request(self, callback = None):
        """
        Public request method. Validate player entity to request
        possibility and itself as single callback argument.
        """
        self.__synced = False
        if not isPlayerAccount():
            yield lambda callback: callback(None)
            LOG_ERROR('[class %s] Player is not account.' % self.__class__.__name__)
        else:
            self.__cache = yield self._requestCache()
        callback(self)

    def isSynced(self):
        return self.__synced

    def clear(self):
        self.__cache.clear()

    def getCacheValue(self, key, defaultValue = None):
        """
        Public interface method to get value from cache.
        
        @param key: value's key in cache
        @param defaultValue: default value if key does not exist
        @return: value
        """
        return self.__cache.get(key, defaultValue)


@ReprInjector.simple(('getWaitingID', 'waitingID'), ('getRequestType', 'requestType'))

class RequestCtx(object):

    def __init__(self, waitingID = ''):
        self._waitingID = waitingID
        self._callback = None
        return

    def getRequestType(self):
        return 0

    def getWaitingID(self):
        return self._waitingID

    def setWaitingID(self, waitingID):
        if not self.isProcessing():
            self._waitingID = waitingID
        else:
            LOG_ERROR('In processing', self)

    def isProcessing(self):
        return self._callback is not None

    def startProcessing(self, callback = None):
        if len(self._waitingID):
            Waiting.show(self._waitingID)
        if callback is not None and callable(callback):
            self._callback = callback
        return

    def stopProcessing(self, result = False):
        if self._callback is not None:
            self._callback(result)
            self._callback = None
        if len(self._waitingID):
            Waiting.hide(self._waitingID)
        return

    def onResponseReceived(self, code):
        if code < 0:
            LOG_ERROR('Server return error for request', code, self)
        self.stopProcessing(result=code >= 0)

    def clear(self):
        self._callback = None
        return

    def getCooldown(self):
        return 0.0


class DataRequestCtx(RequestCtx):

    def stopProcessing(self, result = False, data = None):
        if self._callback is not None:
            self._callback(result, data)
            self._callback = None
        if len(self._waitingID):
            Waiting.hide(self._waitingID)
        return


class RequestsByIDProcessor(object):

    def __init__(self):
        super(RequestsByIDProcessor, self).__init__()
        self._requests = {}

    def init(self):
        pass

    def fini(self):
        self.stopProcessing()

    def stopProcessing(self):
        while len(self._requests):
            _, data = self._requests.popitem()
            data[0].stopProcessing(False)

    def getSender(self):
        raise NotImplementedError

    def doRequest(self, ctx, methodName, *args, **kwargs):
        result, _ = self._sendRequest(ctx, methodName, [], *args, **kwargs)
        if result:
            ctx.startProcessing()
        return result

    def doRequestChain(self, ctx, chain):
        result, _ = self._sendNextRequest(ctx, chain)
        if result:
            ctx.startProcessing()
        return result

    def doRequestEx(self, ctx, callback, methodName, *args, **kwargs):
        result, _ = self._sendRequest(ctx, methodName, [], *args, **kwargs)
        if result:
            ctx.startProcessing(callback)
        return result

    def doRequestChainEx(self, ctx, callback, chain):
        result, _ = self._sendNextRequest(ctx, chain)
        if result:
            ctx.startProcessing(callback)
        return result

    def doRawRequest(self, methodName, *args, **kwargs):
        sender = self.getSender()
        method = getattr(sender, methodName)
        result = False
        if callable(method):
            method(*args, **kwargs)
            result = True
        else:
            LOG_ERROR('Name of method is invalid', methodName)
        return result

    def _onResponseReceived(self, requestID, result):
        if requestID > 0:
            ctx, chain = self._requests.pop(requestID, (None, None))
            if ctx is not None:
                if result and len(chain):
                    BigWorld.callback(ctx.getCooldown(), lambda : self._sendNextRequest(ctx, chain))
                    return
                ctx.stopProcessing(result)
        else:
            self.stopProcessing()
        return

    def _sendRequest(self, ctx, methodName, chain, *args, **kwargs):
        result, requestID = False, 0
        requester = self.getSender()
        if not requester:
            return (result, requestID)
        else:
            method = getattr(requester, methodName, None)
            if callable(method):
                requestID = method(*args, **kwargs)
                if requestID > 0:
                    self._requests[requestID] = (ctx, chain)
                    result = True
                else:
                    LOG_ERROR('Request ID can not be null')
            else:
                LOG_ERROR('Name of method is invalid', methodName)
            return (result, requestID)

    def _sendNextRequest(self, ctx, chain):
        methodName, args, kwargs = chain[0]
        return self._sendRequest(ctx, methodName, chain[1:], *args, **kwargs)


class DataRequestsByIDProcessor(RequestsByIDProcessor):

    def __init__(self):
        super(DataRequestsByIDProcessor, self).__init__()
        self._requestID = 0

    def _sendRequest(self, ctx, methodName, chain, *args, **kwargs):
        result, requestID = False, 0
        requester = self.getSender()
        if not requester:
            return (result, requestID)
        else:
            method = getattr(requester, methodName, None)
            if callable(method):
                requestID = self.__getNextRequestID()
                if requestID > 0:
                    method(requestID, *args, **kwargs)
                    self._requests[requestID] = (ctx, chain)
                    result = True
                else:
                    LOG_ERROR('Request ID can not be nil')
            else:
                LOG_ERROR('Name of method is invalid', methodName)
            return (result, requestID)

    def _onResponseReceived(self, requestID, result, data):
        if requestID > 0:
            ctx, chain = self._requests.pop(requestID, (None, None))
            if ctx is not None:
                if result and len(chain):
                    self._sendNextRequest(ctx, chain)
                    return
                ctx.stopProcessing(result, data)
        else:
            self.stopProcessing()
        return

    def __getNextRequestID(self):
        self._requestID += 1
        return self._requestID
