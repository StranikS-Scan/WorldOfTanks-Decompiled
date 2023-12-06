# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/new_year/info_page/ny_info_view.py
from ExtensionsManager import g_extensionsManager
from constants import CURRENT_REALM
from gui.impl.gen.view_models.views.lobby.new_year.views.new_year_info_view_model import NewYearInfoViewModel, Tabs
from gui.impl.lobby.new_year.ny_views_helpers import showInfoVideo
from gui.impl.lobby.new_year.sub_model_presenter import HistorySubModelPresenter
from gui.impl.new_year.navigation import NewYearNavigation
from gui.impl.wrappers.function_helpers import replaceNoneKwargsModel
from gui.server_events.events_dispatcher import showDebutBoxesQuests
from gui.shared.event_dispatcher import showLootBoxEntry
from gui.shared.gui_items.loot_box import NewYearLootBoxes
from helpers import dependency, getLanguageCode
from helpers.server_settings import GUI_LOOT_BOXES_CONFIG
from new_year.ny_bonuses import BonusHelper, getBonusConfig
from new_year.ny_constants import NyTabBarAlbumsView, NyTabBarRewardsView
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.game_control import IGuiLootBoxesController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
_giftsOrder = (NewYearInfoViewModel.LEVELS,
 NewYearInfoViewModel.STYLES,
 NewYearInfoViewModel.SMALLBOXES,
 NewYearInfoViewModel.BIGBOXES)

class NyInfoView(HistorySubModelPresenter):
    __slots__ = ('__slideLogger', '__smallBoxesCount')
    __lobbyContext = dependency.descriptor(ILobbyContext)
    __settingsCore = dependency.descriptor(ISettingsCore)
    __guiLootBoxes = dependency.descriptor(IGuiLootBoxesController)
    __itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, parentView, *args, **kwargs):
        super(NyInfoView, self).__init__(viewModel, parentView)
        self.__slideLogger = None
        self.__smallBoxesCount = 0
        return

    @property
    def viewModel(self):
        return self.getViewModel()

    def initialize(self, *args, **kwargs):
        super(NyInfoView, self).initialize()
        maxBonus = BonusHelper.getCommonMaxBonus()
        multipliersList = getBonusConfig().getAtmosphereMultipliers()
        startTab = Tabs.DEFAULT
        self.__smallBoxesCount = self.__getSmallBoxesCount()
        with self.viewModel.transaction() as model:
            model.setMaxBonus(maxBonus)
            model.setUsualMaxBonus(maxBonus)
            model.region.setRealm(CURRENT_REALM)
            model.region.setLanguage(getLanguageCode())
            model.setMinMultiplier(min(multipliersList))
            model.setMaxMultiplier(max(multipliersList))
            model.setStartTab(startTab)
            self.__updateStatus(model=model)
            self.__updateBoxesExistance(model=model)

    def _getEvents(self):
        return ((self.viewModel.videoCover.onClick, self.__onClickVideo),
         (self.viewModel.onButtonClick, self.__onButtonClick),
         (self.viewModel.onSlideChanged, self.__onSlideChanged),
         (self.__lobbyContext.getServerSettings().onServerSettingsChange, self.__onServerSettingsChanged),
         (self.__guiLootBoxes.onBoxesCountChange, self.__onBoxesCountChange),
         (NewYearNavigation.onUpdateCurrentView, self.__onUpdateView))

    def finalize(self):
        self.__onSlideClosed()
        super(NyInfoView, self).finalize()

    @replaceNoneKwargsModel
    def __updateStatus(self, model=None):
        isLootBoxesEnabled = self.__lobbyContext.getServerSettings().isLootBoxesEnabled()
        isLootBoxesBuyEnabled = False
        if g_extensionsManager.isExtensionEnabled('gui_lootboxes'):
            isLootBoxesBuyEnabled = self.__guiLootBoxes.isBuyAvailable()
        model.setIsLootBoxEnabled(isLootBoxesEnabled)
        model.setIsLootBoxesBuyEnabled(isLootBoxesBuyEnabled)

    @replaceNoneKwargsModel
    def __updateBoxesExistance(self, model=None):
        model.setHasSmallBoxes(self.__smallBoxesCount > 0)

    def __getSmallBoxesCount(self):
        boxes = self.__itemsCache.items.tokens.getLootBoxes()
        return sum((box.getInventoryCount() for box in boxes.itervalues() if box.getType() == NewYearLootBoxes.NY_24_STANDARD))

    def __onButtonClick(self, args):
        action = args['value']
        if action == NewYearInfoViewModel.LEVELS:
            self._goToRewardsView(tabName=NyTabBarRewardsView.FOR_LEVELS, popHistory=True)
        elif action == NewYearInfoViewModel.STYLES:
            self.goToAlbumView(tabName=NyTabBarAlbumsView.NY_2024, popHistory=True)
        elif action == NewYearInfoViewModel.BIGBOXES:
            self.__guiLootBoxes.openShop()
        elif action == NewYearInfoViewModel.SMALLBOXES:
            if self.__smallBoxesCount > 0:
                showLootBoxEntry(lootBoxType=NewYearLootBoxes.NY_24_STANDARD)
            else:
                showDebutBoxesQuests()

    @staticmethod
    def __onClickVideo():
        showInfoVideo()

    def __onSlideChanged(self, args):
        self.__onSlideClosed()

    def __onUpdateView(self, *_, **kwargs):
        prevViewAlias = kwargs.get('previousViewAlias')
        if prevViewAlias and self._navigationHistory.getLast() != prevViewAlias:
            self._navigationHistory.clear()
            self._navigationHistory.addToHistory(prevViewAlias, {})
            self._updateBackButton()
            startTab = Tabs.DEFAULT
            self.viewModel.setStartTab(startTab)
            self.__onSlideClosed()

    def __onServerSettingsChanged(self, diff):
        if {'isLootBoxesEnabled', 'lootBoxes_config', GUI_LOOT_BOXES_CONFIG}.intersection(diff.keys()):
            self.__updateStatus()

    def __onBoxesCountChange(self, *_):
        self.__smallBoxesCount = self.__getSmallBoxesCount()
        self.__updateBoxesExistance()

    def __onSlideClosed(self):
        pass
