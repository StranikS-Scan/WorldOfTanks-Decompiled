# Embedded file name: scripts/client/gui/game_control/links.py
import base64
import re
from urllib import quote_plus
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
        patterns = []
        for macro in self.__macros.iterkeys():
            patterns.append('\\%(macro)s\\(.*\\)|\\%(macro)s' % {'macro': self._getUserMacrosName(macro)})

        self.__filter = re.compile('|'.join(patterns))
        self.__argsFilter = re.compile('\\$(\\w*)(\\((.*)\\))?')
        self.__targetURL = ''
        self.__tokenRqs = TokenRequester(TOKEN_TYPE.WGNI, cache=False)

    def clear(self):
        self.__tokenRqs.clear()
        self.__macros.clear()
        self.__argsFilter = None
        self.__filter = None
        return

    def hasMarcos(self, url):
        return len(self.__filter.findall(url)) > 0

    @async
    @process
    def parse(self, url, callback):
        yield lambda callback: callback(True)
        for macros in self.__filter.findall(url):
            macroName, _, args = self.__argsFilter.match(macros).groups()
            replacement = yield self._replace(macroName, args)
            url = url.replace(macros, replacement)

        callback(url)

    @async
    def getLanguageCode(self, args, callback):
        code = getClientLanguage()
        callback(code.replace('_', '-'))

    @async
    def getAreaID(self, args, callback):
        areaID = connectionManager.areaID
        if areaID:
            result = str(areaID)
        else:
            result = 'errorArea'
        callback(result)

    @async
    def getEncodedLogin(self, args, callback):
        login = connectionManager.loginName
        if login:
            result = login
        else:
            result = 'errorLogin'
        callback(base64.b64encode(result))

    @async
    def getQuotedLogin(self, args, callback):
        login = connectionManager.lastLoginName
        if login:
            result = quote_plus(login)
        else:
            result = ''
        callback(result)

    @async
    def getDatabaseID(self, args, callback):
        dbID = connectionManager.databaseID
        if dbID:
            result = str(dbID)
        else:
            result = 'errorID'
        callback(result)

    @async
    def getTargetURL(self, args, callback):
        if args:
            result = args
        else:
            result = self.__targetURL
        if result:
            result = quote_plus(result)
        callback(result)

    @async
    def getWgniToken(self, args, callback):

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
    def _replace(self, macros, args, callback):
        yield lambda callback: callback(True)
        result = ''
        if macros in self.__macros:
            result = yield getattr(self, self.__macros[macros])(args)
        else:
            LOG_ERROR('URL marcos is not found', macros)
        callback(result)

    def _getUserMacrosName(self, macros):
        return '%s%s' % (self.__MACROS_PREFIX, str(macros))
