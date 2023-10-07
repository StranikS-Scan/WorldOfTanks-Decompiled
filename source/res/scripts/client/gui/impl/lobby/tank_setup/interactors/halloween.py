# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/halloween.py
import typing
import BigWorld
from helpers import dependency
from wg_async import wg_async, wg_await, await_callback
import adisp
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.interactors.base import BaseAutoRenewal
from gui.impl.lobby.tank_setup.interactors.base import BaseInteractor
from gui.shared.utils import decorators
from BWUtil import AsyncReturn
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.tank_setup.tank_setup_helper import NONE_ID
from gui.shared.event_dispatcher import showHWTankSetupExitConfirmDialog
from gui.shared.gui_items.items_actions.actions import AmmunitionBuyAndInstall
from gui.shared.gui_items.processors.messages.items_processor_messages import ItemBuyProcessorMessage, ConsumablesApplyProcessorMessage
from gui.shared.gui_items.processors import Processor, plugins as proc_plugs, makeSuccess
from gui.shared.money import Money
from gui.shared.gui_items.gui_item_economics import ITEM_PRICE_ZERO
from gui.impl.dialogs.dialogs import SingleDialogResult
from gui.impl.pub.dialog_window import DialogResult
from skeletons.gui.game_control import IHalloweenController

def getVehicleHWConsumablesLayoutPrice(vehicle):
    result = sum([ item.getBuyPrice() for item in vehicle.hwConsumables.layout.getItems() if not item.isInInventory and item not in vehicle.hwConsumables.installed ], ITEM_PRICE_ZERO)
    return result


class HWConsumablesInstallValidator(proc_plugs.ConsumablesInstallValidator):

    def _getLayout(self):
        return self._vehicle.hwConsumables.layout

    def _getInstalled(self):
        return self._vehicle.hwConsumables.installed


class HWBuyAndInstallConsumablesProcessor(Processor):

    def __init__(self, vehicle):
        super(HWBuyAndInstallConsumablesProcessor, self).__init__()
        self._vehicle = vehicle
        self._setupPlugins()

    def _setupPlugins(self):
        self.addPlugins((proc_plugs.VehicleValidator(self._vehicle), proc_plugs.MoneyValidator(getVehicleHWConsumablesLayoutPrice(self._vehicle).price, byCurrencyError=False), HWConsumablesInstallValidator(self._vehicle)))

    def _request(self, callback):
        eqCtrl = BigWorld.player().HWAccountEquipmentController
        eqCtrl.updateSelectedEquipment(self._vehicle.invID, self.__getLayoutRaw(), lambda _, code, errStr, ext={}: self._response(code, callback, errStr=errStr, ctx=ext))

    def _successHandler(self, code, ctx=None):
        additionalMessages = []
        if ctx:
            additionalMessages = [ ItemBuyProcessorMessage(self.itemsCache.items.getItemByCD(cd), count, Money.makeFromMoneyTuple(price)).makeSuccessMsg() for cd, price, count in ctx.get('eqs', []) ]
        return makeSuccess(auxData=additionalMessages)

    def _errorHandler(self, code, errStr='', ctx=None):
        return ConsumablesApplyProcessorMessage(self._vehicle).makeErrorMsg(errStr)

    def __getLayoutRaw(self):
        return [ (item.intCD if item is not None else 0) for item in self._vehicle.hwConsumables.layout ]


class HWBuyAndInstallConsumables(AmmunitionBuyAndInstall):
    __slots__ = ()

    def __init__(self, vehicle, confirmOnlyExchange=False, skipConfirm=False):
        changeItems = [ item for item in vehicle.hwConsumables.layout.getItems() if item not in vehicle.hwConsumables.installed ]
        super(HWBuyAndInstallConsumables, self).__init__(vehicle, changeItems, confirmOnlyExchange)
        self.skipConfirm = skipConfirm

    @adisp.adisp_async
    @decorators.adisp_process('techMaintenance')
    def _action(self, callback):
        result = yield HWBuyAndInstallConsumablesProcessor(self._vehicle).request()
        callback(result)


