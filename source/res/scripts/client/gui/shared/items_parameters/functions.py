# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/shared/items_parameters/functions.py
from operator import itemgetter
from items import utils, tankmen

def getVehicleFactors(vehicle):
    factors = utils.makeDefaultVehicleAttributeFactors()
    vehicleDescr = vehicle.descriptor
    eqs = [ eq.descriptor for eq in vehicle.equipment.regularConsumables if eq is not None ]
    if vehicle.equipment.battleBoosterConsumables[0] is not None:
        eqs.append(vehicle.equipment.battleBoosterConsumables[0].descriptor)
    crewCompactDescrs = extractCrewDescrs(vehicle)
    utils.updateAttrFactorsWithSplit(vehicleDescr, crewCompactDescrs, eqs, factors)
    return factors


def extractCrewDescrs(vehicle, replaceNone=True):
    crewCompactDescrs = []
    emptySlots = []
    otherVehicleSlots = []
    vehicleDescr = vehicle.descriptor
    for idx, tankman in sorted(vehicle.crew, key=itemgetter(0)):
        if tankman is not None:
            if hasattr(tankman, 'strCompactDescr'):
                tankmanDescr = tankman.strCompactDescr
                if tankman.efficiencyRoleLevel < tankman.roleLevel:
                    otherVehicleSlots.append(idx)
            else:
                tankmanDescr = tankman
        elif not replaceNone:
            tankmanDescr = None
            emptySlots.append(idx)
        else:
            role = vehicleDescr.type.crewRoles[idx][0]
            tankmanDescr = createFakeTankmanDescr(role, vehicleDescr.type)
        crewCompactDescrs.append(tankmanDescr)

    if replaceNone:
        return crewCompactDescrs
    else:
        return (crewCompactDescrs, emptySlots, otherVehicleSlots)
        return


def createFakeTankmanDescr(role, vehicleType, roleLevel=100):
    nationID, vehicleTypeID = vehicleType.id
    passport = tankmen.generatePassport(nationID)
    return tankmen.generateCompactDescr(passport, vehicleTypeID, role, roleLevel)


def getBasicShell(vehDescr):
    """
        basic is shell which goes first in XML describing particular gun
    """
    return vehDescr.gun.shots[0].shell
