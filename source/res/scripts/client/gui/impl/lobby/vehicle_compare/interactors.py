# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/vehicle_compare/interactors.py
import Event
from gui.Scaleform.daapi.view.lobby.vehicle_compare import cmp_helpers
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.tank_setup.interactors.base import InteractingItem
from gui.impl.lobby.tank_setup.interactors.battle_booster import BaseBattleBoosterInteractor
from gui.impl.lobby.tank_setup.interactors.consumable import BaseConsumableInteractor
from gui.impl.lobby.tank_setup.interactors.opt_device import BaseOptDeviceInteractor
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID

def _sendSwapSlotAction(interactor, leftID, rightID):
    currentLayout = interactor.getCurrentLayout()
    leftID, rightID = sorted((leftID, rightID))
    leftItem, rightItem = currentLayout[leftID], currentLayout[rightID]
    interactor.onSlotAction(actionType=BaseSetupModel.SWAP_SLOTS_ACTION, leftID=leftID, rightID=rightID, leftIntCD=leftItem.intCD if leftItem else NONE_ID, rightIntCD=rightItem.intCD if rightItem else NONE_ID)
    interactor._item.onSelected()


def _sendSelectSlotAction(interactor, slotID, itemIntCD):
    if itemIntCD is not None:
        interactor.onSlotAction(actionType=BaseSetupModel.SELECT_SLOT_ACTION, intCD=itemIntCD, slotID=slotID)
    else:
        interactor.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION, slotID=slotID)
    interactor._item.onSelected()
    return


class CompareInteractingItem(InteractingItem):
    __slots__ = ('onSelected',)

    def __init__(self, item):
        super(CompareInteractingItem, self).__init__(item)
        self.onSelected = Event.Event()

    def clear(self):
        super(CompareInteractingItem, self).clear()
        self.onSelected.clear()


class CompareBattleBoosterInteractor(BaseBattleBoosterInteractor):

    def changeSlotItem(self, slotID, itemIntCD):
        if itemIntCD is not None:
            cmp_helpers.getCmpConfiguratorMainView().installBattleBooster(itemIntCD)
        else:
            cmp_helpers.getCmpConfiguratorMainView().removeBattleBooster()
        _sendSelectSlotAction(self, slotID, itemIntCD)
        return

    def swapSlots(self, leftID, rightID):
        pass

    def revertSlot(self, slotID):
        self.changeSlotItem(slotID, None)
        return


class CompareOptDeviceInteractor(BaseOptDeviceInteractor):

    def changeSlotItem(self, slotID, itemIntCD):
        if itemIntCD is not None:
            cmp_helpers.getCmpConfiguratorMainView().installOptionalDevice(itemIntCD, slotID)
        else:
            cmp_helpers.getCmpConfiguratorMainView().removeOptionalDevice(slotID)
        _sendSelectSlotAction(self, slotID, itemIntCD)
        return

    def swapSlots(self, leftID, rightID):
        cmp_helpers.getCmpConfiguratorMainView().swapOptionalDevice(leftID, rightID)
        _sendSwapSlotAction(self, leftID, rightID)

    def revertSlot(self, slotID):
        self.changeSlotItem(slotID, None)
        return


class CompareConsumableInteractor(BaseConsumableInteractor):

    def changeSlotItem(self, slotID, itemIntCD):
        if itemIntCD is not None:
            cmp_helpers.getCmpConfiguratorMainView().installEquipment(itemIntCD, slotID)
        else:
            cmp_helpers.getCmpConfiguratorMainView().removeEquipment(slotID)
        _sendSelectSlotAction(self, slotID, itemIntCD)
        return

    def swapSlots(self, leftID, rightID):
        cmp_helpers.getCmpConfiguratorMainView().swapEquipment(leftID, rightID)
        _sendSwapSlotAction(self, leftID, rightID)

    def revertSlot(self, slotID):
        self.changeSlotItem(slotID, None)
        return
