# Embedded file name: scripts/client/gui/game_control/links.py
import base64
import re
from urllib import quote_plus
import BigWorld
from constants import TOKEN_TYPE
from ConnectionManager import connectionManager
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from adisp import process, async
from gui import GUI_SETTINGS
from gui.game_control.controllers import Controller
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
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

        self.__tokenRqs.request()(_cbWrapper)

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


_LISTENERS = {OpenLinkEvent.SPECIFIED: '_handleSpecifiedURL',
 OpenLinkEvent.REGISTRATION: '_handleOpenRegistrationURL',
 OpenLinkEvent.RECOVERY_PASSWORD: '_handleOpenRecoveryPasswordURL',
 OpenLinkEvent.PAYMENT: '_handleOpenPaymentURL',
 OpenLinkEvent.SECURITY_SETTINGS: '_handleSecuritySettingsURL',
 OpenLinkEvent.SUPPORT: '_handleSupportURL',
 OpenLinkEvent.MIGRATION: '_handleMigrationURL',
 OpenLinkEvent.FORT_DESC: '_handleFortDescription',
 OpenLinkEvent.CLAN_SEARCH: '_handleClanSearch',
 OpenLinkEvent.CLAN_CREATE: '_handleClanCreate',
 OpenLinkEvent.INVIETES_MANAGEMENT: '_handleInvitesManagementURL'}

class ExternalLinksHandler(Controller):

    def __init__(self, proxy):
        super(ExternalLinksHandler, self).__init__(proxy)
        self.__urlMarcos = None
        return

    def init(self):
        self.__urlMarcos = URLMarcos()
        addListener = g_eventBus.addListener
        for eventType, handlerName in _LISTENERS.iteritems():
            handler = getattr(self, handlerName, None)
            if not handler:
                LOG_ERROR('Handler is not found', eventType, handlerName)
                continue
            if not callable(handler):
                LOG_ERROR('Handler is invalid', eventType, handlerName, handler)
                continue
            addListener(eventType, handler)

        return

    def fini(self):
        if self.__urlMarcos is not None:
            self.__urlMarcos.clear()
            self.__urlMarcos = None
        removeListener = g_eventBus.removeListener
        for eventType, handlerName in _LISTENERS.iteritems():
            handler = getattr(self, handlerName, None)
            if handler:
                removeListener(eventType, handler)

        super(ExternalLinksHandler, self).fini()
        return

    def open(self, url):
        if not url:
            LOG_ERROR('URL is empty', url)
            return
        try:
            BigWorld.wg_openWebBrowser(url)
        except Exception:
            LOG_ERROR('There is error while opening web browser at page:', url)
            LOG_CURRENT_EXCEPTION()

    @async
    @process
    def getURL(self, name, callback):
        urlSettings = GUI_SETTINGS.lookup(name)
        if urlSettings:
            url = yield self.__urlMarcos.parse(str(urlSettings))
        else:
            url = yield lambda callback: callback('')
        callback(url)

    def _handleSpecifiedURL(self, event):
        self.open(event.url)

    @process
    def __openParsedUrl(self, urlName):
        parsedUrl = yield self.getURL(urlName)
        self.open(parsedUrl)

    def _handleOpenRegistrationURL(self, _):
        self.__openParsedUrl('registrationURL')

    def _handleOpenRecoveryPasswordURL(self, _):
        self.__openParsedUrl('recoveryPswdURL')

    def _handleOpenPaymentURL(self, _):
        self.__openParsedUrl('paymentURL')

    def _handleSecuritySettingsURL(self, _):
        self.__openParsedUrl('securitySettingsURL')

    def _handleSupportURL(self, _):
        self.__openParsedUrl('supportURL')

    def _handleMigrationURL(self):
        self.__openParsedUrl('migrationURL')

    def _handleFortDescription(self, _):
        self.__openParsedUrl('fortDescription')

    def _handleClanSearch(self, _):
        self.__openParsedUrl('clanSearch')

    def _handleClanCreate(self, _):
        self.__openParsedUrl('clanCreate')

    def _handleInvitesManagementURL(self, _):
        self.__openParsedUrl('invitesManagementURL')
