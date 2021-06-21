# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/shell.py
from itertools import izip
import adisp
from async import await, async, await_callback
from BWUtil import AsyncReturn
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.dialogs.auxiliary.buy_and_exchange_state_machine import BuyAndExchangeStateEnum
from gui.impl.lobby.tank_setup.interactors.base import BaseInteractor, BaseAutoRenewal
from gui.shared.event_dispatcher import showExitFromShellsDialog
from gui.shared.gui_items.gui_item_economics import getVehicleShellsLayoutPrice
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.gui_items.processors.vehicle import VehicleAutoLoadProcessor
from gui.shared.money import ZERO_MONEY
from gui.shared.utils import decorators

def _hasChanged(leftLayout, rightLayout):
    for leftShell, rightShell in izip(leftLayout, rightLayout):
        if leftShell.intCD != rightShell.intCD or leftShell.count != rightShell.count:
            return True

    return False


class ShellAutoRenewal(BaseAutoRenewal):

    def getValue(self):
        return self._vehicle.isAutoLoad

    @decorators.process('techMaintenance')
    def changeValue(self, callback):
        value = self.getLocalValue()
        if value != self.getValue():
            yield VehicleAutoLoadProcessor(self._vehicle, value).request()
            self.setLocalValue(None)
        callback(None)
        return


class ShellInteractor(BaseInteractor):
    __slots__ = ('_playerLayout',)

    def getVehicleAfterInstall(self):
        vehicle = super(ShellInteractor, self).getVehicleAfterInstall()
        vehicle.shells.setInstalled(*self.getItem().shells.layout)
        return vehicle

    def getName(self):
        return TankSetupConstants.SHELLS

    def setItem(self, item):
        super(ShellInteractor, self).setItem(item)
        self._resetPlayerLayout()

    def getInstalledLayout(self):
        return self.getItem().shells.installed

    def getCurrentLayout(self):
        return self.getItem().shells.layout

    def getSetupLayout(self):
        return self.getItem().shells.setupLayouts

    def getPlayerLayout(self):
        return self._playerLayout

    def hasChanged(self):
        return _hasChanged(self.getInstalledLayout(), self.getCurrentLayout())

    def isPlayerLayout(self):
        return not _hasChanged(self.getPlayerLayout(), self.getCurrentLayout())

    @async
    def applyQuit(self, callback, skipApplyAutoRenewal):
        if not self.isPlayerLayout():
            yield await_callback(self.confirm)(skipDialog=True)
        super(ShellInteractor, self).applyQuit(callback, skipApplyAutoRenewal)

    def getCurrentShellSlotID(self, intCD):
        changedSlotID = None
        for slotID, shell in enumerate(self.getCurrentLayout()):
            if shell.intCD == intCD:
                changedSlotID = slotID
                break

        return changedSlotID

    def getChangedList(self):
        result = []
        for installedShell in self.getInstalledLayout():
            for currentShell in self.getCurrentLayout():
                if installedShell.intCD == currentShell.intCD and installedShell.count != currentShell.count:
                    result.append((installedShell.intCD, installedShell.count, currentShell.count))

        return result

    def swapSlots(self, leftID, rightID, actionType=BaseSetupModel.SWAP_SLOTS_ACTION):
        shellLayout = self.getCurrentLayout()
        shellLayout[rightID], shellLayout[leftID] = shellLayout[leftID], shellLayout[rightID]
        self.onSlotAction(actionType=actionType, leftID=leftID, rightID=rightID, leftIntCD=shellLayout[leftID].intCD, rightIntCD=shellLayout[rightID].intCD)
        self.itemUpdated()

    def changeShell(self, intCD, count):
        changedSlotID = self.getCurrentShellSlotID(intCD)
        if changedSlotID is not None:
            shell = self.getCurrentLayout()[changedSlotID]
            shell.count = count
            self.getCurrentLayout()[changedSlotID] = shell
            self.itemUpdated()
        return

    def revert(self):
        self.getItem().shells.setLayout(*self.getInstalledLayout())
        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()

    @adisp.process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_SHELLS, self.getItem(), confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    def _resetPlayerLayout(self):
        self._playerLayout = self.getCurrentLayout().copy()

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(ShellInteractor, self).updateFrom(vehicle, onlyInstalled)
        items = self.getItem().shells
        items.setInstalled(*vehicle.shells.installed)
        items.setupLayouts.setSetups(vehicle.shells.setupLayouts.setups)
        self._playerLayout = vehicle.shells.layout.copy()
        if not onlyInstalled:
            self.getItem().shells.setLayout(*vehicle.shells.layout)

    @async
    def showExitConfirmDialog(self):
        price = getVehicleShellsLayoutPrice(self.getItem())
        result = yield await(showExitFromShellsDialog(price=price, shells=self.getCurrentLayout().getItems(), startState=BuyAndExchangeStateEnum.BUY_NOT_REQUIRED if price.price == ZERO_MONEY else None))
        raise AsyncReturn(result)
        return

    def _createAutoRenewal(self):
        return ShellAutoRenewal(self.getItem())
