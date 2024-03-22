# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/opt_device.py
import typing
import adisp
from wg_async import wg_async, wg_await, await_callback
from BWUtil import AsyncReturn
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.tank_setup.interactors.base import BaseInteractor
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from gui.shared.event_dispatcher import showTankSetupExitConfirmDialog
from gui.shared.gui_items.items_actions import factory as ActionsFactory
if typing.TYPE_CHECKING:
    from gui.shared.gui_items.artefacts import OptionalDevice

class BaseOptDeviceInteractor(BaseInteractor):
    __slots__ = ()

    def getName(self):
        return TankSetupConstants.OPT_DEVICES

    def getInstalledLayout(self):
        return self.getItem().optDevices.installed

    def getCurrentLayout(self):
        return self.getItem().optDevices.layout

    def getSetupLayout(self):
        return self.getItem().optDevices.setupLayouts

    def getCurrentCategories(self, slotID):
        return self.getItem().optDevices.slots[slotID].categories


class OptDeviceInteractor(BaseOptDeviceInteractor):
    __slots__ = ()

    def getVehicleAfterInstall(self):
        vehicle = super(OptDeviceInteractor, self).getVehicleAfterInstall()
        vehicle.optDevices.setInstalled(*self.getItem().optDevices.layout)
        vehicle.optDevices.dynSlotType = self.getItem().optDevices.dynSlotType
        return vehicle

    def setItemInCurrentLayout(self, slotID, item):
        self.getCurrentLayout()[slotID] = item
        if item is not None:
            self.getItem().descriptor.installOptionalDevice(item.intCD, slotID)
        elif self.getItem().descriptor.optionalDevices[slotID] is not None:
            self.getItem().descriptor.removeOptionalDevice(slotID)
        return

    @adisp.adisp_process
    def demountProcess(self, slotID, isDestroy=False, isFitting=False, everywhere=True, callback=None):
        action = ActionsFactory.getAction(ActionsFactory.REMOVE_OPT_DEVICE, self.getItem(), self.getInstalledLayout()[slotID], slotID, isDestroy, isFitting, everywhere)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @adisp.adisp_process
    def deconstructProcess(self, slotID, callback=None):
        action = ActionsFactory.getAction(ActionsFactory.DECONSTRUCT_OPT_DEVICE, self.getInstalledLayout()[slotID], self.getItem(), slotID)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @wg_async
    def changeSlotItem(self, slotID, itemIntCD):
        item = self._itemsCache.items.getItemByCD(int(itemIntCD)) if itemIntCD is not None else None
        canChange = True
        removedItem = self.getCurrentLayout()[slotID]
        needToRemoveItem = removedItem is not None and removedItem in self.getInstalledLayout()
        if needToRemoveItem:
            everywhere = self.getSetupLayout().getIntCDs().count(removedItem.intCD) == 1
            canChange = yield await_callback(self.demountProcess)(self.getInstalledLayout().index(removedItem), isFitting=True, everywhere=everywhere)
        if canChange:
            self.setItemInCurrentLayout(slotID, item)
            if needToRemoveItem:
                self.onSlotAction(actionType=BaseSetupModel.DEMOUNT_SLOT_ACTION, intCD=itemIntCD, slotID=slotID)
            elif item is not None:
                self.onSlotAction(actionType=BaseSetupModel.SELECT_SLOT_ACTION, intCD=itemIntCD, slotID=slotID)
            else:
                self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION, slotID=slotID)
            self.itemUpdated()
        return

    def swapSlots(self, leftID, rightID, actionType=BaseSetupModel.SWAP_SLOTS_ACTION):
        optLayout = self.getCurrentLayout()
        leftID, rightID = sorted((leftID, rightID))
        leftItem, rightItem = optLayout[leftID], optLayout[rightID]
        self.setItemInCurrentLayout(rightID, None)
        self.setItemInCurrentLayout(leftID, rightItem)
        self.setItemInCurrentLayout(rightID, leftItem)
        self.onSlotAction(actionType=actionType, leftID=leftID, rightID=rightID, leftIntCD=leftItem.intCD if leftItem else NONE_ID, rightIntCD=rightItem.intCD if rightItem else NONE_ID)
        self.itemUpdated()
        return

    @wg_async
    def demountItem(self, itemIntCD, isDestroy=False, everywhere=True):
        result = None
        item = self._itemsCache.items.getItemByCD(itemIntCD)
        currentSlotID = self.getCurrentLayout().index(item)
        installedSlotID = self.getInstalledLayout().index(item)
        if currentSlotID is not None and installedSlotID is not None:
            if item.isModernized and isDestroy:
                result = yield await_callback(self.deconstructProcess)(installedSlotID)
            else:
                result = yield await_callback(self.demountProcess)(installedSlotID, isDestroy=isDestroy, everywhere=everywhere)
            if result:
                self.setItemInCurrentLayout(currentSlotID, None)
                actionType = BaseSetupModel.DESTROY_SLOT_ACTION if isDestroy else BaseSetupModel.DEMOUNT_SLOT_ACTION
                self.onSlotAction(actionType=actionType, intCD=itemIntCD, slotID=currentSlotID)
                self.itemUpdated()
        raise AsyncReturn(result)
        return

    def revert(self):
        for slotID in range(self.getInstalledLayout().getCapacity()):
            self.setItemInCurrentLayout(slotID, None)

        for slotID, optDevice in enumerate(self.getInstalledLayout()):
            self.setItemInCurrentLayout(slotID, optDevice)

        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()
        return

    @adisp.adisp_process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, self.getItem(), confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @adisp.adisp_process
    def upgradeModule(self, itemIntCD, onDeconstructed, callback):
        optDevice = self._itemsCache.items.getItemByCD(int(itemIntCD))
        slotIdx = self.getInstalledLayout().index(optDevice)
        setupIdx = None
        for layoutIdx, setup in self.getSetupLayout().setups.iteritems():
            if optDevice in setup:
                setupIdx = layoutIdx
                slotIdx = setup.index(optDevice)
                break

        vehicle = None if setupIdx is None else self.getItem()
        action = ActionsFactory.getAction(ActionsFactory.UPGRADE_OPT_DEVICE, vehicle=vehicle, module=optDevice, setupIdx=setupIdx, slotIdx=slotIdx, onDeconstructed=onDeconstructed)
        result = yield action.doAction() if action is not None else None
        if result:
            upgradedIntCD = optDevice.descriptor.upgradeInfo.upgradedCompDescr
            upgradedDevice = self._itemsCache.items.getItemByCD(upgradedIntCD)
            currentSlotIdx = self.getCurrentLayout().index(optDevice)
            if currentSlotIdx is not None:
                self.setItemInCurrentLayout(currentSlotIdx, upgradedDevice)
        self.itemUpdated()
        callback(result)
        return

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(OptDeviceInteractor, self).updateFrom(vehicle, onlyInstalled)
        items = self.getItem().optDevices
        items.setInstalled(*vehicle.optDevices.installed)
        items.setupLayouts.setSetups(vehicle.optDevices.setupLayouts.setups)
        if not onlyInstalled:
            for slotID in range(vehicle.optDevices.layout.getCapacity()):
                self.setItemInCurrentLayout(slotID, None)

            for slotID, optDevice in enumerate(vehicle.optDevices.layout):
                self.setItemInCurrentLayout(slotID, optDevice)

        return

    @wg_async
    def showExitConfirmDialog(self):
        changedList = self.getChangedList()
        result = yield wg_await(showTankSetupExitConfirmDialog(items=changedList, vehicle=self.getItem(), fromSection=self.getName(), startState=BuyAndExchangeStateEnum.BUY_NOT_REQUIRED if not changedList else None))
        raise AsyncReturn(result)
        return

    def updateAmmunitionPanelChangedItems(self):
        setOfPrevLayout = set((item.intCD for item in self.getInstalledLayout() if item is not None))
        vehicle = self.getItem()
        for slotID, item in enumerate(self.getCurrentLayout()):
            if item and item.intCD not in setOfPrevLayout and not self.getInstalledLayout()[slotID]:
                if not self.__canInstall(item, vehicle):
                    self.setItemInCurrentLayout(slotID, None)
                    self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION, slotID=slotID)
                    self.itemUpdated()

        return

    def __canInstall(self, item, vehicle):
        if item.isHidden and not item.isRegular:
            isInInventory = item.isInInventory
            if vehicle.isPostProgressionExists:
                return isInInventory or self.getSetupLayout().getIntCDs().count(item.intCD) > 0
            return isInInventory
        return True
