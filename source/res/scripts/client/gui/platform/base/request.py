# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/platform/base/request.py
import typing
import copy
import hashlib
import httplib
import json
import urllib
import urlparse
from functools import partial
from enum import Enum
import adisp
import async
import BigWorld
import soft_exception
from BWUtil import AsyncReturn
from constants import WG_GAMES, CURRENT_REALM
from gui.platform.base.settings import REQUEST_TIMEOUT, POLLING_PERIOD, POLLING_REQUEST_TIMEOUT, SOLVE_POW_TIMEOUT, ACCEPTED_HTTP_CODES
from gui.platform.base import logger
from gui.platform.base.response import PlatformResponse
from helpers import dependency, getClientVersion
from skeletons.gui.web import IWebController
from wotdecorators import noexceptReturn

class ContentType(str, Enum):
    JSON = 'application/json'
    FORM_URLENCODED = 'application/x-www-form-urlencoded'
    FORM_DATA = 'multipart/form-data'


class Params(object):
    response = PlatformResponse
    url = ''
    queryParams = None
    headers = None
    method = 'GET'
    postData = None
    auth = True
    proofOfWorkURL = ''
    addUserAgentHeader = True

    def __init__(self, urlHost='', powHost=''):
        self._logger = logger.getWithContext(instance=self)
        self.queryParams = copy.deepcopy(self.queryParams) if self.queryParams else {}
        self.headers = self._prepareHeaders()
        self.postData = copy.deepcopy(self.postData) if self.postData else {}
        self.url = self._addHost(urlHost, self._prepareUrl())
        self.proofOfWorkURL = self._addHost(powHost or urlHost, self.proofOfWorkURL)

    def getHash(self):
        hashBuilder = hashlib.md5()
        attrs = (self.url,
         self.headers,
         self.method,
         self.queryParams,
         self.postData,
         self.auth,
         self.proofOfWorkURL)
        hashBuilder.update(''.join((str(attr) for attr in attrs)))
        return hashBuilder.hexdigest()

    def encodePostData(self):
        contentType = self.headers.get('Content-Type')
        if contentType is None or contentType == 'multipart/form-data':
            return self.postData
        elif contentType == 'application/x-www-form-urlencoded':
            return urllib.urlencode(self.postData)
        elif contentType == 'application/json':
            return json.dumps(self.postData)
        else:
            raise soft_exception.SoftException('Unsupported header content type: {}'.format(contentType))
            return

    def _prepareUrl(self):
        if not self.url:
            raise soft_exception.SoftException('Broken request url: {} '.format(self.url))
        url = self.url
        if self.queryParams:
            values = []
            for k, val in self.queryParams.iteritems():
                if not isinstance(val, (list, tuple)):
                    val = [val]
                values.append((k, ','.join((str(i) for i in val))))

            urlencodedString = urllib.urlencode(values)
            url = '{}?{}'.format(self.url, urlencodedString)
        return url

    def _prepareHeaders(self):
        headers = copy.deepcopy(self.headers) if self.headers else {}
        if self.addUserAgentHeader:
            if 'User-Agent' in headers:
                self._logger.warning('User-Agent=%s in default headers will be replaced.', headers['User-Agent'])
            headers['User-Agent'] = '{app}-{realm}/{version}'.format(app=WG_GAMES.TANKS, realm=CURRENT_REALM, version=getClientVersion(force=False))
        return headers

    def _addHost(self, host, url):
        if host and url:
            if bool(urlparse.urlparse(url).netloc):
                self._logger.error('Url already absolute in %s', self)
            else:
                url = urlparse.urljoin(host, url)
        return url

    def __str__(self):
        return '<{cls_}> auth:{auth}, url:{url}, method:{method}, headers:{headers}, powUrl:{powUrl}, response:{response}.'.format(cls_=self.__class__.__name__, auth=self.auth, url=self.url, method=self.method, headers=self.headers, powUrl=self.proofOfWorkURL, response=self.response)


