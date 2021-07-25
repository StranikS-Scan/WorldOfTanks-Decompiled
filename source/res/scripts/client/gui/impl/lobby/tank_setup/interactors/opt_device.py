# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/opt_device.py
import typing
import adisp
from async import async, await, await_callback
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
    from gui.shared.gui_items.Vehicle import Vehicle

class BaseOptDeviceInteractor(BaseInteractor):
    __slots__ = ()

    def getName(self):
        return TankSetupConstants.OPT_DEVICES

    def getInstalledLayout(self):
        return self.getItem().optDevices.installed

    def getCurrentLayout(self):
        return self.getItem().optDevices.layout

    def getCurrentCategories(self, slotID):
        return self.getItem().optDevices.slots[slotID].categories


class OptDeviceInteractor(BaseOptDeviceInteractor):
    __slots__ = ('__previewDevice',)

    def __init__(self, item):
        super(OptDeviceInteractor, self).__init__(item)
        self.__previewDevice = None
        return

    def getVehicleAfterInstall(self):
        vehicle = super(OptDeviceInteractor, self).getVehicleAfterInstall()
        vehicle.optDevices.setInstalled(*self.getItem().optDevices.layout)
        return vehicle

    def getVehiclePreview(self):
        vehicle = super(OptDeviceInteractor, self).getVehicleAfterInstall()
        if self.__previewDevice:
            slotID, item = self.__previewDevice
            layout = vehicle.optDevices.layout
            if item in layout:
                installedSlotID = list(layout).index(item)
                if installedSlotID != slotID:
                    otherItem = layout[slotID]
                    self.setItemInCurrentLayout(installedSlotID, otherItem, vehicle)
            self.setItemInCurrentLayout(slotID, item, vehicle)
        vehicle.optDevices.setInstalled(*vehicle.optDevices.layout)
        return vehicle

    def setItemInCurrentLayout(self, slotID, item, vehicle=None):
        vehicle = vehicle or self.getItem()
        vehicle.optDevices.layout[slotID] = item
        if item is not None:
            vehicle.descriptor.installOptionalDevice(item.intCD, slotID)
        elif vehicle.descriptor.optionalDevices[slotID] is not None:
            vehicle.descriptor.removeOptionalDevice(slotID)
        return

    @adisp.process
    def demountProcess(self, slotID, isDestroy=False, isFitting=False, callback=None):
        action = ActionsFactory.getAction(ActionsFactory.REMOVE_OPT_DEVICE, self.getItem(), self.getInstalledLayout()[slotID], slotID, isDestroy, isFitting)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    def setPreviewSlotItem(self, slotID, itemIntCD):
        item = self._itemsCache.items.getItemByCD(int(itemIntCD)) if itemIntCD is not None else None
        self.__previewDevice = (slotID, item) if item else None
        self.itemPreviewUpdated()
        return

    @async
    def changeSlotItem(self, slotID, itemIntCD):
        item = self._itemsCache.items.getItemByCD(int(itemIntCD)) if itemIntCD is not None else None
        canChange = True
        removedItem = self.getCurrentLayout()[slotID]
        needToRemoveItem = removedItem is not None and removedItem in self.getInstalledLayout()
        if needToRemoveItem:
            canChange = yield await_callback(self.demountProcess)(self.getInstalledLayout().index(removedItem), isFitting=True)
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

    @async
    def demountItem(self, itemIntCD, isDestroy=False):
        result = None
        item = self._itemsCache.items.getItemByCD(itemIntCD)
        currentSlotID = self.getCurrentLayout().index(item)
        installedSlotID = self.getInstalledLayout().index(item)
        if currentSlotID is not None and installedSlotID is not None:
            result = yield await_callback(self.demountProcess)(installedSlotID, isDestroy=isDestroy)
            if result:
                self.setItemInCurrentLayout(currentSlotID, None)
                actionType = BaseSetupModel.DESTROY_SLOT_ACTION if isDestroy else BaseSetupModel.DEMOUNT_SLOT_ACTION
                self.onSlotAction(actionType=actionType, intCD=itemIntCD, slotID=currentSlotID)
                self.itemUpdated()
        raise AsyncReturn(result)
        return

    def revert(self):
        for slotID in xrange(self.getInstalledLayout().getCapacity()):
            self.setItemInCurrentLayout(slotID, None)

        for slotID, optDevice in enumerate(self.getInstalledLayout()):
            self.setItemInCurrentLayout(slotID, optDevice)

        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()
        return

    @adisp.process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_OPT_DEVICES, self.getItem(), confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    @adisp.process
    def upgradeModule(self, itemIntCD, callback):
        optDevice = self._itemsCache.items.getItemByCD(int(itemIntCD))
        slotIdx = self.getInstalledLayout().index(optDevice)
        action = ActionsFactory.getAction(ActionsFactory.UPGRADE_OPT_DEVICE, vehicle=self.getItem(), module=optDevice, slotIdx=slotIdx)
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
        self.getItem().optDevices.setInstalled(*vehicle.optDevices.installed)
        if not onlyInstalled:
            for slotID in xrange(vehicle.optDevices.layout.getCapacity()):
                self.setItemInCurrentLayout(slotID, None)

            for slotID, optDevice in enumerate(vehicle.optDevices.layout):
                self.setItemInCurrentLayout(slotID, optDevice)

        return

    @async
    def showExitConfirmDialog(self):
        result = yield await(showTankSetupExitConfirmDialog(items=self.getChangedList(), vehInvID=self.getItem().invID, fromSection=self.getName(), startState=BuyAndExchangeStateEnum.BUY_NOT_REQUIRED if not self.getChangedList() else None))
        raise AsyncReturn(result)
        return
