# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: new_year/scripts/client/new_year/gui/impl/new_year/views/tabs_controller.py
import inspect
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.new_year_tab_model import NewYearTabModel, MenuNames
from new_year.gui.impl.gen.view_models.views.lobby.new_year.components.ny_main_menu_tab_model import NyMainMenuTabModel
from new_year.helpers.server_settings import getNewYearMachineConfig
from new_year.skeletons.new_year import ITamagotchiDataProvider
from new_year.ny_constants import NyWidgetTopMenu
from helpers import dependency

def tabUpdateFunc(tabName):

    def decorator(fn):

        def wrapper(self, viewModel):
            fn(self, viewModel)

        wrapper.tabName = tabName
        return wrapper

    return decorator


class TabsController(object):
    __slots__ = ('_tabs', '_autoCreating', '_iconNamePostfix', '_selectedTabIdx')

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
            viewModel.setName(MenuNames(name))
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
            key = viewModel.getName().value
            updateFunc = self._tabs[key]
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
    _dataProvider = dependency.descriptor(ITamagotchiDataProvider)

    def _createViewModel(self):
        return NyMainMenuTabModel()

    @tabUpdateFunc(NyWidgetTopMenu.CITY)
    def _updateCity(self, viewModel):
        pass

    @tabUpdateFunc(NyWidgetTopMenu.LEADERS)
    def _updateLeaders(self, viewModel):
        viewModel.setIsEnabled(self._dataProvider.raccoonState)

    @tabUpdateFunc(NyWidgetTopMenu.SURPRISE_MACHINE)
    def _updateSurpriseMachine(self, viewModel):
        config = getNewYearMachineConfig()
        viewModel.setIsEnabled(config.isEnabled() if config is not None else False)
        return

    @tabUpdateFunc(NyWidgetTopMenu.PET)
    def _updatePet(self, viewModel):
        viewModel.setHasBubble(self._dataProvider.raccoonState and self._dataProvider.isOnboarding)
        viewModel.setIsEnabled(self._dataProvider.raccoonState)

    @tabUpdateFunc(NyWidgetTopMenu.INFO)
    def _updateInfo(self, viewModel):
        pass

    def tabOrderKey(self, tabName):
        return self.getTabsArray().index(tabName)

    def getTabsArray(self):
        return NyWidgetTopMenu.ALL
