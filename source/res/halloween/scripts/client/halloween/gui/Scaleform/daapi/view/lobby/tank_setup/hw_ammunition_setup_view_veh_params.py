# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/halloween/gui/Scaleform/daapi/view/lobby/tank_setup/hw_ammunition_setup_view_veh_params.py
import BigWorld
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import TankSetupParamsDataProvider, VehPreviewParamsDataProvider
from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_vehicle import g_tankSetupVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
from gui.Scaleform.daapi.view.lobby.tank_setup.ammunition_setup_view_veh_params import AmmunitionSetupViewVehicleParams
from gui.prb_control import prbDispatcherProperty
from constants import QUEUE_TYPE, PREBATTLE_TYPE
from gui.shared.items_parameters import params_helper
from gui.shared.items_parameters.comparator import VehiclesComparator
from gui.shared.items_parameters.params_cache import g_paramsCache
from halloween.gui.Scaleform.daapi.view.lobby.hangar.hw_vehicle_params import HWVehicleParams

class HWTankSetupParamsDataProvider(VehPreviewParamsDataProvider):

    def _getComparator(self):
        return self.hwTankSetupVehiclesComparator(self._cache.item, self._cache.defaultItem)

    @staticmethod
    def hwTankSetupVehiclesComparator(comparableVehicle, vehicle):
        hwEqCtrl = BigWorld.player().HWAccountEquipmentController
        comparableVehicle = hwEqCtrl.makeVehicleHWAdapter(comparableVehicle)
        vehicleParams = HWVehicleParams(comparableVehicle)
        idealCrewVehicle = hwEqCtrl.makeVehicleHWAdapter(params_helper._getIdealCrewVehicle(vehicle))
        return VehiclesComparator(vehicleParams.getParamsDict(), HWVehicleParams(idealCrewVehicle).getParamsDict(), suitableArtefacts=g_paramsCache.getCompatibleArtefacts(vehicle), bonuses=vehicleParams.getBonuses(vehicle), penalties=vehicleParams.getPenalties(vehicle))


class HWAmmunitionSetupViewVehicleParams(AmmunitionSetupViewVehicleParams):

    @prbDispatcherProperty
    def prbDispatcher(self):
        return None

    def _createDataProvider(self):
        return HWTankSetupParamsDataProvider(TOOLTIPS_CONSTANTS.VEHICLE_TANK_SETUP_PARAMETERS) if self.prbDispatcher is not None and (self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EVENT_BATTLES) or self.prbDispatcher.getFunctionalState().isInUnit(PREBATTLE_TYPE.EVENT) or self.prbDispatcher.getFunctionalState().isInPreQueue(QUEUE_TYPE.EVENT_BATTLES_2)) else TankSetupParamsDataProvider(TOOLTIPS_CONSTANTS.VEHICLE_TANK_SETUP_PARAMETERS)

    def _getVehicleCache(self):
        return g_tankSetupVehicle
