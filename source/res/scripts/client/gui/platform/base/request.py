# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/request.py
import httplib
import logging
import json
import urllib
from functools import partial
import BigWorld
import adisp
import async
from BWUtil import AsyncReturn
from AccountCommands import RES_FAILURE
from client_request_lib import exceptions
from gui.platform.base.settings import REQUEST_TIMEOUT, POLLING_PERIOD, POLLING_REQUEST_TIMEOUT, BW_TIMEOUT_CODE, SOLVE_POW_TIMEOUT, LOGGER_NAME
from gui.shared.utils.requesters.abstract import Response
from helpers import dependency
from skeletons.gui.web import IWebController
from wotdecorators import noexceptReturn
_logger = logging.getLogger(LOGGER_NAME)

class PlatformResponse(Response):

    def isTimeout(self):
        return self.extraCode in (httplib.REQUEST_TIMEOUT, BW_TIMEOUT_CODE)

    def isServiceUnavailable(self):
        return self.code == RES_FAILURE


class Request(object):
    __slots__ = ('isCanceled', 'requestId', 'url', 'headers', 'method', 'queryParams', 'postData', 'auth', 'proofOfWorkURL')
    webCtrl = dependency.descriptor(IWebController)

    def __init__(self, requestId, url, headers=None, method='GET', queryParams=None, postData=None, auth=False, proofOfWorkURL=None):
        self.isCanceled = False
        self.requestId = requestId
        self.url = url
        self.headers = headers or {}
        self.method = method
        self.queryParams = queryParams
        self.postData = postData or {}
        self.auth = auth
        self.proofOfWorkURL = proofOfWorkURL

    def cancel(self):
        self.isCanceled = True
        _logger.debug('Cancelling request with requestId=%s.', self.requestId)

    @async.async
    def send(self):
        self.headers['Content-Type'] = 'application/json'
        if self.auth:
            accessTokenData = yield async.await_callback(self._getAccessTokenData)()
            _logger.debug('requestId=%s: Authorization token: %s.', self.requestId, accessTokenData)
            if self.isCanceled:
                raise AsyncReturn(PlatformResponse(RES_FAILURE, '', {}, httplib.SERVICE_UNAVAILABLE))
            if accessTokenData is None:
                raise AsyncReturn(PlatformResponse(RES_FAILURE, '', {}, httplib.UNAUTHORIZED))
            self.headers['Authorization'] = 'Bearer {}'.format(accessTokenData.accessToken)
        if self.proofOfWorkURL is not None:
            response = yield async.await_callback(self._fetchUrl)(url=self.proofOfWorkURL)
            if self.isCanceled:
                raise AsyncReturn(PlatformResponse(RES_FAILURE, '', {}, httplib.SERVICE_UNAVAILABLE))
            if not response.isSuccess():
                raise AsyncReturn(response)
            _logger.debug('Got challenge response=%s for request requestId=%s', response, self.requestId)
            solved, counter = yield async.await(self._solvePoW(response, SOLVE_POW_TIMEOUT))
            if self.isCanceled:
                raise AsyncReturn(PlatformResponse(RES_FAILURE, '', {}, httplib.SERVICE_UNAVAILABLE))
            if not solved:
                raise AsyncReturn(PlatformResponse(RES_FAILURE, '', {}, httplib.BAD_REQUEST))
            self.postData['pow'] = counter
            self.headers['X-Wg-Challenge-Key'] = response.getHeaders().get('X-Wg-Challenge-Key', '')
        self._prepare()
        _logger.debug('Send request requestId=%s from url=%s, headers=%s, method=%s, postData=%s.', self.requestId, self.url, self.headers.items(), self.method, self.postData)
        response = yield async.await_callback(self._fetchUrl)(self.url, self.headers.items(), self.method, self.postData)
        raise AsyncReturn(response)
        return

    def _prepare(self):
        if self.queryParams:
            values = []
            for k, val in self.queryParams.iteritems():
                if not isinstance(val, (list, tuple)):
                    val = [val]
                values.append((k, ','.join((str(i) for i in val))))

            urlencodedString = urllib.urlencode(values)
            self.url = '{}?{}'.format(self.url, urlencodedString)
        self.postData = json.dumps(self.postData)

    @adisp.process
    def _getAccessTokenData(self, callback):
        force = True if not self.webCtrl.isLoggedOn() else False
        _logger.debug('Getting access token with force=%s.', force)
        accessTokenData = yield self.webCtrl.getAccessTokenData(force=force)
        callback(accessTokenData)

    @async.async
    def _solvePoW(self, response, timeout=None):
        data = response.getData()['pow']
        solved, counter = yield async.await_callback(_solvePow)(data['algorithm']['version'], data['complexity'], str(data['timestamp']), data['algorithm']['resourse'], data['algorithm']['extension'], data['random_string'], timeout)
        _logger.debug('Challenge for requestId=%s was solved=%s, counter=%s', self.requestId, solved, counter)
        raise AsyncReturn((solved, counter))

    def _fetchUrl(self, url, headers=None, method='GET', postData=None, callback=lambda x: x):
        _urlFetcher(url, partial(self._pollResponseCallback, callback), headers, REQUEST_TIMEOUT, method, postData)

    @async.async
    def _pollResponseCallback(self, callback, response):
        try:
            _logger.debug('On request requestId=%s response with code=%s, body=%s, headers=%s.', self.requestId, response.responseCode, response.body, response.headers())
            if self.isCanceled:
                callback(PlatformResponse(RES_FAILURE, '', {}, httplib.SERVICE_UNAVAILABLE))
                return
            while response.responseCode == httplib.ACCEPTED:
                yield async.await(async.delay(POLLING_PERIOD))
                if self.isCanceled:
                    callback(PlatformResponse(RES_FAILURE, '', {}, httplib.SERVICE_UNAVAILABLE))
                    return
                headers, _ = self.__loadResponse(response)
                _logger.debug('Sending poll request for requestId=%s to %s.', self.requestId, headers['Location'])
                response = yield async.await_callback(_urlFetcher)(url=headers['Location'], timeout=POLLING_REQUEST_TIMEOUT)
                _logger.debug('Received poll response requestId=%s with code=%s.', self.requestId, response.responseCode)
                if self.isCanceled:
                    callback(PlatformResponse(RES_FAILURE, '', {}, httplib.SERVICE_UNAVAILABLE))
                    return

            headers, data = self.__loadResponse(response)
            if response.responseCode != httplib.OK:
                callback(PlatformResponse(response.responseCode, '', data, response.responseCode, headers))
            else:
                callback(PlatformResponse(exceptions.ResponseCodes.NO_ERRORS, '', data, response.responseCode, headers))
        except Exception:
            _logger.exception('Got an exception on getting response on requestId=%s.', self.requestId)
            callback(PlatformResponse(RES_FAILURE, 'Failed to handle result', {}, httplib.SERVICE_UNAVAILABLE))

    @noexceptReturn((None, None))
    def __loadResponse(self, response):
        headers = response.headers()
        try:
            data = json.loads(response.body)
        except (TypeError, ValueError):
            _logger.warning('Can not load response body from %s.', response.body)
            data = None

        return (headers, data)


def _urlFetcher(url, callback, headers=None, timeout=REQUEST_TIMEOUT, method='GET', postData=None):
    return BigWorld.fetchURL(url, callback, headers, timeout, method, postData)


def _solvePow(version, complexity, timestamp, resource, extension, randomString, timeout, callback):
    BigWorld.solvePow(version, complexity, timestamp, resource, extension, randomString, callback, timeout)
