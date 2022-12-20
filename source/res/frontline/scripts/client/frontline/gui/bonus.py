# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: frontline/scripts/client/frontline/gui/bonus.py
import typing
from epic_constants import EPIC_SKILL_TOKEN_NAME, EPIC_SELECT_BONUS_NAME
from gui.server_events.bonuses import SimpleBonus

class FrontlineSkillBonus(SimpleBonus):

    def __init__(self, value, ctx=None):
        super(FrontlineSkillBonus, self).__init__(EPIC_SKILL_TOKEN_NAME, value, ctx=ctx)


def isBonusesEqual(lhv, rhv):
    if len(lhv) != len(rhv):
        return False
    for index, bonus in enumerate(lhv):
        if not bonus.isEqual(rhv[index]):
            return False

    return True


def mergeSelectable(frontlineLevel, startLvl, endLvl, bonuses, bonusesByLvl):
    indexToCheck = []
    for idx, bonus in enumerate(bonuses):
        if bonus.getName() == EPIC_SELECT_BONUS_NAME:
            if bonus.isReceived():
                indexToCheck.append(idx)
            elif frontlineLevel >= startLvl:
                bonuses[idx].updateContext({'canClaim': True})

    level = startLvl + 1
    while level <= endLvl:
        if not indexToCheck:
            break
        for idx in indexToCheck:
            mergedBonus = bonusesByLvl[level][idx]
            if level > frontlineLevel:
                bonuses[idx].updateContext({'canClaim': False})
                indexToCheck.remove(idx)
            if not mergedBonus.isReceived():
                bonuses[idx].updateContext({'canClaim': True})
                indexToCheck.remove(idx)

        level += 1
