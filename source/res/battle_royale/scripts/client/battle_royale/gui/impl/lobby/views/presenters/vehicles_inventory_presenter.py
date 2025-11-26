# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: battle_royale/scripts/client/battle_royale/gui/impl/lobby/views/presenters/vehicles_inventory_presenter.py
from __future__ import absolute_import
import json
import typing
from future.utils import itervalues
from CurrentVehicle import g_currentVehicle
from battle_royale.gui.impl.gen.view_models.views.lobby.views.vehicles_inventory_model import VehiclesInventoryModel
from battle_royale.gui.impl.lobby.tooltips.vehicle_tooltip_view import VehicleTooltipView
from gui.impl.gen import R
from gui.impl.pub.view_component import ViewComponent
from gui.prb_control.ctrl_events import g_prbCtrlEvents
from gui.shared.items_cache import CACHE_SYNC_REASON
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IRentalsController
from skeletons.gui.shared import IItemsCache
if typing.TYPE_CHECKING:
    from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter
    from gui.shared.gui_items.Vehicle import Vehicle
    from gui.shared.utils.requesters import RequestCriteria

class BattleRoyaleVehiclesInventoryPresenter(ViewComponent[VehiclesInventoryModel]):
    __itemsCache = dependency.descriptor(IItemsCache)
    __rentalsCtrl = dependency.descriptor(IRentalsController)
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, vehiclesComponent, vehiclesCriteria):
        super(BattleRoyaleVehiclesInventoryPresenter, self).__init__(model=VehiclesInventoryModel)
        self.__vehiclesComponent = vehiclesComponent
        self.__vehiclesCriteria = vehiclesCriteria

    @property
    def viewModel(self):
        return super(BattleRoyaleVehiclesInventoryPresenter, self).getViewModel()

    def createToolTipContent(self, event, contentID):
        return VehicleTooltipView(int(event.getArgument('intCD'))) if contentID == R.views.battle_royale.mono.lobby.tooltips.vehicle() else super(BattleRoyaleVehiclesInventoryPresenter, self).createToolTipContent(event=event, contentID=contentID)

    def _getEvents(self):
        return ((g_currentVehicle.onChanged, self.__onVehicleChanged),
         (self.__itemsCache.onSyncCompleted, self.__onCacheResync),
         (self.__vehiclesComponent.onDiff, self.__onUpdateVehicles),
         (self.__rentalsCtrl.onRentChangeNotify, self.__onUpdateVehicles),
         (g_prbCtrlEvents.onVehicleClientStateChanged, self.__onVehicleClientStateChanged),
         (self.viewModel.onSelect, self.__onSelectVehicle))

    def _onLoading(self, *args, **kwargs):
        super(BattleRoyaleVehiclesInventoryPresenter, self)._onLoading(*args, **kwargs)
        self.__updateModel()

    def _toModelItem(self, vehicle):
        vState = self.__getVehicleStatus(vehicle)
        return {'id': str(vehicle.intCD),
         'vehicleId': vehicle.intCD,
         'inventoryId': vehicle.invID,
         'nationId': vehicle.nationID,
         'type': vehicle.type,
         'name': vehicle.name,
         'shortName': vehicle.shortUserName,
         'fullName': vehicle.typeDescr.userString,
         'status': vState}

    @staticmethod
    def __getVehicleStatus(vehicle):
        vState, _ = vehicle.getState()
        if vehicle.isRotationApplied():
            if vState in (Vehicle.VEHICLE_STATE.AMMO_NOT_FULL, Vehicle.VEHICLE_STATE.LOCKED):
                vState = Vehicle.VEHICLE_STATE.ROTATION_GROUP_UNLOCKED
        if not vehicle.activeInNationGroup:
            vState = Vehicle.VEHICLE_STATE.NOT_PRESENT
        return vState

    def __onVehicleClientStateChanged(self, vehicles=None):
        if vehicles:
            self.__onUpdateVehicles(vehicles)

    def __onCacheResync(self, reason, diff):
        if reason == CACHE_SYNC_REASON.CLIENT_UPDATE:
            with self.viewModel.transaction() as model:
                self.__setupCurrentVehicle(model)

    def __onVehicleChanged(self):
        if g_currentVehicle.intCD in self.__itemsCache.items.getVehicles(self.__vehiclesCriteria):
            with self.viewModel.transaction() as model:
                self.__setupCurrentVehicle(model)

    def __setItem(self, model, vehicle):
        item = self._toModelItem(vehicle)
        model.getVehicles().set(str(item['id']), json.dumps(item))

    def __setupVehicles(self, model, vehicles):
        for vehicle in itervalues(vehicles):
            self.__setItem(model, vehicle)

    def __onUpdateVehicles(self, diff):
        with self.viewModel.transaction() as model:
            for intCD in diff:
                if intCD in self.__vehiclesComponent.vehicles:
                    self.__setItem(model, self.__vehiclesComponent.vehicles[intCD])
                model.getVehicles().remove(str(intCD))

    def __onSelectVehicle(self, vehId):
        inventoryId = int(vehId['id'])
        g_currentVehicle.selectVehicle(inventoryId)

    def __updateModel(self):
        with self.viewModel.transaction() as model:
            self.__setupVehicles(model, self.__vehiclesComponent.vehicles)
            self.__setupCurrentVehicle(model)

    def __setupCurrentVehicle(self, model):
        if not g_currentVehicle.isPresent():
            g_currentVehicle.selectVehicle()
        if g_currentVehicle.isPresent():
            model.setCurrentVehicleInventoryId(g_currentVehicle.invID)
            model.setCurrentVehicleIntCD(g_currentVehicle.intCD)
        else:
            model.setCurrentVehicleInventoryId(VehiclesInventoryModel.NO_VEHICLE_ID)
            model.setCurrentVehicleIntCD(VehiclesInventoryModel.NO_VEHICLE_ID)
