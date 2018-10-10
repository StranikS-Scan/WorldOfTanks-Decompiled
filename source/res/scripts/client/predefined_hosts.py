# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/predefined_hosts.py
import operator
import random
import time
import threading
import urllib2
from urllib import urlencode
from collections import namedtuple
import BigWorld
import ResMgr
import constants
from Event import Event, EventManager
from helpers.time_utils import ONE_MINUTE
from shared_utils import BitmaskHelper
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_WARNING
from helpers import i18n
AUTO_LOGIN_QUERY_ENABLED = not (constants.IS_DEVELOPMENT or constants.IS_CHINA)
AUTO_LOGIN_QUERY_URL = 'auto.login.app:0000'
AUTO_LOGIN_QUERY_TIMEOUT = 5
CSIS_REQUEST_TIMEOUT = 10
CSIS_REQUEST_TIMER = 10 * ONE_MINUTE
_PING_FORCE_COOLDOWN_TIME = ONE_MINUTE
_PING_COOLDOWN_TIME = 10 * ONE_MINUTE
UNDEFINED_PING_VAL = -1
_DEFINED_PING_VAL = 0
_LOW_PING_BOUNDARY_VAL = 59
_NORM_PING_BOUNDARY_VAL = 119

class PING_STATUSES(object):
    UNDEFINED = 0
    HIGH = 1
    NORM = 2
    LOW = 3
    REQUESTED = 4


PingData = namedtuple('PingData', 'value, status')
_DEFAULT_PING_DATA = PingData(UNDEFINED_PING_VAL, PING_STATUSES.UNDEFINED)

def _getPingStatus(pingVal):
    if pingVal < _DEFINED_PING_VAL:
        return PING_STATUSES.UNDEFINED
    if pingVal <= _LOW_PING_BOUNDARY_VAL:
        return PING_STATUSES.LOW
    return PING_STATUSES.NORM if pingVal <= _NORM_PING_BOUNDARY_VAL else PING_STATUSES.HIGH


def _isReplay(opType=''):
    import BattleReplay
    if BattleReplay.isLoading() or BattleReplay.isPlaying():
        LOG_DEBUG('Replay is currently playing. {} requesting operations are forbidden'.format(opType))
        return True
    return False


class HOST_AVAILABILITY(object):
    NOT_AVAILABLE = -1
    NOT_RECOMMENDED = 0
    RECOMMENDED = 1
    REQUESTED = 2
    IGNORED = 3
    UNKNOWN = 4


class REQUEST_RATE(object):
    NEVER = 0
    ON_REQUEST = 1
    ALWAYS = 2


class AUTO_LOGIN_QUERY_STATE(object):
    DEFAULT = 0
    START = 1
    PING_PERFORMED = 2
    CSIS_RESPONSE_RECEIVED = 4
    COMPLETED = START | PING_PERFORMED | CSIS_RESPONSE_RECEIVED


class CSIS_ACTION(BitmaskHelper):
    DEFAULT = 0
    UPDATE_ON_TIME = 1
    AUTO_LOGIN_REQUEST = 2


_csisQueryMutex = threading.Lock()

def _CSISResponseParser(out, requestedIDs):
    result = _createDefaultCSISResponse(requestedIDs)
    root = ResMgr.DataSection().createSectionFromString(out)
    itemsSec = None
    if root is not None:
        itemsSec = root['items']
    if itemsSec is not None:
        for _, subSec in itemsSec.items():
            rType = subSec.readString('type')
            name = subSec.readInt('name')
            if rType == 'periphery' and name:
                result[name] = subSec.readInt('availability', HOST_AVAILABILITY.UNKNOWN)

    return result


def _createDefaultCSISResponse(requestedIDs):
    return dict(((reqID, HOST_AVAILABILITY.UNKNOWN) for reqID in requestedIDs))


