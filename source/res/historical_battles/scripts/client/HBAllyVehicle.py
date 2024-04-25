# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBAllyVehicle.py
import logging
from HBHangarTankObject import HBHangarTankObject, _VehicleVisualInfo
from historical_battles.diorama_vehicles_config import DioramaVehiclesConfig
_logger = logging.getLogger(__name__)

class _AllyVehicleVisualInfo(_VehicleVisualInfo):
    __slots__ = ('frontId',)

    def __init__(self, frontId, intCD):
        super(_AllyVehicleVisualInfo, self).__init__(intCD)
        self.frontId = frontId

    def __eq__(self, key):
        if key is None:
            return False
        else:
            return False if self.frontId != key.frontId else super(_AllyVehicleVisualInfo, self).__eq__(key)


class HBAllyVehicle(HBHangarTankObject):

    def onEnterWorld(self, prereqs):
        self._gameEventController.onSelectedFrontChanged += self.__onSelectedFrontChanged
        self.__setUpVehicle()

    def onLeaveWorld(self):
        self._gameEventController.onSelectedFrontChanged -= self.__onSelectedFrontChanged

    def _getVehicleIndex(self):
        return self.vehicleIndex

    def _showVehicleMarker(self):
        self._hideVehicleMarker()

    def _getPlayerName(self):
        pass

    def _getClanName(self):
        pass

    def _getRoleId(self):
        return None

    def _isInBattle(self):
        return False

    def __onSelectedFrontChanged(self):
        self.__setUpVehicle()

    def __setUpVehicle(self):
        if self.vehicleIndex <= 0:
            _logger.error('The vehicle index %d is incorrect', self.vehicleIndex)
            return
        else:
            vehicleData = DioramaVehiclesConfig.getSelectedFrontLayoutVehicle(self.vehicleIndex)
            if vehicleData is None:
                return
            frontId = self._gameEventController.frontController.getSelectedFrontID()
            visualInfo = _AllyVehicleVisualInfo(frontId, vehicleData.intCD)
            if visualInfo != self._visualInfo:
                self._loadTank(visualInfo)
            else:
                self._reloadEffects()
            return
