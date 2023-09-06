# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/comp7/meta_view/pages/yearly_statistics_page.py
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.pages.yearly_statistics_model import YearlyStatisticsModel
from skeletons.gui.game_control import IComp7Controller
from skeletons.gui.server_events import IEventsCache
from gui.impl.lobby.comp7.meta_view.pages import PageSubModelPresenter
from helpers import dependency
from gui.impl.gen.view_models.views.lobby.comp7.meta_view.root_view_model import MetaRootViews

class YearlyStatisticsPage(PageSubModelPresenter):
    __slots__ = ()
    __eventsCache = dependency.descriptor(IEventsCache)
    __comp7Controller = dependency.descriptor(IComp7Controller)

    @property
    def pageId(self):
        return MetaRootViews.YEARLYSTATISTICS

    @property
    def viewModel(self):
        return super(YearlyStatisticsPage, self).getViewModel()
