# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/consumable.py
import typing
from wg_async import wg_async, await_callback
from gui import shop
from adisp import adisp_process
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.interactors.base import BaseAutoRenewal
from gui.impl.lobby.tank_setup.interactors.base_equipment import BaseEquipmentInteractor
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from gui.shared.gui_items.processors.vehicle import VehicleAutoEquipProcessor
from gui.shared.utils import decorators

class ConsumableAutoRenewal(BaseAutoRenewal):

    def getValue(self):
        return self._vehicle.isAutoEquip

    @decorators.adisp_process('techMaintenance')
    def processVehicleAutoRenewal(self, callback):
        yield VehicleAutoEquipProcessor(self._vehicle, self.getLocalValue()).request()
        self.setLocalValue(None)
        callback(None)
        return


class BaseConsumableInteractor(BaseEquipmentInteractor):
    __slots__ = ()

    def getName(self):
        return TankSetupConstants.CONSUMABLES

    def getInstalledLayout(self):
        return self.getItem().consumables.installed

    def getCurrentLayout(self):
        return self.getItem().consumables.layout

    def getSetupLayout(self):
        return self.getItem().consumables.setupLayouts


class ConsumableInteractor(BaseConsumableInteractor):
    __slots__ = ('__installedIndices',)

    def getVehicleAfterInstall(self):
        vehicle = super(ConsumableInteractor, self).getVehicleAfterInstall()
        layout = self.getItem().consumables.layout
        vehicle.consumables.setInstalled(*layout)
        vehicle.initCrew()
        return vehicle

    def revert(self):
        self.getItem().consumables.setLayout(*self.getInstalledLayout())
        self._resetInstalledIndices()
        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()

    @wg_async
    def applyQuit(self, callback, skipApplyAutoRenewal):
        if not self.isPlayerLayout():
            yield await_callback(self.confirm)(skipDialog=True)
        super(ConsumableInteractor, self).applyQuit(callback, skipApplyAutoRenewal)

    @adisp_process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_CONSUMABLES, self.getItem(), confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    def buyMore(self, itemCD):
        if itemCD is not None:
            shop.showBuyEquipmentOverlay(itemId=int(itemCD), source=shop.Source.EXTERNAL, origin=shop.Origin.CONSUMABLES, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)
        return

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(ConsumableInteractor, self).updateFrom(vehicle, onlyInstalled)
        items = self.getItem().consumables
        items.setInstalled(*vehicle.consumables.installed)
        items.setupLayouts.setSetups(vehicle.consumables.setupLayouts.setups)
        self._playerLayout = vehicle.consumables.layout.copy()
        if not onlyInstalled:
            self.getItem().consumables.setLayout(*vehicle.consumables.layout)

    def _createAutoRenewal(self):
        return ConsumableAutoRenewal(self.getItem())
