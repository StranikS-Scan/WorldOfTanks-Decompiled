# Embedded file name: scripts/client/gui/shared/utils/requesters/RequestsController.py
from functools import partial
import BigWorld
from debug_utils import LOG_ERROR, LOG_DEBUG
from shared_utils import safeCancelCallback
from gui.shared.rq_cooldown import RequestCooldownManager, REQUEST_SCOPE

class _NoCooldownsManager(RequestCooldownManager):

    def __init__(self):
        super(_NoCooldownsManager, self).__init__(REQUEST_SCOPE.GLOBAL)

    def lookupName(self, rqTypeID):
        return str(rqTypeID)

    def getDefaultCoolDown(self):
        return 0.0


class RequestsController(object):

    def __init__(self, requester, cooldowns = _NoCooldownsManager()):
        self._requester = requester
        self._cooldowns = cooldowns
        self._waiters = {}
        self._rqQueue = []
        self._rqCallbackID = None
        self._rqCtx = None
        self._rqHandler = None
        return

    def fini(self):
        self.stopProcessing()
        if self._requester:
            self._requester.fini()
            self._requester = None
        return

    def stopProcessing(self):
        self._rqQueue = []
        self._clearWaiters()
        self._clearDelayedRequest()
        if self._requester is not None:
            self._requester.stopProcessing()
        return

    def request(self, ctx, callback = lambda *args: None, allowDelay = None):
        LOG_DEBUG('Send server request', self.__class__.__name__, ctx, callback, allowDelay)
        if allowDelay is None:
            allowDelay = bool(self._cooldowns._commonCooldown)
        requestType = ctx.getRequestType()
        handler = self._getHandlerByRequestType(requestType)
        if handler:
            cooldown = ctx.getCooldown()

            def _doRequest():
                self._clearDelayedRequest()
                cb = partial(self._callbackWrapper, requestType, callback, cooldown)
                if handler(ctx, callback=cb):
                    self._waiters[requestType] = BigWorld.callback(self._getRequestTimeOut(), partial(self._onTimeout, cb, requestType, ctx))
                    self._cooldowns.process(requestType, cooldown)

            if not allowDelay:
                if self._cooldowns.validate(requestType, cooldown):
                    self._doRequestError(ctx, 'cooldown', callback)
                else:
                    _doRequest()
            else:
                self._rqQueue.append((requestType, ctx, _doRequest))
                self._doNextRequest()
        else:
            self._doRequestError(ctx, 'handler not found', callback)
        return

    def isInCooldown(self, requestTypeID):
        return self._cooldowns.isInProcess(requestTypeID)

    def getCooldownTime(self, requestTypeID):
        return self._cooldowns.getTime(requestTypeID)

    def isProcessing(self, requestTypeID):
        return requestTypeID in self._waiters

    def hasHandler(self, requestTypeID):
        return self._getHandlerByRequestType(requestTypeID) is not None

    def _doNextRequest(self, adjustCooldown = None):
        if len(self._rqQueue) and self._rqCallbackID is None:
            requestType, ctx, request = self._rqQueue.pop(0)
            cooldownLeft = self._cooldowns.getTime(requestType)
            if cooldownLeft:
                self._loadDelayedRequest(cooldownLeft, ctx, request)
            else:
                request()
        elif adjustCooldown and self._rqCallbackID is not None:
            self._loadDelayedRequest(adjustCooldown, self._rqCtx, self._rqHandler)
        return

    def _getHandlerByRequestType(self, requestTypeID):
        raise NotImplementedError

    def _getRequestTimeOut(self):
        return 30.0

    def _callbackWrapper(self, requestType, callback, cooldown, *args):
        callbackID = self._waiters.pop(requestType, None)
        if callbackID is not None:
            safeCancelCallback(callbackID)
        self._cooldowns.adjust(requestType, cooldown)
        if callback:
            callback(*args)
        self._doNextRequest(adjustCooldown=cooldown)
        return

    def _clearWaiters(self):
        if self._waiters is not None:
            while len(self._waiters):
                _, callbackID = self._waiters.popitem()
                safeCancelCallback(callbackID)

        return

    def _onTimeout(self, cb, requestType, ctx):
        LOG_ERROR('Request timed out', self, requestType, ctx)
        self._doRequestError(ctx, 'time out', cb)

    def _doRequestError(self, ctx, msg, callback = None):
        if self._requester:
            self._requester._stopProcessing(ctx, msg, callback)
        LOG_ERROR(msg, ctx)
        return False

    def _loadDelayedRequest(self, seconds, ctx, request):
        self._clearDelayedRequest()
        self._rqCtx = ctx
        self._rqHandler = request
        self._rqCtx.startProcessing()
        self._rqCallbackID = BigWorld.callback(seconds, request)

    def _clearDelayedRequest(self):
        if self._rqCallbackID is not None:
            safeCancelCallback(self._rqCallbackID)
            self._rqCallbackID = None
        if self._rqCtx is not None:
            self._rqCtx.stopProcessing()
            self._rqCtx = None
        if self._rqHandler is not None:
            self._rqHandler = None
        return
