# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/sabaton_crew.py
from items import tankmen, vehicles
SABATON_VEH_NAME = 'sweden:S23_Strv_81_sabaton'
SABATON_VEHICLE_TYPE_ID = (8, 205)

def getSabatonVehType():
    return vehicles.g_cache.vehicle(*SABATON_VEHICLE_TYPE_ID)


def isSabatonCrew(tankmanDescr):
    return tankmen.hasTagInTankmenGroup(tankmanDescr.nationID, tankmanDescr.gid, tankmanDescr.isPremium, SABATON_VEH_NAME)


def generateTankmenForSpecialEvent():
    """Generate tankmens for sabaton vehicle
    :return: list of TankmanDescr
    """
    vehType = getSabatonVehType()
    nationID, vehTypeID = vehType.id
    roles = __sortTankmenRoles(vehType.crewRoles)
    return tankmen.generateTankmen(nationID, vehTypeID, roles, isPremium=True, roleLevel=100, skillsMask=0, isPreview=True)


def __sortTankmenRoles(roles):
    RO = tankmen.TANKMEN_ROLES_ORDER
    return sorted(roles, cmp=lambda a, b: RO[[a[0]][0]] - RO[[b[0]][0]])
