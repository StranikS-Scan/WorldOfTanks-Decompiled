# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/battle_booster.py
import typing
from adisp import adisp_process
from wg_async import wg_async, await_callback
from gui import shop
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.interactors.base import BaseAutoRenewal
from gui.impl.lobby.tank_setup.interactors.base_equipment import BaseEquipmentInteractor
from gui.shared.gui_items.processors.vehicle import VehicleAutoBattleBoosterEquipProcessor
from gui.shared.utils import decorators
from gui.shared.gui_items.items_actions import factory as ActionsFactory

class BattleBoosterAutoRenewal(BaseAutoRenewal):
    __slots__ = ()

    def getValue(self):
        return self._vehicle.isAutoBattleBoosterEquip()

    @decorators.adisp_process('techMaintenance')
    def changeValue(self, callback):
        value = self.getLocalValue()
        if value != self.getValue():
            yield VehicleAutoBattleBoosterEquipProcessor(self._vehicle, value).request()
            self.setLocalValue(None)
        callback(None)
        return


class BaseBattleBoosterInteractor(BaseEquipmentInteractor):
    __slots__ = ()

    def getName(self):
        return TankSetupConstants.BATTLE_BOOSTERS

    def getInstalledLayout(self):
        return self.getItem().battleBoosters.installed

    def getCurrentLayout(self):
        return self.getItem().battleBoosters.layout

    def getSetupLayout(self):
        return self.getItem().battleBoosters.setupLayouts


class BattleBoosterInteractor(BaseBattleBoosterInteractor):
    __slots__ = ()

    def getVehicleAfterInstall(self):
        vehicle = super(BattleBoosterInteractor, self).getVehicleAfterInstall()
        vehicle.battleBoosters.setInstalled(*self.getItem().battleBoosters.layout)
        vehicle.initCrew()
        return vehicle

    def revert(self):
        self.getItem().battleBoosters.setLayout(*self.getInstalledLayout())
        self.onSlotAction(actionType=BaseSetupModel.REVERT_SLOT_ACTION)
        self.itemUpdated()

    @wg_async
    def applyQuit(self, callback, skipApplyAutoRenewal):
        if not self.isPlayerLayout():
            yield await_callback(self.confirm)(skipDialog=True)
        super(BattleBoosterInteractor, self).applyQuit(callback, skipApplyAutoRenewal)

    @adisp_process
    def confirm(self, callback, skipDialog=False):
        action = ActionsFactory.getAction(ActionsFactory.BUY_AND_INSTALL_BATTLE_BOOSTERS, self.getItem(), confirmOnlyExchange=True, skipConfirm=skipDialog)
        if action is not None:
            result = yield action.doAction()
            callback(result)
        else:
            callback(None)
        return

    def buyMore(self, itemCD):
        if itemCD is not None:
            shop.showBattleBoosterOverlay(itemId=int(itemCD), source=shop.Source.EXTERNAL, origin=shop.Origin.BATTLE_BOOSTERS, alias=VIEW_ALIAS.BROWSER_LOBBY_TOP_SUB)
        return

    def updateFrom(self, vehicle, onlyInstalled=True):
        super(BattleBoosterInteractor, self).updateFrom(vehicle, onlyInstalled)
        items = self.getItem().battleBoosters
        items.setInstalled(*vehicle.battleBoosters.installed)
        items.setupLayouts.setSetups(vehicle.battleBoosters.setupLayouts.setups)
        self._playerLayout = vehicle.battleBoosters.layout.copy()
        if not onlyInstalled:
            self.getItem().battleBoosters.setLayout(*vehicle.battleBoosters.layout)

    def _createAutoRenewal(self):
        return BattleBoosterAutoRenewal(self.getItem())
