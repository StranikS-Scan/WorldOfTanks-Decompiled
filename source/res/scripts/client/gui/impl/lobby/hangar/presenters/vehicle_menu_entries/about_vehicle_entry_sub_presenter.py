# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/about_vehicle_entry_sub_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from gui.shared.event_dispatcher import showVehicleHubOverview

class AboutVehicleEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):

    def onNavigate(self):
        showVehicleHubOverview(g_currentVehicle.item.intCD)

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getEvents(self):
        return ((self._cameraController.onEnabledChange, self.__onCameraEnabledChange),)

    def _getState(self):
        return VehicleMenuModel.DISABLED if g_currentVehicle.item is None or g_currentVehicle.isInBattle() else VehicleMenuModel.ENABLED

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
