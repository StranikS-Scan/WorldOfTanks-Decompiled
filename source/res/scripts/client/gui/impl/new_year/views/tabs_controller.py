# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/tabs_controller.py
import inspect
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_album_tab_model import NewYearAlbumTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_loot_box_tab_model import NewYearLootBoxTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel
from gui.impl.lobby.loot_box.loot_box_helper import getLootBoxByTypeAndCategory
from gui.impl.lobby.loot_box.loot_box_notification import LootBoxNotification
from gui.impl.new_year.mega_toy_bubble import MegaToyBubble
from gui.shared.gui_items.loot_box import NewYearCategories, NewYearLootBoxes, CATEGORIES_GUI_ORDER
from helpers import dependency
from items.components.ny_constants import YEARS, ToyTypes
from new_year.celebrity.celebrity_quests_helpers import hasCelebrityBubble
from new_year.collection_presenters import NY18CollectionPresenter, NY20CollectionPresenter, NY19CollectionPresenter, CurrentNYCollectionPresenter
from new_year.ny_constants import NyWidgetTopMenu, NyTabBarMainView, NyTabBarAlbumsView, NyTabBarRewardsView
from skeletons.gui.lobby_context import ILobbyContext
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ITalismanSceneController
from uilogging.decorators import loggerTarget, loggerEntry, simpleLog, logProperty
from uilogging.ny.constants import NY_LOG_KEYS, NY_LOG_ACTIONS
from uilogging.ny.loggers import NYLogger

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

    def closeTabs(self):
        pass

    def getSelectedTabIdx(self):
        return self._selectedTabIdx

    def selectTab(self, tabName):
        tabIdx = self.tabOrderKey(tabName)
        self._selectedTabIdx = tabIdx

    def createTabModels(self, tabsArray):
        tabsArray.clear()
        for name in sorted(self._tabs.iterkeys(), key=self.tabOrderKey):
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

    def tabOrderKey(self, tabName):
        pass

    def _createViewModel(self):
        return NewYearTabModel()


