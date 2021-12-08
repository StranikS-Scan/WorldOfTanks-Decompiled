# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/tabs_controller.py
import inspect
from shared_utils import findFirst
from gifts.gifts_common import GiftEventID
from gui.gift_system.constants import NY_STAMP_CODE
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_album_tab_model import NyAlbumTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_loot_box_tab_model import NewYearLootBoxTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_main_menu_tab_model import NyMainMenuTabModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootBoxByTypeAndCategory
from gui.impl.lobby.loot_box.loot_box_notification import LootBoxNotification
from gui.impl.new_year.mega_toy_bubble import MegaToyBubble
from gui.shared.gui_items.loot_box import NewYearCategories, NewYearLootBoxes, CATEGORIES_GUI_ORDER
from helpers import dependency
from items.components.ny_constants import YEARS
from new_year.celebrity.celebrity_quests_helpers import hasCelebrityBubble
from new_year.collection_presenters import NY18CollectionPresenter, NY19CollectionPresenter, NY20CollectionPresenter, NY21CollectionPresenter, CurrentNYCollectionPresenter
from new_year.ny_constants import NyWidgetTopMenu, NyTabBarMainView, NyTabBarAlbumsView, NyTabBarRewardsView
from skeletons.gui.game_control import IGiftSystemController
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController

def tabUpdateFunc(tabName):

    def decorator(fn):

        def wrapper(self, viewModel):
            fn(self, viewModel)

        wrapper.tabName = tabName
        return wrapper

    return decorator


class TabsController(object):
    __slots__ = ('_tabsArray', '_tabs', '_autoCreating', '_iconNamePostfix', '_selectedTabIdx')

    def __init__(self, autoCreating=True):
        self._autoCreating = autoCreating
        self._iconNamePostfix = ''
        self._tabs = {wrapper.tabName:wrapper for _, wrapper in inspect.getmembers(self.__class__, inspect.ismethod) if getattr(wrapper, 'tabName', None)}
        self._selectedTabIdx = 0

    def getSelectedTabIdx(self):
        return self._selectedTabIdx

    def setSelectedTabIdx(self, idx):
        if 0 <= idx < len(self.getTabsArray()):
            self._selectedTabIdx = idx

    def selectTab(self, tabName):
        tabIdx = self.tabOrderKey(tabName)
        self._selectedTabIdx = tabIdx

    def createTabModels(self, tabsArray):
        tabsArray.clear()
        for name in self.getTabsArray():
            viewModel = self._createViewModel()
            viewModel.setName(name)
            viewModel.setIconName(name + self._iconNamePostfix)
            updateFunc = self._tabs[name]
            updateFunc(self, viewModel)
            tabsArray.addViewModel(viewModel)

        tabsArray.invalidate()
        self._autoCreating = False

    def updateTabModels(self, tabsArray):
        if self._autoCreating:
            self.createTabModels(tabsArray)
            return
        for viewModel in tabsArray:
            name = viewModel.getName()
            updateFunc = self._tabs[name]
            updateFunc(self, viewModel)

        tabsArray.invalidate()

    def getSelectedName(self, tabsArray):
        return tabsArray[self._selectedTabIdx].getName() if self._selectedTabIdx < len(tabsArray) else None

    def getCurrentTabName(self):
        tabsArray = self.getTabsArray()
        return tabsArray[self._selectedTabIdx] if self._selectedTabIdx < len(tabsArray) else None

    def getTabsArray(self):
        return []

    def getEnabledTabsArray(self):
        return self.getTabsArray()

    def tabOrderKey(self, tabName):
        pass

    def _createViewModel(self):
        return NewYearTabModel()