class _CSISRequestWorker(threading.Thread):

    def __init__(self, url, callback, params=None):
        super(_CSISRequestWorker, self).__init__()
        self.__url = url
        self.__callback = callback
        self.__params = params

    def run(self):
        if self.__callback is None:
            return
        else:
            response = {}
            info = None
            try:
                try:
                    url = self._makeUrl()
                    LOG_DEBUG('CSIS url', url)
                    req = urllib2.Request(url=url)
                    urllib2.build_opener(urllib2.HTTPHandler())
                    info = urllib2.urlopen(req, timeout=CSIS_REQUEST_TIMEOUT)
                    if info.code == 200 and info.headers.type == 'text/xml':
                        response = _CSISResponseParser(info.read(), self.__params)
                except IOError:
                    response = _createDefaultCSISResponse(self.__params)
                    LOG_CURRENT_EXCEPTION()

            finally:
                if info is not None:
                    info.close()

            _csisQueryMutex.acquire()
            try:
                self.__callback(response)
            finally:
                self.__callback = None
                _csisQueryMutex.release()

            return

    def _makeUrl(self):
        url = self.__url
        if self.__params:
            data = urlencode([ ('periphery', param) for param in self.__params ])
            url = '{0:>s}?{1:>s}'.format(self.__url, data)
        return url


def _getCSISWorker(csisUrl, receiveCsisResponse, peripheries):
    return _CSISRequestWorker(csisUrl, receiveCsisResponse, peripheries)


class _LoginAppUrlIterator(list):

    def __init__(self, *args):
        list.__init__(self, *args)
        self.cursor = 0
        self.primary = self[0] if self else None
        self.__lock = False
        random.shuffle(self)
        return

    def end(self):
        return self.cursor >= len(self)

    def suspend(self):
        if self.cursor > 0 and not self.__lock:
            self.cursor -= 1
        self.__lock = True

    def resume(self):
        self.__lock = False

    def next(self):
        value = self[self.cursor]
        if not self.__lock:
            self.cursor += 1
        return value


_HostItem = namedtuple('HostItem', ' '.join(['name',
 'shortName',
 'url',
 'urlToken',
 'urlIterator',
 'keyPath',
 'areaID',
 'peripheryID']))

def getHostURL(item, token2=None, useIterator=False):
    result = item.url
    if token2 and item.urlToken:
        result = item.urlToken
        LOG_DEBUG('Gets alternative LoginApp url:', result)
    else:
        urls = item.urlIterator
        if useIterator and urls is not None:
            if urls.end():
                urls.cursor = 0
            url = urls.next()
            LOG_DEBUG('Gets next LoginApp url:', url)
    return result


class _PingRequester(object):

    def __init__(self, pingPerformedCallback):
        self.__pingResult = {}
        self.__pingPerformedCallback = pingPerformedCallback
        self.__isRequestPingInProgress = False
        self.__lastUpdateTime = 0
        self.__setPingCallback = False
        try:
            BigWorld.WGPinger.setOnPingCallback(self.__pingCallback)
            self.__setPingCallback = True
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

    def request(self, peripheries, forced=False):
        if _isReplay('Ping'):
            self.__updatePing([], PING_STATUSES.UNDEFINED)
            return
        peripheries = [ host.url for host in peripheries ]
        if not self.__isRequestPingInProgress and peripheries:
            cooldownTime = _PING_FORCE_COOLDOWN_TIME if forced else _PING_COOLDOWN_TIME
            if time.time() - self.__lastUpdateTime >= cooldownTime:
                pData = [ (periphery, UNDEFINED_PING_VAL) for periphery in peripheries ]
                try:
                    LOG_DEBUG('Ping starting', peripheries)
                    self.__isRequestPingInProgress = True
                    self.__updatePing(pData, PING_STATUSES.REQUESTED)
                    BigWorld.WGPinger.ping(peripheries)
                except (AttributeError, TypeError):
                    LOG_CURRENT_EXCEPTION()
                    self.__updatePing(pData, PING_STATUSES.UNDEFINED)

            else:
                self.__pingPerformedCallback(self.__pingResult)

    def result(self):
        return self.__pingResult

    def clear(self):
        self.__pingResult.clear()

    def fini(self):
        self.__isRequestPingInProgress = False
        self.__setPingCallback = False
        self.__pingPerformedCallback = None
        self.clear()
        try:
            BigWorld.WGPinger.clearOnPingCallback()
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

        return

    def __pingCallback(self, result):
        self.__isRequestPingInProgress = False
        LOG_DEBUG('Ping performed {}'.format(result))
        self.__updatePing(result)

    def __updatePing(self, pingData, state=None):
        self.__lastUpdateTime = time.time()
        for rKey, pData in self.__pingResult.iteritems():
            self.__pingResult[rKey] = PingData(pData.value, PING_STATUSES.UNDEFINED)

        try:
            for periphery, pingValue in pingData:
                self.__pingResult[periphery] = PingData(pingValue, state if state is not None else _getPingStatus(pingValue))

        except Exception:
            LOG_CURRENT_EXCEPTION()

        self.__pingPerformedCallback(self.__pingResult)
        return


