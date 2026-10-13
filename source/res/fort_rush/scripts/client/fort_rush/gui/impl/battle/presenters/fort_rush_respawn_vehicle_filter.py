# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fort_rush/scripts/client/fort_rush/gui/impl/battle/presenters/fort_rush_respawn_vehicle_filter.py
from __future__ import absolute_import
from future.utils import viewitems
from typing import TYPE_CHECKING, Dict
import BigWorld
import Event
from fort_rush.skeletons.battle_controller import IFortRushBattleController
from fort_rush_common.component_helpers import getVehicleRespawnComponent
from gui.battle_control import avatar_getter
from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from gui.shared.gui_items.fitting_item import RentalInfoProvider
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency, time_utils
from skeletons.gui.shared.gui_items import IGuiItemsFactory
from event_platform.gui.shared.events import RespawnFrameworkEvent
if TYPE_CHECKING:
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.utils.requesters import RequestCriteria

class FortRushRespawnVehicleFilter(IVehicleFilter):
    __slots__ = ('__criteria',)
    _itemsFactory = dependency.descriptor(IGuiItemsFactory)
    _fortRushCtrl = dependency.descriptor(IFortRushBattleController)

    def __init__(self):
        self.onDiff = Event.Event()
        self._vehicles = {}
        self.__criteria = None
        return

    @property
    def criteria(self):
        return self.__criteria

    @property
    def vehicles(self):
        return self._vehicles

    def initialize(self):
        self.__criteria = self._buildCriteria()
        g_eventBus.addListener(RespawnFrameworkEvent.VEHICLES_LOADED, self._onVehiclesLoaded, EVENT_BUS_SCOPE.BATTLE)

    def _buildCriteria(self):
        return REQ_CRITERIA.CUSTOM(lambda v: self._fortRushCtrl.isSuitableVehicle(v) is None)

    def destroy(self):
        g_eventBus.removeListener(RespawnFrameworkEvent.VEHICLES_LOADED, self._onVehiclesLoaded, EVENT_BUS_SCOPE.BATTLE)
        self.onDiff.clear()
        self._vehicles = None
        self.__criteria = None
        return

    def _onVehiclesLoaded(self, _):
        vehicle = BigWorld.entities.get(avatar_getter.getPlayerVehicleID())
        if vehicle is None:
            return
        else:
            respawnComponent = getVehicleRespawnComponent(vehicle)
            if respawnComponent is None or not respawnComponent.respawnVehicles:
                return
            self._vehicles = {}
            for vehicleCD, vehData in viewitems(respawnComponent.respawnVehicles):
                invData = {'settings': vehData.get('settings', 0)}
                vehicleItem = self._itemsFactory.createVehicle(typeCompDescr=vehicleCD, invData=invData)
                vehicleItem._isElite = vehData.get('isElite', False)
                isRent = vehData.get('isRent', False)
                if isRent:
                    vehicleItem._rentInfo = RentalInfoProvider(isRented=isRent, time=time_utils.getCurrentLocalServerTimestamp() + 6400, battles=99, wins=99)
                else:
                    vehicleItem._rentInfo = RentalInfoProvider(isRented=isRent)
                self._vehicles[vehicleCD] = vehicleItem

            self.onDiff(self._vehicles)
            return
