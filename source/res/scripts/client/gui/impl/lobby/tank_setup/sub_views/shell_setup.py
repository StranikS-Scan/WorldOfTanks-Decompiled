# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/sub_views/shell_setup.py
from functools import partial
from gui.shared import sound_helpers
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.configurations.shell import ShellTabsController, ShellDealPanel
from gui.impl.lobby.tank_setup.sub_views.deal_base_setup import DealBaseSetupSubView
from gui.shared.items_parameters import isAutoReloadGun
from gui.shared.event_dispatcher import showModuleInfo

class ShellSetupSubView(DealBaseSetupSubView):
    __slots__ = ()

    def updateSlots(self, slotID, fullUpdate=True, updateData=True):
        gun = self._interactor.getItem().descriptor.gun
        self._viewModel.setClipCount(1 if isAutoReloadGun(gun) else gun.clip[0])
        super(ShellSetupSubView, self).updateSlots(slotID, fullUpdate, updateData)

    def _createTabsController(self):
        return ShellTabsController()

    def _getDealPanel(self):
        return ShellDealPanel

    def _addListeners(self):
        super(ShellSetupSubView, self)._addListeners()
        self._addSlotAction(BaseSetupModel.SHOW_INFO_SLOT_ACTION, self.__onShowItemInfo)
        self._addSlotAction(BaseSetupModel.SWAP_SLOTS_ACTION, partial(self.__onSwapSlots, BaseSetupModel.SWAP_SLOTS_ACTION))
        self._addSlotAction(BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION, partial(self.__onSwapSlots, BaseSetupModel.DRAG_AND_DROP_SLOT_ACTION))
        self._viewModel.onShellUpdate += self.__onShellUpdate
        self._itemsCache.onSyncCompleted += self.__onItemsSyncCompleted

    def _removeListeners(self):
        super(ShellSetupSubView, self)._removeListeners()
        self._viewModel.onShellUpdate -= self.__onShellUpdate
        self._itemsCache.onSyncCompleted -= self.__onItemsSyncCompleted

    def _updateSlots(self, fullUpdate=True, updateData=True):
        self._viewModel.setMaxCount(self._interactor.getItem().ammoMaxSize)
        self._viewModel.setInstalledCount(sum((shell.count for shell in self._interactor.getCurrentLayout())))
        super(ShellSetupSubView, self)._updateSlots(fullUpdate, updateData)

    def __onItemsSyncCompleted(self, *_):
        self._updateSlots()

    def __onSwapSlots(self, actionType, args):
        leftID = int(args.get('leftID'))
        rightID = int(args.get('rightID'))
        self._interactor.swapSlots(leftID, rightID, actionType)
        self.update()

    def __onShowItemInfo(self, args):
        itemIntCD = args.get('intCD')
        showModuleInfo(itemIntCD, self._interactor.getItem().descriptor)

    def __onShellUpdate(self, args):
        intCD = int(args.get('intCD'))
        newCount = int(args.get('newCount'))
        oldCount = self._interactor.getCurrentLayout()[self._interactor.getCurrentShellSlotID(intCD)].count
        totalCount = oldCount + (self._viewModel.getMaxCount() - self._viewModel.getInstalledCount())
        self._interactor.changeShell(intCD, newCount)
        sound_helpers.playSliderUpdateSound(oldCount, newCount, totalCount)
        self.update()