@loggerTarget(logKey=NY_LOG_KEYS.NY_LOBBY_MENU, loggerCls=NYLogger)
class NewYearMainTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _talismanController = dependency.descriptor(ITalismanSceneController)

    def __init__(self, autoCreating=True):
        super(NewYearMainTabsController, self).__init__(autoCreating)
        NYLogger.__init__(self)

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    def closeTabs(self):
        pass

    @loggerEntry
    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def createTabModels(self, tabsArray):
        super(NewYearMainTabsController, self).createTabModels(tabsArray)

    @tabUpdateFunc(NyWidgetTopMenu.GLADE)
    def _updateGlade(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys() or self._talismanController.hasTalismanGiftBubble() or hasCelebrityBubble() or MegaToyBubble.mustBeShownByType())

    @tabUpdateFunc(NyWidgetTopMenu.REWARDS)
    def _updateRewards(self, viewModel):
        viewModel.setUnseenCount(self._nyController.getFreeTalisman() > 0)

    @tabUpdateFunc(NyWidgetTopMenu.INFO)
    def _updateMail(self, viewModel):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.DECORATIONS)
    def _updateDecorations(self, viewModel):
        pass

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
        return NyWidgetTopMenu.ALL.index(tabName)

    def getTabsArray(self):
        return NyWidgetTopMenu.ALL

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    @simpleLog(argsIndex=0, resetTime=False, preProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def selectTab(self, tabName):
        super(NewYearMainTabsController, self).selectTab(tabName)


@loggerTarget(logKey=NY_LOG_KEYS.NY_GLADE_MENU, loggerCls=NYLogger)
class GladeTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)
    _talismanController = dependency.descriptor(ITalismanSceneController)

    def __init__(self, autoCreating=True):
        super(GladeTabsController, self).__init__(autoCreating)
        NYLogger.__init__(self)

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    def closeTabs(self):
        pass

    @loggerEntry
    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def createTabModels(self, tabsArray):
        super(GladeTabsController, self).createTabModels(tabsArray)

    @tabUpdateFunc(NyTabBarMainView.FIR)
    def _updateFir(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.FIR) or MegaToyBubble.mustBeShownByType(megaToyType=ToyTypes.MEGA_FIR))

    @tabUpdateFunc(NyTabBarMainView.TABLEFUL)
    def _updateTableful(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.TABLEFUL) or MegaToyBubble.mustBeShownByType(megaToyType=ToyTypes.MEGA_TABLEFUL))

    @tabUpdateFunc(NyTabBarMainView.INSTALLATION)
    def _updateInstallation(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.INSTALLATION) or MegaToyBubble.mustBeShownByType(megaToyType=ToyTypes.MEGA_INSTALLATION))

    @tabUpdateFunc(NyTabBarMainView.ILLUMINATION)
    def _updateIllumination(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.ILLUMINATION) or MegaToyBubble.mustBeShownByType(megaToyType=ToyTypes.MEGA_ILLUMINATION))

    @tabUpdateFunc(NyTabBarMainView.MASCOT)
    def _updateMascot(self, viewModel):
        viewModel.setUnseenCount(self._talismanController.hasTalismanGiftBubble())

    @tabUpdateFunc(NyTabBarMainView.CELEBRITY)
    def _updateCelebrity(self, viewModel):
        viewModel.setUnseenCount(hasCelebrityBubble())

    def tabOrderKey(self, tabName):
        return NyTabBarMainView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarMainView.ALL

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    @simpleLog(argsIndex=0, resetTime=False, preProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def selectTab(self, tabName):
        super(GladeTabsController, self).selectTab(tabName)


@loggerTarget(logKey=NY_LOG_KEYS.NY_ALBUM_MENU, loggerCls=NYLogger)
class AlbumsTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, autoCreating=True):
        super(AlbumsTabsController, self).__init__(autoCreating)
        NYLogger.__init__(self)

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    def closeTabs(self):
        pass

    @loggerEntry
    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def createTabModels(self, tabsArray):
        super(AlbumsTabsController, self).createTabModels(tabsArray)

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
        self.__updateAlbumsTab(viewModel, CurrentNYCollectionPresenter)

    def tabOrderKey(self, tabName):
        return NyTabBarAlbumsView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarAlbumsView.ALL

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    @simpleLog(argsIndex=0, resetTime=False, preProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def selectTab(self, tabName):
        super(AlbumsTabsController, self).selectTab(tabName)

    @staticmethod
    def __updateAlbumsTab(viewModel, presenter):
        viewModel.setCollectionName(presenter.getName())
        viewModel.setCurrentValue(presenter.getCount())
        viewModel.setTotalValue(presenter.getTotalCount())

    def _createViewModel(self):
        return NewYearAlbumTabModel()


@loggerTarget(logKey=NY_LOG_KEYS.NY_REWARDS_MENU, loggerCls=NYLogger)
class RewardsTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, autoCreating=True):
        super(RewardsTabsController, self).__init__(autoCreating)
        self._iconNamePostfix = 'Reward'
        NYLogger.__init__(self)

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    def closeTabs(self):
        pass

    @loggerEntry
    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def createTabModels(self, tabsArray):
        super(RewardsTabsController, self).createTabModels(tabsArray)

    @tabUpdateFunc(NyTabBarRewardsView.FOR_LEVELS)
    def _updateForLevels(self, viewModel):
        viewModel.setUnseenCount(self._nyController.getFreeTalisman() > 0)

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY18)
    def _updateCollection2018(self, viewModel):
        pass

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY19)
    def _updateCollection2019(self, viewModel):
        pass

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY20)
    def _updateCollection2020(self, viewModel):
        pass

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY21)
    def _updateCollection2021(self, viewModel):
        pass

    def tabOrderKey(self, tabName):
        return NyTabBarRewardsView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarRewardsView.ALL

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    @simpleLog(argsIndex=0, resetTime=False, preProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def selectTab(self, tabName):
        super(RewardsTabsController, self).selectTab(tabName)


@loggerTarget(logKey=NY_LOG_KEYS.NY_LOOT_BOX_MENU, loggerCls=NYLogger)
class LootBoxesEntryViewTabsController(TabsController):
    _lobbyContext = dependency.descriptor(ILobbyContext)
    _ORDER = CATEGORIES_GUI_ORDER + (NewYearLootBoxes.COMMON,)

    def __init__(self, autoCreating=True):
        super(LootBoxesEntryViewTabsController, self).__init__(autoCreating)
        self.__availableBoxes = {}
        NYLogger.__init__(self)

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    def closeTabs(self):
        pass

    @loggerEntry
    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def createTabModels(self, tabsArray):
        super(LootBoxesEntryViewTabsController, self).createTabModels(tabsArray)

    def tabOrderKey(self, tabName):
        return self._ORDER.index(tabName)

    def getTabsArray(self):
        return self._ORDER

    @logProperty(objProperty='getCurrentTabName', needCall=True, postProcessAction=NY_LOG_ACTIONS.NY_TABS_EXIT.format)
    @simpleLog(argsIndex=0, resetTime=False, preProcessAction=NY_LOG_ACTIONS.NY_TABS_ENTERING.format)
    def selectTab(self, tabName):
        super(LootBoxesEntryViewTabsController, self).selectTab(tabName)

    def setInitState(self, initLootBoxType, initCategory):
        if initLootBoxType in self._ORDER:
            self.selectTab(initLootBoxType)
        elif initLootBoxType == NewYearLootBoxes.PREMIUM and not initCategory:
            category = self.__getInitCategory()
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
        viewModel.setInfoCount(self.__availableBoxes.get(NewYearLootBoxes.COMMON).get('total', 0))
        viewModel.setUnseenCount(LootBoxNotification.hasNewBox(NewYearLootBoxes.COMMON))
        boxItem = getLootBoxByTypeAndCategory(boxType=NewYearLootBoxes.COMMON)
        viewModel.setIsEnabled(self._lobbyContext.getServerSettings().isLootBoxEnabled(boxItem.getID()))

    def _updatePremiumLootBox(self, viewModel, category):
        viewModel.setInfoCount(self._getBoxCountByCategory(category))
        viewModel.setUnseenCount(LootBoxNotification.hasNewBox(NewYearLootBoxes.PREMIUM, category))
        boxItem = getLootBoxByTypeAndCategory(boxType=NewYearLootBoxes.PREMIUM, boxCategory=category)
        viewModel.setIsEnabled(self._lobbyContext.getServerSettings().isLootBoxEnabled(boxItem.getID()))

    def _getBoxCountByCategory(self, category):
        return self.__availableBoxes.get(NewYearLootBoxes.PREMIUM).get('categories').get(category, 0)

    def __getInitCategory(self):
        category = None
        for categoryName in CATEGORIES_GUI_ORDER:
            if LootBoxNotification.hasDeliveredBox(categoryName):
                return categoryName
            if category is None and self._getBoxCountByCategory(categoryName):
                category = categoryName

        return category
