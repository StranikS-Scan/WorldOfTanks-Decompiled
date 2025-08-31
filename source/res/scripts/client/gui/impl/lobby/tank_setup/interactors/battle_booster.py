# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/tank_setup/interactors/battle_booster.py
import typing
from adisp import adisp_process
from th_async import th_async, await_callback
from gui import shop
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.impl.gen.view_models.views.lobby.tank_setup.sub_views.base_setup_model import BaseSetupModel
from gui.impl.gen.view_models.views.lobby.tank_setup.tank_setup_constants import TankSetupConstants
from gui.impl.lobby.tank_setup.interactors.base import BaseAutoRenewal
from gui.impl.lobby.tank_setup.interactors.base_equipment import BaseEquipmentInteractor
from gui.shared.gui_items.processors.vehicle import VehicleAutoBattleBoosterEquipProcessor
from gui.shared.utils import decorators
from gui.shared.gui_items.items_actions import factory as ActionsFactory
from AccountCommands import VEHICLE_SETTINGS_FLAG
from gui.impl.gen.view_models.views.lobby.tank_setup.common.deal_panel_model import AutoRenewalType
_VEHICLE_EQUIP_SETTING = {VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER_SOFT | VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER: AutoRenewalType.SOFT,
 VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER: AutoRenewalType.HARD}
_NAME_TO_SETTING = {AutoRenewalType.SOFT: VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER_SOFT | VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER,
 AutoRenewalType.HARD: VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER}

class BattleBoosterAutoRenewal(BaseAutoRenewal):
    __slots__ = ()

    def setLocalTypeEquip(self, typeEquip):
        self._typeEquip = typeEquip

    def getLocalTypeEquip(self):
        return self.getTypeEquip() if self._typeEquip is None else self._typeEquip

    def getTypeEquip(self):
        return _VEHICLE_EQUIP_SETTING.get(self._vehicle.settings & (VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER | VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER_SOFT), AutoRenewalType.SOFT)

    def getValue(self):
        return self._vehicle.isAutoBattleBoosterEquip()

    @decorators.adisp_process('techMaintenance')
    def changeValue(self, callback):
        value = self.getLocalValue()
        typeEquip = self.getLocalTypeEquip()
        if value != self.getValue():
            if not value:
                yield VehicleAutoBattleBoosterEquipProcessor(self._vehicle, value, settings=VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER_SOFT | VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER).request()
            else:
                yield VehicleAutoBattleBoosterEquipProcessor(self._vehicle, value, settings=_NAME_TO_SETTING[typeEquip]).request()
            self.setLocalValue(None)
            self.setLocalTypeEquip(None)
        elif typeEquip != self.getTypeEquip() and typeEquip != AutoRenewalType.UNDEFINED:
            flag = bool(self._vehicle.settings & VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER_SOFT)
            yield VehicleAutoBattleBoosterEquipProcessor(self._vehicle, not flag, settings=VEHICLE_SETTINGS_FLAG.AUTO_EQUIP_BOOSTER_SOFT).request()
            self.setLocalValue(None)
            self.setLocalTypeEquip(None)
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

    @th_async
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
