# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: mt_birthday/scripts/client/mt_birthday/gui/impl/lobby/birthday/web_browser_view.py
from frameworks.wulf import ViewFlags
from gui.impl.gen import R
from gui.impl.lobby.common.browser_view import makeSettings, BrowserView
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from web.web_client_api.promo import PromoWebApi
from web.web_client_api.request import RequestWebApi
from web.web_client_api.shop import ShopWebApi
from web.web_client_api.reactive_comm import ReactiveCommunicationWebApi
from web.web_client_api.uilogging import UILoggingWebApi
from web.web_client_api import webApiCollection, ui as ui_web_api, sound as sound_web_api
from mt_birthday.web.web_client_api.ticket_exchange.ticket_exchange import TicketExchangeWebApi
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
_BLANK_BROWSER_PAGE = 'about:blank'

def getBrowserSettings(url=''):
    return makeSettings(url=url, viewFlags=ViewFlags.VIEW, webHandlers=webApiCollection(PromoWebApi, RequestWebApi, ShopWebApi, ReactiveCommunicationWebApi, TicketExchangeWebApi, UILoggingWebApi, ui_web_api.OpenWindowWebApi, ui_web_api.CloseWindowWebApi, ui_web_api.OpenTabWebApi, ui_web_api.NotificationWebApi, ui_web_api.ContextMenuWebApi, ui_web_api.UtilWebApi, sound_web_api.SoundWebApi, sound_web_api.HangarSoundWebApi))


class WebBrowserView(BrowserView):
    __slots__ = ('_mainViewEvents', '_currentTabId', '__isSkipEscape')
    __appLoader = dependency.descriptor(IAppLoader)

    def __init__(self, mainViewEvents, currentTabId, url='', skipEscape=True):
        super(WebBrowserView, self).__init__(R.views.common.Browser(), getBrowserSettings(url))
        self._mainViewEvents = mainViewEvents
        self._currentTabId = currentTabId
        self.__isSkipEscape = skipEscape
        self.browser.skipEscape = True

    def _getEvents(self):
        return super(WebBrowserView, self)._getEvents() + ((self._mainViewEvents.onTabChange, self._onTabChange), (self.onBrowserObtained, self.__setIsAudioMutable))

    def __setIsAudioMutable(self, _):
        self.browser.setIsAudioMutable(True)

    def _onTabChange(self, tabId, newTabID):
        if self.browser is not None:
            if newTabID == self._currentTabId:
                self.browser.navigate(self.url)
                self.browser.skipEscape = self.__isSkipEscape
            else:
                self.browser.navigate(_BLANK_BROWSER_PAGE)
                self.browser.skipEscape = True
        return

    def _finalize(self):
        self.__appLoader.getApp().getToolTipMgr().onHideTooltip(TOOLTIPS_CONSTANTS.BIRTHDAY_ENTRY_POINT)
        super(WebBrowserView, self)._finalize()


class StaticWebBrowserView(WebBrowserView):

    def _onTabChange(self, tabId, _):
        if tabId == self._currentTabId and self.browser is not None:
            self.browser.refresh()
        return
