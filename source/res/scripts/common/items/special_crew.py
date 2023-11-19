# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/special_crew.py
import typing
from items import tankmen
from items.components.tankmen_components import SPECIAL_CREW_TAG
if typing.TYPE_CHECKING:
    from items.vehicles import VehicleType

def isSabatonCrew(tankmanDescr):
    return _hasTagInTankmenGroup(tankmanDescr, SPECIAL_CREW_TAG.SABATON)


def isOffspringCrew(tankmanDescr):
    return _hasTagInTankmenGroup(tankmanDescr, SPECIAL_CREW_TAG.OFFSPRING)


def isYhaCrew(tankmanDescr):
    return _hasTagInTankmenGroup(tankmanDescr, SPECIAL_CREW_TAG.YHA)


def isWitchesCrew(tankmanDescr):
    return _hasTagInTankmenGroup(tankmanDescr, SPECIAL_CREW_TAG.WITCHES_CREW)


def isMihoCrewCompleted(vehicleType, tankmenGroups):
    return _isCrewCompleted(vehicleType, tankmenGroups, SPECIAL_CREW_TAG.MIHO)


def isYhaCrewCompleted(vehicleType, tankmenGroups):
    return _isCrewCompleted(vehicleType, tankmenGroups, SPECIAL_CREW_TAG.YHA)


def isWitchesCrewCompleted(vehicleType, tankmenGroups):
    _, _, isPremium = tankmen.unpackCrewParams(tankmenGroups[0])
    nationID, _ = vehicleType.id
    requiredGroupIDs = tankmen.getTankmenWithTag(nationID, isPremium, SPECIAL_CREW_TAG.WITCHES_CREW)
    uniqueRoles = set([ role[0] for role in vehicleType.crewRoles ])
    actualGroupIDs = set([ tankmen.unpackCrewParams(tGroup)[0] for tGroup in tankmenGroups ])
    return len(actualGroupIDs & requiredGroupIDs) == len(uniqueRoles)


def _hasTagInTankmenGroup(tankmanDescr, tag):
    return tankmen.hasTagInTankmenGroup(tankmanDescr.nationID, tankmanDescr.gid, tankmanDescr.isPremium, tag)


def _isCrewCompleted(vehicleType, tankmenGroups, tag):
    _, _, isPremium = tankmen.unpackCrewParams(tankmenGroups[0])
    nationID, _ = vehicleType.id
    requiredCrew = tankmen.getTankmenWithTag(nationID, isPremium, tag)
    actualCrew = [ tankmen.unpackCrewParams(tGroup)[0] for tGroup in tankmenGroups ]
    return set(actualCrew) <= requiredCrew if len(actualCrew) <= len(requiredCrew) else requiredCrew < set(actualCrew)
