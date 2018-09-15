# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/vehicle_compare/cmp_configurator_parameters.py
from gui.Scaleform.daapi.view.lobby.hangar.VehicleParameters import VehicleParameters, VehPreviewParamsDataProvider
from gui.Scaleform.genConsts.TOOLTIPS_CONSTANTS import TOOLTIPS_CONSTANTS

class _CmpCacheWrapper(object):

    def __init__(self):
        super(_CmpCacheWrapper, self).__init__()
        self.__vehicle = None
        self.__defaultVehicle = None
        return

    def setVehicle(self, value):
        self.__vehicle = value

    def setDefaultVehicle(self, value):
        self.__defaultVehicle = value

    @property
    def item(self):
        return self.__vehicle

    @property
    def defaultItem(self):
        return self.__defaultVehicle

    def isPresent(self):
        return self.__vehicle is not None

    def dispose(self):
        self.__vehicle = None
        self.__defaultVehicle = None
        return


class VehicleCompareParameters(VehicleParameters):

    def __init__(self):
        self.__vehWrapper = _CmpCacheWrapper()
        super(VehicleCompareParameters, self).__init__()

    def init(self, vehicle, initialVehicle=None):
        self.__vehWrapper.setVehicle(vehicle)
        if initialVehicle:
            self.__vehWrapper.setDefaultVehicle(initialVehicle)
        self.update()

    def getVehicle(self):
        return self.__vehWrapper.item

    def _createDataProvider(self):
        return VehPreviewParamsDataProvider(TOOLTIPS_CONSTANTS.VEHICLE_CMP_PARAMETERS)

    def _dispose(self):
        self.__vehWrapper.dispose()
        self.__vehWrapper = None
        super(VehicleCompareParameters, self)._dispose()
        return

    def _getVehicleCache(self):
        return self.__vehWrapper
