# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/ui/browser.py
from adisp import process
from helpers import dependency
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.framework import ViewTypes
from gui.app_loader import g_appLoader
from gui.shared.utils.functions import getViewName
from skeletons.gui.game_control import IBrowserController, IExternalLinksController
from web_client_api import WebCommandException, w2c, W2CSchema, Field
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
            app = g_appLoader.getApp()
            if app is not None and app.containerManager is not None:
                supportedBrowserViewTypes = (ViewTypes.WINDOW, ViewTypes.OVERLAY)
                browserWindow = None
                for viewType in supportedBrowserViewTypes:
                    browserWindow = app.containerManager.getView(viewType, criteria=BrowserSearchCriteria(windowAlias))
                    if browserWindow is not None:
                        break

                if not browserWindow:
                    for viewType in supportedBrowserViewTypes:
                        browserWindow = app.containerManager.getView(viewType, criteria={POP_UP_CRITERIA.UNIQUE_NAME: windowAlias})
                        if browserWindow is not None:
                            break

                if browserWindow is not None:
                    browserWindow.destroy()
                else:
                    raise WebCommandException('Browser window could not be found! May be alias "{}" is wrong or probably browser has unsupported viewType.'.format(windowAlias))
        self._onBrowserClose()
        return

    def _onBrowserClose(self):
        pass


class CloseBrowserViewWebApiMixin(object):

    @w2c(W2CSchema, 'browser')
    def browser(self, cmd, ctx):
        app = g_appLoader.getApp()
        if app is not None and app.containerManager is not None:
            browserView = app.containerManager.getView(ViewTypes.LOBBY_SUB, criteria={POP_UP_CRITERIA.VIEW_ALIAS: ctx.get('browser_alias')})
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
