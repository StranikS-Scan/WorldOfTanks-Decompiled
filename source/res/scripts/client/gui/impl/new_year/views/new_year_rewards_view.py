# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_rewards_view.py
import logging
from collections import namedtuple
import typing
from frameworks.wulf import ViewSettings
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_rewards_view_model import NewYearRewardsViewModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.views.new_year_collections_reward_view import NewYearCollectionsRewardView
from gui.impl.new_year.views.ny_levels_rewards_view import NyLevelsRewardsView
from gui.shared import g_eventBus, events, EVENT_BUS_SCOPE
from helpers import uniprof
from new_year.ny_constants import NyTabBarRewardsView, Collections, NyWidgetTopMenu
if typing.TYPE_CHECKING:
    from gui.shared.event_dispatcher import NYTabCtx
_logger = logging.getLogger(__name__)
_TabSwitchInfo = namedtuple('_TabSwitchInfo', 'clazz kwargs')
_NAVIGATION_TAB = {NyTabBarRewardsView.FOR_LEVELS: _TabSwitchInfo(NyLevelsRewardsView, {}),
 NyTabBarRewardsView.COLLECTION_NY18: _TabSwitchInfo(NewYearCollectionsRewardView, {'year': Collections.NewYear18}),
 NyTabBarRewardsView.COLLECTION_NY19: _TabSwitchInfo(NewYearCollectionsRewardView, {'year': Collections.NewYear19}),
 NyTabBarRewardsView.COLLECTION_NY20: _TabSwitchInfo(NewYearCollectionsRewardView, {'year': Collections.NewYear20}),
 NyTabBarRewardsView.COLLECTION_NY21: _TabSwitchInfo(NewYearCollectionsRewardView, {'year': Collections.NewYear21})}

class NewYearRewardsView(NewYearHistoryNavigation):
    _navigationAlias = ViewAliases.REWARDS_VIEW
    __slots__ = ('__viewChangeCtx',)

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_rewards_view.NewYearRewardsView())
        settings.model = NewYearRewardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearRewardsView, self).__init__(settings)
        self.__viewChangeCtx = None
        return

    @property
    def viewModel(self):
        return super(NewYearRewardsView, self).getViewModel()

    @uniprof.regionDecorator(label='ny.rewards', scope='enter')
    def _initialize(self, tabName=None, *args, **kwargs):
        super(NewYearRewardsView, self)._initialize()
        self.viewModel.onSwitchContent += self.__onSwitchContent
        self.viewModel.setBgChangeViewName(NyTabBarRewardsView.FOR_LEVELS)
        g_eventBus.addListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        tabName = tabName or self._tabCache.getRewardsTab() or NyTabBarRewardsView.FOR_LEVELS
        self.__changeTab(tabName, **kwargs)

    @uniprof.regionDecorator(label='ny.rewards', scope='exit')
    def _finalize(self):
        self.__viewChangeCtx = None
        self.viewModel.onSwitchContent -= self.__onSwitchContent
        g_eventBus.removeListener(events.NewYearEvent.ON_SIDEBAR_SELECTED, self.__onSideBarSelected, scope=EVENT_BUS_SCOPE.LOBBY)
        super(NewYearRewardsView, self)._finalize()
        return

    def _getInfoForHistory(self):
        return {}

    def __switchView(self, tabName, *args, **kwargs):
        tabInfo = _NAVIGATION_TAB.get(tabName)
        kwargs = kwargs or tabInfo.kwargs
        view = tabInfo.clazz(*args, **kwargs)
        self.setChildView(R.dynamic_ids.newYearRewardsView(), view)
        self._tabCache.setRewardsTab(tabName)

    def __onSwitchContent(self, ctx):
        kwargs = self.__viewChangeCtx
        self.__switchView(self.viewModel.getNextViewName(), **kwargs)
        self.__viewChangeCtx = None
        return

    def __onSideBarSelected(self, event):
        ctx = event.ctx
        if ctx.menuName != NyWidgetTopMenu.REWARDS:
            return
        self.__changeTab(ctx.tabName)

    def __changeTab(self, tabName, **kwargs):
        self.viewModel.setNextViewName(tabName)
        self.__viewChangeCtx = kwargs
