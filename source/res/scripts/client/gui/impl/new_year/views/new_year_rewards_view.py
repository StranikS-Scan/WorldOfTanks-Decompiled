# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/new_year_rewards_view.py
import logging
from collections import namedtuple
from frameworks.wulf import ViewSettings
from gui.ClientUpdateManager import g_clientUpdateManager
from gui.impl.gen import R
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_rewards_view_model import NewYearRewardsViewModel
from gui.impl.new_year.history_navigation import NewYearHistoryNavigation
from gui.impl.new_year.navigation import ViewAliases
from gui.impl.new_year.sounds import NewYearSoundConfigKeys, NewYearSoundEvents, NewYearSoundStates
from gui.impl.new_year.views.new_year_collections_reward_view import NewYearCollectionsRewardView
from gui.impl.new_year.views.ny_levels_rewards_view import NyLevelsRewardsView
from gui.impl.new_year.views.tabs_controller import RewardsTabsController
from helpers import dependency, uniprof
from items.components.ny_constants import TOKEN_FREE_TALISMANS
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ICustomizableObjectsManager
from new_year.ny_constants import NyTabBarRewardsView, Collections, SyncDataKeys
_logger = logging.getLogger(__name__)
_TabSwitchInfo = namedtuple('_TabSwitchInfo', 'clazz kwargs')
_NAVIGATION_TAB = {NyTabBarRewardsView.FOR_LEVELS: _TabSwitchInfo(NyLevelsRewardsView, {}),
 NyTabBarRewardsView.COLLECTION_NY18: _TabSwitchInfo(NewYearCollectionsRewardView, {'year': Collections.NewYear18}),
 NyTabBarRewardsView.COLLECTION_NY19: _TabSwitchInfo(NewYearCollectionsRewardView, {'year': Collections.NewYear19}),
 NyTabBarRewardsView.COLLECTION_NY20: _TabSwitchInfo(NewYearCollectionsRewardView, {'year': Collections.NewYear20})}

class NewYearRewardsView(NewYearHistoryNavigation):
    _itemsCache = dependency.descriptor(IItemsCache)
    _customizableObjMgr = dependency.descriptor(ICustomizableObjectsManager)
    _navigationAlias = ViewAliases.REWARDS_VIEW
    _nyController = dependency.descriptor(INewYearController)
    __slots__ = ('__currentViewName', '__tabsController')

    def __init__(self, *args, **kwargs):
        settings = ViewSettings(R.views.lobby.new_year.views.new_year_rewards_view.NewYearRewardsView())
        settings.model = NewYearRewardsViewModel()
        settings.args = args
        settings.kwargs = kwargs
        super(NewYearRewardsView, self).__init__(settings)
        self.__tabsController = RewardsTabsController()

    @property
    def viewModel(self):
        return super(NewYearRewardsView, self).getViewModel()

    @uniprof.regionDecorator(label='ny20.rewards', scope='enter')
    def _initialize(self, viewName=None, *args, **kwargs):
        soundConfig = {NewYearSoundConfigKeys.ENTRANCE_EVENT: NewYearSoundEvents.REWARDS_LEVELS,
         NewYearSoundConfigKeys.EXIT_EVENT: NewYearSoundEvents.REWARDS_LEVELS_EXIT,
         NewYearSoundConfigKeys.STATE_VALUE: NewYearSoundStates.REWARDS_LEVELS}
        super(NewYearRewardsView, self)._initialize(soundConfig)
        if viewName is None:
            viewName = self._tabCache.getRewardsTab() or NyTabBarRewardsView.FOR_LEVELS
        self.viewModel.onSwitchContent += self.__onSwitchContent
        self._nyController.onDataUpdated += self.__onDataUpdated
        g_clientUpdateManager.addCallbacks({'tokens': self.__onTokensChanged})
        with self.viewModel.transaction() as tx:
            self.__tabsController.updateTabModels(tx.getItemsTabBar())
            tx.setStartIndex(self.__tabsController.tabOrderKey(viewName))
            tx.setBgChangeViewName(NyTabBarRewardsView.FOR_LEVELS)
        self.__switchView(viewName, **kwargs)
        return

    @uniprof.regionDecorator(label='ny20.rewards', scope='exit')
    def _finalize(self):
        self.viewModel.onSwitchContent -= self.__onSwitchContent
        self._nyController.onDataUpdated -= self.__onDataUpdated
        g_clientUpdateManager.removeCallback('tokens', self.__onTokensChanged)
        self._tabCache.setRewardsTab(self.__currentViewName)
        super(NewYearRewardsView, self)._finalize()

    def _getInfoForHistory(self):
        return {}

    def __switchView(self, viewName, **kwargs):
        self.__currentViewName = viewName
        tabInfo = _NAVIGATION_TAB.get(viewName)
        self.setChildView(R.dynamic_ids.newYearRewardsView(), tabInfo.clazz(**(kwargs if kwargs else tabInfo.kwargs)))

    def __onSwitchContent(self, args):
        self.__switchView(args.get('view'))

    def __onDataUpdated(self, keys):
        if SyncDataKeys.TALISMANS in keys:
            with self.viewModel.transaction() as tx:
                self.__tabsController.updateTabModels(tx.getItemsTabBar())

    def __onTokensChanged(self, tokens):
        if TOKEN_FREE_TALISMANS in tokens:
            self.__tabsController.updateTabModels(self.viewModel.getItemsTabBar())
