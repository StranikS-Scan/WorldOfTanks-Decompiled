# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/requester.py
import typing
import sys
import async
from BWUtil import AsyncReturn
from gui.Scaleform.Waiting import Waiting
from gui.platform.base import logger
from gui.platform.base.request import Request
from gui.platform.base.settings import REQUEST_TIMEOUT
from ids_generators import SequenceIDGenerator
if typing.TYPE_CHECKING:
    from gui.platform.base.request import Params

class Pending(object):
    __slots__ = ('_event', '_request', '_response', '_logger')

    def __init__(self, request):
        self._event = async.AsyncEvent()
        self._request = request
        self._response = request.params.response.createUnexpectedError('Failed to send request')
        self._logger = logger.getWithContext(instance=self)
        self._logger.debug('Initialized.')

    @async.async
    def wait(self):
        try:
            yield async.await(self._event.wait())
        except async.BrokenPromiseError:
            self._logger.debug('Event was destroyed while waiting for event.')

        raise AsyncReturn(self._response)

    @property
    def requestId(self):
        return self._request.requestId

    def release(self, response=None):
        self._response = response or self._response
        self._logger.debug('Releasing with: %s.', self._response)
        self._event.set()
        self._event.destroy()
        self._request.cancel()


class PlatformRequester(object):

    def __init__(self):
        self._pendings = {}
        self._reqIdGen = SequenceIDGenerator(highBound=sys.maxint)
        self._logger = logger.getWithContext(instance=self)

    def clear(self):
        for pending in self._pendings.itervalues():
            pending.release()

        self._pendings.clear()
        self._logger.debug('Pendings released and cleared.')

    @async.async
    def request(self, params, timeout=REQUEST_TIMEOUT, waitingID=None):
        if waitingID is not None:
            Waiting.show(waitingID)
        paramsHash = params.getHash()
        pending = self._pendings.get(paramsHash)
        if pending is None:
            requestId = self._reqIdGen.next()
            request = Request(requestId, params)
            self._pendings[paramsHash] = Pending(request)
            try:
                self._logger.debug('Sending request with id=%s and timeout=%s.', requestId, timeout)
                response = yield async.await(request.send(), timeout=timeout)
            except async.TimeoutError:
                response = params.response.createRequestTimeout()
            except async.BrokenPromiseError:
                response = params.response.createRequestDestroyed()
            except Exception:
                response = params.response.createUnexpectedError('Failed to send request')
                self._logger.exception('Got an exception on sending requestId=%s.', requestId)

            self._logger.debug('Got response=%s for requestId=%s.', response, requestId)
            pending = self._pendings.get(paramsHash)
            if pending is not None and pending.requestId == requestId:
                pending.release(response)
                self._pendings.pop(paramsHash, None)
            else:
                self._logger.debug('No pending to release for requestId=%s.', requestId)
        else:
            self._logger.debug('Waiting response for requestId=%s.', pending.requestId)
            response = yield async.await(pending.wait())
            self._logger.debug('Got pending response=%s for requestId=%s.', response, pending.requestId)
        if waitingID is not None:
            Waiting.hide(waitingID)
        raise AsyncReturn(response)
        return
