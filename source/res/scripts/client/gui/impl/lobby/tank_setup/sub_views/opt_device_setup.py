# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/opt_device_setup.py
from functools import partial
from gui.shared.event_dispatcher import showDeconstructionDeviceWindow
from wg_async import wg_async, wg_await
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabsController, OptDeviceSelectedFilters, getOptDeviceTabByItem, OptDeviceIntroductionController, OptDeviceTabs
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView
from helpers import dependency
from skeletons.gui.shared import IItemsCache

class OptDeviceSetupSubView(BaseEquipmentSetupSubView):
    __itemsCache = dependency.descriptor(IItemsCache)

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        if fullUpdate:
            self._filter.resetFilters(self._viewModel.filter)
        item = self._interactor.getCurrentLayout()[slotID]
        if item is not None:
            tabName = getOptDeviceTabByItem(item)
            if self._currentTabName != tabName:
                self._setTab(tabName)
                fullUpdate = True
        super(OptDeviceSetupSubView, self).updateSlots(slotID, fullUpdate, updateData)
        return

    def _updateSlots(self, fullUpdate=True, updateData=True):
        super(OptDeviceSetupSubView, self)._updateSlots(fullUpdate, updateData)
        self._viewModel.setHasUnfitItems(self._provider.hasUnfitItems())
        self._introductionUpdate(self._viewModel.tabs.getSelectedTabName())

    def revertItem(self, slotID):
        self._selectItem(slotID, None)
        return

    def _updateTabs(self):
        super(OptDeviceSetupSubView, self)._updateTabs()
        if self._tabsController is not None:
            tabName = self._viewModel.tabs.getSelectedTabName()
            currencyModel = self._viewModel.specialCurrency
            currencyName = self._tabsController.getTabCurrency(tabName)
            currencyAmount = self._itemsCache.items.stats.actualMoney.get(currencyName, 0)
            currencyModel.setName(currencyName)
            currencyModel.setValue(currencyAmount)
        return

    def _onGetMoreCurrency(self):
        showDeconstructionDeviceWindow(onDeconstructedCallback=self._onDeconstructed)

    def _onDeconstructed(self, deconstructedItemsOnVehicle, upgradItemPair):
        for item in deconstructedItemsOnVehicle:
            slotID = self._interactor.getCurrentLayout().index(item)
            if slotID is not None:
                self.revertItem(slotID)

        if upgradItemPair:
            upgradDevice = upgradItemPair[0]
            upgradedIntCD = upgradDevice.descriptor.upgradeInfo.upgradedCompDescr
            slotID = self._interactor.getCurrentLayout().index(upgradDevice)
            if slotID is not None:
                self._selectItem(slotID, upgradedIntCD)
        return

    def _createTabsController(self):
        return OptDeviceTabsController()

    def _createFilter(self):
        return OptDeviceSelectedFilters()

    def _addListeners(self):
        super(OptDeviceSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.DEMOUNT_SLOT_ACTION, self.__onDemountItem)
        self._addSlotAction(BaseSetupModel.DEMOUNT_SLOT_FROM_SETUP_ACTION, partial(self.__onDemountItem, everywhere=False))
        self._addSlotAction(BaseSetupModel.DEMOUNT_SLOT_FROM_SETUPS_ACTION, self.__onDemountItem)
        self._addSlotAction(BaseSetupModel.DESTROY_SLOT_ACTION, partial(self.__onDemountItem, isDestroy=True))
        self._addSlotAction(BaseSetupModel.UPGRADE_SLOT_ACTION, self.__onUpgradeItem)
        self._addSlotAction(BaseSetupModel.DECONSTRUCT_SLOT_ACTION, partial(self.__onDemountItem, isDestroy=True))
        self._viewModel.onIntroPassed += self._onIntroPassed
        self._viewModel.specialCurrency.onGetMoreCurrency += self._onGetMoreCurrency

    def _removeListeners(self):
        super(OptDeviceSetupSubView, self)._removeListeners()
        self._viewModel.onIntroPassed -= self._onIntroPassed
        self._viewModel.specialCurrency.onGetMoreCurrency -= self._onGetMoreCurrency

    def _setTab(self, tabName):
        if self._currentTabName != tabName:
            super(OptDeviceSetupSubView, self)._setTab(tabName)
            self._introductionUpdate(tabName, True)

    def _updateItemByFilter(self):
        if self._currentTabName == OptDeviceTabs.SIMPLE:
            super(OptDeviceSetupSubView, self)._updateItemByFilter()

    @wg_async
    def _selectItem(self, slotID, item):
        yield wg_await(self._asyncActionLock.tryAsyncCommand(self._interactor.changeSlotItem, slotID, item))
        self.update()

    def _introductionUpdate(self, tabName, forceUpdateTabs=False):
        hasItems = len(self._provider.getItems()) > 0
        introduction = OptDeviceIntroductionController.getIntroduction(tabName, hasItems)
        self._viewModel.setIntroductionType(introduction or '')
        self._viewModel.setWithIntroduction(introduction is not None)
        if not introduction or forceUpdateTabs:
            self._updateTabs()
        return

    def _onIntroPassed(self):
        OptDeviceIntroductionController.setIntroductionValue(self._viewModel.getIntroductionType())
        self._introductionUpdate(self._currentTabName)

    @wg_async
    def __onDemountItem(self, args, isDestroy=False, everywhere=True):
        itemIntCD = int(args.get('intCD'))
        yield wg_await(self._asyncActionLock.tryAsyncCommand(self._interactor.demountItem, itemIntCD, isDestroy, everywhere))
        self.update()

    @wg_async
    def __onUpgradeItem(self, args):
        itemIntCD = int(args['intCD'])
        result = yield wg_await(self._asyncActionLock.tryAsyncCommandWithCallback(self._interactor.upgradeModule, itemIntCD, self._onDeconstructed))
        if result:
            self.update(fullUpdate=True)
