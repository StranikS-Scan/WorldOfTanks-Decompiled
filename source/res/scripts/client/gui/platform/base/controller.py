# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/controller.py
import hashlib
import httplib
import logging
import sys
import async
from AccountCommands import RES_FAILURE
from BWUtil import AsyncReturn
from gui.Scaleform.Waiting import Waiting
from gui.platform.base.request import Request, PlatformResponse
from gui.platform.base.settings import LOGGER_NAME, REQUEST_TIMEOUT
from ids_generators import SequenceIDGenerator
_logger = logging.getLogger(LOGGER_NAME)

class Pending(object):
    __slots__ = ('_event', '_request', '_response')

    def __init__(self, request):
        self._event = async.AsyncEvent()
        self._request = request
        self._response = PlatformResponse(RES_FAILURE, 'Failed to send request', {}, httplib.SERVICE_UNAVAILABLE)

    @async.async
    def wait(self):
        try:
            yield async.await(self._event.wait())
        except async.BrokenPromiseError:
            _logger.info('Event was destroyed while waiting for event')

        raise AsyncReturn(self._response)

    @property
    def requestId(self):
        return self._request.requestId

    def release(self, response=None):
        self._response = response or self._response
        self._event.set()
        self._event.destroy()
        self._request.cancel()


class PlatformRequestsController(object):

    def __init__(self):
        self._pendings = {}
        self._reqIdGen = SequenceIDGenerator(highBound=sys.maxint)

    def clear(self):
        _logger.debug('Clear all pendings.')
        for pending in self._pendings.itervalues():
            pending.release()

        self._pendings.clear()

    @async.async
    def request(self, url, headers=None, timeout=REQUEST_TIMEOUT, method='GET', queryParams=None, postData=None, auth=False, proofOfWorkURL=None, waitingID=None):
        if waitingID is not None:
            Waiting.show(waitingID)
        requestType = _getHash(url, headers, method, queryParams, postData, auth, proofOfWorkURL)
        pending = self._pendings.get(requestType)
        if pending is None:
            requestId = self._reqIdGen.next()
            request = Request(requestId, url, headers, method, queryParams, postData, auth, proofOfWorkURL)
            self._pendings[requestType] = Pending(request)
            try:
                _logger.debug('Send requestId=%s from requester=%s.', requestId, self)
                response = yield async.await(request.send(), timeout=timeout)
            except async.TimeoutError:
                response = PlatformResponse(RES_FAILURE, 'Time out error', {}, httplib.REQUEST_TIMEOUT)
            except async.BrokenPromiseError:
                response = PlatformResponse(RES_FAILURE, 'Already destroyed', {}, httplib.SERVICE_UNAVAILABLE)
            except Exception:
                response = PlatformResponse(RES_FAILURE, 'Failed to send request', {}, httplib.SERVICE_UNAVAILABLE)
                _logger.exception('Got an exception on sending requestId=%s from requester=%s.', requestId, self)

            _logger.debug('Received response=%s with requestId=%s for requester=%s', response, requestId, self)
            pending = self._pendings.get(requestType)
            if pending is not None and pending.requestId == requestId:
                pending.release(response)
                self._pendings.pop(requestType, None)
            else:
                _logger.debug('No pending to release for requestId=%s from requester=%s.', requestId, self)
        else:
            response = yield async.await(pending.wait())
            _logger.debug('Received pending response=%s with requestId=%s for requester=%s', response, pending.requestId, self)
        if waitingID is not None:
            Waiting.hide(waitingID)
        raise AsyncReturn(response)
        return


def _getHash(*args):
    hashBuilder = hashlib.md5()
    hashBuilder.update(''.join((str(arg) for arg in args)))
    return hashBuilder.hexdigest()
