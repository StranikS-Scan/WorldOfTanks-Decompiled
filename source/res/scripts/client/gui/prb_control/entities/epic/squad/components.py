# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/epic/squad/components.py
from constants import VEHICLE_CLASS_INDICES
from gui.prb_control.entities.base.squad.components import RestrictedVehicleTagDataProvider
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from items import vehicles
from helpers import dependency
from items.vehicles import VEHICLE_TAGS
from skeletons.gui.lobby_context import ILobbyContext

class RestrictedSPGDataProvider(RestrictedVehicleTagDataProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _VEHICLE_TAG = VEHICLE_CLASS_NAME.SPG

    def getCurrentVehiclesCount(self):
        enableSPGCount = 0
        unitMgrId, unit = (0, None) if self._unitEntity is None else self._unitEntity.getUnit(safe=True)
        if unit is None:
            return enableSPGCount
        else:
            enableSPGCount = sum((slot.vehicle is not None and slot.vehicle.vehClassIdx == VEHICLE_CLASS_INDICES['SPG'] for slot in self._unitEntity.getSlotsIterator(unitMgrId, unit)))
            return enableSPGCount

    def getRestrictionLevels(self):
        return None

    def getMaxPossibleVehicles(self):
        return self.__lobbyContext.getServerSettings().getMaxSPGinSquads()


class RestrictedFlamethrowerDataProvider(RestrictedVehicleTagDataProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _VEHICLE_TAG = VEHICLE_TAGS.FLAMETHROWER

    def getCurrentVehiclesCount(self):
        enableFlamethrowerCount = 0
        unitMgrId, unit = (0, None) if self._unitEntity is None else self._unitEntity.getUnit(safe=True)
        if unit is None:
            return enableFlamethrowerCount
        else:
            enableFlamethrowerCount = sum((slot.vehicle is not None and vehicles.getVehicleType(slot.vehicle.vehTypeCompDescr).isFlamethrower for slot in self._unitEntity.getSlotsIterator(unitMgrId, unit)))
            return enableFlamethrowerCount

    def getRestrictionLevels(self):
        return None

    def getMaxPossibleVehicles(self):
        return self.__lobbyContext.getServerSettings().getMaxFlamethrowerInSquads()
