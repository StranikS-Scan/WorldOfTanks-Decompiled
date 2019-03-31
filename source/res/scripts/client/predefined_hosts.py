# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/predefined_hosts.py
# Compiled at: 2018-11-29 14:33:44
import BigWorld, ResMgr
import base64, pickle, random, time, threading
from collections import namedtuple
import constants
from debug_utils import LOG_CURRENT_EXCEPTION, LOG_DEBUG, LOG_WARNING
import Settings
from helpers import i18n
from urllib import urlencode
import urllib2
AUTO_LOGIN_QUERY_ENABLED = constants.IS_DEVELOPMENT or not constants.IS_CHINA
AUTO_LOGIN_QUERY_URL = 'auto.login.app:0000'
STORED_AS_RECOMMEND_DELTA = 15 * 60

class HOST_AVAILABILITY(object):
    NOT_AVAILABLE = -1
    NOT_RECOMMENDED = 0
    RECOMMENDED = 1


class AUTO_LOGIN_QUERY_STATE(object):
    DEFAULT = 0
    START = 1
    CSIS_RESPONSE_RECEIVED = 2
    COMPLETED = START | CSIS_RESPONSE_RECEIVED


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
                result[name] = subSec.readInt('availability', HOST_AVAILABILITY.NOT_AVAILABLE)

    return result


class _CSISRequestWorker(threading.Thread):

    def __init__(self, url, callback, params=None):
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
                try:
                    url = self._makeUrl()
                    LOG_DEBUG('CSIS url', url)
                    req = urllib2.Request(url=url)
                    urllib2.build_opener(urllib2.HTTPHandler())
                    info = urllib2.urlopen(req)
                    if info.code == 200 and info.headers.type == 'text/xml':
                        response = _CSISResponseParser(info.read())
                except (urllib2.URLError, IOError):
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
 'url',
 'urlIterator',
 'keyPath',
 'areaID',
 'peripheryID']))

