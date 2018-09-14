# Embedded file name: scripts/client/gui/game_control/PromoController.py
import weakref
import BigWorld
from PlayerEvents import g_playerEvents
from account_helpers.AccountSettings import AccountSettings, PROMO
from debug_utils import LOG_DEBUG
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control.links import URLMarcos
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import getClientVersion, i18n, getClientLanguage

class PromoController(object):
    _PROMO_BROWSER_SIZE = (780, 470)
    _PROMO_BROWSER_BACKGROUND = 'file:///gui/maps/promo_bg.png'
    _PATCH_TEMPLATE = 'promo_patchnote'
    _ACTION_PREFIX = 'promo_action'

    def __init__(self, proxy):
        self.__proxy = weakref.proxy(proxy)
        self.__currentVersionPromoUrl = None
        self.__currentVersionBrowserID = None
        self.__currentVersionBrowserShown = False
        self.__promoShown = set()
        self.__availablePromo = set()
        self.__urlMacros = URLMarcos()
        return

    def init(self):
        pass

    def fini(self):
        self.__urlMacros.clear()
        self.__urlMacros = None
        return

    def start(self):
        self._updatePromo(self._getEventNotifications())
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotification
        g_eventBus.addListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)
        self._getBrowserController().onBrowserDeleted += self.__onBrowserDeleted

    def stop(self):
        self.__currentVersionPromoUrl = None
        self.__currentVersionBrowserID = None
        self.__currentVersionBrowserShown = False
        self._getBrowserController().onBrowserDeleted -= self.__onBrowserDeleted
        g_eventBus.removeListener(events.GUICommonEvent.LOBBY_VIEW_LOADED, self.__handleLobbyLoaded)
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotification
        return

    def showPatchPromo(self, isAsync = False):
        self.__currentVersionBrowserID = self.__showPromoBrowser(self.__currentVersionPromoUrl, i18n.makeString(MENU.PROMO_PATCH_TITLE, version=getClientVersion()), browserID=self.__currentVersionBrowserID, isAsync=isAsync)

    def isPatchPromoAvailable(self):
        return self.__currentVersionPromoUrl is not None

    def _processPromo(self, promo):
        if self.isPatchPromoAvailable() and self.__currentVersionPromoUrl not in self.__promoShown:
            LOG_DEBUG('Showing patchnote promo:', self.__currentVersionPromoUrl)
            self.__promoShown.add(self.__currentVersionPromoUrl)
            self.__savePromoShown()
            self.__currentVersionBrowserShown = True
            self.showPatchPromo()
            return
        actionsPromo = [ item for item in promo if item['type'].startswith(self._ACTION_PREFIX) ]
        for actionPromo in actionsPromo:
            promoUrl = self.__urlMacros.parse(actionPromo['data'])
            promoTitle = actionPromo['text'].get(getClientLanguage())
            if promoUrl not in self.__promoShown:
                LOG_DEBUG('Showing action promo:', promoUrl)
                self.__promoShown.add(promoUrl)
                self.__savePromoShown()
                self.__showPromoBrowser(promoUrl, promoTitle)
                return

    def _updatePromo(self, promosData):
        for item in filter(lambda item: item['type'] in (self._PATCH_TEMPLATE, self._ACTION_PREFIX), promosData):
            promoUrl = self.__urlMacros.parse(item['data'])
            self.__availablePromo.add(promoUrl)
            if item['type'] == self._PATCH_TEMPLATE and self.__currentVersionPromoUrl is None:
                self.__currentVersionPromoUrl = promoUrl

        promoShownSource = AccountSettings.getFilter(PROMO)
        self.__promoShown = {url for url in promoShownSource if url in self.__availablePromo}
        self.__savePromoShown()
        return

    def _getEventNotifications(self):
        return BigWorld.player().eventNotifications

    def _getBrowserController(self):
        return self.__proxy.browser

    def __savePromoShown(self):
        AccountSettings.setFilter(PROMO, self.__promoShown)

    def __onEventNotification(self, diff):
        self._updatePromo(self._getEventNotifications())
        added = diff.get('added')
        if added is not None:
            self._processPromo(added)
        return

    def __handleLobbyLoaded(self, *args):
        self._processPromo(self._getEventNotifications())

    def __onBrowserDeleted(self, browserID):
        if self.__currentVersionBrowserID == browserID:
            self.__currentVersionBrowserID = None
            if self.__currentVersionBrowserShown:
                self.__currentVersionBrowserShown = False
                g_eventBus.handleEvent(events.BubbleTooltipEvent(events.BubbleTooltipEvent.SHOW, i18n.makeString(TOOLTIPS.HEADER_VERSIONINFOHINT)), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    def __showPromoBrowser(self, promoUrl, promoTitle, browserID = None, isAsync = True):
        return self._getBrowserController().load(promoUrl, promoTitle, showActionBtn=False, isAsync=isAsync, browserID=browserID, browserSize=self._PROMO_BROWSER_SIZE, background=self._PROMO_BROWSER_BACKGROUND, isDefault=False)
