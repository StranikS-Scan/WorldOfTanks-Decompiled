# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/lobby/new_year/info_page/ny_info_view.py
from new_year.gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel, Tabs
from new_year.gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.gen.view_models.views.lobby.daily.daily_quests_view_model import DailyTabs
from new_year.gui.impl.lobby.new_year.ny_menu_component import NAVIGATION_ALIAS_VIEWS
from new_year.gui.impl.lobby.new_year.ny_views_helpers import showInfoVideo
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from new_year.helpers.server_settings import getNewYearGeneralConfig
from new_year.gui.impl.new_year.navigation import NewYearNavigation
from new_year.gui.shared.event_dispatcher import showNYProgressView
from new_year.helpers.server_settings import getNewYearBonusConfig
from gui.server_events.events_dispatcher import showDailyQuests
from new_year.skeletons.new_year import ITamagotchiDataProvider
from skeletons.gui.game_control import IGuiLootBoxesController
from helpers.server_settings import GUI_LOOT_BOXES_CONFIG
from new_year.gui.shared.ny_bonuses import BonusHelper
from skeletons.gui.lobby_context import ILobbyContext
from ExtensionsManager import g_extensionsManager
from new_year.ny_constants import NyWidgetTopMenu, InternalViewState
from helpers import dependency, getLanguageCode
from constants import CURRENT_REALM
from debug_utils import LOG_ERROR

class NyInfoView(HistorySubModelPresenter):
    __slots__ = ('__config',)
    _INTERNAL_VIEW_STATE = InternalViewState.RACCOON
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NyInfoView, self).__init__(viewModel, parentView)
        self.__config = getNewYearGeneralConfig()

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyInfoView, self).initialize(*args, **kwargs)
        maxBonus = BonusHelper.getCommonMaxBonus()
        multipliersList = getNewYearBonusConfig().getAtmosphereMultipliers()
        startTab = kwargs.get('startTab', Tabs.DEFAULT)
        with self.viewModel.transaction() as model:
            model.setMaxBonus(maxBonus)
            model.setUsualMaxBonus(maxBonus)
            model.region.setRealm(CURRENT_REALM)
            model.region.setLanguage(getLanguageCode())
            model.setMinMultiplier(min(multipliersList))
            model.setMaxMultiplier(max(multipliersList))
            model.setStartTab(startTab)
            model.setStartDate(self.__config.getNewYearStartDate())
            model.setEndDate(self.__config.getNewYearEndDate())
            model.setHasTamagochiUnlock(self._dataProvider.raccoonState)
            self.__updateStatus(model=model)

    def _getEvents(self):
        return ((self.viewModel.videoCover.onClick, self.__onClickVideo),
         (self.viewModel.onButtonClick, self.__onButtonClick),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdateView),
         (self._dataProvider.onRaccoonStateUpdated, self.__onTamagochiUnlock))

    @replaceNoneKwargsModel
    def __updateStatus(self, model=None):
        isLootBoxesEnabled = self.__lobbyContext.getServerSettings().isLootBoxesEnabled()
        isLootBoxesBuyEnabled = False
        if g_extensionsManager.isExtensionEnabled('gui_lootboxes'):
            isLootBoxesBuyEnabled = self.__guiLootBoxes.isBuyAvailable()
        model.setIsLootBoxEnabled(isLootBoxesEnabled)
        model.setIsLootBoxesBuyEnabled(isLootBoxesBuyEnabled)

    def __onButtonClick(self, args):
        action = args['value']
        if action in NyWidgetTopMenu.ALL:
            viewAlias = NAVIGATION_ALIAS_VIEWS[action]
            NewYearNavigation.showNavigationView(viewAlias)
        elif action == NewYearInfoViewModel.REWARDS:
            showNYProgressView(self.getParentWindow())
        elif action == NewYearInfoViewModel.BIGBOXES:
            self.__guiLootBoxes.openShop()
        elif action == NewYearInfoViewModel.QUESTS:
            showDailyQuests(subTab=DailyTabs.NYQUESTS)
        else:
            LOG_ERROR('Action is unsupported, action: ', action)

    @staticmethod
    def __onClickVideo():
        showInfoVideo()

    def __onUpdateView(self, *_, **kwargs):
        prevViewAlias = kwargs.get('previousViewAlias')
        if prevViewAlias and self._navigationHistory.getLast() != prevViewAlias:
            self._navigationHistory.clear()
            self._navigationHistory.addToHistory(prevViewAlias, {})
            self._updateBackButton()
            self.viewModel.setStartTab(Tabs.DEFAULT)

    def __onServerSettingsChanged(self, diff):
        if {'isLootBoxesEnabled', 'lootBoxes_config', GUI_LOOT_BOXES_CONFIG}.intersection(diff.keys()):
            self.__updateStatus()

    def __onTamagochiUnlock(self, isUnlock):
        self.viewModel.setHasTamagochiUnlock(isUnlock)
