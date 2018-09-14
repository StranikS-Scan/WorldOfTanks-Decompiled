# Embedded file name: scripts/client/gui/game_control/ExternalLinksHandler.py
import BigWorld
from adisp import async, process
from debug_utils import LOG_ERROR, LOG_CURRENT_EXCEPTION
from gui import GUI_SETTINGS
from gui.game_control import gc_constants
from gui.game_control.controllers import Controller
from gui.game_control.links import URLMarcos
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
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
 OpenLinkEvent.CLUB_SETTINGS: '_handleClubSettings',
 OpenLinkEvent.INVIETES_MANAGEMENT: '_handleInvitesManagementURL',
 OpenLinkEvent.GLOBAL_MAP_SUMMARY: '_handleGmSummaryURL',
 OpenLinkEvent.GLOBAL_MAP_PROMO_SUMMARY: '_handleGmPromoSummaryURL',
 OpenLinkEvent.GLOBAL_MAP_CAP: '_handleGmCapURL',
 OpenLinkEvent.GLOBAL_MAP_PROMO: '_handleGmPromoURL'}

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

    def _handleClubSettings(self, _):
        self.__openParsedUrl('clubSettings')

    def _handleInvitesManagementURL(self, _):
        self.__openParsedUrl('invitesManagementURL')

    def _handleGmSummaryURL(self, _):
        self.__openParsedUrl('globalMapSummary')

    def _handleGmPromoSummaryURL(self, _):
        self.__openParsedUrl('globalMapPromoSummary')

    def _handleGmCapURL(self, _):
        self.__openParsedUrl('globalMapCap')

    def _handleGmPromoURL(self, _):
        self.__openParsedUrl('globalMapPromo')
