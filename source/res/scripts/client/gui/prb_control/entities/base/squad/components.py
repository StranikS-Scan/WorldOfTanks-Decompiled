# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/prb_control/entities/base/squad/components.py
from __future__ import absolute_import
from collections import defaultdict
import typing
from future.utils import viewitems, viewkeys
import account_helpers
from constants import MAX_VEHICLE_LEVEL
from items.vehicles import getVehicleType
if typing.TYPE_CHECKING:
    from typing import Dict, Generator, KeysView, List, Tuple, Union
    from gui.prb_control.entities.base.squad.entity import SquadEntity
    from gui.shared.gui_items.Vehicle import Vehicle
    from items.vehicles import VehicleType

def _countVehiclesByCompDescr(intCDs):
    vehicleCounter = defaultdict(int)
    for cd in intCDs:
        vehicleCounter[cd] += 1

    return vehicleCounter


def _countVehiclesByTagAndLevel(vehicles, tagsToCount):
    vehicleCounter = defaultdict(lambda : [0] * MAX_VEHICLE_LEVEL)
    for v in vehicles:
        for tag, level in _getVehicleInfo(v, tagsToCount):
            vehicleCounter[tag][level - 1] += 1

    return vehicleCounter


def _totalVehNumberByLevels(countedVehiclesByLevels, levels):
    return sum((countedVehiclesByLevels[level - 1] for level in levels))


def _getVehicleInfo(vehicle, tagsToGet):
    vehicleTags = vehicle.tags
    for tag in tagsToGet:
        if tag in vehicleTags:
            yield (tag, vehicle.level)


class SquadRestrictionsProvider(object):
    __slots__ = ('_unitEntity',)

    def __init__(self):
        self._unitEntity = None
        return

    def init(self, unitEntity):
        self._unitEntity = unitEntity

    def fini(self):
        self._unitEntity = None
        return

    def isValid(self):
        return self._unitEntity is not None

    def hasSlotForVehicle(self, vehicle, ignoreOwnVehiclesInUnit=False):
        isCommander = self._unitEntity.isCommander(account_helpers.getAccountDatabaseID())
        if isCommander:
            return (True, set())
        squadVehicles = self._getAllSelectedVehicles(ignoreOwnVehiclesInUnit)
        tagsWithoutSlot = self.__getTagsWithoutSlot(squadVehicles + [vehicle], self.__squadRestrictions.get('tags', {}))
        if tagsWithoutSlot:
            return (False, tagsWithoutSlot)
        intCDs = [ v.compactDescr for v in squadVehicles ] + [vehicle.intCD]
        return (self.__applyVehicleGroupsRestrictions(intCDs, self.__squadRestrictions.get('vehicleGroups', [])), set())

    def _getAllSelectedVehicles(self, ignoreOwnVehiclesInUnit):
        _, unit = self._unitEntity.getUnit(safe=True)
        if unit is None:
            return []
        else:
            unitVehicles = unit.getVehicles()
            ownDbID = account_helpers.getAccountDatabaseID()
            vehicles = []
            for dbID, vInfos in viewitems(unitVehicles):
                if ignoreOwnVehiclesInUnit and dbID == ownDbID:
                    continue
                for vInfo in vInfos:
                    vehicles.append(getVehicleType(vInfo.vehTypeCompDescr))

            return vehicles

    @property
    def __squadRestrictions(self):
        return self._unitEntity.squadRestrictions

    @staticmethod
    def __getTagsWithoutSlot(vehicles, platoonTagRestrictions):
        tagsWithoutSlot = set()
        countByTagAndLevel = _countVehiclesByTagAndLevel(vehicles, viewkeys(platoonTagRestrictions))
        for tag, restriction in platoonTagRestrictions.items():
            if tag not in countByTagAndLevel:
                continue
            countByLevel = countByTagAndLevel[tag]
            totalVehicles = _totalVehNumberByLevels(countByLevel, restriction['levels'])
            if totalVehicles > restriction['maxCount']:
                tagsWithoutSlot.add(tag)

        return tagsWithoutSlot

    @staticmethod
    def __applyVehicleGroupsRestrictions(intCDs, platoonVehicleGroupsRestrictions):
        countByCompDescr = _countVehiclesByCompDescr(intCDs)
        for vehiclesGroup in platoonVehicleGroupsRestrictions:
            totalVehicles = sum((countByCompDescr[compDescr] for compDescr in vehiclesGroup['vehicles']))
            if totalVehicles > vehiclesGroup['maxCount']:
                return False

        return True