class NewYearMainTabsController(TabsController):
    __giftsController = dependency.descriptor(IGiftSystemController)
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)

    def _createViewModel(self):
        return NyMainMenuTabModel()

    @tabUpdateFunc(NyWidgetTopMenu.GLADE)
    def _updateGlade(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys() or MegaToyBubble.mustBeShownByType())

    @tabUpdateFunc(NyWidgetTopMenu.REWARDS)
    def _updateRewards(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldRewardsBubbleNeeded(YEARS.ALL[0:-1]))

    @tabUpdateFunc(NyWidgetTopMenu.VEHICLES)
    def _updateVehicles(self, viewModel):
        viewModel.setUnseenCount(len(self._nyController.getVehicleBranch().getFreeVehicleSlots()) > 0)

    @tabUpdateFunc(NyWidgetTopMenu.DECORATIONS)
    def _updateDecorations(self, viewModel):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.GIFT_SYSTEM)
    def _updateGiftSystem(self, viewModel):
        eventHub = self.__giftsController.getEventHub(GiftEventID.NY_HOLIDAYS)
        isEventHubEnabled = bool(eventHub and eventHub.getSettings().isEnabled)
        viewModel.setInfoCount(eventHub.getStamper().getStampCount(NY_STAMP_CODE) if isEventHubEnabled else 0)
        viewModel.setIsEnabled(isEventHubEnabled)

    @tabUpdateFunc(NyWidgetTopMenu.CHALLENGE)
    def _updateChallenge(self, viewModel):
        viewModel.setUnseenCount(hasCelebrityBubble())

    @tabUpdateFunc(NyWidgetTopMenu.SHARDS)
    def _updateShards(self, viewModel):
        infoCount = self._itemsCache.items.festivity.getShardsCount()
        viewModel.setInfoCount(infoCount)

    @tabUpdateFunc(NyWidgetTopMenu.COLLECTIONS)
    def _updateCollection(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldCollectionBubbleNeeded(YEARS.ALL[0:-1]))
        count = CurrentNYCollectionPresenter.getCount()
        if count:
            viewModel.setInfoCount(count)

    def tabOrderKey(self, tabName):
        return self.getTabsArray().index(tabName)

    def getTabsArray(self):
        eHub = self.__giftsController.getEventHub(GiftEventID.NY_HOLIDAYS)
        return NyWidgetTopMenu.ALL if eHub and not eHub.getSettings().isDisabled else NyWidgetTopMenu.ALTERNATIVE

    def getEnabledTabsArray(self):
        eHub = self.__giftsController.getEventHub(GiftEventID.NY_HOLIDAYS)
        if eHub and eHub.getSettings().isEnabled:
            return NyWidgetTopMenu.ALL
        return NyWidgetTopMenu.ACTIVE if eHub and eHub.getSettings().isSuspended else NyWidgetTopMenu.ALTERNATIVE


class GladeTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    @tabUpdateFunc(NyTabBarMainView.FIR)
    def _updateFir(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.FIR))

    @tabUpdateFunc(NyTabBarMainView.FAIR)
    def _updateFair(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.FAIR))

    @tabUpdateFunc(NyTabBarMainView.INSTALLATION)
    def _updateInstallation(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.INSTALLATION))

    @tabUpdateFunc(NyTabBarMainView.MEGAZONE)
    def _updateMegazone(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.MEGAZONE) or MegaToyBubble.mustBeShownByType())

    def tabOrderKey(self, tabName):
        return NyTabBarMainView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarMainView.ALL


class AlbumsTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2018)
    def _updateNewYear2018(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldCollectionBubbleNeeded((YEARS.YEAR18,)))
        self.__updateAlbumsTab(viewModel, NY18CollectionPresenter)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2019)
    def _updateNewYear2019(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldCollectionBubbleNeeded((YEARS.YEAR19,)))
        self.__updateAlbumsTab(viewModel, NY19CollectionPresenter)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2020)
    def _updateNewYear2020(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldCollectionBubbleNeeded((YEARS.YEAR20,)))
        self.__updateAlbumsTab(viewModel, NY20CollectionPresenter)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2021)
    def _updateNewYear2021(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldCollectionBubbleNeeded((YEARS.YEAR21,)))
        self.__updateAlbumsTab(viewModel, NY21CollectionPresenter)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2022)
    def _updateNewYear2022(self, viewModel):
        self.__updateAlbumsTab(viewModel, CurrentNYCollectionPresenter)

    def tabOrderKey(self, tabName):
        return NyTabBarAlbumsView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarAlbumsView.ALL

    @staticmethod
    def __updateAlbumsTab(viewModel, presenter):
        viewModel.setCollectionName(presenter.getName())
        viewModel.setCurrentValue(presenter.getCount())
        viewModel.setTotalValue(presenter.getTotalCount())

    def _createViewModel(self):
        return NyAlbumTabModel()


class RewardsTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, autoCreating=True):
        super(RewardsTabsController, self).__init__(autoCreating)
        self._iconNamePostfix = 'Reward'

    @tabUpdateFunc(NyTabBarRewardsView.FOR_LEVELS)
    def _updateForLevels(self, viewModel):
        pass

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY18)
    def _updateCollection2018(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldRewardsBubbleNeeded((YEARS.YEAR18,)))

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY19)
    def _updateCollection2019(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldRewardsBubbleNeeded((YEARS.YEAR19,)))

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY20)
    def _updateCollection2020(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldRewardsBubbleNeeded((YEARS.YEAR20,)))

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY21)
    def _updateCollection2021(self, viewModel):
        viewModel.setUnseenCount(self._nyController.isOldRewardsBubbleNeeded((YEARS.YEAR21,)))

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY22)
    def _updateCollection2022(self, viewModel):
        pass

    def tabOrderKey(self, tabName):
        return NyTabBarRewardsView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarRewardsView.ALL


