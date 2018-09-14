# Embedded file name: scripts/client/predefined_hosts.py
import operator
import cPickle as pickle
import base64
import random
import time
import threading
import urllib2
from urllib import urlencode
from collections import namedtuple
import BigWorld
import ResMgr
import Settings
import constants
from Event import Event, EventManager
from shared_utils import BitmaskHelper
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_WARNING, LOG_ERROR
from helpers import i18n
AUTO_LOGIN_QUERY_ENABLED = not (constants.IS_DEVELOPMENT or constants.IS_CHINA)
AUTO_LOGIN_QUERY_URL = 'auto.login.app:0000'
AUTO_LOGIN_QUERY_TIMEOUT = 5
STORED_AS_RECOMMEND_DELTA = 15 * 60
CSIS_REQUEST_TIMEOUT = 10
CSIS_REQUEST_TIMER = 10 * 60

class HOST_AVAILABILITY(object):
    NOT_AVAILABLE = -1
    NOT_RECOMMENDED = 0
    RECOMMENDED = 1
    UNKNOWN = 2
    IGNORED = 3

    @classmethod
    def getDefault(cls):
        from gui import GUI_SETTINGS
        defAvail = HOST_AVAILABILITY.IGNORED
        if len(g_preDefinedHosts.hosts()) > 1:
            defAvail = HOST_AVAILABILITY.UNKNOWN
        if GUI_SETTINGS.csisRequestRate == REQUEST_RATE.NEVER:
            defAvail = HOST_AVAILABILITY.IGNORED
        return defAvail


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

def _CSISResponseParser(out):
    result = {}
    root = ResMgr.DataSection().createSectionFromString(out)
    itemsSec = None
    if root is not None:
        itemsSec = root['items']
    if itemsSec is not None:
        for _, subSec in itemsSec.items():
            type = subSec.readString('type')
            name = subSec.readInt('name')
            if type == 'periphery' and name:
                result[name] = subSec.readInt('availability', HOST_AVAILABILITY.UNKNOWN)

    return result


class _CSISRequestWorker(threading.Thread):

    def __init__(self, url, callback, params = None):
        super(_CSISRequestWorker, self).__init__()
        self.__url = url
        self.__callback = callback
        self.__params = params

    def _makeUrl(self):
        url = self.__url
        if self.__params is not None and len(self.__params):
            data = urlencode(map(lambda param: ('periphery', param), self.__params))
            url = '{0:>s}?{1:>s}'.format(self.__url, data)
        return url

    def run(self):
        if self.__callback is None:
            return
        else:
            response = {}
            info = None
            try:
                url = self._makeUrl()
                LOG_DEBUG('CSIS url', url)
                req = urllib2.Request(url=url)
                urllib2.build_opener(urllib2.HTTPHandler())
                info = urllib2.urlopen(req, timeout=CSIS_REQUEST_TIMEOUT)
                if info.code == 200 and info.headers.type == 'text/xml':
                    response = _CSISResponseParser(info.read())
            except IOError:
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


class _LoginAppUrlIterator(list):

    def __init__(self, *args):
        list.__init__(self, *args)
        self.cursor = 0
        self.primary = self[0] if len(self) > 0 else None
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

def getHostURL(item, token2 = None, useIterator = False):
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


