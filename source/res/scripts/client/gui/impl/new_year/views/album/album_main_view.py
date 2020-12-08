# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/album/album_main_view.py
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_album_main_model import NewYearAlbumMainModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.views.album.album_tab_view import AlbumTabView
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import dependency
from helpers import uniprof
from new_year.ny_constants import NyWidgetTopMenu
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYTabCtx

class AlbumMainView(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    __slots__ = ('__yearName',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_album_view.NewYearAlbumMainView())
        settings.model = NewYearAlbumMainModel()
        settings.args = args
        settings.kwargs = kwargs
        super(AlbumMainView, self).__init__(settings)

    @property
    def viewModel(self):
        return super(AlbumMainView, self).getViewModel()

    @uniprof.regionDecorator(label='ny.album', scope='enter')
    def _initialize(self, tabName=None, stateInfo=None):
        super(AlbumMainView, self)._initialize()
        self.viewModel.onSwitchContent += self.__onSwitchContent
        g_eventBus.addListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self.__yearName = tabName if tabName else self._tabCache.getCurrentYear()
        self.setChildView(R.dynamic_ids.newYearAlbumMain(), AlbumTabView(self.__yearName, stateInfo))

    @uniprof.regionDecorator(label='ny.album', scope='exit')
    def _finalize(self):
        self.viewModel.onSwitchContent -= self.__onSwitchContent
        g_eventBus.removeListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        self._tabCache.saveCurrentYear(self.__yearName)
        super(AlbumMainView, self)._finalize()

    def __onSwitchContent(self, ctx):
        self._navigationHistory.clear()
        nextYearName = self.viewModel.getNextViewName()
        self.getChildView(R.dynamic_ids.newYearAlbumMain()).switchYear(nextYearName)
        self.__yearName = nextYearName

    def __onSideBarSelected(self, event):
        ctx = event.ctx
        if ctx.menuName != NyWidgetTopMenu.COLLECTIONS:
            return
        self.viewModel.setNextViewName(ctx.tabName)
