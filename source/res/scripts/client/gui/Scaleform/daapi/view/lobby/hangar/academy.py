# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/hangar/academy.py
import re
from adisp import process
from gui import game_control
from gui.shared import events
from gui.shared.event_bus import EVENT_BUS_SCOPE
from gui.Scaleform.daapi import LobbySubView
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.Scaleform.daapi.view.meta.AcademyViewMeta import AcademyViewMeta
from helpers.http import url_formatters
from gui.Scaleform.Waiting import Waiting
_CONTENT_ID_FILTER_SUFFIX = '/?(\\d+)/?(?:\\?.+|$)'

class Academy(LobbySubView, AcademyViewMeta):
    __background_alpha__ = 1.0

    def __init__(self, _=None):
        LobbySubView.__init__(self, 0)
        self.__browserID = None
        self.__controller = game_control.getEncyclopediaController()
        self.__urlFilter = None
        return

    @process
    def reload(self):
        browser = game_control.getBrowserCtrl().getBrowser(self.__browserID)
        if browser is not None:
            url = yield self.__controller.buildUrl()
            if url:
                browser.doNavigate(url)
        else:
            yield lambda callback: callback(True)
        self.__controller.resetHasNew()
        return

    def closeView(self):
        self.fireEvent(events.LoadViewEvent(VIEW_ALIAS.LOBBY_HANGAR), scope=EVENT_BUS_SCOPE.LOBBY)

    def _populate(self):
        super(Academy, self)._populate()
        self.__controller.resetHasNew()
        Waiting.hide('loadPage')

    def _dispose(self):
        browser = game_control.getBrowserCtrl().getBrowser(self.__browserID)
        if browser is not None:
            browser.removeFilter(self.__onFilterNavigation)
        super(Academy, self)._dispose()
        return

    @process
    def _onRegisterFlashComponent(self, viewPy, alias):
        super(Academy, self)._onRegisterFlashComponent(viewPy, alias)
        if alias == VIEW_ALIAS.BROWSER:
            url = yield self.__controller.buildUrl()
            browserID = yield game_control.getBrowserCtrl().load(url=url, useBrowserWindow=False)
            self.__browserID = browserID
            viewPy.init(browserID)
            browser = game_control.getBrowserCtrl().getBrowser(browserID)
            if browser is not None:
                self.__prepareUrlFilter(url)
                browser.addFilter(self.__onFilterNavigation)
        return

    def __onFilterNavigation(self, url, _):
        if self.__urlFilter is not None:
            contentID = self.__urlFilter.findall(url)
            if len(contentID) == 1:
                self.__controller.moveEncyclopediaRecommendationToEnd(contentID[0])
        return False

    def __prepareUrlFilter(self, url):
        urlBase, _ = url_formatters.separateQuery(url)
        self.__urlFilter = re.compile(urlBase + _CONTENT_ID_FILTER_SUFFIX)
