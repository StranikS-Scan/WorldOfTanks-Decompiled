# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_configurator_parameters.py
import typing
from gui.Scaleform.daapi.view.lobby.detachment.detachment_setup_vehicle import g_detachmentTankSetupVehicle
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters, VehPreviewParamsDataProvider
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS
if typing.TYPE_CHECKING:
    from gui.shared.gui_items import Vehicle

class VehicleCompareParameters(VehicleParameters):

    def setVehicle(self, value):
        g_detachmentTankSetupVehicle.setCompareVehicle(value)

    def setInitialVehicle(self, value):
        g_detachmentTankSetupVehicle.setVehicle(value)

    def _createDataProvider(self):
        return VehPreviewParamsDataProvider(TOOLTIPS_CONSTANTS.VEHICLE_TANK_SETUP_PARAMETERS)

    def _dispose(self):
        g_detachmentTankSetupVehicle.setVehicle(None)
        super(VehicleCompareParameters, self)._dispose()
        return

    def _getVehicleCache(self):
        return g_detachmentTankSetupVehicle
