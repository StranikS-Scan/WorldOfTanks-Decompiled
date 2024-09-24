# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/links_handlers/ExternalLinksHandler.py
import typing
import logging
from adisp import adisp_async, adisp_process
from gui import GUI_SETTINGS
from gui.game_control.links import URLMacros
from gui.shared import g_eventBus
from gui.shared.events import OpenLinkEvent
from helpers import dependency
from skeletons.gui.game_control import IExternalLinksController
from gui.game_control.links_handlers import external
from skeletons.gui.login_manager import ILoginManager
if typing.TYPE_CHECKING:
    from gui.game_control.links_handlers.external import ILinksHandler
_logger = logging.getLogger(__name__)
_LISTENERS = {OpenLinkEvent.SPECIFIED: '_handleSpecifiedURL',
 OpenLinkEvent.PARSED: '_handleParsedURL',
 OpenLinkEvent.REGISTRATION: '_handleOpenRegistrationURL',
 OpenLinkEvent.RECOVERY_PASSWORD: '_handleOpenRecoveryPasswordURL',
 OpenLinkEvent.PAYMENT: '_handleOpenPaymentURL',
 OpenLinkEvent.SECURITY_SETTINGS: '_handleSecuritySettingsURL',
 OpenLinkEvent.CLAN_RULES: '_handleClanRulesURL',
 OpenLinkEvent.SUPPORT: '_handleSupportURL',
 OpenLinkEvent.MIGRATION: '_handleMigrationURL',
 OpenLinkEvent.FORT_DESC: '_handleFortDescription',
 OpenLinkEvent.CLAN_SEARCH: '_handleClanSearch',
 OpenLinkEvent.CLAN_CREATE: '_handleClanCreate',
 OpenLinkEvent.INVIETES_MANAGEMENT: '_handleInvitesManagementURL',
 OpenLinkEvent.GLOBAL_MAP_SUMMARY: '_handleGmSummaryURL',
 OpenLinkEvent.GLOBAL_MAP_PROMO_SUMMARY: '_handleGmPromoSummaryURL',
 OpenLinkEvent.GLOBAL_MAP_CAP: '_handleGmCapURL',
 OpenLinkEvent.GLOBAL_MAP_PROMO: '_handleGmPromoURL',
 OpenLinkEvent.PREM_SHOP: '_handleOpenPremShopURL',
 OpenLinkEvent.FRONTLINE_CHANGES: '_handleFrontlineChangesURL',
 OpenLinkEvent.TOKEN_SHOP: '_handleTokenShopURL',
 OpenLinkEvent.WOT_PLUS_STEAM_SHOP: '_handleWotPlusSteamShopURL',
 OpenLinkEvent.WOT_PLUS_SHOP: '_handleWotPlusShopURL',
 OpenLinkEvent.STEAM_SUBSCRIPTION_MANAGEMENT: '_handleSteamSubscriptionManagementURL',
 OpenLinkEvent.LOOT_BOXES_LIST: '_handleLootBoxesListURL'}

class ExternalLinksHandler(IExternalLinksController):
    __loginManager = dependency.descriptor(ILoginManager)

    def __init__(self):
        super(ExternalLinksHandler, self).__init__()
        self.__urlMacros = None
        self.__linksHandlers = None
        return

    def init(self):
        self.__urlMacros = URLMacros()
        addListener = g_eventBus.addListener
        for eventType, handlerName in _LISTENERS.iteritems():
            handler = getattr(self, handlerName, None)
            if not handler:
                _logger.error('Handler is not found %s %s', eventType, handlerName)
                continue
            if not callable(handler):
                _logger.error('Handler is invalid %s %s %r', eventType, handlerName, handler)
                continue
            addListener(eventType, handler)

        return

    def fini(self):
        if self.__urlMacros is not None:
            self.__urlMacros.clear()
            self.__urlMacros = None
        removeListener = g_eventBus.removeListener
        for eventType, handlerName in _LISTENERS.iteritems():
            handler = getattr(self, handlerName, None)
            if handler:
                removeListener(eventType, handler)

        super(ExternalLinksHandler, self).fini()
        return

    def open(self, url):
        if not url:
            _logger.error('URL is empty %r', url)
            return
        handled = False
        for handler in self._getHandlers():
            handled = handler.handle(url)
            if handled:
                break

        if not handled:
            _logger.error('Cant handle external link: %s', url)

    @adisp_async
    @adisp_process
    def getURL(self, name, params=None, callback=lambda *args: None):
        urlSettings = GUI_SETTINGS.lookup(name)
        if urlSettings:
            url = yield self.__urlMacros.parse(str(urlSettings), params)
        else:
            url = yield lambda callback: callback('')
        callback(url)

    def externalAllowed(self, url):
        for handler in self._getHandlers():
            result = handler.checkHandle(url)
            if result.handled:
                return result.externalAllowed

        return False

    def _handleSpecifiedURL(self, event):
        self.open(event.url)

    @adisp_process
    def __openParsedUrl(self, urlName, params=None):
        parsedUrl = yield self.getURL(urlName, params)
        self.open(parsedUrl)

    def _handleParsedURL(self, event):
        self.__openParsedUrl(event.url)

    def _handleOpenRegistrationURL(self, _):
        self.__openParsedUrl('registrationURL')

    def _handleOpenRecoveryPasswordURL(self, _):
        self.__openParsedUrl('recoveryPswdURL')

    def _handleOpenPaymentURL(self, _):
        self.__openParsedUrl('paymentURL')

    def _handleSecuritySettingsURL(self, _):
        self.__openParsedUrl('securitySettingsURL')

    def _handleClanRulesURL(self, _):
        self.__openParsedUrl('clanRulesURL')

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

    def _handleGmSummaryURL(self, _):
        self.__openParsedUrl('globalMapSummary')

    def _handleGmPromoSummaryURL(self, _):
        self.__openParsedUrl('globalMapPromoSummary')

    def _handleGmCapURL(self, _):
        self.__openParsedUrl('globalMapCap')

    def _handleGmPromoURL(self, _):
        self.__openParsedUrl('globalMapPromo')

    def _handleOpenPremShopURL(self, _):
        self.__openParsedUrl('premShopURL')

    def _handleFrontlineChangesURL(self, _):
        self.__openParsedUrl('frontlineChangesURL')

    def _handleTokenShopURL(self, event):
        self.__openParsedUrl('tokenShopURL', event.params)

    def _handleWotPlusSteamShopURL(self, _):
        self.__openParsedUrl('wotPlusSteamURL')

    def _handleWotPlusShopURL(self, _):
        self.__openParsedUrl('wotPlusShopURL')

    def _handleSteamSubscriptionManagementURL(self, _):
        self.__openParsedUrl('steamSubscriptionManagementURL')

    def _handleLootBoxesListURL(self, _):
        self.__openParsedUrl('lootBoxesListURL')

    def _getHandlers(self):
        if not self.__linksHandlers:
            self.__linksHandlers = []
            if self.__loginManager.isWgcSteam:
                self.__linksHandlers.append(external.PremShopLinksHandler())
                self.__linksHandlers.append(external.AddPlatformTagLinksHandler())
                self.__linksHandlers.append(external.PremShopLinksForArgsUrlHandler())
                self.__linksHandlers.append(external.AddPlatformTagLinksToArgsUrlHandler())
            self.__linksHandlers.append(external.OpenBrowserHandler())
        return self.__linksHandlers
