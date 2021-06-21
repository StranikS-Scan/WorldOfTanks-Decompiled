# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/game_control/PromoController.py
import logging
from collections import namedtuple
import BigWorld
from Event import Event, EventManager
from account_helpers.settings_core.ServerSettingsManager import UI_STORAGE_KEYS
from adisp import process, async
from frameworks.wulf import WindowLayer
from gui import GUI_SETTINGS
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework.managers.loaders import SFViewLoadParams
from gui.Scaleform.locale.TOOLTIPS import TOOLTIPS
from gui.app_loader import sf_lobby
from gui.game_control import gc_constants
from gui.game_control.links import URLMacros
from gui.promo.promo_logger import PromoLogSourceType, PromoLogActions, PromoLogSubjectType
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showBubbleTooltip
from gui.shared.events import BrowserEvent
from gui.shared.utils import isPopupsWindowsOpenDisabled
from gui.shared.utils.functions import getUniqueViewName
from gui.wgcg.promo_screens.contexts import PromoGetTeaserRequestCtx, PromoSendTeaserShownRequestCtx, PromoGetUnreadCountRequestCtx
from helpers import i18n, isPlayerAccount, dependency
from helpers.http import url_formatters
from shared_utils import findFirst
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IPromoController, IBrowserController, IEventsNotificationsController, IBootcampController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared.promo import IPromoLogger
from skeletons.gui.web import IWebController
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
from web.web_client_api.platform import PlatformWebApi
from web.web_client_api.promo import PromoWebApi
from web.web_client_api.battle_pass import BattlePassWebApi
from web.web_client_api.ranked_battles import RankedBattlesWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.social import SocialWebApi
from web.web_client_api.vehicles import VehiclesWebApi
from web.web_client_api.blueprints_convert_sale import BlueprintsConvertSaleWebApi
_PromoData = namedtuple('_PromoData', ['url', 'closeCallback', 'source'])
_logger = logging.getLogger(__name__)

