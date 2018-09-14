# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/utils.py
from VehicleDescrCrew import VehicleDescrCrew
from VehicleQualifiersApplier import VehicleQualifiersApplier
from items.qualifiers import QUALIFIER_TYPE

def updateVehicleAttrFactors(vehicleDescr, crewCompactDescrs, eqs, factors):
    crewLevelIncrease = vehicleDescr.miscAttrs['crewLevelIncrease'] + sumCrewLevelIncrease(eqs)
    factors['crewLevelIncrease'] = crewLevelIncrease
    mainSkillBonuses = VehicleQualifiersApplier({}, vehicleDescr)[QUALIFIER_TYPE.MAIN_SKILL]
    vehicleDescrCrew = VehicleDescrCrew(vehicleDescr, crewCompactDescrs, mainSkillBonuses)
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
