# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/impl/lobby/crew/crew_helpers/skill_helpers.py
import copy
from typing import Tuple
from gui.impl.gen.view_models.views.lobby.crew.crew_constants import CrewConstants
from gui.shared.gui_items.Tankman import Tankman
from gui.shared.gui_items.Vehicle import sortCrew
from gui.shared.skill_parameters.skills_packers import g_skillPackers, packBase
from items import tankmen
from items.components import perks_constants
from items.tankmen import COMMON_SKILLS, MAX_SKILLS_EFFICIENCY, MAX_SKILLS_EFFICIENCY_XP, MAX_SKILL_LEVEL, generateCompactDescr, getSkillsConfig
from skill_formatters import SkillLvlFormatter

def getSkillsLevelsForXp(tankman, possibleXp=0):
    skillsCount, lastSkillLvl = tankman.descriptor.getTotalSkillsProgress(withFree=False, extraXP=possibleXp)
    tmanResidualXp, tmanlvlCost = tankman.descriptor.getResidualXpForNextSkillLevel(skillsCount, lastSkillLvl, possibleXp)
    currSkillLevel = SkillLvlFormatter(lastSkillLvl, tmanResidualXp, tmanlvlCost)
    return (skillsCount, currSkillLevel)


def getTmanNewSkillCount(tankman, useOnlyFull=False, withFree=False):
    newSkillsCount, lastSkillLevel = tankman.descriptor.getNewSkillsCount(fullOnly=useOnlyFull, withFree=withFree)
    return (newSkillsCount, SkillLvlFormatter(lastSkillLevel))


def quickEarnTmanSkills(tankman, possibleXp):
    currCnt, currLvl = getSkillsLevelsForXp(tankman)
    currPossibleXp = possibleXp - tankman.descriptor.needEfficiencyXP
    if currPossibleXp > 0 and not (tankman.descriptor.isMaxSkillXp() and tankman.isMaxSkillEfficiency):
        possSkillEff = tankmen.MAX_SKILLS_EFFICIENCY
        possCnt, possLvl = getSkillsLevelsForXp(tankman, currPossibleXp)
    else:
        possSkillEff = float(tankman.skillsEfficiencyXP + possibleXp) / tankmen.MAX_SKILLS_EFFICIENCY_XP
        possCnt, possLvl = CrewConstants.DONT_SHOW_LEVEL, SkillLvlFormatter()
    if tankman.currentVehicleSkillsEfficiency < 0 or not possibleXp or tankman.descriptor.isMaxSkillXp():
        possSkillEff = CrewConstants.DONT_SHOW_LEVEL
    return ((currCnt,
      possCnt,
      currLvl,
      possLvl), possSkillEff)


def quickEarnCrewSkills(crew, selectedTankmanID, personalXP, commonXP):
    res = [(CrewConstants.DONT_SHOW_LEVEL,
      CrewConstants.DONT_SHOW_LEVEL,
      SkillLvlFormatter(),
      SkillLvlFormatter())] * len(crew)
    res2 = [CrewConstants.DONT_SHOW_LEVEL] * len(crew)
    for slotIdx, tankman in crew:
        if tankman is None:
            continue
        res[slotIdx], res2[slotIdx] = quickEarnTmanSkills(tankman, commonXP + personalXP if tankman.invID == selectedTankmanID else commonXP)

    return (res, res2)


def getTmanWithSkill(tankman, tankmanVehicle, skill, itemsFactory):
    tmanDescr = tankman.descriptor
    skills = tmanDescr.skills[:]
    if not skills:
        skills.append(skill.name)
        lastSkillLevel = MAX_SKILL_LEVEL
    else:
        skills.insert(0, skill.name)
        lastSkillLevel = tmanDescr.lastSkillLevel
    rolesBonusSkills = {}
    for role, bonusSkills in tankman.bonusSkills.iteritems():
        rolesBonusSkills[role] = [ skill.name for skill in bonusSkills if skill ]

    skilledTman = itemsFactory.createTankman(generateCompactDescr(tmanDescr.getPassport(), tmanDescr.vehicleTypeID, tmanDescr.role, tmanDescr.roleLevel, skills, lastSkillLevel, skillsEfficiencyXP=tmanDescr.skillsEfficiencyXP, rolesBonusSkills=rolesBonusSkills), vehicle=tankmanVehicle, vehicleSlotIdx=tankman.vehicleSlotIdx, bonusSkillsLevels=[tmanDescr.bonusSkillsLevels])
    return skilledTman


