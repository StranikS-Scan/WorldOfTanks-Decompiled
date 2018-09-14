# Embedded file name: scripts/client/gui/game_control/links.py
import base64
import re
from urllib import quote_plus
import BigWorld
from constants import TOKEN_TYPE
from ConnectionManager import connectionManager
from debug_utils import LOG_ERROR
from adisp import process, async
from gui.shared.utils.requesters import TokenRequester
from helpers import getClientLanguage

class URLMarcos(object):
    __MACROS_PREFIX = '$'

    def __init__(self):
        super(URLMarcos, self).__init__()
        self.__macros = {'LANGUAGE_CODE': 'getLanguageCode',
         'AREA_ID': 'getAreaID',
         'ENCODED_LOGIN': 'getEncodedLogin',
         'QUOTED_LOGIN': 'getQuotedLogin',
         'TARGET_URL': 'getTargetURL',
         'DB_ID': 'getDatabaseID',
         'WGNI_TOKEN': 'getWgniToken'}
        pattern = ('\\%s(' + reduce(lambda x, y: x + '|' + y, self.__macros.iterkeys()) + ')') % self.__MACROS_PREFIX
        self.__filter = re.compile(pattern)
        self.__targetURL = ''
        self.__tokenRqs = TokenRequester(TOKEN_TYPE.WGNI, cache=False)

    def clear(self):
        self.__tokenRqs.clear()
        self.__macros.clear()
        self.__filter = None
        return

    def hasMarcos(self, url):
        return len(self.__filter.findall(url)) > 0

    @async
    @process
    def parse(self, url, callback):
        yield lambda callback: callback(True)
        for macros in self.__filter.findall(url):
            replacement = yield self._replace(macros)
            url = url.replace(self._getUserMacrosName(macros), replacement)

        callback(url)

    @async
    def getLanguageCode(self, callback):
        code = getClientLanguage()
        callback(code.replace('_', '-'))

    @async
    def getAreaID(self, callback):
        areaID = connectionManager.areaID
        if areaID:
            result = str(areaID)
        else:
            result = 'errorArea'
        callback(result)

    @async
    def getEncodedLogin(self, callback):
        login = connectionManager.loginName
        if login:
            result = login
        else:
            result = 'errorLogin'
        callback(base64.b64encode(result))

    @async
    def getQuotedLogin(self, callback):
        login = connectionManager.lastLoginName
        if login:
            result = quote_plus(login)
        else:
            result = ''
        callback(result)

    @async
    def getDatabaseID(self, callback):
        dbID = connectionManager.databaseID
        if dbID:
            result = str(dbID)
        else:
            result = 'errorID'
        callback(result)

    @async
    def getTargetURL(self, callback):
        result = self.__targetURL
        if self.__targetURL:
            result = quote_plus(self.__targetURL)
        callback(result)

    @async
    def getWgniToken(self, callback):

        def _cbWrapper(response):
            if response and response.isValid():
                callback(str(response.getToken()))
            else:
                callback('')

        if not self.__tokenRqs.isInProcess():
            self.__tokenRqs.request(timeout=10.0)(_cbWrapper)
        else:
            _cbWrapper(response=None)
        return

    def setTargetURL(self, targetURL):
        self.__targetURL = targetURL

    @async
    @process
    def _replace(self, macros, callback):
        yield lambda callback: callback(True)
        result = ''
        if macros in self.__macros:
            result = yield getattr(self, self.__macros[macros])()
        else:
            LOG_ERROR('URL marcos is not found', macros)
        callback(result)

    def _getUserMacrosName(self, macros):
        return '%s%s' % (self.__MACROS_PREFIX, str(macros))
