# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: server_side_replay/scripts/client/server_side_replay/gui/impl/lobby/replays_root_view.py
import logging
import typing
from frameworks.wulf import ViewFlags, ViewSettings
from ..gen.view_models.views.lobby.root_view_model import RootViewModel
from ..gen.view_models.views.lobby.tab_model import TabModel
from ..gen.view_models.views.lobby.enums import ReplaysViews
from gui.impl.gui_decorators import args2params
from .replays_lobby_sounds import REPLAYS_SOUND_SPACE
from .pages.best_replays_page import BestReplaysPage
from .pages.my_replays_page import MyReplaysPage
from .pages.find_replay_page import FindReplayPage
from gui.impl.pub import ViewImpl
from gui.prb_control.entities.listener import IGlobalListener
from gui.prb_control.events_dispatcher import g_eventDispatcher
from gui.shared.event_dispatcher import showHangar
if typing.TYPE_CHECKING:
    from ..lobby.pages import PageSubModelPresenter
_logger = logging.getLogger(__name__)

class ReplaysRootView(ViewImpl, IGlobalListener):
    __slots__ = ('__pages', '__tabId')
    _COMMON_SOUND_SPACE = REPLAYS_SOUND_SPACE

    def __init__(self, layoutID, *args, **kwargs):
        settings = ViewSettings(layoutID)
        settings.flags = ViewFlags.LOBBY_SUB_VIEW
        settings.model = RootViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(ReplaysRootView, self).__init__(settings)
        self.__pages = {}
        self.__tabId = ReplaysViews.BESTREPLAYS

    @property
    def viewModel(self):
        return super(ReplaysRootView, self).getViewModel()

    @property
    def tabId(self):
        return self.__tabId

    def createToolTip(self, event):
        if self.__currentPage.isLoaded:
            window = self.__currentPage.createToolTip(event)
            if window is not None:
                return window
        return super(ReplaysRootView, self).createToolTip(event)

    def createToolTipContent(self, event, contentID):
        if self.__currentPage.isLoaded:
            content = self.__currentPage.createToolTipContent(event, contentID)
            if content is not None:
                return content
        return super(ReplaysRootView, self).createToolTipContent(event, contentID)

    def createContextMenu(self, event):
        if self.__currentPage.isLoaded:
            window = self.__currentPage.createContextMenu(event)
            if window is not None:
                return window
        return super(ReplaysRootView, self).createContextMenu(event)

    def createPopOver(self, event):
        if self.__currentPage.isLoaded:
            window = self.__currentPage.createPopOver(event)
            if window is not None:
                return window
        return super(ReplaysRootView, self).createPopOver(event)

    def switchPage(self, tabId, *args, **kwargs):
        if self.__currentPage.isLoaded:
            self.__currentPage.finalize()
        page = self.__pages[tabId]
        page.initialize(*args, **kwargs)
        self.viewModel.setPageViewId(page.pageId)
        self.__tabId = tabId
        g_eventDispatcher.updateUI()

    def _finalize(self):
        self.__removeListeners()
        self.__clearPages()

    def _onLoading(self, *args, **kwargs):
        tabId = kwargs.pop('tabId', None)
        if tabId is not None:
            if tabId in tuple(ReplaysViews):
                self.__tabId = tabId
            else:
                _logger.error('Wrong tabId: %s', tabId)
        self.__initPages()
        self.__updateTabs()
        page = self.__pages[self.__tabId]
        page.initialize(*args, **kwargs)
        self.viewModel.setPageViewId(page.pageId)
        self.__addListeners()
        return

    @property
    def __currentPage(self):
        return self.__pages[self.__tabId]

    def __addListeners(self):
        self.viewModel.onClose += self.__onClose
        self.viewModel.sidebar.onSideBarTabChange += self.__onSideBarTabChanged
        self.startGlobalListening()

    def __removeListeners(self):
        self.viewModel.onClose -= self.__onClose
        self.viewModel.sidebar.onSideBarTabChange -= self.__onSideBarTabChanged
        self.stopGlobalListening()

    def __initPages(self):
        pages = (BestReplaysPage(self.viewModel.bestReplays, self), MyReplaysPage(self.viewModel.myReplays, self), FindReplayPage(self.viewModel.findReplay, self))
        self.__pages = {p.pageId:p for p in pages}

    def __clearPages(self):
        if self.__currentPage.isLoaded:
            self.__currentPage.finalize()
        self.__pages.clear()

    def __updateTabs(self):
        with self.viewModel.transaction() as tx:
            tabs = tx.sidebar.getItems()
            tabs.clear()
            for tab in tuple(ReplaysViews):
                tabModel = TabModel()
                tabModel.setId(tab)
                tabs.addViewModel(tabModel)

            tabs.invalidate()

    def __onClose(self):
        showHangar()

    @args2params(int)
    def __onSideBarTabChanged(self, tabId):
        if tabId == self.__tabId:
            return
        if tabId not in self.__pages:
            _logger.error('Wrong tabId: %s', tabId)
            return
        self.switchPage(tabId)
