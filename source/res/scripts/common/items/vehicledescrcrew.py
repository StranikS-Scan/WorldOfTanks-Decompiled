# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/VehicleDescrCrew.py
from typing import Tuple, List, Set, Dict, Iterator
from constants import PerkData, SkillProcessorArgs, GroupSkillProcessorArgs, CHANCE_TO_HIT_SUFFIX_FACTOR, CrewContextArgs
from debug_utils import *
from items.artefacts import SkillEquipment
from items.combined_crew_skill import CombinedCrewSkill
from items.components.perks_constants import SKIP_SE_PERKS
from items.components.skills_constants import ROLES_BY_SKILLS
from items.utils import isclose
from soft_exception import SoftException
import tankmen
import vehicles
if IS_CLIENT:
    from items import perks
_DO_DEBUG_LOG = False
CREW_CONTEXT_FORCE_UPDATE_INDEX = -29222
_ADDITIVE_FACTORS = frozenset([ ten + CHANCE_TO_HIT_SUFFIX_FACTOR for ten in vehicles.TANKMAN_EXTRA_NAMES ] + ['circularVisionRadiusB'])
_COMPLEX_FACTORS = frozenset(('circularVisionRadius', 'circularVisionRadiusB'))

class VehicleDescrCrew(object):

    def __init__(self, vehicleDescr, crewCompactDescrs, activityFlags=None, isFire=False, defaultSixthSenseDisabled=False):
        if activityFlags is None:
            activityFlags = [True] * len(crewCompactDescrs)
        self._vehicleDescr = vehicleDescr
        self._crewCompactDescrs = crewCompactDescrs
        self._activityFlags = activityFlags
        self._isFire = isFire
        self._defaultSixthSenseDisabled = defaultSixthSenseDisabled
        self._crewSkillsEfficiency = {}
        skills, self._perks = self._validateAndComputeCrew()
        self._skills = skills
        if _DO_DEBUG_LOG:
            items = skills.iteritems()
            for skillName, skillData in sorted(items, cmp=lambda x, y: cmp(x[0], y[0])):
                LOG_DEBUG("TankmanIdxs/levels with skill '%s': %s" % (skillName, str(skillData)))

        self._commanderIdx = skills['commander'][0][0]
        self.__factorsDirty = True
        self._levelIncreaseByVehicle = 0.0
        self._levelIncreaseByBrotherhood = 0.0
        self._affectingFactors = {'crewRolesFactor': 1.0,
         'radioDistanceFactor': 0.0}
        self._camouflageFactor = 1.0
        self._boostedSkills = {}
        self._useCachedLevelIncrease = False
        self.lastUsedLevels = {}
        self._extendedSkills = {}
        return

    def boostSkillBy(self, equipment):
        if equipment.skillName in self._skills:
            self._boostedSkills[equipment.skillName] = equipment
            self._factorsDirty = True

    def discardSkillBoostBy(self, equipment):
        if equipment.skillName not in self._skills:
            return
        else:
            skill = self._boostedSkills.get(equipment.skillName)
            if skill is None:
                LOG_ERROR('Failed to discard skill (arenaUniqueID, vehicleID, skillName):', self.__getUniqueArenaID(), self.__getVehicleID(), equipment.skillName, stack=True)
                return
            del self._boostedSkills[equipment.skillName]
            self._factorsDirty = True
            return

    def callSkillProcessor(self, skillName, *args):
        try:
            skillProcessor = self._skillProcessors.get(skillName)
            if skillProcessor is None:
                return
            equipment = self._boostedSkills.get(skillName)
            if equipment is not None:
                equipment.updateCrewSkill(*args)
            skillProcessor(self, *args)
        except:
            LOG_ERROR('Failed to process skill (arenaUniqueID, vehicleID, skillName, skillData):', self.__getUniqueArenaID(), self.__getVehicleID(), skillName, self._skills.get(skillName), stack=True)
            LOG_CURRENT_EXCEPTION()

        return

    def extendSkillProcessor(self, skillName, skillData, skillProcessor):
        if not skillData or skillName in self._skills:
            return
        self._skillProcessors[skillName] = skillProcessor
        self._extendedSkills[skillName] = skillData
        self._factorsDirty = True

    def contractSkillProcessor(self, skillName):
        if skillName in self._skillProcessors:
            self._skillProcessors.pop(skillName)
        if skillName in self._extendedSkills:
            self._extendedSkills.pop(skillName)
        self._factorsDirty = True

    @property
    def skills(self):
        return self._skills

    @property
    def camouflageFactor(self):
        if self._factorsDirty:
            self._buildFactors()
        return self._camouflageFactor

    @property
    def _factorsDirty(self):
        return self.__factorsDirty

    @_factorsDirty.setter
    def _factorsDirty(self, necessity):
        self.__factorsDirty = necessity

    @property
    def useCachedLevelIncrease(self):
        return self._useCachedLevelIncrease

    @useCachedLevelIncrease.setter
    def useCachedLevelIncrease(self, value):
        self._useCachedLevelIncrease = value

    def isCrewActive(self):
        return True in self._activityFlags

    def recomputeSkill(self, skillName):
        for idxInCrew, level in self._skills.get(skillName, ()):
            if self._activityFlags[idxInCrew]:
                self._factorsDirty = True
                break

    def onCollectShotDispersionFactors(self, factors):
        if self._factorsDirty:
            self._buildFactors()
        factors[0] *= self._shotDispFactor

    def onCollectFactors(self, factors):
        newLevelIncreaseByVehicle = factors['crewLevelIncrease'] + self._vehicleDescr.miscAttrs['crewLevelIncrease']
        if self._levelIncreaseByVehicle != newLevelIncreaseByVehicle:
            self._levelIncreaseByVehicle = newLevelIncreaseByVehicle
            if hasattr(self, '_vehicle') and not self._useCachedLevelIncrease:
                self._vehicle.events.onTankmanStatusChanged(self._vehicle, CREW_CONTEXT_FORCE_UPDATE_INDEX)
            self._factorsDirty = True
        for key, factor in self._affectingFactors.iteritems():
            if not isclose(factors[key], factor):
                self._affectingFactors.update(((k, factors[k]) for k in self._affectingFactors.iterkeys()))
                self._factorsDirty = True
                break

        if self._factorsDirty:
            self._buildFactors()
        for name, value in self._factors.iteritems():
            try:
                if name in _COMPLEX_FACTORS:
                    continue
                if name in _ADDITIVE_FACTORS:
                    factors[name] += value
                else:
                    factors[name] *= value
            except:
                pass

        cvrA = self._factors.get('circularVisionRadius', 1.0)
        cvrB = self._factors.get('circularVisionRadiusB', 0.0)
        factors['circularVisionRadius'] *= cvrA * (1.0 + cvrB)
        try:
            r = factors['chassis/terrainResistance']
            value = self._terrainResistanceFactors
            r[0] *= value[0]
            r[1] *= value[1]
            r[2] *= value[2]
        except:
            pass

    def saveLastUsedPerkLevel(self, perkID, level):
        skillName = tankmen.getSkillsConfig().vsePerkToSkill.get(perkID)
        self.lastUsedLevels[skillName] = level

    def collectDefaultCrewData(self):
        crewData = []
        for idx, compactDescr in enumerate(self._crewCompactDescrs):
            descr = tankmen.TankmanDescr(compactDescr, True)
            crewData.append((idx, float(descr.roleLevel)))

        return crewData

    def _calcLeverIncreaseForNonCommander(self, commonLevelIncrease):
        if not self._activityFlags[self._commanderIdx]:
            levelIncreaseByCommander = 0.0
        else:
            commanderLevel = self._skills['commander'][0][1] + commonLevelIncrease
            levelIncreaseByCommander = commanderLevel / tankmen.COMMANDER_ADDITION_RATIO
        result = commonLevelIncrease + levelIncreaseByCommander
        if _DO_DEBUG_LOG:
            LOG_DEBUG('levelIncreaseByCommander={}'.format(levelIncreaseByCommander))
            LOG_DEBUG('nonCommanderLeverIncrease={}'.format(result))
        return result

    def _buildFactors(self):
        self._factors = {}
        self._shotDispFactor = 1.0
        self._terrainResistanceFactors = [1.0, 1.0, 1.0]
        self._levelIncreaseByBrotherhood = self._calculateLevelIncreaseByBrotherhood()
        commonLevelIncrease = self._levelIncreaseByBrotherhood + self._levelIncreaseByVehicle
        nonCommanderLevelIncrease = self._calcLeverIncreaseForNonCommander(commonLevelIncrease)
        if _DO_DEBUG_LOG:
            LOG_DEBUG('Crew level increase by vehicle={}, by brotherhood={}'.format(self._levelIncreaseByVehicle, self._levelIncreaseByBrotherhood))
        skillEfficiencies = self._calculateSkillEfficiencies(commonLevelIncrease, nonCommanderLevelIncrease)
        self._processSkills(skillEfficiencies, commonLevelIncrease, nonCommanderLevelIncrease)
        self._factorsDirty = False

    def _calculateLevelIncreaseByBrotherhood(self):
        value = 0.0
        if self._isFire:
            return value
        else:
            skillData = self._skills.get('brotherhood')
            if skillData is None:
                return value
            broSum = 0
            broLen = len(skillData)
            for crewIdx, level in skillData:
                if self._activityFlags[crewIdx]:
                    skillsEfficiency = self._getSkillsEfficiencyByCrewIdx(crewIdx)
                    if level is not None:
                        broSum += level * skillsEfficiency

            broLevel = broSum / (broLen * tankmen.MAX_SKILL_LEVEL)
            return broLevel * tankmen.getSkillsConfig().getSkill('brotherhood').crewLevelIncrease

    def _calculateSkillEfficiencies(self, commonLevelIncrease, nonCommanderLevelIncrease):
        skillEfficiencies = []
        tutorAddition = self._calculateTutorAddition(commonLevelIncrease)
        self._updateCommanderTutorNotifications(tutorAddition)
        skills = {skillName:self._skills[skillName] for skillName in tankmen.ROLES}
        skills.update({skillName:self._skills.get(skillName) for skillName in ('repair', 'camouflage')})
        skills.update(self._extendedSkills)
        for skillName, skillData in skills.iteritems():
            if not skillData or self._isFire:
                summLevel = 0.0
                baseSummLevel = 0.0
                summEfficiency = 0.0
            else:
                isRoleSkill = skillName in tankmen.ROLES
                isExtendedSkill = skillName in self._extendedSkills
                isBoostedSkill = skillName in self._boostedSkills
                baseSummLevel, summLevel, summEfficiency = self._computeSummSkillLevel(skillData, nonCommanderLevelIncrease=nonCommanderLevelIncrease, commanderLevelIncrease=commonLevelIncrease, isUseSE=not (isRoleSkill or isExtendedSkill or isBoostedSkill))
                if isRoleSkill:
                    numInactive = sum((int(not self._activityFlags[idx]) for idx, _ in skillData))
                    summLevel += numInactive * tutorAddition / len(skillData) / tankmen.MAX_SKILL_LEVEL
            skillEfficiencies.append((skillName,
             summLevel,
             baseSummLevel,
             summEfficiency))

        return skillEfficiencies

    def _calculateTutorAddition(self, commonLevelIncrease):
        tutorAddition = 0
        if self._isFire or not self._activityFlags[self._commanderIdx]:
            return tutorAddition
        else:
            numInactive = self._activityFlags.count(False)
            if numInactive:
                skillData = self._skills.get('commander_tutor')
                if skillData is not None:
                    level = skillData[0][1]
                    if level is not None:
                        tutorAddition = (level + commonLevelIncrease) / numInactive
                        tutorAddition *= tankmen.getSkillsConfig().getSkill('commander_tutor').efficiency
                        tutorAddition *= self._getSkillsEfficiencyByCrewIdx(self._commanderIdx)
            return tutorAddition

    def _processSkills(self, skillEfficiencies, commonLevelIncrease, nonCommanderLevelIncrease):
        skills = self._skills
        isFire = self._isFire
        getSkill = tankmen.getSkillsConfig().getSkill
        skillToBoost = set(self._boostedSkills.iterkeys())
        callSkillProcessor = self.callSkillProcessor
        for skillName, efficiency, baseAvgLevel, summEfficiency in skillEfficiencies:
            self.lastUsedLevels[skillName] = efficiency * 100
            factor = 0.57 + 0.43 * efficiency
            skillToBoost.discard(skillName)
            callSkillProcessor(skillName, GroupSkillProcessorArgs(factor, baseAvgLevel, summEfficiency))

        for skillName, tmanLevels in skills.iteritems():
            if skillName in tankmen.ROLES_AND_COMMON_SKILLS:
                continue
            skillConfig = getSkill(skillName)
            perkID = skillConfig.vsePerk
            perkData = self._perks.get(perkID)
            skillData = {'crew': tmanLevels,
             'booster': None,
             'b_crew': set((idx for idx, _ in tmanLevels))} if perkData is None else perkData.args.skillData
            ccs = self._findBestTankmanForSkill(skillData, skillName)
            self.lastUsedLevels[skillName] = ccs.level
            skillToBoost.discard(skillName)
            callSkillProcessor(skillName, SkillProcessorArgs(level=ccs.tankmanLevel, levelIncrease=ccs.levelIncrease, skillsEfficiency=ccs.skillsEfficiency, isActive=ccs.isTankmanActive, isFire=isFire, skillConfig=skillConfig, hasActiveTankmanForBooster=self._hasActiveTankmanForBooster(skillData)))

        for skillName in skillToBoost:
            callSkillProcessor(skillName, SkillProcessorArgs(level=0, levelIncrease=0, skillsEfficiency=1, isActive=False, isFire=isFire, skillConfig=getSkill(skillName), hasActiveTankmanForBooster=False))

        return

    def _getCrewForSkillBooster(self, skillName):
        crew = set()
        crewRoles = self._vehicleDescr.type.crewRoles
        rolesBySkill = ROLES_BY_SKILLS[skillName]
        for idxInCrew, roles in enumerate(crewRoles):
            for role in roles:
                if role not in rolesBySkill:
                    continue
                crew.add(idxInCrew)

        return crew

    def _hasActiveTankmanForBooster(self, skillData):
        return any((self._activityFlags[idx] for idx in skillData.get('b_crew', ())))

    def _updateCommanderFactors(self, a):
        a.factor *= self._affectingFactors['crewRolesFactor']
        self._factors['circularVisionRadius'] = a.factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel/crewRolesFactor of skill '%s': (%s, %s, %s)" % ('commander',
             a.factor,
             a.baseAvgLevel,
             self._affectingFactors['crewRolesFactor']))

    def _updateRadiomanFactors(self, a):
        a.factor *= self._affectingFactors['crewRolesFactor']
        self._factors['radio/distance'] = a.factor * (1.0 + self._affectingFactors['radioDistanceFactor'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel/crewRolesFactor of skill '%s': (%s, %s, %s)" % ('radioman',
             a.factor,
             a.baseAvgLevel,
             self._affectingFactors['crewRolesFactor']))

    def _updateDriverFactors(self, a):
        a.factor *= self._affectingFactors['crewRolesFactor']
        factor = 1.0 / a.factor
        r = self._terrainResistanceFactors
        r[0] *= factor
        r[1] *= factor
        r[2] *= factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel/crewRolesFactor of skill '%s': (%s, %s, %s)" % ('driver',
             factor,
             a.baseAvgLevel,
             self._affectingFactors['crewRolesFactor']))

    def _updateLoaderFactors(self, a):
        a.factor *= self._affectingFactors['crewRolesFactor']
        self._factors['gun/reloadTime'] = 1.0 / a.factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel/crewRolesFactor of skill '%s': (%s, %s, %s)" % ('loader',
             a.factor,
             a.baseAvgLevel,
             self._affectingFactors['crewRolesFactor']))

    def _updateGunnerFactors(self, a):
        a.factor *= self._affectingFactors['crewRolesFactor']
        factors = self._factors
        factors['turret/rotationSpeed'] = a.factor
        factors['gun/rotationSpeed'] = a.factor
        factors['gun/aimingTime'] = 1.0 / a.factor
        self._shotDispFactor = 1.0 / a.factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel/crewRolesFactor of skill '%s': (%s, %s, %s)" % ('gunner',
             a.factor,
             a.baseAvgLevel,
             self._affectingFactors['crewRolesFactor']))

    def _updateRepairFactors(self, a):
        self._factors['repairSpeed'] = a.factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('repair', a.factor, a.baseAvgLevel))

    def _updateCamouflageFactors(self, a):
        self._camouflageFactor = a.factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('camouflage', a.factor, a.baseAvgLevel))

    def _process_commander_eagleEye(self, a):
        self._process_perk(a, 'increaseCircularVisionRadius', 'circularVisionRadiusB')

    def _process_radioman_finder(self, a):
        self._process_perk(a, 'vehicleCircularVisionRadius', 'circularVisionRadiusB')

    def _process_perk(self, a, argName, factorName):
        if not IS_CLIENT:
            return
        if not a.isActive or a.isFire:
            return
        vsePerk = a.skillConfig.vsePerk
        perkCfg = perks.g_cache.perks.get(vsePerk)
        factorPerLevel = perkCfg.defaultBlockSettings[argName].value
        self._setFactor(factorName, round(a.level + a.levelIncrease) * factorPerLevel)

    def _findBestTankmanForSkill(self, skillData, skillName=None):
        if not self._useCachedLevelIncrease:
            commanderLevelIncrease = self._levelIncreaseByBrotherhood + self._levelIncreaseByVehicle
            nonCommanderLevelIncrease = self._calcLeverIncreaseForNonCommander(commanderLevelIncrease)
            self._cachedLevelIncrease = (commanderLevelIncrease, nonCommanderLevelIncrease)
        else:
            commanderLevelIncrease, nonCommanderLevelIncrease = self._cachedLevelIncrease
        commanderIdx = self._commanderIdx
        levelSum = 0
        levelIncreaseSum = 0
        sumSkillsEfficency = 0.0
        isAnyoneActive = False
        boosterMultiplier = skillData.get('booster')
        for idxInCrew, level in skillData.get('crew', []):
            levelIncrease = commanderLevelIncrease if idxInCrew == commanderIdx else nonCommanderLevelIncrease
            if self._activityFlags[idxInCrew]:
                realSkillsEfficiency = self._getSkillsEfficiencyByCrewIdx(idxInCrew)
                skillsEfficiency = realSkillsEfficiency if skillName not in SKIP_SE_PERKS and boosterMultiplier is None else tankmen.MAX_SKILLS_EFFICIENCY
                if level is not None:
                    levelSum += level * skillsEfficiency
                    levelIncreaseSum += levelIncrease * skillsEfficiency
                sumSkillsEfficency += realSkillsEfficiency
                isAnyoneActive = True

        crewLen = len(self._getCrewForSkillBooster(skillName) if skillName is not None else skillData.get('crew', []))
        bestActiveTankmanSkill = None
        if crewLen:
            isUseMaxEfficiency = boosterMultiplier is not None or skillName is not None and skillName not in SKIP_SE_PERKS
            bestActiveTankmanSkill = CombinedCrewSkill(tankmanLevel=levelSum / crewLen, levelIncrease=levelIncreaseSum / crewLen, skillsEfficiency=sumSkillsEfficency / crewLen if isUseMaxEfficiency else tankmen.MAX_SKILLS_EFFICIENCY, isTankmanActive=isAnyoneActive)
        ccs = bestActiveTankmanSkill or CombinedCrewSkill(tankmanLevel=0, levelIncrease=0, skillsEfficiency=tankmen.MAX_SKILLS_EFFICIENCY, isTankmanActive=False)
        ccs.hasActiveTankmanForBooster = self._hasActiveTankmanForBooster(skillData)
        ccs.boosterMultiplier = boosterMultiplier
        return ccs

    def _isPerkActive(self, skillName):
        for idxInCrew, level in self._skills.get(skillName, ()):
            if self._activityFlags[idxInCrew]:
                return True

        return False

    def _getSkillsEfficiencyByCrewIdx(self, crewIdx):
        return self._crewSkillsEfficiency.get(crewIdx, tankmen.MAX_SKILLS_EFFICIENCY)

    def _setFactor(self, name, value):
        if name in _ADDITIVE_FACTORS:
            self._factors[name] = self._factors.get(name, 0.0) + value
        else:
            self._factors[name] = self._factors.get(name, 1.0) * value

    def _getEquipmentIdsFromAmmoIter(self):
        g_cache = vehicles.g_cache
        return iter([]) if g_cache is None else g_cache.equipments().iterkeys()

    def _getSkillEquipmentForVehicle(self):
        skillBoosters = {}
        g_cache = vehicles.g_cache
        if g_cache is not None:
            for equipmentID in self._getEquipmentIdsFromAmmoIter():
                equipment = g_cache.equipments().get(equipmentID)
                if equipment is None:
                    continue
                if isinstance(equipment, SkillEquipment):
                    skillBoosters[equipment.skillName] = equipment

        return skillBoosters

    def _validateAndComputeCrew(self):

        def makeError(err):
            return '%s: %s, %s' % (err, repr(crewCompactDescrs), repr(vehicleDescr.name))

        crewCompactDescrs = self._crewCompactDescrs
        vehicleDescr = self._vehicleDescr
        vehicleType = vehicleDescr.type
        crewRoles = vehicleType.crewRoles
        vehicleNationID = vehicleType.id[0]
        skillConfig = tankmen.getSkillsConfig()
        MAX_SKILL_LEVEL = tankmen.MAX_SKILL_LEVEL
        if len(crewCompactDescrs) != len(crewRoles):
            raise SoftException(makeError('wrong number or tankmen'))
        perks = {}
        skills = {}
        skillEquipmentBoosters = self._getSkillEquipmentForVehicle()
        for idxInCrew, tman in enumerate(zip(crewCompactDescrs, crewRoles)):
            compactDescr, roles = tman
            descr = tankmen.TankmanDescr(compactDescr, True)
            if descr.nationID != vehicleNationID:
                raise SoftException(makeError('wrong tankman nation'))
            if descr.role != roles[0]:
                raise SoftException(makeError('wrong tankman role'))
            activeSkills = set()
            for roleName in roles:
                skills.setdefault(roleName, []).append((idxInCrew, float(descr.roleLevel)))
                activeSkills.update(tankmen.SKILLS_BY_ROLES[roleName])

            activeBoosters = {skillName:equipment for skillName, equipment in skillEquipmentBoosters.iteritems() if skillName in activeSkills}
            if descr.isOwnVehicleOrPremium(vehicleDescr.type):
                self._addTankmanSkillRoles(idxInCrew, roles, descr, skillConfig, activeSkills, skills, perks)
            self._addSkillEquipmentRoles(vehicleDescr, idxInCrew, roles, descr, skillConfig, activeBoosters, skills, perks)
            self._crewSkillsEfficiency[idxInCrew] = descr.skillsEfficiency

        if not self._defaultSixthSenseDisabled:
            skills.setdefault('commander_sixthSense', []).append((0, MAX_SKILL_LEVEL * 1.0))
        self._addDuplicateRoles(skillConfig, skills, perks)
        return (skills, perks)

    def _addTankmanSkillRoles(self, tmanIdxInCrew, tmanRoles, tmanDescr, skillConfig, activeSkills, tm_skills, tm_perks):
        for skillName, level in tmanDescr.skillLevels(tmanRoles):
            if skillName not in activeSkills:
                continue
            vsePerk = skillConfig.getSkill(skillName).vsePerk
            tmanLevels = tm_skills.setdefault(skillName, [])
            self.extendAffectedTankman(tmanLevels, tmanIdxInCrew, float(level))
            if vsePerk is not None:
                skillData = tm_perks.setdefault(vsePerk, PerkData(0, CrewContextArgs({'crew': [],
                 'booster': None,
                 'b_crew': set()}))).args.skillData
                skillData['b_crew'].add(tmanIdxInCrew)
                self.extendAffectedTankman(skillData['crew'], tmanIdxInCrew, float(level))

        return

    def _addDuplicateRoles(self, skillConfig, tm_skills, tm_perks):
        for skillName, crew in tm_skills.iteritems():
            if skillName in tankmen.ROLES:
                continue
            b_crew = self._getCrewForSkillBooster(skillName)
            self.extendAffectedCrew(crew, b_crew)
            vsePerk = skillConfig.getSkill(skillName).vsePerk
            if vsePerk is not None:
                skillData = tm_perks.setdefault(vsePerk, PerkData(0, CrewContextArgs({'crew': [],
                 'booster': None,
                 'b_crew': set()}))).args.skillData
                self.extendAffectedCrew(skillData['crew'], b_crew)

        return

    def _addSkillEquipmentRoles(self, vehicleDescr, tmanIdxInCrew, tmanRoles, tmanDescr, skillConfig, skillBoosters, tm_skills, tm_perks):
        for skillName, equipment in skillBoosters.iteritems():
            if not any((role in ROLES_BY_SKILLS[skillName] for role in tmanRoles)):
                continue
            if not tmanDescr.validateSkillEquipment(vehicleDescr, tmanIdxInCrew, equipment):
                continue
            tmanLevels = tm_skills.setdefault(skillName, [])
            self.extendAffectedTankman(tmanLevels, tmanIdxInCrew)
            vsePerk = skillConfig.getSkill(skillName).vsePerk
            if vsePerk is not None:
                skillData = tm_perks.setdefault(vsePerk, PerkData(0, CrewContextArgs({'crew': [],
                 'booster': None,
                 'b_crew': set()}))).args.skillData
                skillData['booster'] = equipment.perkLevelMultiplier
                skillData['b_crew'].add(tmanIdxInCrew)
                self.extendAffectedTankman(skillData['crew'], tmanIdxInCrew)

        return

    @staticmethod
    def extendAffectedTankman(indexLevels, tmanIdxInCrew, level=None):
        if not any((tmanIdxInCrew == idx for idx, _ in indexLevels)):
            indexLevels.append((tmanIdxInCrew, level))

    @staticmethod
    def extendAffectedCrew(indexLevels, affectedCrew):
        for tmanIdxInCrew in affectedCrew:
            VehicleDescrCrew.extendAffectedTankman(indexLevels, tmanIdxInCrew)

    def checkPerksOverLimitForBooster(self, equipment):
        vehicleDescr = self._vehicleDescr
        crewRoles = vehicleDescr.type.crewRoles
        for idxInCrew, tman in enumerate(zip(self._crewCompactDescrs, crewRoles)):
            compactDescr, roles = tman
            descr = tankmen.TankmanDescr(compactDescr, True)
            if descr.validateSkillEquipment(vehicleDescr, idxInCrew, equipment):
                return True

        return False

    def _computeSummSkillLevel(self, skillData, nonCommanderLevelIncrease=0.0, commanderLevelIncrease=0.0, isUseSE=False):
        sumLevel = 0.0
        baseSumLevel = 0.0
        sumEfficiency = 0.0
        skillDataLen = len(skillData)
        if skillDataLen:
            for idx, level in skillData:
                if not self._activityFlags[idx]:
                    continue
                realSkillsEfficiency = self._getSkillsEfficiencyByCrewIdx(idx)
                skillsEfficiency = realSkillsEfficiency if isUseSE else tankmen.MAX_SKILLS_EFFICIENCY
                if level is not None:
                    baseSumLevel += level * skillsEfficiency
                    level += nonCommanderLevelIncrease if idx != self._commanderIdx else commanderLevelIncrease
                    sumLevel += level * skillsEfficiency / tankmen.MAX_SKILL_LEVEL
                sumEfficiency += realSkillsEfficiency

            sumLevel = sumLevel / skillDataLen
            sumEfficiency = sumEfficiency / skillDataLen
            baseSumLevel = baseSumLevel / skillDataLen
        return (baseSumLevel, sumLevel, sumEfficiency)

    def _updateCommanderTutorNotifications(self, tutorAddition):
        pass

    def _crewComp(self):
        roleSkills = {name:data for name, data in self._skills.iteritems() if name in tankmen.ROLES}
        return roleSkills

    _skillProcessors = {'commander': _updateCommanderFactors,
     'radioman': _updateRadiomanFactors,
     'driver': _updateDriverFactors,
     'gunner': _updateGunnerFactors,
     'loader': _updateLoaderFactors,
     'repair': _updateRepairFactors,
     'camouflage': _updateCamouflageFactors,
     'commander_tutor': None,
     'commander_sixthSense': None,
     'commander_eagleEye': _process_commander_eagleEye,
     'commander_enemyShotPredictor': None,
     'commander_practical': None,
     'commander_emergency': None,
     'driver_smoothDriving': None,
     'driver_virtuoso': None,
     'driver_badRoadsKing': None,
     'driver_rammingMaster': None,
     'driver_motorExpert': None,
     'driver_reliablePlacement': None,
     'gunner_smoothTurret': None,
     'gunner_armorer': None,
     'gunner_sniper': None,
     'gunner_rancorous': None,
     'gunner_focus': None,
     'gunner_quickAiming': None,
     'loader_pedant': None,
     'loader_desperado': None,
     'loader_intuition': None,
     'loader_perfectCharge': None,
     'loader_melee': None,
     'loader_ammunitionImprove': None,
     'radioman_finder': None,
     'radioman_expert': None,
     'radioman_sideBySide': None,
     'fireFighting': None,
     'radioman_interference': None,
     'radioman_signalInterception': None}

    def __getUniqueArenaID(self):
        return -1 if not hasattr(self, '_vehicle') else self._vehicle.arenaUniqueID

    def __getVehicleID(self):
        return -1 if not hasattr(self, '_vehicle') else self._vehicle.id

    def recalculateSkills(self):
        self._skills, self._perks = self._validateAndComputeCrew()