class _PreDefinedHostList(object):

    def __init__(self):
        super(_PreDefinedHostList, self).__init__()
        self._eManager = EventManager()
        self.onCsisQueryStart = Event(self._eManager)
        self.onCsisQueryComplete = Event(self._eManager)
        self.onPingPerformed = Event(self._eManager)
        self._hosts = []
        self._urlMap = {}
        self._nameMap = {}
        self._peripheryMap = {}
        self._isDataLoaded = False
        self._isCSISQueryInProgress = False
        self.__csisUrl = ''
        self.__csisResponse = {}
        self.__lastRoamingHosts = []
        self.__csisCallbackID = None
        self.__lastCsisUpdateTime = 0
        self.__queryCallback = None
        self.__autoLoginQueryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
        self.__csisAction = CSIS_ACTION.DEFAULT
        self.__recommended = []
        self.__pingRequester = _PingRequester(self.__onPingPerformed)
        return

    def fini(self):
        self._hosts = []
        self._urlMap.clear()
        self._nameMap.clear()
        self._peripheryMap.clear()
        self._isDataLoaded = False
        self.__csisResponse.clear()
        self.__csisUrl = ''
        self.__lastCsisUpdateTime = None
        self.__queryCallback = None
        self.__autoLoginQueryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
        self.__csisAction = CSIS_ACTION.DEFAULT
        self._eManager.clear()
        self.__pingRequester.fini()
        self.__cleanCsisTimerCallback()
        return

    @property
    def lastRoamingHosts(self):
        return self.__lastRoamingHosts

    def startCSISUpdate(self):
        if len(self.hosts()) > 1:
            self.__csisAction = CSIS_ACTION.addIfNot(self.__csisAction, CSIS_ACTION.UPDATE_ON_TIME)
            self.__sendCsisQuery()

    def stopCSISUpdate(self):
        self.__csisAction = CSIS_ACTION.removeIfHas(self.__csisAction, CSIS_ACTION.UPDATE_ON_TIME)
        self.__cleanCsisTimerCallback()

    def requestPing(self, forced=False):
        self.__pingRequester.request(self._hosts, forced)

    def getPingResult(self):
        return self.__pingRequester.result()

    def getHostPingData(self, host):
        return self.getPingResult().get(host, _DEFAULT_PING_DATA)

    def autoLoginQuery(self, callback):
        if callback is None:
            LOG_WARNING('Callback is not defined.')
            return
        elif self.__autoLoginQueryState != AUTO_LOGIN_QUERY_STATE.DEFAULT:
            LOG_WARNING('Auto login query in process. Current state: {}'.format(self.__autoLoginQueryState))
            return
        elif len(self._hosts) < 2:
            callback(self.first())
            return
        elif self.__recommended:
            LOG_DEBUG('Gets recommended from previous query', self.__recommended)
            host = self.__choiceFromRecommended()
            LOG_DEBUG('Recommended host', host)
            callback(host)
            return
        else:
            self.__autoLoginQueryState = AUTO_LOGIN_QUERY_STATE.START
            self.__queryCallback = callback
            self.__pingRequester.request(self.peripheries())
            self.__csisAction = CSIS_ACTION.addIfNot(self.__csisAction, CSIS_ACTION.AUTO_LOGIN_REQUEST)
            self.__sendCsisQuery()
            return

    def resetQueryResult(self):
        self.__recommended = []
        self.__pingRequester.clear()

    def readScriptConfig(self, dataSection, userDataSection=None):
        if self._isDataLoaded or dataSection is None:
            return
        else:

            def _readSvrList(section, nodeName):
                return section[nodeName].items() if section is not None and section.has_key(nodeName) else []

            self.__csisUrl = dataSection.readString('csisUrl')
            self._hosts = []
            self._urlMap.clear()
            self._nameMap.clear()
            self._peripheryMap.clear()
            svrList = _readSvrList(dataSection, 'login') + _readSvrList(userDataSection, 'development/login')
            for name, subSec in svrList:
                name = subSec.readString('name')
                shortName = subSec.readString('short_name')
                urls = _LoginAppUrlIterator(subSec.readStrings('url'))
                host = urls.primary
                if host is not None:
                    if not name:
                        name = host
                    keyPath = subSec.readString('public_key_path')
                    if not keyPath:
                        keyPath = None
                    areaID = subSec.readString('game_area_id')
                    if not areaID:
                        areaID = None
                    app = self._makeHostItem(name, shortName, host, urlToken=subSec.readString('url_token'), urlIterator=urls if len(urls) > 1 else None, keyPath=keyPath, areaID=areaID, peripheryID=subSec.readInt('periphery_id', 0))
                    idx = len(self._hosts)
                    url = app.url
                    if url in self._urlMap:
                        LOG_WARNING('Host url is already added. This host is ignored', url)
                        continue
                    self._urlMap[url] = idx
                    urlToken = app.urlToken
                    if urlToken:
                        if urlToken in self._urlMap:
                            LOG_WARNING('Alternative host url is already added. This url is ignored', app.url)
                        else:
                            self._urlMap[urlToken] = idx
                    self._nameMap[app.name] = idx
                    self._peripheryMap[app.peripheryID] = idx
                    self._hosts.append(app)

            self._isDataLoaded = True
            return

    def predefined(self, url):
        return url in self._urlMap

    def roaming(self, url):
        return url in [ p.url for p in self.roamingHosts() ]

    def first(self):
        return self._hosts[0] if self._hosts else self._makeHostItem('', '', '')

    def byUrl(self, url):
        result = self._makeHostItem('', '', url)
        index = self._urlMap.get(url, -1)
        if index > -1:
            result = self._hosts[index]
        else:
            for host in self.roamingHosts():
                if host.url == url:
                    result = host

        return result

    def byName(self, name):
        result = self._makeHostItem(name, '', '')
        index = self._nameMap.get(name, -1)
        if index > -1:
            result = self._hosts[index]
        else:
            for host in self.roamingHosts():
                if host.name == name:
                    result = host

        return result

    def hosts(self):
        return self._hosts[:]

    def shortList(self):
        result = self.getSimpleHostsList(self._hosts)
        if AUTO_LOGIN_QUERY_ENABLED and len(result) > 1 and len(self.peripheries()) > 1:
            result.insert(0, (AUTO_LOGIN_QUERY_URL,
             i18n.makeString('#menu:login/auto'),
             HOST_AVAILABILITY.IGNORED,
             None))
        return result

    def getSimpleHostsList(self, hosts, withShortName=False):
        result = []
        defAvail = self.getDefaultCSISStatus()
        predefined = tuple((host.url for host in self.peripheries()))
        isInProgress = self._isCSISQueryInProgress
        csisResGetter = self.__csisResponse.get
        for item in hosts:
            if item.url not in predefined:
                status = HOST_AVAILABILITY.IGNORED
            else:
                status = defAvail if isInProgress else csisResGetter(item.peripheryID, defAvail)
            if withShortName:
                result.append((item.url,
                 item.name,
                 item.shortName,
                 status,
                 item.peripheryID))
            result.append((item.url,
             item.name,
             status,
             item.peripheryID))

        return result

    def getDefaultCSISStatus(self):
        from gui import GUI_SETTINGS
        if not self.__csisUrl:
            defAvail = HOST_AVAILABILITY.IGNORED
        elif GUI_SETTINGS.csisRequestRate == REQUEST_RATE.NEVER:
            defAvail = HOST_AVAILABILITY.IGNORED
        elif len(g_preDefinedHosts.hosts()) > 1:
            defAvail = HOST_AVAILABILITY.REQUESTED
        else:
            defAvail = HOST_AVAILABILITY.IGNORED
        return defAvail

    def urlIterator(self, primary):
        result = None
        index = self._urlMap.get(primary, -1)
        if index > -1:
            result = self._hosts[index].urlIterator
        return result

    def periphery(self, peripheryID, useRoaming=True):
        if peripheryID in self._peripheryMap:
            index = self._peripheryMap[peripheryID]
            return self._hosts[index]
        else:
            if useRoaming:
                roamingHosts = dict(((host.peripheryID, host) for host in self.roamingHosts()))
                if peripheryID in roamingHosts:
                    return roamingHosts[peripheryID]
            return None

    def peripheries(self):
        return [ app for app in self._hosts if app.peripheryID ]

    def roamingHosts(self):
        p = BigWorld.player()
        result = []
        if hasattr(p, 'serverSettings'):
            for peripheryID, name, shortName, host, keyPath in p.serverSettings['roaming'][3]:
                result.append(self._makeHostItem(name, shortName, host, keyPath=keyPath, peripheryID=peripheryID))

            self.__lastRoamingHosts = sorted(result, key=operator.itemgetter(0))
        return self.__lastRoamingHosts

    def hostsWithRoaming(self):
        predefined = tuple((host.url for host in self.peripheries()))
        hosts = self.peripheries()
        for h in self.roamingHosts():
            if h.url not in predefined:
                hosts.append(h)

        return hosts

    def isRoamingPeriphery(self, peripheryID):
        return peripheryID not in [ p.peripheryID for p in self.peripheries() ]

    def _makeHostItem(self, name, shortName, url, urlToken='', urlIterator=None, keyPath=None, areaID=None, peripheryID=0):
        if not shortName:
            shortName = name
        return _HostItem(name, shortName, url, urlToken, urlIterator, keyPath, areaID, peripheryID)

    def _determineRecommendHost(self):
        defAvail = HOST_AVAILABILITY.NOT_AVAILABLE
        csisResGetter = self.__csisResponse.get
        queryResult = [ (host, self.getHostPingData(host.url).value, csisResGetter(host.peripheryID, defAvail)) for host in self.peripheries() ]
        self.__recommended = [ item for item in queryResult if item[2] == HOST_AVAILABILITY.RECOMMENDED ]
        if not self.__recommended:
            self.__recommended = [ item for item in queryResult if item[2] == HOST_AVAILABILITY.NOT_RECOMMENDED ]
        recommendLen = len(self.__recommended)
        if not recommendLen:
            if len(queryResult) > 1:
                LOG_DEBUG('List of recommended is empty. Gets host by ping')
                self.__recommended = self.__filterRecommendedByPing(queryResult)
                LOG_DEBUG('Recommended by ping', self.__recommended)
                result = self.__choiceFromRecommended()
            else:
                LOG_DEBUG('Gets first as recommended')
                result = self.first()
        else:
            LOG_DEBUG('Recommended by CSIS', self.__recommended)
            if recommendLen > 1:
                self.__recommended = self.__filterRecommendedByPing(self.__recommended)
                LOG_DEBUG('Recommended by ping', self.__recommended)
            result = self.__choiceFromRecommended()
        return result

    def __startCsisTimer(self):
        self.__cleanCsisTimerCallback()
        self.__csisCallbackID = BigWorld.callback(CSIS_REQUEST_TIMER, self.__onCsisTimer)

    def __cleanCsisTimerCallback(self):
        if self.__csisCallbackID:
            BigWorld.cancelCallback(self.__csisCallbackID)
            self.__csisCallbackID = None
        return

    def __onCsisTimer(self):
        self.__csisCallbackID = None
        self.__sendCsisQuery()
        return

    def __sendCsisQuery(self):
        isReplay = _isReplay('CSIS')
        if not isReplay and self.__csisUrl:
            if not self._isCSISQueryInProgress:
                timeFromLastUpdate = time.time() - self.__lastCsisUpdateTime
                if timeFromLastUpdate >= CSIS_REQUEST_TIMER:
                    self._isCSISQueryInProgress = True
                    self.onCsisQueryStart()
                    allHosts = self.hosts()
                    peripheries = [ host.peripheryID for host in allHosts if host.peripheryID ]
                    LOG_DEBUG('CSIS query sending', peripheries)
                    worker = _getCSISWorker(self.__csisUrl, self.__receiveCsisResponse, peripheries)
                    worker.start()
                else:
                    self.__finishCsisQuery()
        else:
            if not isReplay:
                LOG_DEBUG('CSIS url is not defined - ignore')
            self._isCSISQueryInProgress = False
            self.stopCSISUpdate()
            self.__finishCsisQuery()
            self.__lastCsisUpdateTime = 0

    def __receiveCsisResponse(self, response):
        LOG_DEBUG('CSIS query received', response)
        self._isCSISQueryInProgress = False
        self.__csisResponse = response
        self.__lastCsisUpdateTime = time.time()
        self.__finishCsisQuery()

    def __finishCsisQuery(self):
        if self.__csisAction & CSIS_ACTION.AUTO_LOGIN_REQUEST:
            self.__receiveAutoLoginCSISResponse(self.__csisResponse)
        if self.__csisAction & CSIS_ACTION.UPDATE_ON_TIME:
            self.__startCsisTimer()
        self.onCsisQueryComplete(self.__csisResponse)

    def __onPingPerformed(self, result):
        self.onPingPerformed(result)
        if self.__autoLoginQueryState & AUTO_LOGIN_QUERY_STATE.START:
            self.__autoLoginQueryCompleted(AUTO_LOGIN_QUERY_STATE.PING_PERFORMED)

    def __receiveAutoLoginCSISResponse(self, response):
        self.__csisAction = CSIS_ACTION.removeIfHas(self.__csisAction, CSIS_ACTION.AUTO_LOGIN_REQUEST)
        self.__autoLoginQueryCompleted(AUTO_LOGIN_QUERY_STATE.CSIS_RESPONSE_RECEIVED)

    def __autoLoginQueryCompleted(self, state):
        if not self.__autoLoginQueryState & state:
            self.__autoLoginQueryState |= state
        if self.__autoLoginQueryState == AUTO_LOGIN_QUERY_STATE.COMPLETED:
            host = self._determineRecommendHost()
            LOG_DEBUG('Recommended host', host)
            self.__autoLoginQueryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
            self.__queryCallback(host)
            self.__queryCallback = None
        return

    def __filterRecommendedByPing(self, recommended):
        result = recommended
        filtered = [ item for item in recommended if item[1] > UNDEFINED_PING_VAL ]
        if filtered:
            minPingTime = min(filtered, key=lambda item: item[1])[1]
            maxPingTime = 1.2 * minPingTime
            result = [ item for item in filtered if item[1] < maxPingTime ]
        return result

    def __choiceFromRecommended(self):
        recommended = random.choice(self.__recommended)
        self.__recommended = [ item for item in self.__recommended if item != recommended ]
        return recommended[0]


g_preDefinedHosts = _PreDefinedHostList()
