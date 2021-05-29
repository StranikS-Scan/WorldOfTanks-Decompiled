# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/opt_device_setup.py
from functools import partial
from async import async, await
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.configurations.opt_device import OptDeviceTabsController, OptDeviceSelectedFilters, getOptDeviceTabByItem, OptDeviceIntroductionController, OptDeviceTabs
from gui.impl.lobby.tank_setup.sub_views.base_equipment_setup import BaseEquipmentSetupSubView

class OptDeviceSetupSubView(BaseEquipmentSetupSubView):

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

    def revertItem(self, slotID):
        self._selectItem(slotID, None)
        return

    def _createTabsController(self):
        return OptDeviceTabsController()

    def _createFilter(self):
        return OptDeviceSelectedFilters()

    def _addListeners(self):
        super(OptDeviceSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.DEMOUNT_SLOT_ACTION, self.__onDemountItem)
        self._addSlotAction(BaseSetupModel.DESTROY_SLOT_ACTION, partial(self.__onDemountItem, isDestroy=True))
        self._addSlotAction(BaseSetupModel.UPGRADE_SLOT_ACTION, self.__onUpgradeItem)
        self._viewModel.onIntroPassed += self._onIntroPassed

    def _removeListeners(self):
        super(OptDeviceSetupSubView, self)._removeListeners()
        self._viewModel.onIntroPassed -= self._onIntroPassed

    def _setTab(self, tabName):
        if self._currentTabName != tabName:
            super(OptDeviceSetupSubView, self)._setTab(tabName)
            self._introductionUpdate(tabName)

    def _updateItemByFilter(self):
        if self._currentTabName == OptDeviceTabs.SIMPLE:
            super(OptDeviceSetupSubView, self)._updateItemByFilter()

    @async
    def _selectItem(self, slotID, item):
        yield await(self._asyncActionLock.tryAsyncCommand(self._interactor.changeSlotItem, slotID, item))
        self.update()

    def _introductionUpdate(self, tabName):
        introduction = OptDeviceIntroductionController.getIntroduction(tabName)
        self._viewModel.setIntroductionType(introduction or '')
        self._viewModel.setWithIntroduction(introduction is not None)
        if not introduction:
            self._updateTabs()
        return

    def _onIntroPassed(self):
        OptDeviceIntroductionController.setIntroductionValue(self._viewModel.getIntroductionType())
        self._introductionUpdate(self._currentTabName)

    @async
    def __onDemountItem(self, args, isDestroy=False):
        itemIntCD = int(args.get('intCD'))
        yield await(self._asyncActionLock.tryAsyncCommand(self._interactor.demountItem, itemIntCD, isDestroy))
        self.update()

    @async
    def __onUpgradeItem(self, args):
        itemIntCD = int(args['intCD'])
        result = yield await(self._asyncActionLock.tryAsyncCommandWithCallback(self._interactor.upgradeModule, itemIntCD))
        if result:
            self.update(fullUpdate=True)
