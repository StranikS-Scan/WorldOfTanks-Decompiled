# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/battle_control/controllers/commander/spawn_ctrl/entities.py
import typing
from RTSShared import RTSSupply
from gui.battle_control.controllers.commander.spawn_ctrl.interfaces import ISpawnEntity, ISupplyContainerEntity
if typing.TYPE_CHECKING:
    from typing import List

class SpawnEntity(ISpawnEntity):

    def __init__(self, vehicleType, vehicleID):
        super(SpawnEntity, self).__init__()
        self.__vehicleID = vehicleID
        self.__vehicleType = vehicleType
        self.__chosenPointData = None
        return

    def __repr__(self):
        return 'SpawnEntity(vehicleID=%r, vehicleType=%r, chosenPointData=%r, isSupply=%r)' % (self.__vehicleID,
         self.__vehicleType,
         self.__chosenPointData,
         self.isSupply)

    def getID(self):
        return self.__vehicleID

    def getType(self):
        return self.__vehicleType

    @property
    def isVehicle(self):
        return not self.isSupply

    @property
    def isSupply(self):
        return self.__vehicleType in RTSSupply.SUPPLY_TAG_LIST

    @property
    def isSettled(self):
        return self.__chosenPointData is not None

    @property
    def chosenPointData(self):
        return self.__chosenPointData

    @chosenPointData.setter
    def chosenPointData(self, value):
        self.__chosenPointData = value


class SupplyContainerEntity(ISupplyContainerEntity):

    def __init__(self, supplyType, supplies=None):
        super(SupplyContainerEntity, self).__init__()
        self.__supplies = supplies or []
        self.__supplyType = supplyType

    def __repr__(self):
        return 'SupplyContainerEntity(supplyType=%r, supplies=%r)' % (self.__supplyType, self.__supplies)

    def getID(self):
        supplies = self.__supplies
        return supplies[-1].getID() if supplies else None

    def getType(self):
        return self.__supplyType

    @property
    def isVehicle(self):
        return False

    @property
    def isSupply(self):
        return True

    @property
    def isSettled(self):
        return all((supply.isSettled for supply in self.__supplies))

    @property
    def chosenPointData(self):
        supplies = self.__supplies
        return supplies[-1].chosenPointData if supplies else None

    @property
    def settledCount(self):
        return len([ s for s in self.__supplies if s.isSettled ])

    @property
    def supplies(self):
        return self.__supplies

    def addSupply(self, entityID):
        self.__supplies.append(SpawnEntity(self.__supplyType, entityID))

    def selectSupply(self, entity):
        supplies = self.__supplies
        supplies.append(supplies.pop(supplies.index(entity)))
