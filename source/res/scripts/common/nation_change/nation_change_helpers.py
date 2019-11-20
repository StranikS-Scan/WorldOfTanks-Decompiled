# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/nation_change/nation_change_helpers.py
import typing
from operator import add, contains
import nation_change
from items import vehicles
from AccountCommands import VEHICLE_EXTRA_SETTING_FLAG
MAIN_VEHICLE_INDEX = 0

def activeInNationGroup(flag):
    return not bool(flag & VEHICLE_EXTRA_SETTING_FLAG.NOT_ACTIVE_IN_NATION_GROUP)


def isMainInNationGroupSafe(vehCompDescr):
    groupID = getNationGroupID(vehCompDescr)
    return True if groupID == nation_change.UNDEFINED_ID else isMainInNationGroup(vehCompDescr)


def isMainInNationGroup(vehCompDescr):
    if not vehicles.isVehicleTypeCompactDescr(vehCompDescr):
        vehCompDescr = vehicles.getVehicleTypeCompactDescr(vehCompDescr)
    return getMainVehicleInNationGroup(getNationGroupID(vehCompDescr)) == vehCompDescr


def getNationGroupID(vehCompDescr):
    return vehicles.getVehicleType(vehCompDescr).nationChangeGroupId


def hasNationGroupByVehicleType(vehicleType):
    return vehicleType.nationChangeGroupId != nation_change.UNDEFINED_ID


def hasNationGroup(vehCompactDescr):
    vh = vehicles.getVehicleType(vehCompactDescr)
    return hasNationGroupByVehicleType(vh)


def getVehiclesInNationGroup(groupId):
    group = nation_change.g_settings.getGroupById(groupId)
    return tuple() if group is None else tuple(group.tankList)


def getGroupByVehicleType(vehicleType):
    return getVehiclesInNationGroup(vehicleType.nationChangeGroupId)


def getGroupByVehTypeCompactDescr(vehTypeCompactDescr):
    vehType = vehicles.getVehicleType(vehTypeCompactDescr)
    return getGroupByVehicleType(vehType)


def getGroupByVehicleDescr(vehicleDescr):
    return getGroupByVehicleType(vehicleDescr.type)


def getGroupByVehCompactDescr(vehCompactDescr):
    vehDescr = vehicles.VehicleDescriptor(compactDescr=vehCompactDescr)
    return getGroupByVehicleDescr(vehDescr)


def isInSameGroup(vehTypeNameFrom, vehTypeNameTo):
    if vehTypeNameFrom == vehTypeNameTo:
        return False
    else:
        group1 = nation_change.g_settings.findVehicleGroup(vehTypeNameFrom)
        group2 = nation_change.g_settings.findVehicleGroup(vehTypeNameTo)
        return group1 is not None and group2 is not None and group1.ID == group2.ID


def iterVehTypeCDsInNationGroup(requestVehTypeCD):
    for vehTypeName in getGroupByVehTypeCompactDescr(requestVehTypeCD):
        vehTypeCD = vehicles.makeVehicleTypeCompDescrByName(vehTypeName)
        if vehTypeCD == requestVehTypeCD:
            continue
        yield vehTypeCD


def iterInventoryVehiclesInNationGroup(funcGetVehicleInvID, theVehTypeCompDescr):
    for vehTypeCompDescr in iterVehTypeCDsInNationGroup(theVehTypeCompDescr):
        vehInvID = funcGetVehicleInvID(vehTypeCompDescr)
        if vehInvID == 0:
            continue
        yield vehInvID


def iterVehiclesWithNationGroupInOrder(vehTypeCompDescrs):
    for vehTypeCD in vehTypeCompDescrs:
        yield vehTypeCD
        for vehTypeCDFromGroup in iterVehTypeCDsInNationGroup(vehTypeCD):
            yield vehTypeCDFromGroup


def getMainVehicleInNationGroup(nationGroupID):
    group = nation_change.g_settings.getGroupById(nationGroupID)
    return vehicles.makeVehicleTypeCompDescrByName(group.tankList[MAIN_VEHICLE_INDEX])


def getMainVehicleInNationGroupByVehTypeCD(vehTypeCD):
    vehType = vehicles.getVehicleType(vehTypeCD)
    nationGroupID = vehType.nationChangeGroupId
    return vehTypeCD if nationGroupID == nation_change.UNDEFINED_ID else getMainVehicleInNationGroup(nationGroupID)


class NationalGroupDataAccumulator(dict):

    def __init__(self, dictData, operator=add):
        super(NationalGroupDataAccumulator, self).__init__(dictData)
        self.__operator = operator

    def __getitem__(self, vehTypeCD):

        def _dataIter():
            found = False
            for vtCD in iterVehiclesWithNationGroupInOrder([vehTypeCD]):
                if vtCD in self:
                    found = True
                    yield super(NationalGroupDataAccumulator, self).__getitem__(vtCD)

            if not found:
                raise KeyError(vehTypeCD)

        return reduce(self.__operator, _dataIter())

    def get(self, vehTypeCD, default=None):
        if not bool(vehTypeCD):
            return default
        return self[vehTypeCD] if any((contains(self, x) for x in iterVehiclesWithNationGroupInOrder([vehTypeCD]))) else default