class Request(object):
    __slots__ = ('requestId', 'isCanceled', 'params', '_logger')
    webCtrl = dependency.descriptor(IWebController)

    def __init__(self, requestId, params):
        self.requestId = requestId
        self.isCanceled = False
        self.params = params
        self._logger = logger.getWithContext(instance=self, requestId=requestId)

    def cancel(self):
        self.isCanceled = True
        self._logger.debug('Canceled.')

    @async.async
    def send(self):
        self._logger.debug('Processing %s.', self.params)
        if self.params.auth:
            accessTokenData = yield async.await_callback(self._getAccessTokenData)()
            self._logger.debug('Authorization token: %s.', accessTokenData)
            if self.isCanceled:
                raise AsyncReturn(self.params.response.createRequestCanceled())
            if accessTokenData is None:
                raise AsyncReturn(self.params.response.createAuthorizationError())
            self.params.headers['Authorization'] = 'Bearer {}'.format(accessTokenData.accessToken)
        if self.params.proofOfWorkURL:
            response = yield async.await_callback(self._fetchUrl)(url=self.params.proofOfWorkURL, headers={'User-Agent': self.params.headers.get('User-Agent')} if self.params.addUserAgentHeader else None)
            if self.isCanceled:
                raise AsyncReturn(self.params.response.createRequestCanceled())
            if not response.isSuccess():
                raise AsyncReturn(response)
            self._logger.debug('Got pow response=%s.', response)
            solved, counter = yield async.await(self._solvePoW(response, SOLVE_POW_TIMEOUT))
            if self.isCanceled:
                raise AsyncReturn(self.params.response.createRequestCanceled())
            if not solved:
                raise AsyncReturn(self.params.response.createPowNotSolved())
            self.params.postData['pow'] = counter
            self.params.headers['X-Wg-Challenge-Key'] = response.getHeaders().get('X-Wg-Challenge-Key', '')
        self._logger.debug('Sending with %s.', self.params)
        response = yield async.await_callback(self._fetchUrl)(self.params.url, self.params.headers.items(), self.params.method, self.params.encodePostData())
        raise AsyncReturn(response)
        return

    @adisp.process
    def _getAccessTokenData(self, callback):
        force = True if not self.webCtrl.isLoggedOn() else False
        self._logger.debug('Getting access token with force=%s.', force)
        accessTokenData = yield self.webCtrl.getAccessTokenData(force=force)
        callback(accessTokenData)

    @async.async
    def _solvePoW(self, response, timeout=None):
        data = response.getData()['pow']
        solved, counter = yield async.await_callback(_solvePow)(data['algorithm']['version'], data['complexity'], str(data['timestamp']), data['algorithm']['resourse'], data['algorithm']['extension'], data['random_string'], timeout)
        self._logger.debug('Challenge was solved=%s, counter=%s', solved, counter)
        raise AsyncReturn((solved, counter))

    def _fetchUrl(self, url, headers=None, method='GET', postData=None, callback=lambda x: x):
        _urlFetcher(url, partial(self._pollResponseCallback, callback), headers, REQUEST_TIMEOUT, method, postData)

    @async.async
    def _pollResponseCallback(self, callback, response):
        try:
            self._logger.debug('Got url response with code=%s, body=%s, headers=%s.', response.responseCode, response.body, response.headers())
            if self.isCanceled:
                callback(self.params.response.createRequestCanceled())
                return
            while response.responseCode == httplib.ACCEPTED:
                yield async.await(async.delay(POLLING_PERIOD))
                if self.isCanceled:
                    callback(self.params.response.createRequestCanceled())
                    return
                headers, _ = self.__loadResponse(response)
                self._logger.debug('Sending poll request to %s.', headers['Location'])
                location, userAgent = headers['Location'], self.params.headers.get('User-Agent')
                response = yield async.await_callback(_urlFetcher)(url=location, headers={'User-Agent': userAgent} if userAgent else None, timeout=POLLING_REQUEST_TIMEOUT)
                self._logger.debug('Got poll response with code=%s.', response.responseCode)
                if self.isCanceled:
                    callback(self.params.response.createRequestCanceled())
                    return

            headers, data = self.__loadResponse(response)
            if response.responseCode not in ACCEPTED_HTTP_CODES:
                callback(self.params.response.createHttpError(response.responseCode, '', data, headers))
            else:
                callback(self.params.response.createSuccess(response.responseCode, '', data, headers))
        except Exception:
            self._logger.exception('Got an exception processing poll.')
            callback(self.params.response.createUnexpectedError('Failed to handle result'))

        return

    @noexceptReturn((None, None))
    def __loadResponse(self, response):
        headers = response.headers()
        try:
            data = json.loads(response.body)
        except (TypeError, ValueError):
            self._logger.warning('Can not load response body from response: %s.', response)
            data = None

        return (headers, data)


def _urlFetcher(url, callback, headers=None, timeout=REQUEST_TIMEOUT, method='GET', postData=None):
    return BigWorld.fetchURL(url, callback, headers, timeout, method, postData)


def _solvePow(version, complexity, timestamp, resource, extension, randomString, timeout, callback):
    BigWorld.solvePow(version, complexity, timestamp, resource, extension, randomString, callback, timeout)
