# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/base_setup.py
import logging
from BWUtil import AsyncReturn
from async import async, await_callback
from gui.impl.lobby.tank_setup.array_providers.base import BaseVehSectionContext
from gui.impl.lobby.tank_setup.base_sub_model_view import BaseSubModelView
from gui.impl.lobby.tank_setup.tank_setup_helper import TankSetupAsyncCommandLock
from gui.impl.lobby.tank_setup.tank_setup_sounds import playSectionSelectSound
from helpers import dependency
from skeletons.gui.shared import IItemsCache
_logger = logging.getLogger(__name__)

class BaseSetupSubView(BaseSubModelView):
    __slots__ = ('_interactor', '_tabsController', '_provider', '_filter', '_curSlotID', '__slotActions', '_currentTabName', '_asyncActionLock')
    _itemsCache = dependency.descriptor(IItemsCache)

    def __init__(self, viewModel, interactor):
        super(BaseSetupSubView, self).__init__(viewModel)
        self._interactor = interactor
        self._tabsController = self._createTabsController()
        self._filter = self._createFilter()
        self.__slotActions = {}
        self._curSlotID = None
        self._provider = None
        self._currentTabName = None
        self._asyncActionLock = TankSetupAsyncCommandLock()
        return

    def getInteractor(self):
        return self._interactor

    def onLoading(self, currentSlotID, *args, **kwargs):
        self._updateTabs()
        if self._tabsController is not None:
            self._setTab(self._tabsController.getDefaultTab())
        if self._filter is not None:
            self._filter.initFilters(self._viewModel.filter)
        self.updateSlots(currentSlotID)
        return

    def initialize(self, *args, **kwargs):
        super(BaseSetupSubView, self).initialize()
        self._addListeners()

    def finalize(self):
        self._removeListeners()
        super(BaseSetupSubView, self).finalize()

    def update(self, fullUpdate=False):
        if self._viewModel is None:
            return
        else:
            with self._viewModel.transaction():
                self._updateTabs()
                self._updateSlots(fullUpdate)
            return

    def updateSlots(self, slotID, fullUpdate=True):
        self._curSlotID = slotID
        self._updateSlots(fullUpdate)

    @async
    def canQuit(self):
        yield await_callback(lambda callback: callback())()
        raise AsyncReturn(True)

    def revertItem(self, slotID):
        pass

    def onSlotAction(self, args):
        self.__onSlotAction(args)

    def _addListeners(self):
        self._viewModel.onSlotAction += self.__onSlotAction
        self._viewModel.onTabChanged += self._onTabChanged
        self._viewModel.onFilterChanged += self._onFilterChanged
        self._viewModel.onFilterReset += self._onFilterReset

    def _removeListeners(self):
        self._viewModel.onSlotAction -= self.__onSlotAction
        self._viewModel.onTabChanged -= self._onTabChanged
        self._viewModel.onFilterChanged -= self._onFilterChanged
        self._viewModel.onFilterReset -= self._onFilterReset
        self.__slotActions.clear()

    def _createTabsController(self):
        return None

    def _updateTabs(self):
        if self._tabsController is not None:
            self._tabsController.updateTabModels(self._viewModel.tabs.getTabs())
        return

    def _onTabChanged(self, args):
        tabName = args.get('name')
        if tabName and tabName != self._viewModel.tabs.getSelectedTabName():
            self._setTab(tabName)
            self._updateSlots(fullUpdate=True)
            playSectionSelectSound()

    def _setTab(self, tabName):
        if self._currentTabName != tabName:
            self._viewModel.tabs.setSelectedTabName(tabName)
            if self._tabsController is not None:
                self._provider = self._tabsController.getProvider(tabName)(self._interactor)
            self._currentTabName = tabName
        return

    def _updateSlots(self, fullUpdate=True):
        if self._provider is None:
            return
        else:
            if fullUpdate:
                self._provider.updateItems()
                self._provider.fillArray(self._viewModel.getSlots(), self._getSectionContext())
                self._updateItemByFilter()
            else:
                self._provider.updateArray(self._viewModel.getSlots(), self._getSectionContext())
                self._updateItemByFilter()
            return

    def _getSectionContext(self):
        return BaseVehSectionContext(self._curSlotID)

    def _createFilter(self):
        return None

    def _onFilterChanged(self, args):
        filterName = args.get('name')
        if filterName:
            self._filter.changeFilter(filterName, self._viewModel.filter)
            self._updateItemByFilter()

    def _onFilterReset(self):
        self._filter.resetFilters(self._viewModel.filter)
        self._updateItemByFilter()

    def _updateItemByFilter(self):
        if self._filter is None:
            return
        else:
            isVisibleCount = 0
            for slotModel in self._viewModel.getSlots():
                item = self._itemsCache.items.getItemByCD(slotModel.getIntCD())
                isVisible = self._filter.checkItem(item)
                slotModel.setIsVisible(isVisible)
                if isVisible:
                    isVisibleCount += 1

            self._viewModel.filter.setSelectedFilterCount(isVisibleCount)
            self._viewModel.filter.setTotalFilterCount(len(self._viewModel.getSlots()))
            return

    def _addSlotAction(self, actionType, method):
        self.__slotActions[actionType] = method

    def _onConfirm(self, callback, skipDialog=False):
        self._interactor.confirm(callback, skipDialog=skipDialog)

    def __onSlotAction(self, args):
        actionType = args.pop('actionType')
        actionMethod = self.__slotActions.get(actionType)
        if actionMethod is not None:
            actionMethod(args)
        else:
            _logger.error('__slotActions doesnt exist action type : %s(viewName %s)', actionType, self.__class__.__name__)
        return
