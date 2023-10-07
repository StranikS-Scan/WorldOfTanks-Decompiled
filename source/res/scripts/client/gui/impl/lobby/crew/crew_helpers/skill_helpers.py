# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/skill_helpers.py
from typing import Tuple
from collections import OrderedDict
from gui import TANKMEN_ROLES_ORDER_DICT
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.shared.gui_items.Tankman import Tankman
from items import tankmen
from items.components.skills_constants import SKILLS_BY_ROLES, UNLEARNABLE_SKILLS
from skill_formatters import SkillLvlFormatter

def isTmanSkillIrrelevant(tankman, skill):
    return not any([ skill.name in SKILLS_BY_ROLES.get(role) for role in tankman.roles() ])


def isTmanMaxed(tankman):
    if tankman:
        newSkillsCount, lastNewSkillLvl = getSkillsLevelsForXp(tankman)
        return newSkillsCount == getAvailableSkillsNum(tankman) and lastNewSkillLvl.intSkillLvl == tankmen.MAX_SKILL_LEVEL
    return False


def getLastSkillSequenceNum(tankman):
    tdescr = tankman.descriptor
    return max(tdescr.lastSkillNumber - tdescr.freeSkillsNumber, 0)


def getAvailableSkillsNum(tankman):
    return len(tankman.availableSkills(True)) + getLastSkillSequenceNum(tankman) - tankman.newFreeSkillsCount


def getSkillsLevelsForXp(tankman, possibleXp=0):
    tmanDescr = tankman.descriptor
    lastSkillNumber = getLastSkillSequenceNum(tankman)
    availableSkillsNum = getAvailableSkillsNum(tankman)
    wallet = tmanDescr.freeXP + possibleXp
    if tmanDescr.roleLevel < tankmen.MAX_SKILL_LEVEL:
        if not lastSkillNumber or possibleXp > 0:
            wallet += tankmen.TankmanDescr.getXpCostForSkillsLevels(tmanDescr.roleLevel, 0)
            wallet -= tankmen.TankmanDescr.getXpCostForSkillsLevels(tankmen.MAX_SKILL_LEVEL, 0)
    wallet += tankmen.TankmanDescr.getXpCostForSkillsLevels(tmanDescr.lastSkillLevel if lastSkillNumber else 0, lastSkillNumber)
    currCnt = tankmen.TankmanDescr.getSkillsCountFromXp(wallet)
    currLvl = tankmen.TankmanDescr.getSkillLevelFromXp(currCnt, wallet)
    if currCnt > availableSkillsNum or currCnt == availableSkillsNum and currLvl >= tankmen.MAX_SKILL_LEVEL:
        currCnt = availableSkillsNum
        currLvl = tankmen.MAX_SKILL_LEVEL
    tmanResidualXp, tmanlvlCost = getXpResidualForNextSkillLevel(tankman, currCnt, currLvl, possibleXp)
    currSkillLevel = SkillLvlFormatter(currLvl, tmanResidualXp, tmanlvlCost)
    return (currCnt, currSkillLevel)


def getXpResidualForNextSkillLevel(tankman, currSkillsCount, currSkillLevel, possibleXp=0):
    tmanDescr = tankman.descriptor
    lastSkillNumber = getLastSkillSequenceNum(tankman)
    availableSkillsNum = getAvailableSkillsNum(tankman)
    if currSkillsCount <= availableSkillsNum:
        totalXpCost = tmanDescr.freeXP + possibleXp
        totalXpCost += tankmen.TankmanDescr.getXpCostForSkillsLevels(tmanDescr.roleLevel, 0)
        totalXpCost -= tankmen.TankmanDescr.getXpCostForSkillsLevels(tankmen.MAX_SKILL_LEVEL, 0)
        totalXpCost += tankmen.TankmanDescr.getXpCostForSkillsLevels(tmanDescr.lastSkillLevel if lastSkillNumber else 0, lastSkillNumber)
        levelUpXpCost = tankmen.TankmanDescr.levelUpXpCost(min(tankmen.MAX_SKILL_LEVEL - 1, currSkillLevel), currSkillsCount)
        currXpCost = tankmen.TankmanDescr.getXpCostForSkillsLevels(currSkillLevel, currSkillsCount)
        return (totalXpCost - currXpCost, levelUpXpCost)


def getTmanNewSkillCount(tankman, useOnlyFull=False):
    newSkillsCount = 0
    lastSkillLevel = SkillLvlFormatter()
    lastSkillNumber = getLastSkillSequenceNum(tankman)
    if not tankman.isMaxRoleLevel:
        return (0, SkillLvlFormatter(tankman.descriptor.lastSkillLevel))
    if tankman.hasNewSkill(useCombinedRoles=True) or lastSkillNumber:
        newSkillsCount, lastSkillLevel = getSkillsLevelsForXp(tankman)
        newSkillsCount -= lastSkillNumber
        if useOnlyFull and lastSkillLevel.intSkillLvl < tankmen.MAX_SKILL_LEVEL:
            newSkillsCount = max(newSkillsCount - 1, 0)
            lastSkillLevel = SkillLvlFormatter(tankmen.MAX_SKILL_LEVEL if newSkillsCount else tankman.descriptor.lastSkillLevel)
        elif not useOnlyFull and lastSkillLevel.realSkillLvl >= tankmen.MAX_SKILL_LEVEL and newSkillsCount < len(tankman.availableSkills(True)) - tankman.newFreeSkillsCount:
            newSkillsCount += 1
            lastSkillLevel = SkillLvlFormatter(0)
    return (newSkillsCount, lastSkillLevel)


def getAllPossibleSkillsByRoles():
    result = OrderedDict()
    for skill in tankmen.COMMON_SKILLS_ORDERED:
        result.setdefault('common', []).append(skill)

    for role in TANKMEN_ROLES_ORDER_DICT['plain']:
        roleSkills = tankmen.SKILLS_BY_ROLES_ORDERED.get(role, tuple())
        for skill in roleSkills:
            if skill in tankmen.COMMON_SKILLS:
                continue
            if skill in UNLEARNABLE_SKILLS:
                continue
            result.setdefault(role, []).append(skill)

    return result


def quickEarnTmanSkills(tankman, possibleXp):
    currCnt, currLvl = getSkillsLevelsForXp(tankman)
    if possibleXp:
        possCnt, possLvl = getSkillsLevelsForXp(tankman, possibleXp)
    else:
        possCnt, possLvl = CrewConstants.DONT_SHOW_LEVEL, SkillLvlFormatter()
    return (currCnt,
     possCnt,
     currLvl,
     possLvl)


def quickEarnCrewSkills(crew, selectedTankmanID, personalXP, commonXP):
    res = [(CrewConstants.DONT_SHOW_LEVEL,
      CrewConstants.DONT_SHOW_LEVEL,
      SkillLvlFormatter(),
      SkillLvlFormatter())] * len(crew)
    for slotIdx, tankman in crew:
        if tankman is None:
            continue
        res[slotIdx] = quickEarnTmanSkills(tankman, commonXP + personalXP if tankman.invID == selectedTankmanID else commonXP)

    return res
