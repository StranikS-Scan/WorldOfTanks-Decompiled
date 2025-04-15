# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/client/HBTeamInfoComponent.py
import logging
import Event
from script_component.DynamicScriptComponent import DynamicScriptComponent
_logger = logging.getLogger(__name__)

class HBTeamInfoComponent(DynamicScriptComponent):
    onAllyInfoUpdated = Event.Event()

    def set_alliesInfo(self, _):
        self.onAllyInfoUpdated()

    def getDivisionLevel(self, vehicleID):
        allyInfo = self.__getAllyInfo(vehicleID)
        return allyInfo.divisionLevel if allyInfo else 1

    def getAliveVehicleCount(self, vehicleID):
        allyInfo = self.__getAllyInfo(vehicleID)
        return allyInfo.vehicleCount if allyInfo else 0

    def getRespawnTime(self, vehicleID):
        allyInfo = self.__getAllyInfo(vehicleID)
        return allyInfo.respawnTime if allyInfo else 0.0

    def __getAllyInfo(self, vehicleID):
        allyInfo = next((info for info in self.alliesInfo if info.vehicleID == vehicleID), None)
        if not allyInfo:
            _logger.error('There is no info for vehicle %d', vehicleID)
        return allyInfo
