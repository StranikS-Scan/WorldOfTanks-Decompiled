# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/ui/browser.py
from adisp import process
from frameworks.wulf import WindowLayer
from gui.shop import showBuyGoldWebOverlay
from gui.shared.event_dispatcher import showBrowserOverlayView
from helpers import dependency
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared.utils.functions import getViewName
from skeletons.gui.app_loader import IAppLoader
from skeletons.gui.game_control import IBrowserController, IExternalLinksController
from web.web_client_api import WebCommandException, w2c, W2CSchema, Field
from gui.Scaleform.framework.managers.containers import POP_UP_CRITERIA, ExternalCriteria

class _OpenBrowserWindowSchema(W2CSchema):
    url = Field(required=True, type=basestring)
    title = Field(required=True, type=basestring)
    width = Field(required=True, type=(int, long))
    height = Field(required=True, type=(int, long))
    is_modal = Field(type=bool, default=False)
    show_refresh = Field(type=bool, default=True)
    show_create_waiting = Field(type=bool, default=False)
    is_solid_border = Field(type=bool, default=False)


class _OpenExternalBrowserSchema(W2CSchema):
    url = Field(required=True, type=basestring)


class _OpenBrowserOverlaySchema(W2CSchema):
    url = Field(required=True, type=basestring)
    blur_bg = Field(type=bool, default=False)


class _OpenBuyGoldOverlaySchema(W2CSchema):
    params = Field(required=False, type=dict)


class OpenBrowserWindowWebApiMixin(object):

    @w2c(_OpenBrowserWindowSchema, 'browser')
    def browser(self, cmd):
        self.__loadBrowser(cmd.url, cmd.title, cmd.width, cmd.height, cmd.is_modal, cmd.show_refresh, cmd.show_create_waiting)

    def _onBrowserOpen(self, alias):
        pass

    def _createHandlers(self):
        return []

    @process
    def __loadBrowser(self, url, title, width, height, isModal, showRefresh, showCreateWaiting):
        browserCtrl = dependency.instance(IBrowserController)
        browserId = yield browserCtrl.load(url=url, title=title, browserSize=(width, height), isModal=isModal, showActionBtn=showRefresh, showCreateWaiting=showCreateWaiting, handlers=self._createHandlers())
        browser = browserCtrl.getBrowser(browserId)
        if browser is not None:
            browser.ignoreKeyEvents = True
        alias = getViewName(VIEW_ALIAS.BROWSER_WINDOW_MODAL if isModal else VIEW_ALIAS.BROWSER_WINDOW, browserId)
        self._onBrowserOpen(alias)
        return


class BrowserSearchCriteria(ExternalCriteria):

    def __init__(self, neededAlias):
        super(BrowserSearchCriteria, self).__init__()
        self.__neededAlias = neededAlias

    def find(self, view, browserWindow):
        return getattr(browserWindow, 'uniqueBrowserName', 0) == self.__neededAlias


class CloseBrowserWindowWebApiMixin(object):

    @w2c(W2CSchema, 'browser')
    def browser(self, cmd, ctx):
        if 'browser_id' in ctx:
            windowAlias = getViewName(ctx['browser_alias'], ctx['browser_id'])
            appLoader = dependency.instance(IAppLoader)
            app = appLoader.getApp()
            if app is not None and app.containerManager is not None:
                supportedBrowserLayers = (WindowLayer.WINDOW,
                 WindowLayer.FULLSCREEN_WINDOW,
                 WindowLayer.OVERLAY,
                 WindowLayer.TOP_SUB_VIEW)
                browserWindow = None
                for layer in supportedBrowserLayers:
                    browserWindow = app.containerManager.getView(layer, criteria=BrowserSearchCriteria(windowAlias))
                    if browserWindow is not None:
                        break

                if not browserWindow:
                    for layer in supportedBrowserLayers:
                        browserWindow = app.containerManager.getView(layer, criteria={POP_UP_CRITERIA.UNIQUE_NAME: windowAlias})
                        if browserWindow is not None:
                            break

                if browserWindow is not None:
                    browserWindow.destroy()
                else:
                    raise WebCommandException('Browser window could not be found! May be alias "{}" is wrong or probably browser has unsupported layer.'.format(windowAlias))
        self._onBrowserClose()
        return

    def _onBrowserClose(self):
        pass


class CloseBrowserViewWebApiMixin(object):

    @w2c(W2CSchema, 'browser')
    def browser(self, cmd, ctx):
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        if app is not None and app.containerManager is not None:
            browserView = app.containerManager.getView(WindowLayer.SUB_VIEW, criteria={POP_UP_CRITERIA.VIEW_ALIAS: ctx.get('browser_alias')})
            if browserView is not None:
                browserView.onCloseView()
                return
        raise WebCommandException('Unable to find BrowserView!')
        return


class OpenExternalBrowserWebApiMixin(object):

    @w2c(_OpenExternalBrowserSchema, 'external_browser')
    def externalBrowser(self, cmd, ctx):
        linkCtrl = dependency.instance(IExternalLinksController)
        linkCtrl.open(cmd.url)


class OpenBrowserOverlayWebApiMixin(object):

    @w2c(_OpenBrowserOverlaySchema, 'browser_overlay')
    def openBrowserOverlay(self, cmd):
        showBrowserOverlayView(cmd.url, alias=VIEW_ALIAS.WEB_VIEW_TRANSPARENT if cmd.blur_bg else VIEW_ALIAS.OVERLAY_PREM_CONTENT_VIEW)


class OpenBuyGoldWebApiMixin(object):

    @w2c(_OpenBuyGoldOverlaySchema, 'buy_gold')
    def openBuyGoldWebOverlay(self, cmd):
        showBuyGoldWebOverlay(cmd.params)
