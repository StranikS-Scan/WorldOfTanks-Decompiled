# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/sabaton_crew.py
from items import tankmen
SABATON_VEH_NAME = 'sweden:S23_Strv_81_sabaton'

def isSabatonCrew(tankmanDescr):
    return tankmen.hasTagInTankmenGroup(tankmanDescr.nationID, tankmanDescr.gid, tankmanDescr.isPremium, SABATON_VEH_NAME)