class HWVehicleAutoEquipProcessor(Processor):

    def __init__(self, vehicle, value):
        super(HWVehicleAutoEquipProcessor, self).__init__()
        self._value = value
        self._vehicle = vehicle

    def _request(self, callback):
        eqCtrl = BigWorld.player().HWAccountEquipmentController
        eqCtrl.setHwAutoMaintenanceEnabled(self._vehicle.invID, self._value, lambda requestID, code, errStr: self._response(code, callback, errStr=errStr))


class HWConsumableAutoRenewal(BaseAutoRenewal):

    def getValue(self):
        return self._vehicle.hwConsumables.isAutoEquip

    @decorators.adisp_process('techMaintenance')
    def changeValue(self, callback):
        value = self.getLocalValue()
        if value != self.getValue():
            result = yield HWVehicleAutoEquipProcessor(self._vehicle, value).request()
            if result.success:
                self._vehicle.hwConsumables.isAutoEquip = value
            self.setLocalValue(None)
        callback(None)
        return


class HalloweenInteractor(BaseInteractor):
    __slots__ = ('_installedIndices', '_playerLayout')

    @property
    def hwEqCtrl(self):
        return BigWorld.player().HWAccountEquipmentController

    def getName(self):
        return TankSetupConstants.HWCONSUMABLES

    def setItem(self, item):
        super(HalloweenInteractor, self).setItem(item)
        self._resetPlayerLayout()
        self._resetInstalledIndices()

    def getPlayerLayout(self):
        return self._playerLayout

    def getInstalledLayout(self):
        return self.getItem().hwConsumables.installed

    def getCurrentLayout(self):
        return self.getItem().hwConsumables.layout

    def getSetupLayout(self):
        return self.getItem().consumables.setupLayouts

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

    def getVehicleAfterInstall(self):
        vehicle = super(HalloweenInteractor, self).getVehicleAfterInstall()
        vehicle.consumables.setInstalled(*self.getItem().consumables.layout)
        hwVehicle = self.hwEqCtrl.makeVehicleHWAdapter(vehicle)
        hwVehicle.hwConsumables.installed = self.getItem().hwConsumables.layout.copy()
        return hwVehicle

    def revert(self):
        self.getItem().hwConsumables.layout = self.getInstalledLayout().copy()
        self._resetInstalledIndices()
        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(HalloweenInteractor, self).updateFrom(vehicle, onlyInstalled)
        hwVehicle = self.hwEqCtrl.makeVehicleHWAdapter(vehicle)
        self.getItem().hwConsumables.installed = hwVehicle.hwConsumables.installed.copy()
        self.getItem().hwConsumables.isAutoEquip = hwVehicle.hwConsumables.isAutoEquip
        self._playerLayout = hwVehicle.hwConsumables.layout.copy()
        if not onlyInstalled:
            self.getItem().hwConsumables.layout = hwVehicle.hwConsumables.layout.copy()

    @wg_async
    def showExitConfirmDialog(self):
        controller = dependency.instance(IHalloweenController)
        if not controller.isEnabled() or not controller or controller.isPostPhase():
            raise AsyncReturn(SingleDialogResult(busy=False, result=DialogResult(False, {'rollBack': True})))
        result = yield wg_await(showHWTankSetupExitConfirmDialog(items=self.getChangedList(), vehicle=self.getItem(), fromSection=self.getName(), startState=BuyAndExchangeStateEnum.BUY_NOT_REQUIRED if not self.getChangedList() else None))
        raise AsyncReturn(result)
        return

    @wg_async
    def applyQuit(self, callback, skipApplyAutoRenewal):
        if not self.isPlayerLayout():
            yield await_callback(self.confirm)(skipDialog=True)
        super(HalloweenInteractor, self).applyQuit(callback, skipApplyAutoRenewal)

    @adisp.adisp_process
    def confirm(self, callback, skipDialog=False):
        action = HWBuyAndInstallConsumables(self.getItem(), confirmOnlyExchange=True)
        action.skipConfirm = skipDialog
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    def buyMore(self, itemCD):
        eqCtrl = BigWorld.player().HWAccountEquipmentController
        eqCtrl.buyMore(itemCD)

    def _createAutoRenewal(self):
        return HWConsumableAutoRenewal(self.getItem())

    def _resetInstalledIndices(self):
        self._installedIndices = [ i for i in range(len(self.getInstalledLayout())) ]

    def _resetPlayerLayout(self):
        self._playerLayout = self.getCurrentLayout().copy()
