# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicle_menu_entries/compare_entry_sub_presenter.py
from __future__ import absolute_import
from CurrentVehicle import g_currentVehicle
from gui.impl.gen.view_models.views.lobby.hangar.vehicle_menu_model import VehicleMenuModel
from gui.impl.lobby.hangar.presenters.vehicle_menu_entries.base_menu_entry_sub_presenter import BaseMenuEntrySubPresenter
from gui.prb_control.entities.base.listener import IPrbListener
from gui.shared import events, EVENT_BUS_SCOPE
from helpers import dependency
from skeletons.gui.game_control import IVehicleComparisonBasket

class CompareEntrySubPresenter(BaseMenuEntrySubPresenter, IPrbListener):
    __cmpBasket = dependency.descriptor(IVehicleComparisonBasket)

    def onNavigate(self):
        self.__handleCompare()

    def _getEvents(self):
        return ((self.__cmpBasket.onChange, self.__onCmpBasketChange), (self.__cmpBasket.onSwitchChange, self.__onVehCmpBasketStateChanged), (self._cameraController.onEnabledChange, self.__onCameraEnabledChange))

    def _getListeners(self):
        return ((events.PrebattleEvent.SWITCHED, self.__onPrbEntitySwitched, EVENT_BUS_SCOPE.LOBBY),)

    def _getState(self):
        cmpBasket = self.__cmpBasket
        readyToAdd = cmpBasket.isReadyToAdd(g_currentVehicle.item)
        return VehicleMenuModel.DISABLED if not cmpBasket.isEnabled() or not readyToAdd or g_currentVehicle.isInBattle() else VehicleMenuModel.ENABLED

    def __handleCompare(self):
        self.__cmpBasket.addVehicle(g_currentVehicle.item.intCD)
        if self.__cmpBasket.isFull():
            self.packEntry()

    def __onCmpBasketChange(self, *_):
        self.packEntry()

    def __onVehCmpBasketStateChanged(self):
        self.packEntry()

    def __onPrbEntitySwitched(self, _):
        self.packEntry()

    def __onCameraEnabledChange(self, _):
        self.packEntry()
