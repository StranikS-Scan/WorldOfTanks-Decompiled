# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/tabs_controller.py
import inspect
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_album_tab_model import NyAlbumTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.ny_main_menu_tab_model import NyMainMenuTabModel
from helpers import dependency
from new_year.collection_presenters import CurrentNYCollectionPresenter
from new_year.ny_constants import NyWidgetTopMenu, NyTabBarMainView, NyTabBarAlbumsView, NyTabBarRewardsView
from skeletons.gui.game_control import IGiftSystemController
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
        viewModel.setUnseenCount(self._nyController.checkForNewToys())

    @tabUpdateFunc(NyWidgetTopMenu.REWARDS)
    def _updateRewards(self, viewModel):
        viewModel.setUnseenCount(self._nyController.getVariadicDiscountCount())

    @tabUpdateFunc(NyWidgetTopMenu.DECORATIONS)
    def _updateDecorations(self, viewModel):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.SHARDS)
    def _updateShards(self, viewModel):
        infoCount = self._itemsCache.items.festivity.getShardsCount()
        viewModel.setInfoCount(infoCount)

    @tabUpdateFunc(NyWidgetTopMenu.COLLECTIONS)
    def _updateCollection(self, viewModel):
        count = CurrentNYCollectionPresenter.getCount()
        if count:
            viewModel.setInfoCount(count)

    @tabUpdateFunc(NyWidgetTopMenu.INFO)
    def _updateInfo(self, viewModel):
        pass

    def tabOrderKey(self, tabName):
        return self.getTabsArray().index(tabName)

    def getTabsArray(self):
        return NyWidgetTopMenu.ALL


class GladeTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    @tabUpdateFunc(NyTabBarMainView.FIR)
    def _updateFir(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.FIR))

    def tabOrderKey(self, tabName):
        return NyTabBarMainView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarMainView.ALL


class AlbumsTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2024)
    def _updateNewYear2024(self, viewModel):
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

    @tabUpdateFunc(NyTabBarRewardsView.COLLECTION_NY24)
    def _updateCollection2024(self, viewModel):
        pass

    def tabOrderKey(self, tabName):
        return NyTabBarRewardsView.ALL.index(tabName)

    def getTabsArray(self):
        return NyTabBarRewardsView.ALL
