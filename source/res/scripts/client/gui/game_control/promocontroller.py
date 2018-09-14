# Embedded file name: scripts/client/gui/game_control/PromoController.py
from account_helpers import getAccountDatabaseID
from account_helpers.AccountSettings import AccountSettings, PROMO
from debug_utils import LOG_DEBUG
from adisp import async, process
from gui.LobbyContext import g_lobbyContext
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control import gc_constants
from gui.game_control.controllers import Controller
from gui.game_control.links import URLMarcos
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import getClientVersion, i18n

class PromoController(Controller):
    PROMO_AUTO_VIEWS_TEST_VALUE = 5

    def __init__(self, proxy):
        super(PromoController, self).__init__(proxy)
        self.__currentVersionPromoUrl = None
        self.__currentVersionBrowserID = None
        self.__currentVersionBrowserShown = False
        self.__promoShown = set()
        self.__availablePromo = set()
        self.__urlMacros = URLMarcos()
        self._isPromoShown = False
        return

    def fini(self):
        self._stop()
        self.__urlMacros.clear()
        self.__urlMacros = None
        super(PromoController, self).fini()
        return

    def onLobbyInited(self, event):
        self._updatePromo(self._getPromoEventNotifications())
        self._getEventsFotificationController().onEventNotificationsChanged += self.__onEventNotification
        self._getBrowserController().onBrowserDeleted += self.__onBrowserDeleted
        self._processPromo(self._getEventNotifications())

    def onAvatarBecomePlayer(self):
        self._stop()

    def onDisconnected(self):
        self._stop()
        self._isPromoShown = False

    @process
    def showPatchPromo(self, isAsync = False):
        self.__currentVersionBrowserID = yield self.__showPromoBrowser(self.__currentVersionPromoUrl, i18n.makeString(MENU.PROMO_PATCH_TITLE, version=getClientVersion()), browserID=self.__currentVersionBrowserID, isAsync=isAsync)

    def isPatchPromoAvailable(self):
        return self.__currentVersionPromoUrl is not None

    def _stop(self):
        self.__currentVersionPromoUrl = None
        self.__currentVersionBrowserID = None
        self.__currentVersionBrowserShown = False
        self._getBrowserController().onBrowserDeleted -= self.__onBrowserDeleted
        self._getEventsFotificationController().onEventNotificationsChanged -= self.__onEventNotification
        return

    @process
    def _processPromo(self, promo):
        yield lambda callback: callback(True)
        if self.isPatchPromoAvailable() and self.__currentVersionPromoUrl not in self.__promoShown and self.isPromoAutoViewsEnabled() and not self._isPromoShown:
            LOG_DEBUG('Showing patchnote promo:', self.__currentVersionPromoUrl)
            self.__promoShown.add(self.__currentVersionPromoUrl)
            self.__savePromoShown()
            self.__currentVersionBrowserShown = True
            self._isPromoShown = True
            self.showPatchPromo(isAsync=True)
            return
        actionsPromo = [ item for item in promo if item.eventType.startswith(gc_constants.PROMO.TEMPLATE.ACTION) ]
        for actionPromo in actionsPromo:
            promoUrl = yield self.__urlMacros.parse(actionPromo.data)
            promoTitle = actionPromo.text
            if promoUrl not in self.__promoShown and not self._isPromoShown:
                LOG_DEBUG('Showing action promo:', promoUrl)
                self.__promoShown.add(promoUrl)
                self.__savePromoShown()
                self._isPromoShown = True
                yield self.__showPromoBrowser(promoUrl, promoTitle)
                return

    @process
    def _updatePromo(self, promosData):
        yield lambda callback: callback(True)
        for item in filter(lambda item: item.eventType in (gc_constants.PROMO.TEMPLATE.PATCH, gc_constants.PROMO.TEMPLATE.ACTION), promosData):
            promoUrl = yield self.__urlMacros.parse(item.data)
            self.__availablePromo.add(promoUrl)
            if item.eventType == gc_constants.PROMO.TEMPLATE.PATCH and self.__currentVersionPromoUrl is None:
                self.__currentVersionPromoUrl = promoUrl

        promoShownSource = AccountSettings.getFilter(PROMO)
        self.__promoShown = {url for url in promoShownSource if url in self.__availablePromo}
        self.__savePromoShown()
        return

    def _getEventNotifications(self):
        return self._proxy.getController(gc_constants.CONTROLLER.EVENTS_NOTIFICATION).getEventsNotifications()

    def _getPromoEventNotifications(self):
        filterFunc = lambda item: item.eventType in (gc_constants.PROMO.TEMPLATE.PATCH, gc_constants.PROMO.TEMPLATE.ACTION)
        return self._getEventsFotificationController().getEventsNotifications(filterFunc)

    def _getBrowserController(self):
        return self._proxy.getController(gc_constants.CONTROLLER.BROWSER)

    def _getEventsFotificationController(self):
        return self._proxy.getController(gc_constants.CONTROLLER.EVENTS_NOTIFICATION)

    def __savePromoShown(self):
        AccountSettings.setFilter(PROMO, self.__promoShown)

    def __onEventNotification(self, added, removed):
        self._updatePromo(self._getPromoEventNotifications())
        self._processPromo(added)

    def __onBrowserDeleted(self, browserID):
        if self.__currentVersionBrowserID == browserID:
            self.__currentVersionBrowserID = None
            if self.__currentVersionBrowserShown:
                self.__currentVersionBrowserShown = False
                g_eventBus.handleEvent(events.BubbleTooltipEvent(events.BubbleTooltipEvent.SHOW, i18n.makeString(TOOLTIPS.HEADER_VERSIONINFOHINT)), scope=EVENT_BUS_SCOPE.LOBBY)
        return

    @async
    @process
    def __showPromoBrowser(self, promoUrl, promoTitle, browserID = None, isAsync = True, callback = None):
        browserID = yield self._getBrowserController().load(promoUrl, promoTitle, showActionBtn=False, isAsync=isAsync, browserID=browserID, browserSize=gc_constants.BROWSER.PROMO_SIZE, background=gc_constants.BROWSER.PROMO_BACKGROUND, isDefault=False, showCloseBtn=True)
        callback(browserID)

    @classmethod
    def isPromoAutoViewsEnabled(cls):
        return getAccountDatabaseID() % cls.PROMO_AUTO_VIEWS_TEST_VALUE != 0 and g_lobbyContext.getServerSettings().isPromoAutoViewsEnabled()