class _PreDefinedHostList(object):

    def __init__(self):
        super(_PreDefinedHostList, self).__init__()
        self._hosts = []
        self._urlMap = {}
        self._nameMap = {}
        self._peripheryMap = {}
        self._isDataLoaded = False
        self.__csisUrl = ''
        self.__csisResponse = {}
        self.__queryCallback = None
        self.__queryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
        return

    def fini(self):
        self._hosts = []
        self._urlMap.clear()
        self._nameMap.clear()
        self._peripheryMap.clear()
        self._isDataLoaded = False
        self.__csisResponse.clear()
        self.__csisUrl = ''
        self.__queryCallback = None
        self.__queryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
        return

    def _makeLoginAppItem(self, name, url, urlIterator=None, keyPath=None, areaID=None, peripheryID=0):
        return _HostItem(name, url, urlIterator, keyPath, areaID, peripheryID)

    def __sendCSISQuery(self):
        if len(self.__csisUrl):
            peripheries = map(lambda host: host.peripheryID, self.peripheries())
            LOG_DEBUG('CSIS query sending', peripheries)
            _CSISRequestWorker(self.__csisUrl, self.__receiveCSISResponse, peripheries).start()
        else:
            LOG_DEBUG('CSIS url is not defined - ignore')
            self.__csisResponse = {}
            self.__autoLoginQueryCompleted(AUTO_LOGIN_QUERY_STATE.CSIS_RESPONSE_RECEIVED)

    def __receiveCSISResponse(self, response):
        LOG_DEBUG('CSIS query received', response)
        self.__csisResponse = response
        self.__autoLoginQueryCompleted(AUTO_LOGIN_QUERY_STATE.CSIS_RESPONSE_RECEIVED)

    def __autoLoginQueryCompleted(self, state):
        if not self.__queryState & state:
            self.__queryState |= state
        if self.__queryState == AUTO_LOGIN_QUERY_STATE.COMPLETED:
            host = self._determineRecommendHost()
            LOG_DEBUG('Recommended host', host)
            self.__queryState = AUTO_LOGIN_QUERY_STATE.DEFAULT
            self.__queryCallback(host)
            self.__queryCallback = None
        return

    def _determineRecommendHost(self):
        defAvail = HOST_AVAILABILITY.NOT_AVAILABLE
        csisResGetter = self.__csisResponse.get
        queryResult = map(lambda host: (host, csisResGetter(host.peripheryID, defAvail)), self._hosts)
        recommended = filter(lambda item: item[1] == HOST_AVAILABILITY.RECOMMENDED, queryResult)
        if not len(recommended):
            recommended = filter(lambda item: item[1] == HOST_AVAILABILITY.NOT_RECOMMENDED, queryResult)
        if not len(recommended):
            if len(queryResult) > 1:
                LOG_DEBUG('List of recommended is empty. Gets random host')
                recommended = random.choice(queryResult)
                result = recommended[0]
            else:
                LOG_DEBUG('Gets first as recommended')
                result = self.first()
        else:
            LOG_DEBUG('List of recommended', recommended)
            recommended = random.choice(recommended)
            result = recommended[0]
        return result

    def autoLoginQuery(self, callback):
        if callback is None:
            LOG_WARNING('Callback is not defined.')
            return
        elif self.__queryState != AUTO_LOGIN_QUERY_STATE.DEFAULT:
            LOG_WARNING('Auto login query in process.')
            return
        elif len(self._hosts) < 2:
            callback(self.first())
            return
        else:
            peripheryID, expired = self.readPeripheryTL()
            if peripheryID > 0 and expired > 0:
                if expired > time.time():
                    host = self.periphery(peripheryID)
                    if host is not None:
                        LOG_DEBUG('Recommended host taken from cache', host)
                        callback(host)
                        return
            self.__queryState = AUTO_LOGIN_QUERY_STATE.START
            self.__csisResponse.clear()
            self.__queryCallback = callback
            self.__sendCSISQuery()
            return

    def savePeripheryTL(self, peripheryID, delta=STORED_AS_RECOMMEND_DELTA):
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
                    app = self._makeLoginAppItem(name, host, urlIterator=urls if len(urls) > 1 else None, keyPath=keyPath, areaID=areaID, peripheryID=subSec.readInt('periphery_id', 0))
                    idx = len(self._hosts)
                    self._urlMap[app.url] = idx
                    self._nameMap[app.name] = idx
                    if app.peripheryID:
                        self._peripheryMap[app.peripheryID] = idx
                    self._hosts.append(app)

            self._isDataLoaded = True
            return

    def predefined(self, url):
        return url in self._urlMap

    def first(self):
        if len(self._hosts):
            return self._hosts[0]
        return self._makeLoginAppItem('', '')

    def byUrl(self, url):
        result = self._makeLoginAppItem('', url)
        index = self._urlMap.get(url, -1)
        if index > -1:
            result = self._hosts[index]
        return result

    def byName(self, name):
        result = self._makeLoginAppItem(name, '')
        index = self._nameMap.get(name, -1)
        if index > -1:
            result = self._hosts[index]
        return result

    def hosts(self):
        return self._hosts[:]

    def shortList(self):
        result = map(lambda item: (item.url, item.name), self._hosts)
        if AUTO_LOGIN_QUERY_ENABLED and len(result) > 1:
            result.insert(0, (AUTO_LOGIN_QUERY_URL, i18n.makeString('#menu:login/auto')))
        return result

    def urlIterator(self, primary):
        result = None
        index = self._urlMap.get(primary, -1)
        if index > -1:
            result = self._hosts[index].urlIterator
        return result

    def periphery(self, peripheryID):
        result = None
        index = self._peripheryMap.get(peripheryID, -1)
        if index > -1:
            result = self._hosts[index]
        return result

    def peripheries(self):
        return filter(lambda app: app.peripheryID, self._hosts)


g_preDefinedHosts = _PreDefinedHostList()
