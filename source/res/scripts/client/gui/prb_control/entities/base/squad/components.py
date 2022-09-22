# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/components.py
import typing
import account_helpers
from items import vehicles
from gui.shared.gui_items.Vehicle import VEHICLE_CLASS_NAME
from helpers import dependency
from skeletons.gui.lobby_context import ILobbyContext
if typing.TYPE_CHECKING:
    from gui.prb_control.entities.base.squad.entity import SquadEntity
    from typing import Optional, List

class RestrictedVehicleTagDataProvider(object):
    __slots__ = ('__unitEntity',)
    _VEHICLE_TAG = ''

    def __init__(self):
        self.__unitEntity = None
        return

    def init(self, unitEntity):
        self.__unitEntity = unitEntity

    def fini(self):
        self.__unitEntity = None
        return

    def getMaxPossibleVehicles(self):
        raise NotImplementedError

    def getRestrictionLevels(self):
        raise NotImplementedError

    def isTagVehicleAvailable(self):
        accountDbID = account_helpers.getAccountDatabaseID()
        availableVehicles = self.getMaxPossibleVehicles() - self.getCurrentVehiclesCount()
        if self.getMaxPossibleVehicles() == 0:
            return False
        elif self.__unitEntity.isCommander(accountDbID):
            return True
        elif availableVehicles == 0:
            _, _ = self.__unitEntity.getUnit()
            vInfos = self.__unitEntity.getVehiclesInfo()
            for vInfo in vInfos:
                if self.getRestrictionLevels() is not None and vInfo.vehLevel not in self.getRestrictionLevels():
                    continue
                if self._VEHICLE_TAG in vehicles.getVehicleType(vInfo.vehTypeCD).tags:
                    return True

            return False
        else:
            return availableVehicles > 0

    def hasSlotForVehicle(self):
        accountDbID = account_helpers.getAccountDatabaseID()
        return self.getMaxPossibleVehicles() > 0 and (self.getCurrentVehiclesCount() < self.getMaxPossibleVehicles() or self.__unitEntity.isCommander(accountDbID))

    def getCurrentVehiclesCount(self):
        enableVehicleCount = 0
        _, unit = self.__unitEntity.getUnit(safe=True)
        if unit is None:
            return enableVehicleCount
        else:
            unitVehicles = unit.getVehicles()
            for _, vInfos in unitVehicles.iteritems():
                for vInfo in vInfos:
                    vehType = vehicles.getVehicleType(vInfo.vehTypeCompDescr)
                    if self.getRestrictionLevels() is not None and vehType.level not in self.getRestrictionLevels():
                        continue
                    if self._VEHICLE_TAG in vehType.tags:
                        enableVehicleCount += 1

            return enableVehicleCount


class RestrictedSPGDataProvider(RestrictedVehicleTagDataProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _VEHICLE_TAG = VEHICLE_CLASS_NAME.SPG

    def getRestrictionLevels(self):
        return None

    def getMaxPossibleVehicles(self):
        return self.__lobbyContext.getServerSettings().getMaxSPGinSquads()


class RestrictedScoutDataProvider(RestrictedVehicleTagDataProvider):
    __lobbyContext = dependency.descriptor(ILobbyContext)
    _VEHICLE_TAG = 'scout'

    def getRestrictionLevels(self):
        return self.__lobbyContext.getServerSettings().getMaxScoutInSquadsLevels()

    def getMaxPossibleVehicles(self):
        return self.__lobbyContext.getServerSettings().getMaxScoutInSquads()


class RestrictedSquadDataProvider(RestrictedVehicleTagDataProvider):
    _VEHICLE_TAG = 'squad_restricted'

    def getRestrictionLevels(self):
        return None

    def getMaxPossibleVehicles(self):
        pass