class LootBoxesEntryViewTabsController(TabsController):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    __itemsCache = dependency.descriptor(IItemsCache)
    _ORDER = CATEGORIES_GUI_ORDER + (NewYearLootBoxes.COMMON,)

    def __init__(self, autoCreating=True):
        super(LootBoxesEntryViewTabsController, self).__init__(autoCreating)
        self.__availableBoxes = {}

    def tabOrderKey(self, tabName):
        return self._ORDER.index(tabName)

    def getTabsArray(self):
        return self._ORDER

    def setInitState(self, initLootBoxType, initCategory):
        if initLootBoxType in self._ORDER:
            self.selectTab(initLootBoxType)
        elif initLootBoxType == NewYearLootBoxes.PREMIUM and not initCategory:
            category = self.getInitCategory()
            if category is not None:
                self.selectTab(category)
        elif initCategory in self._ORDER:
            self.selectTab(initCategory)
        return

    def updateAvailableBoxes(self, availableBoxes):
        self.__availableBoxes = availableBoxes

    def getSelectedBoxType(self):
        currentTab = self._ORDER[self._selectedTabIdx]
        return NewYearLootBoxes.COMMON if currentTab == NewYearLootBoxes.COMMON else NewYearLootBoxes.PREMIUM

    def getSelectedBoxCategory(self):
        currentTab = self._ORDER[self._selectedTabIdx]
        return None if currentTab == NewYearLootBoxes.COMMON else currentTab

    def getSelectedBoxName(self):
        return self._ORDER[self._selectedTabIdx]

    def getSelectedBoxID(self):
        lootbox = findFirst(lambda l: l.getCategory() == self.getSelectedBoxCategory(), self.__itemsCache.items.tokens.getLootBoxes().itervalues())
        return lootbox.getID() if lootbox else None

    def _createViewModel(self):
        return NewYearLootBoxTabModel()

    @tabUpdateFunc(NewYearCategories.NEWYEAR)
    def _updateNewYear(self, viewModel):
        self._updatePremiumLootBox(viewModel, NewYearCategories.NEWYEAR)

    @tabUpdateFunc(NewYearCategories.CHRISTMAS)
    def _updateChristmas(self, viewModel):
        self._updatePremiumLootBox(viewModel, NewYearCategories.CHRISTMAS)

    @tabUpdateFunc(NewYearCategories.ORIENTAL)
    def _updateOriental(self, viewModel):
        self._updatePremiumLootBox(viewModel, NewYearCategories.ORIENTAL)

    @tabUpdateFunc(NewYearCategories.FAIRYTALE)
    def _updateFairytale(self, viewModel):
        self._updatePremiumLootBox(viewModel, NewYearCategories.FAIRYTALE)

    @tabUpdateFunc(NewYearLootBoxes.COMMON)
    def _updateCommon(self, viewModel):
        viewModel.setInfoCount(self.__availableBoxes.get(NewYearLootBoxes.COMMON, {}).get('total', 0))
        viewModel.setUnseenCount(LootBoxNotification.hasNewBox(NewYearLootBoxes.COMMON))
        boxItem = getLootBoxByTypeAndCategory(boxType=NewYearLootBoxes.COMMON)
        viewModel.setIsEnabled(boxItem is not None and self._lobbyContext.getServerSettings().isLootBoxEnabled(boxItem.getID()))
        return

    def _updatePremiumLootBox(self, viewModel, category):
        viewModel.setInfoCount(self._getBoxCountByCategory(category))
        viewModel.setUnseenCount(LootBoxNotification.hasNewBox(NewYearLootBoxes.PREMIUM, category))
        boxItem = getLootBoxByTypeAndCategory(boxType=NewYearLootBoxes.PREMIUM, boxCategory=category)
        viewModel.setIsEnabled(boxItem is not None and self._lobbyContext.getServerSettings().isLootBoxEnabled(boxItem.getID()))
        return

    def _getBoxCountByCategory(self, category):
        return self.__availableBoxes.get(NewYearLootBoxes.PREMIUM, {}).get('categories', {}).get(category, 0)

    def getInitCategory(self):
        category = None
        for categoryName in CATEGORIES_GUI_ORDER:
            if LootBoxNotification.hasDeliveredBox(categoryName):
                return categoryName
            if category is None and self._getBoxCountByCategory(categoryName):
                category = categoryName

        return category