class _PreDefinedHostList(object):

    def __init__(self):
        super(_PreDefinedHostList, self).__init__()
        self._eManager = EventManager()
        self.onCsisQueryStart = Event(self._eManager)
        self.onCsisQueryComplete = Event(self._eManager)
        self._hosts = []
        self._urlMap = {}
        self._nameMap = {}
        self._peripheryMap = {}
        self._isDataLoaded = False
        self._isCSISQueryInProgress = False
        self.__pingResult = {}
        self.__csisUrl = ''
        self.__csisResponse = {}
        self.__lastRoamingHosts = []
        self.__csisCallbackID = None
        self.__lastCsisUpdateTime = 0
        self.__queryCallback = None
        self.__autoLoginQueryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
        self.__csisAction = CSIS_ACTION.DEFAULT
        self.__recommended = []
        self.__setPingCallback = False
        try:
            BigWorld.WGPinger.setOnPingCallback(self.__onPingPerformed)
            self.__setPingCallback = True
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

        return

    def fini(self):
        self._hosts = []
        self._urlMap.clear()
        self._nameMap.clear()
        self._peripheryMap.clear()
        self._isDataLoaded = False
        self.__pingResult.clear()
        self.__csisResponse.clear()
        self.__csisUrl = ''
        self.__lastCsisUpdateTime = None
        self.__queryCallback = None
        self.__autoLoginQueryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
        self.__csisAction = CSIS_ACTION.DEFAULT
        self._eManager.clear()
        self.__setPingCallback = False
        self.__cleanCsisTimerCallback()
        try:
            BigWorld.WGPinger.clearOnPingCallback()
        except AttributeError:
            LOG_CURRENT_EXCEPTION()

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

    def autoLoginQuery(self, callback):
        if callback is None:
            LOG_WARNING('Callback is not defined.')
            return
        elif self.__autoLoginQueryState != AUTO_LOGIN_QUERY_STATE.DEFAULT:
            LOG_WARNING('Auto login query in process.')
            return
        elif len(self._hosts) < 2:
            callback(self.first())
            return
        else:
            peripheryID, expired = self.readPeripheryTL()
            if peripheryID > 0 and expired > 0:
                if expired > time.time():
                    host = self.periphery(peripheryID, False)
                    if host is not None:
                        LOG_DEBUG('Recommended host taken from cache', host)
                        callback(host)
                        return
            if len(self.__recommended):
                LOG_DEBUG('Gets recommended from previous query', self.__recommended)
                host = self.__choiceFromRecommended()
                LOG_DEBUG('Recommended host', host)
                callback(host)
                return
            self.__autoLoginQueryState = AUTO_LOGIN_QUERY_STATE.START
            self.__queryCallback = callback
            self.__ping()
            self.__csisAction = CSIS_ACTION.addIfNot(self.__csisAction, CSIS_ACTION.AUTO_LOGIN_REQUEST)
            self.__sendCsisQuery()
            return

    def resetQueryResult(self):
        self.__recommended = []
        self.__pingResult.clear()

    def savePeripheryTL(self, peripheryID, delta = STORED_AS_RECOMMEND_DELTA):
        if not AUTO_LOGIN_QUERY_ENABLED or not peripheryID:
            return
        else:
            try:
                loginSec = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO]
                if loginSec is not None:
                    value = base64.b64encode(pickle.dumps((peripheryID, time.time() + delta)))
                    loginSec.writeString('peripheryLifeTime', value)
                    Settings.g_instance.save()
            except Exception:
                LOG_CURRENT_EXCEPTION()

            return

    def readPeripheryTL(self):
        if not AUTO_LOGIN_QUERY_ENABLED:
            return (0, 0)
        else:
            result = (0, 0)
            try:
                loginSec = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO]
                if loginSec is not None:
                    value = loginSec.readString('peripheryLifeTime')
                    if len(value):
                        value = pickle.loads(base64.b64decode(value))
                        if len(value) > 1:
                            result = value
            except Exception:
                result = ('', 0)
                LOG_CURRENT_EXCEPTION()

            return result

    def clearPeripheryTL(self):
        if not AUTO_LOGIN_QUERY_ENABLED:
            return
        else:
            try:
                loginSec = Settings.g_instance.userPrefs[Settings.KEY_LOGIN_INFO]
                if loginSec is not None:
                    loginSec.writeString('peripheryLifeTime', '')
                    Settings.g_instance.save()
            except Exception:
                LOG_CURRENT_EXCEPTION()

            return

    def readScriptConfig(self, dataSection):
        if self._isDataLoaded or dataSection is None:
            return
        else:
            self.__csisUrl = dataSection.readString('csisUrl')
            self._hosts = []
            self._urlMap.clear()
            self._nameMap.clear()
            self._peripheryMap.clear()
            loginSection = dataSection['login']
            if loginSection is None:
                return
            for name, subSec in loginSection.items():
                name = subSec.readString('name')
                shortName = subSec.readString('short_name')
                urls = _LoginAppUrlIterator(subSec.readStrings('url'))
                host = urls.primary
                if host is not None:
                    if not len(name):
                        name = host
                    keyPath = subSec.readString('public_key_path')
                    if not len(keyPath):
                        keyPath = None
                    areaID = subSec.readString('game_area_id')
                    if not len(areaID):
                        areaID = None
                    app = self._makeHostItem(name, shortName, host, urlToken=subSec.readString('url_token'), urlIterator=urls if len(urls) > 1 else None, keyPath=keyPath, areaID=areaID, peripheryID=subSec.readInt('periphery_id', 0))
                    idx = len(self._hosts)
                    url = app.url
                    if url in self._urlMap:
                        LOG_ERROR('Host url is already added. This host is ignored', url)
                        continue
                    self._urlMap[url] = idx
                    urlToken = app.urlToken
                    if len(urlToken):
                        if urlToken in self._urlMap:
                            LOG_ERROR('Alternative host url is already added. This url is ignored', app.url)
                        else:
                            self._urlMap[urlToken] = idx
                    self._nameMap[app.name] = idx
                    if app.peripheryID:
                        self._peripheryMap[app.peripheryID] = idx
                    self._hosts.append(app)

            self._isDataLoaded = True
            return

    def predefined(self, url):
        return url in self._urlMap

    def roaming(self, url):
        return url in [ p.url for p in self.roamingHosts() ]

    def first(self):
        if len(self._hosts):
            return self._hosts[0]
        return self._makeHostItem('', '', '')

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

    def getSimpleHostsList(self, hosts):
        result = []
        defAvail = HOST_AVAILABILITY.getDefault()
        predefined = tuple((host.url for host in self.peripheries()))
        isInProgress = self._isCSISQueryInProgress
        csisResGetter = self.__csisResponse.get
        for item in hosts:
            if item.url not in predefined:
                status = HOST_AVAILABILITY.IGNORED
            else:
                status = defAvail if isInProgress else csisResGetter(item.peripheryID, defAvail)
            result.append((item.url,
             item.name,
             status,
             item.peripheryID))

        return result

    def urlIterator(self, primary):
        result = None
        index = self._urlMap.get(primary, -1)
        if index > -1:
            result = self._hosts[index].urlIterator
        return result

    def periphery(self, peripheryID, useRoaming = True):
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
        return filter(lambda app: app.peripheryID, self._hosts)

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

    def _makeHostItem(self, name, shortName, url, urlToken = '', urlIterator = None, keyPath = None, areaID = None, peripheryID = 0):
        if not len(shortName):
            shortName = name
        return _HostItem(name, shortName, url, urlToken, urlIterator, keyPath, areaID, peripheryID)

    def _determineRecommendHost(self):
        defAvail = HOST_AVAILABILITY.NOT_AVAILABLE
        pResGetter = self.__pingResult.get
        csisResGetter = self.__csisResponse.get
        queryResult = map(lambda host: (host, pResGetter(host.url, -1), csisResGetter(host.peripheryID, defAvail)), self.peripheries())
        self.__recommended = filter(lambda item: item[2] == HOST_AVAILABILITY.RECOMMENDED, queryResult)
        if not len(self.__recommended):
            self.__recommended = filter(lambda item: item[2] == HOST_AVAILABILITY.NOT_RECOMMENDED, queryResult)
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

    def __ping(self):
        if not self.__setPingCallback:
            self.__onPingPerformed([])
            return
        try:
            peripheries = map(lambda host: host.url, self.peripheries())
            LOG_DEBUG('Ping starting', peripheries)
            BigWorld.WGPinger.ping(peripheries)
        except (AttributeError, TypeError):
            LOG_CURRENT_EXCEPTION()
            self.__onPingPerformed([])

    def __onPingPerformed(self, result):
        LOG_DEBUG('Ping performed', result)
        try:
            self.__pingResult = dict(result)
            self.__autoLoginQueryCompleted(AUTO_LOGIN_QUERY_STATE.PING_PERFORMED)
        except Exception:
            LOG_CURRENT_EXCEPTION()
            self.__pingResult = {}

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
        if len(self.__csisUrl):
            if not self._isCSISQueryInProgress:
                timeFromLastUpdate = time.time() - self.__lastCsisUpdateTime
                if timeFromLastUpdate >= CSIS_REQUEST_TIMER:
                    self._isCSISQueryInProgress = True
                    self.onCsisQueryStart()
                    allHosts = self.hosts()
                    peripheries = map(lambda host: host.peripheryID, allHosts)
                    LOG_DEBUG('CSIS query sending', peripheries)
                    _CSISRequestWorker(self.__csisUrl, self.__receiveCsisResponse, peripheries).start()
                else:
                    self.__finishCsisQuery()
        else:
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
        filtered = filter(lambda item: item[1] > -1, recommended)
        if len(filtered):
            minPingTime = min(filtered, key=lambda item: item[1])[1]
            maxPingTime = 1.2 * minPingTime
            result = filter(lambda item: item[1] < maxPingTime, filtered)
        return result

    def __choiceFromRecommended(self):
        recommended = random.choice(self.__recommended)
        self.__recommended = filter(lambda item: item != recommended, self.__recommended)
        return recommended[0]


g_preDefinedHosts = _PreDefinedHostList()