def getMaxSkillsEffAndLikeOwnVehTman(tankman, tankmanVehicle, itemsFactory, removeSkillCopies=False):
    tmanDescr = tankman.descriptor
    vehicleTypeID = tmanDescr.vehicleTypeID
    if tankmanVehicle:
        _, vehicleTypeID = tankmanVehicle.descriptor.type.id
    rolesBonusSkills = {}
    for role, bonusSkills in tankman.bonusSkills.iteritems():
        rolesBonusSkills[role] = [ skill.name for skill in bonusSkills if skill and not (removeSkillCopies and skill.name in tmanDescr.skills) ]

    skilledTman = itemsFactory.createTankman(generateCompactDescr(tmanDescr.getPassport(), vehicleTypeID, tmanDescr.role, tmanDescr.roleLevel, tmanDescr.skills[:], tmanDescr.lastSkillLevel, skillsEfficiencyXP=MAX_SKILLS_EFFICIENCY_XP, rolesBonusSkills=rolesBonusSkills), vehicle=tankmanVehicle, vehicleSlotIdx=tankman.vehicleSlotIdx, bonusSkillsLevels=[tmanDescr.bonusSkillsLevels])
    return skilledTman


def getVehicleWithSkilledTman(skilledTman, tankman, tankmanVehicle, skillName=''):
    newVehicle = copy.copy(tankmanVehicle)
    if skillName in COMMON_SKILLS:
        newVehicle.crew = newVehicle.getCrewWithSkill(skillName)
    else:
        crewItems = list()
        skilledTmanDescr = tankman.descriptor
        for slotIdx, tman in newVehicle.crew:
            if tman and tman.descriptor.role == skilledTmanDescr.role:
                crewItems.append((slotIdx, skilledTman))
                continue
            crewItems.append((slotIdx, tman))

        newVehicle.crew = sortCrew(crewItems, tankmanVehicle.descriptor.type.crewRoles)
    return newVehicle


def getSkillParams(tankman, tankmanVehicle, skillBooster, skill, skillName, skillLevel, isFakeSkill, isIrrelevant=False):
    skillPacker = g_skillPackers.get(skillName, packBase)
    descrArgs = getSkillsConfig().getSkill(skillName).uiSettings.descrArgs
    skillEfficiency = tankman.currentVehicleSkillsEfficiency if tankman else MAX_SKILLS_EFFICIENCY
    isTmanTrainedVeh = not tankmanVehicle or tankman.descriptor.isOwnVehicleOrPremium(tankmanVehicle.descriptor.type)
    if skill.name in perks_constants.SKIP_SE_PERKS or tankman and not skill.isEnable or isIrrelevant:
        skillEfficiency = MAX_SKILLS_EFFICIENCY
    return skillPacker(descrArgs, skillLevel, isSkillAlreadyEarned=True if isFakeSkill else skill.isLearned, lowEfficiency=skillEfficiency < MAX_SKILLS_EFFICIENCY, isTmanTrainedVeh=isTmanTrainedVeh, hasBooster=skillBooster is not None, customValues=dict(((name, lambda b=skillBooster, n=name: b if b and hasattr(b, n) else None) for name, _ in descrArgs)) if skillName in g_skillPackers else None)


def getSkillDescription(tankman, skill, skillLevel, skillBooster, isCmpSkill, isFakeSkillLvl, isIrrelevant):
    isMaxSkillEfficiency = tankman and tankman.isMaxSkillEfficiency
    skillEfficiencyLvl = isMaxSkillEfficiency or not isFakeSkillLvl and skillLevel > 0
    isLearned = skillEfficiencyLvl and not isFakeSkillLvl and skillLevel > 0 and skill.isLearned
    inSkipSEPerks = skill.name in perks_constants.SKIP_SE_PERKS
    validSkillBooster = skillBooster and not (tankman and not skill.isEnable) and not isIrrelevant
    return skill.currentLvlDescription if isCmpSkill or validSkillBooster or isLearned or inSkipSEPerks else skill.maxLvlDescription


def formatDescription(description, params):
    for props in params:
        color = params[props].get('color', '')
        value = params[props].get('value', '')
        description = description.replace('%(' + props + ')s', '{' + color + '_Start}' + value + '{' + color + '_End}')

    return description
