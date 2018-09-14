# Embedded file name: scripts/common/items/utils.py
from VehicleDescrCrew import VehicleDescrCrew

def updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, factors):
    crewLevelIncrease = vehicleDescr.miscAttrs['crewLevelIncrease'] + sumCrewLevelIncrease(eqs)
    factors['crewLevelIncrease'] = crewLevelIncrease
    vehicleDescrCrew = VehicleDescrCrew(vehicleDescr, crewCompactDescrs)
    vehicleDescrCrew.onCollectFactors(factors)
    for eq in eqs:
        if eq is not None:
            eq.updateVehicleAttrFactors(factors)

    return


def sumCrewLevelIncrease(eqs):
    crewLevelIncrease = 0
    for eq in eqs:
        if eq and hasattr(eq, 'crewLevelIncrease'):
            crewLevelIncrease += eq.crewLevelIncrease

    return crewLevelIncrease
