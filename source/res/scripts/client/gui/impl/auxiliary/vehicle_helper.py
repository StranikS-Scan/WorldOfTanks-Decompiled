# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/auxiliary/vehicle_helper.py
from gui.shared.utils.requesters import REQ_CRITERIA
from helpers import dependency
from skeletons.gui.shared import IItemsCache
from shared_utils import first
from gui.shared.gui_items.Vehicle import Vehicle, VEHICLE_TAGS, VEHICLE_TYPES_ORDER

class SessionVehicleTypeFilters(object):
    _vehicleTypeFilter = {}

    @staticmethod
    def getVehicleTypeFilterByKey(key):
        if key not in SessionVehicleTypeFilters._vehicleTypeFilter:
            SessionVehicleTypeFilters._vehicleTypeFilter[key] = VehicleTypesToggleFilter()
        return SessionVehicleTypeFilters._vehicleTypeFilter[key]


class VehicleTypesToggleFilter(object):

    def __init__(self):
        self._states = {vehicleType:False for vehicleType in VEHICLE_TYPES_ORDER}

    def isSelected(self, vehicleType):
        return self._states[vehicleType]

    def select(self, vehicleType):
        self._states[vehicleType] = True

    def deselect(self, vehicleType):
        self._states[vehicleType] = False

    def toggle(self, vehicleType):
        self._states[vehicleType] = not self._states[vehicleType]


def fillVehicleInfo(vehInfo, vehicle):
    vehInfo.setIsElite(vehicle.isElite)
    vehInfo.setVehicleLvl(vehicle.level)
    vehInfo.setVehicleName(vehicle.userName)
    vehInfo.setVehicleType(vehicle.type)


def getBestRecruitsForVehicle(vehicle, native=False):
    items = dependency.instance(IItemsCache).items
    crewRoles = [ first(roles) for roles in vehicle.descriptor.type.crewRoles ]
    recruitsByRole = {role:[] for role in crewRoles}
    criteria = REQ_CRITERIA.TANKMAN.ACTIVE | REQ_CRITERIA.TANKMAN.ROLES(crewRoles) | REQ_CRITERIA.NATIONS([vehicle.nationID]) | ~REQ_CRITERIA.TANKMAN.DISMISSED
    if native:
        criteria |= REQ_CRITERIA.TANKMAN.NATIVE_TANKS([vehicle.intCD])
    else:
        criteria |= ~REQ_CRITERIA.TANKMAN.IN_TANK
        criteria ^= REQ_CRITERIA.CUSTOM(lambda item: item.isInTank and item.vehicleInvID == vehicle.invID)
    excludeCriteria = ~REQ_CRITERIA.VEHICLE.BATTLE_ROYALE | ~REQ_CRITERIA.VEHICLE.EVENT_BATTLE
    excludeCriteria |= ~REQ_CRITERIA.VEHICLE.LOCKED | ~REQ_CRITERIA.VEHICLE.HAS_TAGS([VEHICLE_TAGS.CREW_LOCKED])
    dirtyRecruits = items.getTankmen(criteria)
    suitableRecruits = items.removeUnsuitableTankmen(dirtyRecruits.itervalues(), excludeCriteria)
    for recruit in suitableRecruits:
        recruitsByRole[recruit.role].append(recruit)

    candidates = {role:[ recruit.invID for recruit in sorted(recruits, key=lambda r: (r.descriptor.totalXP(), r.vehicleNativeDescr.type.compactDescr == vehicle.intCD, r.vehicleNativeType == vehicle.type)) ] for role, recruits in recruitsByRole.iteritems()}
    return [ (candidates[role].pop() if candidates[role] else None) for role in crewRoles ]


def validateBestCrewForVehicle(vehicle, crew, native=False):
    bestCrew = getBestRecruitsForVehicle(vehicle, native=native)
    return set(bestCrew) == set(crew) or all((recruit is None for recruit in bestCrew))


@dependency.replace_none_kwargs(itemsCache=IItemsCache)
def isReturnCrewOptionAvailable(vehicle, recruitIDs, itemsCache=None):
    items = itemsCache.items
    lastCrewIDs = vehicle.lastCrew
    if lastCrewIDs is None:
        return False
    else:
        crewRoles = [ first(roles) for roles in vehicle.descriptor.type.crewRoles ]
        for slot, lastRecruitInvID in enumerate(lastCrewIDs):
            if lastRecruitInvID in recruitIDs:
                continue
            actualLastRecruit = items.getTankman(lastRecruitInvID)
            if actualLastRecruit is None:
                continue
            if actualLastRecruit.role != crewRoles[slot]:
                continue
            lastRecruitVehicle = items.getVehicle(actualLastRecruit.vehicleInvID)
            if lastRecruitVehicle and lastRecruitVehicle.isLocked:
                continue
            return True

        return False
