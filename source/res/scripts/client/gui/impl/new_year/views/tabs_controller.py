# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/new_year/views/tabs_controller.py
import inspect
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_album_tab_model import NewYearAlbumTabModel
from gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel
from helpers import dependency
from new_year.collection_presenters import NY18CollectionPresenter, NY20CollectionPresenter, NY19CollectionPresenter
from new_year.ny_constants import NyWidgetTopMenu, NyTabBarMainView, NyTabBarAlbumsView, NyTabBarRewardsView
from skeletons.gui.shared import IItemsCache
from skeletons.new_year import INewYearController, ITalismanSceneController

def tabUpdateFunc(tabName):

    def decorator(fn):

        def wrapper(self, viewModel):
            fn(self, viewModel)

        wrapper.tabName = tabName
        return wrapper

    return decorator


class TabsController(object):
    __slots__ = ('_tabsArray', '_tabs', '_autoCreating', '_iconNamePostfix')

    def __init__(self, autoCreating=True):
        self._autoCreating = autoCreating
        self._iconNamePostfix = ''
        self._tabs = {wrapper.tabName:wrapper for _, wrapper in inspect.getmembers(self.__class__, inspect.ismethod) if getattr(wrapper, 'tabName', None)}

    def addTabModel(self, tabName, updateFunc):
        self._tabs[tabName] = updateFunc

    def createTabModels(self, tabsArray):
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

    def tabOrderKey(self, tabName):
        pass

    def _createViewModel(self):
        return NewYearTabModel()


class NewYearMainTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)
    _itemsCache = dependency.descriptor(IItemsCache)
    _talismanController = dependency.descriptor(ITalismanSceneController)

    @tabUpdateFunc(NyWidgetTopMenu.GLADE)
    def _updateGlade(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys() or self._talismanController.hasTalismanGiftBubble())

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
        count = NY20CollectionPresenter.getCount()
        if count:
            viewModel.setInfoCount(count)

    def tabOrderKey(self, tabName):
        return NyWidgetTopMenu.ALL.index(tabName)


class GladeTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)
    _talismanController = dependency.descriptor(ITalismanSceneController)

    @tabUpdateFunc(NyTabBarMainView.FIR)
    def _updateFir(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.FIR))

    @tabUpdateFunc(NyTabBarMainView.TABLEFUL)
    def _updateTableful(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.TABLEFUL))

    @tabUpdateFunc(NyTabBarMainView.INSTALLATION)
    def _updateInstallation(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.INSTALLATION))

    @tabUpdateFunc(NyTabBarMainView.ILLUMINATION)
    def _updateIllumination(self, viewModel):
        viewModel.setUnseenCount(self._nyController.checkForNewToys(objectType=NyTabBarMainView.ILLUMINATION))

    @tabUpdateFunc(NyTabBarMainView.MASCOT)
    def _updateMascot(self, viewModel):
        viewModel.setUnseenCount(self._talismanController.hasTalismanGiftBubble())

    def tabOrderKey(self, tabName):
        return NyTabBarMainView.ALL.index(tabName)


class AlbumsTabsController(TabsController):

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2018)
    def _updateNewYear2018(self, viewModel):
        self.__updateAlbumsTab(viewModel, NY18CollectionPresenter)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2019)
    def _updateNewYear2019(self, viewModel):
        self.__updateAlbumsTab(viewModel, NY19CollectionPresenter)

    @tabUpdateFunc(NyTabBarAlbumsView.NY_2020)
    def _updateNewYear2020(self, viewModel):
        self.__updateAlbumsTab(viewModel, NY20CollectionPresenter)

    def tabOrderKey(self, tabName):
        return NyTabBarAlbumsView.ALL.index(tabName)

    @staticmethod
    def __updateAlbumsTab(viewModel, presenter):
        viewModel.setCollectionName(presenter.getName())
        viewModel.setCurrentValue(presenter.getCount())
        viewModel.setTotalValue(presenter.getTotalCount())

    def _createViewModel(self):
        return NewYearAlbumTabModel()


class RewardsTabsController(TabsController):
    _nyController = dependency.descriptor(INewYearController)

    def __init__(self, autoCreating=True):
        super(RewardsTabsController, self).__init__(autoCreating)
        self._iconNamePostfix = 'Reward'

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

    def tabOrderKey(self, tabName):
        return NyTabBarRewardsView.ALL.index(tabName)