class PromoController(IPromoController):
    __browserCtrl = dependency.descriptor(IBrowserController)
    __notificationsCtrl = dependency.descriptor(IEventsNotificationsController)
    __webController = dependency.descriptor(IWebController)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __logger = dependency.descriptor(IPromoLogger)
    __bootcamp = dependency.descriptor(IBootcampController)

    def __init__(self):
        super(PromoController, self).__init__()
        self.__urlMacros = URLMacros()
        self.__externalCloseCallback = None
        self.__isLobbyInited = False
        self.__pendingPromo = None
        self.__promoCount = 0
        self.__lastUpdateTimeMark = 0
        self.__promoData = None
        self.__waitingForWebBridgeData = False
        self.__battlesFromLastTeaser = 0
        self.__wasInBattle = False
        self.__hasPendingTeaser = False
        self.__isPromoOpen = False
        self.__browserCreationCallbacks = {}
        self.__browserWatchers = {}
        self.__isInHangar = False
        self.__isTeaserOpen = False
        self.__checkIntervalInBattles = GUI_SETTINGS.checkPromoFrequencyInBattles
        self.__em = EventManager()
        self.onNewTeaserReceived = Event(self.__em)
        self.onPromoCountChanged = Event(self.__em)
        self.onTeaserShown = Event(self.__em)
        self.onTeaserClosed = Event(self.__em)
        return

    @sf_lobby
    def app(self):
        pass

    def fini(self):
        self.__stop()
        self.__pendingPromo = None
        self.__urlMacros.clear()
        self.__urlMacros = None
        self.__externalCloseCallback = None
        self.__em.clear()
        g_eventBus.removeListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)
        self.__browserCreationCallbacks = {}
        self.__browserWatchers = {}
        super(PromoController, self).fini()
        return

    def onLobbyInited(self, event):
        if not isPlayerAccount():
            return
        g_eventBus.addListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)
        self.__isLobbyInited = True
        if self.__needToGetTeasersInfo():
            self.__updateWebBrgData()
        elif self.__hasPendingTeaser:
            self.__tryToShowTeaser()
        self.__notificationsCtrl.onEventNotificationsChanged += self.__onEventNotification
        if not isPopupsWindowsOpenDisabled():
            self.__processPromo(self.__notificationsCtrl.getEventsNotifications())
        self.app.loaderManager.onViewLoaded += self.__onViewLoaded

    @property
    def checkIntervalInBattles(self):
        return self.__checkIntervalInBattles

    def setNewTeaserData(self, teaserData):
        timestamp = teaserData['timestamp']
        if self.__lastUpdateTimeMark < timestamp and not self.__isPromoOpen and not self.__isTeaserOpen:
            self.__updateTeaserData(teaserData)

    def showFieldPost(self):
        url = GUI_SETTINGS.promoscreens
        loadingCallback = self.__logger.getLoggingFuture(action=PromoLogActions.OPEN_FROM_MENU, type=PromoLogSubjectType.INDEX, url=url)
        self.__showBrowserView(url, loadingCallback, soundSpaceID='field_post')

    @process
    def showLastTeaserPromo(self):
        rowUrl = self.__promoData.get('url', '')
        loadingCallback = self.__logger.getLoggingFuture(self.__promoData, action=PromoLogActions.OPEN_FROM_TEASER, type=PromoLogSubjectType.PROMO_SCREEN, url=rowUrl)
        url = yield self.__addAuthParams(rowUrl)
        self.__showBrowserView(url, loadingCallback)

    def setUnreadPromoCount(self, count):
        self.__updatePromoCount(count)

    def isTeaserOpen(self):
        return self.__isTeaserOpen

    def onAvatarBecomePlayer(self):
        if self.__isLobbyInited:
            self.__battlesFromLastTeaser += 1
        self.__stop()

    def onDisconnected(self):
        self.__stop()

    def isActive(self):
        return self.__lobbyContext.getServerSettings().isFieldPostEnabled() and not self.__bootcamp.isInBootcamp()

    def getPromoCount(self):
        return self.__promoCount

    def showPromo(self, url, closeCallback=None, source=None):
        if self.__isLobbyInited:
            if not self.__isPromoOpen and not self.__waitingForWebBridgeData:
                self.__registerAndShowPromoBrowser(url, closeCallback, self.__logger.getLoggingFuture(action=PromoLogActions.OPEN_IN_OLD, type=PromoLogSubjectType.PROMO_SCREEN, source=source, url=url))
        else:
            self.__pendingPromo = _PromoData(url, closeCallback, source)

    def __needToGetTeasersInfo(self):
        return True if self.__battlesFromLastTeaser == 0 else self.__checkIntervalInBattles > 0 and self.__battlesFromLastTeaser % self.__checkIntervalInBattles == 0

    def __onTeaserClosed(self, byUser=False):
        self.__isTeaserOpen = False
        self.onTeaserClosed()
        if byUser:
            self.__showBubbleTooltip()

    def __showBubbleTooltip(self):
        storageData = self.__settingsCore.serverSettings.getUIStorage()
        if not storageData.get(UI_STORAGE_KEYS.FIELD_POST_HINT_IS_SHOWN):
            showBubbleTooltip(i18n.makeString(TOOLTIPS.HEADER_VERSIONINFOHINT))
            self.__settingsCore.serverSettings.saveInUIStorage({UI_STORAGE_KEYS.FIELD_POST_HINT_IS_SHOWN: True})

    @process
    def __updateWebBrgData(self):
        ctx = PromoGetTeaserRequestCtx()
        if self.__battlesFromLastTeaser == 0:
            sourceType = PromoLogSourceType.FIRST_LOGIN
        else:
            sourceType = PromoLogSourceType.AFTER_BATTLE
        answerCallback = self.__logger.getLoggingFuture(action=PromoLogActions.GET_MOST_IMPORTANT, source=sourceType)
        self.__waitingForWebBridgeData = True
        response = yield self.__webController.sendRequest(ctx=ctx)
        self.__waitingForWebBridgeData = False
        if response.isSuccess():
            self.__updateTeaserData(ctx.getDataObj(response.getData()))
        elif self.__hasPendingTeaser:
            self.__tryToShowTeaser()
        if answerCallback:
            answerCallback(success=response.extraCode)

    def __onPromoClosed(self, **kwargs):
        self.__isPromoOpen = False
        if self.__isLobbyInited:
            self.__showBubbleTooltip()
        if self.__externalCloseCallback:
            self.__externalCloseCallback()
        self.__requestPromoCount()
        actionType = PromoLogActions.CLOSED_BY_USER if kwargs.get('byUser') else PromoLogActions.KILLED_BY_SYSTEM
        self.__logger.logAction(action=actionType, type=PromoLogSubjectType.PROMO_SCREEN_OR_INDEX, url=kwargs.get('url'))

    @process
    def __requestPromoCount(self):
        if not self.isActive():
            _logger.warning('Trying to request unread promos count when promo functionality is disabled')
            return
        ctx = PromoGetUnreadCountRequestCtx()
        response = yield self.__webController.sendRequest(ctx=ctx)
        if response.isSuccess():
            self.__updatePromoCount(ctx.getCount(response))

    def __updatePromoCount(self, count):
        countChanged = count != self.__promoCount
        self.__promoCount = count
        if countChanged:
            self.onPromoCountChanged()

    def __updateTeaserData(self, teaserData):
        self.__lastUpdateTimeMark = teaserData['timestamp']
        self.__promoData = teaserData['lastPromo']
        self.__updatePromoCount(teaserData['count'])
        if self.__promoData.get('url'):
            self.__tryToShowTeaser()

    def __showTeaser(self):
        if self.isActive():
            self.__battlesFromLastTeaser = 0
            self.__hasPendingTeaser = False
            self.onNewTeaserReceived(self.__promoData, self.__onTeaserShown, self.__onTeaserClosed)
        else:
            _logger.warning('Impossible to show teaser, functionality is disabled')

    @process
    def __onTeaserShown(self, promoID):
        self.__isTeaserOpen = True
        self.onTeaserShown()
        yield self.__webController.sendRequest(PromoSendTeaserShownRequestCtx(promoID))

    def __tryToShowTeaser(self):
        if self.__isLobbyInited and self.__isInHangar and not self.__waitingForWebBridgeData:
            self.__showTeaser()
        else:
            self.__hasPendingTeaser = True

    def __stop(self):
        if self.app and self.app.loaderManager:
            self.app.loaderManager.onViewLoaded -= self.__onViewLoaded
        self.__isLobbyInited = False
        self.__isInHangar = False
        self.__isPromoOpen = False
        self.__externalCloseCallback = None
        self.__isTeaserOpen = False
        self.__notificationsCtrl.onEventNotificationsChanged -= self.__onEventNotification
        g_eventBus.removeListener(BrowserEvent.BROWSER_CREATED, self.__handleBrowserCreated)
        self.__browserCreationCallbacks = {}
        watcherKeys = self.__browserWatchers.keys()
        for browserID in watcherKeys:
            self.__clearWatcher(browserID)

        return

    def __processPromo(self, promos):
        if not self.__isPromoOpen and not self.__waitingForWebBridgeData:
            logData = {'action': PromoLogActions.OPEN_IN_OLD,
             'type': PromoLogSubjectType.PROMO_SCREEN}
            if self.__pendingPromo is not None:
                promoData = self.__pendingPromo
                logData.update({'source': promoData.source,
                 'url': promoData.url})
                loadingCallback = self.__logger.getLoggingFuture(**logData)
                self.__registerAndShowPromoBrowser(promoData.url, promoData.closeCallback, loadingCallback)
                self.__pendingPromo = None
                return
            promo = findFirst(lambda item: item.eventType.startswith(gc_constants.PROMO.TEMPLATE.ACTION), promos)
            if promo:
                logData.update({'source': PromoLogSourceType.SSE,
                 'url': promo.data})
                self.__showBrowserView(promo.data, self.__logger.getLoggingFuture(**logData))
        return

    def __onEventNotification(self, added, _):
        self.__processPromo(added)

    def __registerAndShowPromoBrowser(self, url, closeCallback, loadingCallback):
        self.__externalCloseCallback = closeCallback
        self.__showBrowserView(url, loadingCallback)

    @process
    def __showBrowserView(self, url, loadingCallback=None, soundSpaceID=None):
        promoUrl = yield self.__urlMacros.parse(url)
        self.__registerLoadingCallback(promoUrl, loadingCallback)
        _showBrowserView(promoUrl, self.__onPromoClosed, soundSpaceID=soundSpaceID)
        self.__isPromoOpen = True

    def __registerLoadingCallback(self, url, callback):
        if callback is not None:
            self.__browserCreationCallbacks[url] = callback
        return

    def __handleBrowserCreated(self, event):
        url = event.ctx.get('url')
        if url in self.__browserCreationCallbacks:
            callback = self.__browserCreationCallbacks.pop(url)
            browserID = event.ctx.get('browserID')
            browser = self.__browserCtrl.getBrowser(browserID)
            if browser is None:
                return

            def callbackWrapper(clbUrl, _, statusCode):
                if clbUrl == url:
                    callback(url=url, success=statusCode)
                    self.__clearWatcher(browserID)

            browser.onLoadEnd += callbackWrapper
            self.__browserWatchers[browserID] = callbackWrapper
        return

    def __clearWatcher(self, browserID):
        if browserID in self.__browserWatchers:
            watcher = self.__browserWatchers.pop(browserID)
            browser = self.__browserCtrl.getBrowser(browserID)
            if browser is not None:
                browser.onLoadEnd -= watcher
        return

    @async
    @process
    def __addAuthParams(self, url, callback):
        if not url or not self.__webController:
            callback(url)
        accessTokenData = yield self.__webController.getAccessTokenData(force=True)
        params = {'access_token': str(accessTokenData.accessToken),
         'spa_id': BigWorld.player().databaseID}
        callback(url_formatters.addParamsToUrlQuery(url, params))

    def __onViewLoaded(self, pyView, _):
        if self.__isLobbyInited:
            if pyView.alias == VIEW_ALIAS.LOBBY_HANGAR:
                self.__isInHangar = True
                if self.__hasPendingTeaser:
                    self.__tryToShowTeaser()
            elif pyView.layer == WindowLayer.SUB_VIEW:
                self.__isInHangar = False


def _showBrowserView(url, returnClb, soundSpaceID=None):
    webHandlers = webApiCollection(PromoWebApi, VehiclesWebApi, RequestWebApi, RankedBattlesWebApi, BattlePassWebApi, ui_web_api.OpenWindowWebApi, ui_web_api.CloseWindowWebApi, ui_web_api.OpenTabWebApi, ui_web_api.NotificationWebApi, ui_web_api.ContextMenuWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi, ShopWebApi, SocialWebApi, BlueprintsConvertSaleWebApi, PlatformWebApi)
    ctx = {'url': url,
     'returnClb': returnClb,
     'webHandlers': webHandlers,
     'returnAlias': VIEW_ALIAS.LOBBY_HANGAR}
    if soundSpaceID is not None:
        ctx['soundSpaceID'] = soundSpaceID
    alias = VIEW_ALIAS.BROWSER_VIEW
    g_eventBus.handleEvent(events.LoadViewEvent(SFViewLoadParams(alias, getUniqueViewName(alias)), ctx=ctx), EVENT_BUS_SCOPE.LOBBY)
    return
