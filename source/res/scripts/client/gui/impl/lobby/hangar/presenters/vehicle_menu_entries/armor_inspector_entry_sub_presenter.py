# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/armor_inspector_entry_sub_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from PlayerEvents import g_playerEvents
from armor_inspector_common.schemas import armorInspectorConfigSchema
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import EVENT_BUS_SCOPE, events
from gui.shared.event_dispatcher import showVehicleHubArmor

class ArmorInspectorEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):

    def onNavigate(self):
        showVehicleHubArmor(g_currentVehicle.item.intCD)

    def _getEvents(self):
        return ((g_playerEvents.onConfigModelUpdated, self.__configChangeHandler), (self._cameraController.onEnabledChange, self.__onCameraEnabledChange))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getState(self):
        vehicle = g_currentVehicle.item
        configModel = armorInspectorConfigSchema.getModel()
        return VehicleMenuModel.DISABLED if vehicle is None or not configModel.enabled or configModel.isDisabledForVehicle(vehicle.name) or g_currentVehicle.isInBattle() else VehicleMenuModel.ENABLED

    def __configChangeHandler(self, gpKey):
        if gpKey == armorInspectorConfigSchema.gpKey:
            self.packEntry()

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
