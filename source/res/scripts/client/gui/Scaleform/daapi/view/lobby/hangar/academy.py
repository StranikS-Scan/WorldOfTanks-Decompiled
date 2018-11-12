# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/academy.py
import re
from adisp import process
from gui.Scaleform.Waiting import Waiting
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.AcademyViewMeta import AcademyViewMeta
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from helpers import dependency
from helpers.http import url_formatters
from skeletons.gui.game_control import IBrowserController, IEncyclopediaController
_CONTENT_ID_FILTER_SUFFIX = '/?(\\d+)/?(?:\\?.+|$)'

class Academy(LobbySubView, AcademyViewMeta):
    __background_alpha__ = 1.0
    browserCtrl = dependency.descriptor(IBrowserController)
    encyclopediaCtrl = dependency.descriptor(IEncyclopediaController)

    def __init__(self, _=None):
        LobbySubView.__init__(self, 0)
        self.__browserID = None
        self.__urlFilter = None
        return

    @process
    def reload(self):
        browser = self.browserCtrl.getBrowser(self.__browserID)
        if browser is not None:
            url = yield self.encyclopediaCtrl.buildUrl()
            if url:
                browser.navigate(url)
        else:
            yield lambda callback: callback(True)
        self.encyclopediaCtrl.resetHasNew()
        return

    def closeView(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(Academy, self)._populate()
        self.encyclopediaCtrl.resetHasNew()
        Waiting.hide('loadPage')

    def _dispose(self):
        browser = self.browserCtrl.getBrowser(self.__browserID)
        if browser is not None:
            browser.removeFilter(self.__catchItemView)
        super(Academy, self)._dispose()
        return

    @process
    def _onRegisterFlashComponent(self, viewPy, alias):
        super(Academy, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            url = yield self.encyclopediaCtrl.buildUrl()
            browserID = yield self.browserCtrl.load(url=url, useBrowserWindow=False)
            self.__browserID = browserID
            viewPy.init(browserID)
            browser = self.browserCtrl.getBrowser(browserID)
            if browser is not None:
                self.__prepareUrlFilter(url)
                browser.addFilter(self.__catchItemView)
                browser.setAllowAutoLoadingScreen(False)
                browser.onReadyToShowContent = self.__removeLoadingScreen
        return

    def __removeLoadingScreen(self, url):
        browser = self.browserCtrl.getBrowser(self.__browserID)
        if browser is not None:
            browser.setLoadingScreenVisible(False)
        return

    def __catchItemView(self, url, _):
        if self.__urlFilter is not None:
            contentID = self.__urlFilter.findall(url)
            if len(contentID) == 1:
                self.encyclopediaCtrl.moveEncyclopediaRecommendationToEnd(contentID[0])
        return False

    def __prepareUrlFilter(self, url):
        urlBase, _ = url_formatters.separateQuery(url)
        self.__urlFilter = re.compile(urlBase + _CONTENT_ID_FILTER_SUFFIX)
