# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/detachment/detachment_view_veh_params.py
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters, VehPreviewParamsDataProvider
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

class DetachmentViewVehicleParams(VehicleParameters):

    def _createDataProvider(self):
        return VehPreviewParamsDataProvider(TOOLTIPS_CONSTANTS.VEHICLE_TANK_SETUP_PARAMETERS)

    def _getVehicleCache(self):
        return g_detachmentTankSetupVehicle
