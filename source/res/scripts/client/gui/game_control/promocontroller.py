# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/PromoController.py
from collections import namedtuple
from account_helpers import getAccountDatabaseID
from account_helpers.AccountSettings import AccountSettings, PROMO, LAST_PROMO_PATCH_VERSION
from account_shared import getClientMainVersion
from adisp import async, process
from debug_utils import LOG_DEBUG, LOG_WARNING
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.view.lobby.shared.web_handlers import handleHangarSoundCommand, handleHangarSoundCommandFini
from gui.Scaleform.locale.MENU import MENU
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.game_control import gc_constants
from gui.game_control.links import URLMarcos
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.utils import isPopupsWindowsOpenDisabled
from helpers import i18n, isPlayerAccount, dependency
from shared_utils import CONST_CONTAINER
from skeletons.gui.game_control import IPromoController, IBrowserController, IEventsNotificationsController
from skeletons.gui.lobby_context import ILobbyContext
from web_client_api.commands.sound import createHangarSoundHandler
_PromoData = namedtuple('_PromoData', ['url', 'title', 'guiActionHandlers'])

class PromoController(IPromoController):
    PROMO_AUTO_VIEWS_TEST_VALUE = 5
    browserCtrl = dependency.descriptor(IBrowserController)
    eventsNotification = dependency.descriptor(IEventsNotificationsController)
    lobbyContext = dependency.descriptor(ILobbyContext)

    class GUI_EVENTS(CONST_CONTAINER):
        CLOSE_GUI_EVENT = 'close_window'

    def __init__(self):
        super(PromoController, self).__init__()
        self.__currentVersionPromoUrl = None
        self.__currentVersionBrowserID = None
        self.__currentVersionBrowserShown = False
        self.__promoShown = set()
        self.__availablePromo = set()
        self.__urlMacros = URLMarcos()
        self.__guiActionsHandlers = None
        self.__isLobbyInited = False
        self.__pendingPromo = None
        self._isPromoShown = False
        return

    def fini(self):
        self._stop()
        self.__pendingPromo = None
        self.__urlMacros.clear()
        self.__urlMacros = None
        self.__guiActionsHandlers = None
        super(PromoController, self).fini()
        return

    def onLobbyInited(self, event):
        if not isPlayerAccount():
            return
        self.__isLobbyInited = True
        self._updatePromo(self._getPromoEventNotifications())
        self.eventsNotification.onEventNotificationsChanged += self.__onEventNotification
        self.browserCtrl.onBrowserDeleted += self.__onBrowserDeleted
        popupsWindowsDisabled = isPopupsWindowsOpenDisabled()
        if not popupsWindowsDisabled:
            self._processPromo(self.eventsNotification.getEventsNotifications())

    def onAvatarBecomePlayer(self):
        self._stop()

    def onDisconnected(self):
        self._stop()
        self._isPromoShown = False

    @process
    def showVersionsPatchPromo(self):
        promoUrl = yield self.__urlMacros.parse(GUI_SETTINGS.promoscreens)
        webBrowser = self.__getCurrentBrowser()
        if not webBrowser or promoUrl != webBrowser.url:
            promoTitle = i18n.makeString(MENU.PROMO_PATCH_TITLE)
            self.__currentVersionBrowserID = yield self.__showPromoBrowser(promoUrl, promoTitle, browserID=self.__currentVersionBrowserID, isAsync=False, showWaiting=True)

    def showPromo(self, url, title, forced=False, handlers=None):
        """
        :param url: url that should be opened in the browser:
        :param title: the title of browser window:
        :param forced: True - promowindow with new URL will be shown in any case,
                       False - new promowindow will be shown
                       if there has not been already shown promowindow during the session:
        :param handlers: Dict:
                key - gui action self.GUI_EVENTS.*
                value - functions that should to be invoked when particular gui action has happened
        """
        if forced:
            self.__registerAndShowPromoBrowser(url, title, handlers)
            self._isPromoShown = True
        elif self.__isLobbyInited:
            if not self._isPromoShown:
                self.__registerAndShowPromoBrowser(url, title, handlers)
                self._isPromoShown = True
        else:
            self.__pendingPromo = _PromoData(url, title, handlers)

    def getCurrentVersionBrowserID(self):
        return self.__currentVersionBrowserID

    @classmethod
    def isPromoAutoViewsEnabled(cls):
        return getAccountDatabaseID() % cls.PROMO_AUTO_VIEWS_TEST_VALUE != 0 and cls.lobbyContext.getServerSettings().isPromoAutoViewsEnabled()

    def isPatchPromoAvailable(self):
        return self.__currentVersionPromoUrl is not None and GUI_SETTINGS.isPatchPromoEnabled

    def isPatchChanged(self):
        mainVersion = getClientMainVersion()
        return mainVersion is not None and AccountSettings.getSettings(LAST_PROMO_PATCH_VERSION) != mainVersion

    def _stop(self):
        self.__isLobbyInited = False
        self.__currentVersionPromoUrl = None
        self.__currentVersionBrowserID = None
        self.__currentVersionBrowserShown = False
        self.browserCtrl.onBrowserDeleted -= self.__onBrowserDeleted
        self.__cleanupGuiActionHandlers()
        self.eventsNotification.onEventNotificationsChanged -= self.__onEventNotification
        return

    @process
    def _showCurrentVersionPatchPromo(self, isAsync=False):
        self.__currentVersionBrowserID = yield self.__showPromoBrowser(self.__currentVersionPromoUrl, i18n.makeString(MENU.PROMO_PATCH_TITLE), browserID=self.__currentVersionBrowserID, isAsync=isAsync, showWaiting=not isAsync)

    @process
    def _processPromo(self, promo):
        yield lambda callback: callback(True)
        if self.isPatchPromoAvailable() and self.isPatchChanged() and self.isPromoAutoViewsEnabled() and not self._isPromoShown:
            LOG_DEBUG('Showing patchnote promo:', self.__currentVersionPromoUrl)
            AccountSettings.setSettings(LAST_PROMO_PATCH_VERSION, getClientMainVersion())
            self.__currentVersionBrowserShown = True
            self._isPromoShown = True
            self._showCurrentVersionPatchPromo(isAsync=True)
            return
        elif not self._isPromoShown and self.__pendingPromo is not None:
            self.__registerAndShowPromoBrowser(*self.__pendingPromo)
            self.__pendingPromo = None
            return
        else:
            actionsPromo = [ item for item in promo if item.eventType.startswith(gc_constants.PROMO.TEMPLATE.ACTION) ]
            for actionPromo in actionsPromo:
                promoUrl = yield self.__urlMacros.parse(actionPromo.data)
                promoTitle = actionPromo.text
                if promoUrl not in self.__promoShown and not self._isPromoShown and promoUrl != self.__currentVersionPromoUrl:
                    LOG_DEBUG('Showing action promo:', promoUrl)
                    self.__promoShown.add(promoUrl)
                    self.__savePromoShown()
                    self._isPromoShown = True
                    yield self.__showPromoBrowser(promoUrl, promoTitle)
                    return

            return

    @process
    def _updatePromo(self, promosData):
        yield lambda callback: callback(True)
        for item in filter(lambda item: item.eventType == gc_constants.PROMO.TEMPLATE.ACTION, promosData):
            promoUrl = yield self.__urlMacros.parse(item.data)
            self.__availablePromo.add(promoUrl)

        if self.__currentVersionPromoUrl is None:
            self.__currentVersionPromoUrl = yield self.__urlMacros.parse(GUI_SETTINGS.currentVersionPromo)
        promoShownSource = AccountSettings.getFilter(PROMO)
        self.__promoShown = {url for url in promoShownSource if url in self.__availablePromo}
        self.__savePromoShown()
        return

    def _getPromoEventNotifications(self):

        def filterFunc(item):
            return item.eventType == gc_constants.PROMO.TEMPLATE.ACTION

        return self.eventsNotification.getEventsNotifications(filterFunc)

    def __onUserRequestToClose(self):
        self.__guiActionsHandlers[self.GUI_EVENTS.CLOSE_GUI_EVENT]()
        self.__cleanupGuiActionHandlers()

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

    def __registerGuiActionHandlers(self, handlers):
        self.__guiActionsHandlers = handlers
        if handlers:
            webBrowser = self.__getCurrentBrowser()
            if webBrowser is not None:
                webBrowser.onUserRequestToClose += self.__onUserRequestToClose
            else:
                LOG_WARNING('Browser with id = "{}" has not been found'.format(self.__currentVersionBrowserID))
        return

    def __cleanupGuiActionHandlers(self):
        webBrowser = self.__getCurrentBrowser()
        if self.__guiActionsHandlers is not None and webBrowser:
            webBrowser.onUserRequestToClose -= self.__onUserRequestToClose
            self.__guiActionsHandlers = None
        return

    @process
    def __registerAndShowPromoBrowser(self, url, title, handlers):
        promoUrl = yield self.__urlMacros.parse(url)
        LOG_DEBUG('Showing promo:', promoUrl)
        webBrowser = self.__getCurrentBrowser()
        if not webBrowser or promoUrl != webBrowser.url:
            self.__cleanupGuiActionHandlers()
            self.__currentVersionBrowserID = yield self.__showPromoBrowser(promoUrl, title, browserID=self.__currentVersionBrowserID, isAsync=False, showWaiting=True)
            self.__registerGuiActionHandlers(handlers)

    def __getCurrentBrowser(self):
        return self.browserCtrl.getBrowser(self.__currentVersionBrowserID)

    @async
    @process
    def __showPromoBrowser(self, promoUrl, promoTitle, browserID=None, isAsync=True, showWaiting=False, callback=None):
        browserID = yield self.browserCtrl.load(promoUrl, promoTitle, showActionBtn=False, isAsync=isAsync, browserID=browserID, browserSize=gc_constants.BROWSER.PROMO_SIZE, isDefault=False, showCloseBtn=True, showWaiting=showWaiting, handlers=self.__createPromoWebHandlers())
        callback(browserID)

    def __createPromoWebHandlers(self):
        return [createHangarSoundHandler(handleHangarSoundCommand, handleHangarSoundCommandFini)]
