# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/easy_equip_entry_sub_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui.easy_tank_equip.easy_tank_equip_helpers import isAvailableForVehicle
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries import isVehicleUnavailable
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showEasyTankEquipScreen
from helpers import dependency
from skeletons.gui.game_control import IEasyTankEquipController, IPlatoonController
NOT_FULL_QS_AMMO_MULTILIER = 0.8

class EasyEquipEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):
    __easyTankEquipCtrl = dependency.descriptor(IEasyTankEquipController)
    __platoonCtrl = dependency.descriptor(IPlatoonController)

    def onNavigate(self):
        showEasyTankEquipScreen()

    def _getEvents(self):
        return ((self.__easyTankEquipCtrl.onUpdated, self.__onSettingsChange), (self.__platoonCtrl.onMembersUpdate, self.__onPlatoonMembersUpdate), (self._cameraController.onEnabledChange, self.__onCameraEnabledChange))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getState(self):
        if not self.__easyTankEquipCtrl.config.enabled:
            return VehicleMenuModel.UNAVAILABLE
        if not g_currentVehicle.isPresent() or isVehicleUnavailable() or g_currentVehicle.item.isOnlyForEventBattles or g_currentVehicle.isUnsuitableToQueue():
            return VehicleMenuModel.DISABLED
        if g_currentVehicle.isPresent() and isAvailableForVehicle(g_currentVehicle.item):
            isHighlight = not g_currentVehicle.item.isCrewFull or not self.__isAmmoNotFull() or not g_currentVehicle.item.consumables.installed.getItems()
            if isHighlight:
                return VehicleMenuModel.WARNING
            return VehicleMenuModel.ENABLED
        return VehicleMenuModel.DISABLED

    @staticmethod
    def __isAmmoNotFull():
        vehicle = g_currentVehicle.item
        return sum((itemData[1] for itemData in vehicle.shells.installed.getStorage if itemData)) >= vehicle.ammoMaxSize * NOT_FULL_QS_AMMO_MULTILIER or vehicle.isOnlyForBattleRoyaleBattles

    def __onSettingsChange(self):
        self.packEntry()

    def __onPlatoonMembersUpdate(self, *_):
        self.packEntry()

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
