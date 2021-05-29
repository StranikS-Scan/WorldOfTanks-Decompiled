# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/special_crew.py
import typing
from items import tankmen
from items.components.tankmen_components import SPECIAL_CREW_TAG

def isSabatonCrew(tankmanDescr):
    return tankmen.hasTagInTankmenGroup(tankmanDescr.nationID, tankmanDescr.gid, tankmanDescr.isPremium, SPECIAL_CREW_TAG.SABATON)


def isOffspringCrew(tankmanDescr):
    return tankmen.hasTagInTankmenGroup(tankmanDescr.nationID, tankmanDescr.gid, tankmanDescr.isPremium, SPECIAL_CREW_TAG.OFFSPRING)


def isMihoCrewCompleted(nationID, isPremium, tankmenGroups):
    mihoCrew = tankmen.getTankmenWithTag(nationID, isPremium, SPECIAL_CREW_TAG.MIHO)
    actualCrew = [ tankmen.unpackCrewParams(tGroup)[0] for tGroup in tankmenGroups ]
    return set(actualCrew) <= mihoCrew if len(actualCrew) <= len(mihoCrew) else mihoCrew < set(actualCrew)
