# Embedded file name: scripts/client/gui/game_control/links.py
import base64
import re
from urllib import quote_plus
import BigWorld
from ConnectionManager import connectionManager
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from helpers import getClientLanguage

class URLMarcos(object):

    def __init__(self):
        super(URLMarcos, self).__init__()
        self.__macros = {'LANGUAGE_CODE': 'getLanguageCode',
         'AREA_ID': 'getAreaID',
         'ENCODED_LOGIN': 'getEncodedLogin',
         'QUOTED_LOGIN': 'getQuotedLogin',
         'TARGET_URL': 'getTargetURL',
         'DB_ID': 'getDatabaseID'}
        filter = '\\$(' + reduce(lambda x, y: x + '|' + y, self.__macros.iterkeys()) + ')'
        self.__filter = re.compile(filter)
        self.__targetURL = ''

    def clear(self):
        self.__macros.clear()
        self.__filter = None
        return

    def hasMarcos(self, url):
        return len(self.__filter.findall(url)) > 0

    def parse(self, url):
        return self.__filter.sub(self._replace, url)

    def getLanguageCode(self):
        code = getClientLanguage()
        return code.replace('_', '-')

    def getAreaID(self):
        areaID = connectionManager.areaID
        if areaID:
            result = str(areaID)
        else:
            result = 'errorArea'
        return result

    def getEncodedLogin(self):
        login = connectionManager.loginName
        if login:
            result = login
        else:
            result = 'errorLogin'
        return base64.b64encode(result)

    def getQuotedLogin(self):
        login = connectionManager.lastLoginName
        if login:
            result = quote_plus(login)
        else:
            result = ''
        return result

    def getDatabaseID(self):
        dbID = connectionManager.databaseID
        if dbID:
            result = str(dbID)
        else:
            result = 'errorID'
        return result

    def getTargetURL(self):
        result = self.__targetURL
        if self.__targetURL:
            result = quote_plus(self.__targetURL)
        return result

    def setTargetURL(self, targetURL):
        self.__targetURL = targetURL

    def _replace(self, match):
        macros = match.group(1)
        result = ''
        if macros in self.__macros.keys():
            getter = self.__macros[macros]
            result = getattr(self, getter)()
        else:
            LOG_ERROR('URL marcos is not found', macros)
        return result


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

class ExternalLinksHandler(object):

    def __init__(self):
        super(ExternalLinksHandler, self).__init__()
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

    def getURL(self, name):
        urlSettings = GUI_SETTINGS.lookup(name)
        if urlSettings:
            url = self.__urlMarcos.parse(str(urlSettings))
        else:
            url = ''
        return url

    def _handleSpecifiedURL(self, event):
        self.open(event.url)

    def _handleOpenRegistrationURL(self, _):
        self.open(self.getURL('registrationURL'))

    def _handleOpenRecoveryPasswordURL(self, _):
        self.open(self.getURL('recoveryPswdURL'))

    def _handleOpenPaymentURL(self, _):
        self.open(self.getURL('paymentURL'))

    def _handleSecuritySettingsURL(self, _):
        self.open(self.getURL('securitySettingsURL'))

    def _handleSupportURL(self, _):
        self.open(self.getURL('supportURL'))

    def _handleMigrationURL(self):
        self.open(self.getURL('migrationURL'))

    def _handleFortDescription(self, _):
        self.open(self.getURL('fortDescription'))

    def _handleClanSearch(self, _):
        self.open(self.getURL('clanSearch'))

    def _handleClanCreate(self, _):
        self.open(self.getURL('clanCreate'))

    def _handleInvitesManagementURL(self, _):
        self.open(self.getURL('invitesManagementURL'))
