# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/base_equipment.py
from wg_async import wg_await, wg_async
from BWUtil import AsyncReturn
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.tank_setup.interactors.base import BaseInteractor
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from gui.shared.event_dispatcher import showTankSetupExitConfirmDialog

class BaseEquipmentInteractor(BaseInteractor):
    __slots__ = ('_installedIndices', '_playerLayout')

    def setItem(self, item):
        super(BaseEquipmentInteractor, self).setItem(item)
        self._resetPlayerLayout()
        self._resetInstalledIndices()

    def getPlayerLayout(self):
        return self._playerLayout

    def changeSlotItem(self, slotID, itemIntCD):
        item = self._itemsCache.items.getItemByCD(int(itemIntCD)) if itemIntCD is not None else None
        self.getCurrentLayout()[slotID] = item
        if item is not None:
            self.onSlotAction(actionType=BaseSetupModel.SELECT_SLOT_ACTION, intCD=itemIntCD, slotID=slotID)
        else:
            self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION, slotID=slotID)
        self.itemUpdated()
        return

    def swapSlots(self, leftID, rightID, actionType=BaseSetupModel.SWAP_SLOTS_ACTION):
        currentLayout = self.getCurrentLayout()
        currentLayout.swap(leftID, rightID)
        indices = self._installedIndices
        indices[rightID], indices[leftID] = indices[leftID], indices[rightID]
        leftID, rightID = sorted((leftID, rightID))
        leftItem, rightItem = currentLayout[leftID], currentLayout[rightID]
        self.onSlotAction(actionType=actionType, leftID=leftID, rightID=rightID, leftIntCD=leftItem.intCD if leftItem else NONE_ID, rightIntCD=rightItem.intCD if rightItem else NONE_ID)
        self.itemUpdated()

    def revertSlot(self, slotID):
        installedIndex = self._installedIndices[slotID]
        item = self.getInstalledLayout()[installedIndex]
        if item is None or item in self.getCurrentLayout():
            self.getCurrentLayout()[slotID] = None
        else:
            self.getCurrentLayout()[slotID] = item
        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION, slotID=slotID)
        self.itemUpdated()
        return

    def buyMore(self, itemCD):
        pass

    @wg_async
    def showExitConfirmDialog(self):
        result = yield wg_await(showTankSetupExitConfirmDialog(items=self.getChangedList(), vehicle=self.getItem(), fromSection=self.getName(), startState=BuyAndExchangeStateEnum.BUY_NOT_REQUIRED if not self.getChangedList() else None))
        raise AsyncReturn(result)
        return

    def _resetInstalledIndices(self):
        self._installedIndices = [ i for i in range(len(self.getInstalledLayout())) ]

    def _resetPlayerLayout(self):
        self._playerLayout = self.getCurrentLayout().copy()
