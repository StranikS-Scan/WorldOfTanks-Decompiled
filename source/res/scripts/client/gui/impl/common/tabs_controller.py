# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/common/tabs_controller.py
import inspect
from account_helpers.AccountSettings import AccountSettings, OPT_DEVICE_TAB_VISITED

def tabUpdateFunc(tabName):

    def decorator(fn):

        def wrapper(self, viewModel, isFirst=False):
            fn(self, viewModel, isFirst)

        wrapper.tabName = tabName
        return wrapper

    return decorator


class TabsController(object):
    __slots__ = ('_tabsArray', '_tabs', '_autoCreating', '_iconNamePostfix')

    def __init__(self, autoCreating=True):
        self._autoCreating = autoCreating
        self._tabs = {wrapper.tabName:wrapper for _, wrapper in inspect.getmembers(self.__class__, inspect.ismethod) if getattr(wrapper, 'tabName', None)}

    def addTabModel(self, tabName, updateFunc):
        self._tabs[tabName] = updateFunc

    def createTabModels(self, tabsArray, **kwargs):
        tabsArray.clear()
        for name in self._getTabs(**kwargs):
            viewModel = self._createViewModel(name)
            viewModel.setName(name)
            updateFunc = self._tabs[name]
            updateFunc(self, viewModel, isFirst=True)
            tabsArray.addViewModel(viewModel)

        self._autoCreating = False
        tabsArray.invalidate()

    def updateTabModels(self, tabsArray):
        if self._autoCreating:
            self.createTabModels(tabsArray)
            return
        for viewModel in tabsArray:
            name = viewModel.getName()
            updateFunc = self._tabs[name]
            updateFunc(self, viewModel)

        tabsArray.invalidate()

    def updateTabModel(self, tabName, tabsArray):
        for viewModel in tabsArray:
            if viewModel.getName() == tabName:
                self._tabs[tabName](self, viewModel)
                break

    def tabOrderKey(self, tabName):
        return None

    def getDefaultTab(self):
        return None

    def _getTabs(self, **kwargs):
        return sorted(self._tabs.iterkeys(), key=self.tabOrderKey)

    def _createViewModel(self, name):
        raise NotImplementedError

    @property
    def tabs(self):
        return self._tabs

    def isVisited(self, tabName):
        visitedDict = AccountSettings.getSettings(OPT_DEVICE_TAB_VISITED)
        return visitedDict.get(tabName, False)

    def setVisited(self, tabName):
        visitedDict = AccountSettings.getSettings(OPT_DEVICE_TAB_VISITED)
        visitedDict[tabName] = True
        AccountSettings.setSettings(OPT_DEVICE_TAB_VISITED, visitedDict)
