# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/hangar/presenters/vehicles_info_presenter.py
from __future__ import absolute_import
import json
import math
import typing
from future.utils import itervalues
from gui.game_control.veh_comparison_basket import isValidVehicleForComparing
from gui.impl.gen.view_models.views.lobby.hangar.sub_views.vehicles_info_model import VehiclesInfoModel
from gui.impl.pub.view_component import ViewComponent
from helpers import dependency
from skeletons.gui.customization import ICustomizationService
from skeletons.gui.game_control import IRentalsController
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle
    from gui.impl.lobby.hangar.base.hangar_interfaces import IVehicleFilter

class VehiclesInfoPresenter(ViewComponent[VehiclesInfoModel]):
    __service = dependency.descriptor(ICustomizationService)
    __rentalsCtrl = dependency.descriptor(IRentalsController)
    __customizationService = dependency.descriptor(ICustomizationService)

    def __init__(self, vehiclesComponent):
        super(VehiclesInfoPresenter, self).__init__(model=VehiclesInfoModel)
        self._vehiclesComponent = vehiclesComponent

    @property
    def viewModel(self):
        return super(VehiclesInfoPresenter, self).getViewModel()

    def _getEvents(self):
        return ((self._vehiclesComponent.onDiff, self.__onUpdateVehicles), (self.__rentalsCtrl.onRentChangeNotify, self.__onUpdateVehicles))

    def _onLoading(self, *args, **kwargs):
        super(VehiclesInfoPresenter, self)._onLoading(*args, **kwargs)
        self.__vehiclesWithAttachments = set(self.__customizationService.getVehiclesWithAttachmentSlot())
        self.__fillVehicles()

    def __fillVehicles(self):
        self.__setupVehicles(self._vehiclesComponent.vehicles)

    def _toModelItem(self, vehicle):
        return {'id': str(vehicle.intCD),
         'vehicleId': vehicle.intCD,
         'inventoryId': vehicle.invID,
         'level': vehicle.level,
         'type': vehicle.type,
         'premium': vehicle.isPremium,
         'name': vehicle.name,
         'fullName': vehicle.typeDescr.userString,
         'shortName': vehicle.shortUserName,
         'nationId': vehicle.nationID,
         'role': vehicle.role,
         'nationChangeAvailable': vehicle.isNationChangeAvailable,
         'favorite': vehicle.isFavorite,
         'crystalEarning': vehicle.isEarnCrystals,
         'comparable': isValidVehicleForComparing(vehicle),
         'canInstallAttachments': vehicle in self.__vehiclesWithAttachments and not vehicle.isOutfitLocked and not vehicle.isProgressionDecalsOnly,
         'rent': {'isRented': vehicle.isRented,
                  'leftTime': vehicle.rentLeftTime if not math.isinf(vehicle.rentLeftTime) else -1,
                  'leftBattles': vehicle.rentLeftBattles or 0,
                  'leftWins': vehicle.rentLeftWins or 0}}

    def __setItem(self, model, vehicle):
        item = self._toModelItem(vehicle)
        model.getVehicles().set(str(item['id']), json.dumps(item))

    def __setupVehicles(self, vehicles):
        with self.viewModel.transaction() as model:
            for vehicle in itervalues(vehicles):
                self.__setItem(model, vehicle)

    def __onUpdateVehicles(self, diff):
        with self.viewModel.transaction() as model:
            for intCD in diff:
                if intCD in self._vehiclesComponent.vehicles:
                    self.__setItem(model, self._vehiclesComponent.vehicles[intCD])
                model.getVehicles().remove(str(intCD))
