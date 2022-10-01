# Python bytecode 2.7 (decompiled from Python 2.7)
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
        pass


class RequestsController(object):

    def __init__(self, requester, cooldowns=_NoCooldownsManager()):
        self._requester = requester
        self._cooldowns = cooldowns
        self._waiters = {}
        self.__rqQueue = []
        self.__rqCallbackID = None
        self.__rqCtx = None
        self.__rqHandler = None
        self.__singulizer = RequestSingulizer()
        return

    def fini(self):
        self.stopProcessing()
        self.__singulizer.clear()
        if self._requester:
            self._requester.fini()
            self._requester = None
        return

    def stopProcessing(self):
        self.__rqQueue = []
        self.__clearWaiters()
        self.__clearDelayedRequest()
        if self._requester is not None:
            self._requester.stopProcessing()
        return

    def request(self, ctx, callback=lambda *args: None, allowDelay=None):
        LOG_DEBUG('Send server request', self.__class__.__name__, ctx, callback, allowDelay)
        if allowDelay is None:
            allowDelay = bool(self._cooldowns.getCommonCooldown())
        requestType = ctx.getRequestType()
        handler = self._getHandlerByRequestType(requestType)
        if handler:
            cooldown = ctx.getCooldown()

            def _doRequest():
                self.__clearDelayedRequest()
                cb = partial(self.__callbackWrapper, ctx, callback, cooldown)
                if handler(ctx, callback=cb):
                    self._waiters[requestType] = BigWorld.callback(self._getRequestTimeOut(), partial(self.__onTimeout, cb, requestType, ctx))
                    self._cooldowns.process(requestType, cooldown)

            if not allowDelay:
                if self._cooldowns.validate(requestType, cooldown):
                    self.__doRequestError(ctx, 'cooldown', callback)
                else:
                    _doRequest()
            else:
                if not self.__singulizer.register(ctx, callback):
                    self.__rqQueue.append((requestType, ctx, _doRequest))
                self.__doNextRequest()
        else:
            self.__doRequestError(ctx, 'handler not found', callback)
        return

    def isInCooldown(self, requestTypeID):
        return self._cooldowns.isInProcess(requestTypeID)

    def getCooldownTime(self, requestTypeID):
        return self._cooldowns.getTime(requestTypeID)

    def isProcessing(self, requestTypeID):
        return requestTypeID in self._waiters

    def hasHandler(self, requestTypeID):
        return self._getHandlerByRequestType(requestTypeID) is not None

    def _getHandlerByRequestType(self, requestTypeID):
        raise NotImplementedError

    def _getRequestTimeOut(self):
        pass

    def __callbackWrapper(self, ctx, callback, cooldown, *args):
        requestType = ctx.getRequestType()
        callbackID = self._waiters.pop(requestType, None)
        if callbackID is not None:
            safeCancelCallback(callbackID)
        self._cooldowns.adjust(requestType, cooldown)
        if callback:
            callback(*args)
        self.__singulizer.processResult(ctx, args)
        self.__doNextRequest(adjustCooldown=cooldown)
        return

    def __doNextRequest(self, adjustCooldown=None):
        if self.__rqQueue and self.__rqCallbackID is None:
            requestType, ctx, request = self.__rqQueue.pop(0)
            cooldownLeft = self._cooldowns.getTime(requestType)
            if cooldownLeft:
                self.__loadDelayedRequest(cooldownLeft, ctx, request)
            else:
                request()
        elif adjustCooldown is not None and self.__rqCallbackID is not None:
            self.__loadDelayedRequest(adjustCooldown, self.__rqCtx, self.__rqHandler)
        return

    def __clearWaiters(self):
        if self._waiters is not None:
            while self._waiters:
                _, callbackID = self._waiters.popitem()
                safeCancelCallback(callbackID)

        return

    def __onTimeout(self, cb, requestType, ctx):
        LOG_ERROR('Request timed out', self, requestType, ctx)
        self.__doRequestError(ctx, 'time out', cb)

    def __doRequestError(self, ctx, msg, callback=None):
        if self._requester:
            self._requester.stopWithFailure(ctx, msg, callback)
        LOG_ERROR(msg, ctx)
        return False

    def __loadDelayedRequest(self, seconds, ctx, request):
        self.__clearDelayedRequest()
        self.__rqCtx = ctx
        self.__rqHandler = request
        self.__rqCtx.startProcessing()
        self.__rqCallbackID = BigWorld.callback(seconds, request)

    def __clearDelayedRequest(self):
        if self.__rqCallbackID is not None:
            safeCancelCallback(self.__rqCallbackID)
            self.__rqCallbackID = None
        if self.__rqCtx is not None:
            self.__rqCtx.stopProcessing()
            self.__rqCtx = None
        if self.__rqHandler is not None:
            self.__rqHandler = None
        return


class RequestSingulizer(object):

    def __init__(self):
        self.__requestCallbacks = {}

    def clear(self):
        self.__requestCallbacks.clear()

    def register(self, ctx, callback):
        key = ctx.getSingulizerKey()
        if key is not None:
            if key in self.__requestCallbacks:
                LOG_DEBUG('Adding consequent callback', key)
                self.__requestCallbacks[key].append(callback)
                return True
            LOG_DEBUG('Adding first callback', key)
            self.__requestCallbacks[key] = []
        return False

    def processResult(self, ctx, args):
        key = ctx.getSingulizerKey()
        if key in self.__requestCallbacks:
            LOG_DEBUG('Retrieved results for singularized request', key, ', total saved calls:', len(self.__requestCallbacks[key]))
            for clb in self.__requestCallbacks[key]:
                clb(*args)

            del self.__requestCallbacks[key]
