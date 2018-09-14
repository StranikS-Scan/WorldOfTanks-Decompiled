# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/VehicleDescrCrew.py
import tankmen
from debug_utils import *
from qualifiers import CREW_ROLE
_DO_DEBUG_LOG = False

class VehicleDescrCrew(object):

    def __init__(self, vehicleDescr, crewCompactDescrs, mainSkillQualifiersApplier, activityFlags=None, isFire=False, stunFactors=None):
        if activityFlags is None:
            activityFlags = [True] * len(crewCompactDescrs)
        self._vehicleDescr = vehicleDescr
        self._crewCompactDescrs = crewCompactDescrs
        self._activityFlags = activityFlags
        self._isFire = isFire
        self._stunFactors = stunFactors
        self._mainSkillQualifiersApplier = mainSkillQualifiersApplier
        skills = self._validateAndComputeCrew()
        self._skills = skills
        if _DO_DEBUG_LOG:
            items = skills.iteritems()
            for skillName, skillData in sorted(items, cmp=lambda x, y: cmp(x[0], y[0])):
                LOG_DEBUG("TankmanIdxs/levels with skill '%s': %s" % (skillName, str(skillData)))

        self._commanderIdx = skills['commander'][0][0]
        self.__factorsDirty = True
        self._levelIncreaseByVehicle = 0.0
        skillData = skills.get('brotherhood')
        if skillData is None or len(skillData) != len(crewCompactDescrs):
            self._levelIncreaseByBrotherhood = 0.0
        else:
            self._levelIncreaseByBrotherhood = tankmen.getSkillsConfig()['brotherhood']['crewLevelIncrease']
        self._camouflageFactor = 1.0
        self._boostedSkills = {}
        return

    def boostSkillBy(self, equipment):
        self._boostedSkills[equipment.skillName] = equipment
        self._factorsDirty = True

    def discardSkillBoostBy(self, equipment):
        del self._boostedSkills[equipment.skillName]
        self._factorsDirty = True

    def callSkillProcessor(self, skillName, *args):
        try:
            skillProcessor = self._skillProcessors.get(skillName)
            if skillProcessor is None:
                return
            equipment = self._boostedSkills.get(skillName)
            if equipment is not None:
                args = equipment.updateCrewSkill(*args)
            skillProcessor(self, *args)
        except:
            LOG_ERROR('Failed to process skill (arenaUniqueID, vehicleID, skillName, skillData):', self.__getUniqueArenaID(), self.__getVehicleID(), skillName, self._skills[skillName], stack=True)
            LOG_CURRENT_EXCEPTION()

        return

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
        if self._levelIncreaseByVehicle != factors['crewLevelIncrease']:
            self._levelIncreaseByVehicle = factors['crewLevelIncrease']
            self._factorsDirty = True
        if self._factorsDirty:
            self._buildFactors()
        for name, value in self._factors.iteritems():
            try:
                factors[name] *= value
            except:
                pass

        try:
            r = factors['chassis/terrainResistance']
            value = self._terrainResistanceFactors
            r[0] *= value[0]
            r[1] *= value[1]
            r[2] *= value[2]
        except:
            pass

    def _calcLeverIncreaseForNonCommander(self, commonLevelIncrease):
        applier = self._mainSkillQualifiersApplier
        if not self._activityFlags[self._commanderIdx]:
            levelIncreaseByCommander = 0.0
        else:
            commanderLevel = self._skills['commander'][0][1] + commonLevelIncrease
            commanderUpdatedLevel = applier[CREW_ROLE.ALL](commanderLevel)
            commanderUpdatedLevel = applier['commander'](commanderUpdatedLevel)
            levelIncreaseByCommander = commanderUpdatedLevel / tankmen.COMMANDER_ADDITION_RATIO
        result = commonLevelIncrease + levelIncreaseByCommander
        if _DO_DEBUG_LOG:
            LOG_DEBUG('levelIncreaseByCommander={}'.format(levelIncreaseByCommander))
            LOG_DEBUG('nonCommanderLeverIncrease={}'.format(result))
        return result

    def _buildFactors(self):
        self._factors = {}
        self._shotDispFactor = 1.0
        self._terrainResistanceFactors = [1.0, 1.0, 1.0]
        commonLevelIncrease = self._levelIncreaseByBrotherhood + self._levelIncreaseByVehicle
        nonCommanderLevelIncrease = self._calcLeverIncreaseForNonCommander(commonLevelIncrease)
        if _DO_DEBUG_LOG:
            LOG_DEBUG('Crew level increase by vehicle={}, by brotherhood={}'.format(self._levelIncreaseByVehicle, self._levelIncreaseByBrotherhood))
        skillEfficiencies = self._calculateSkillEfficiencies(commonLevelIncrease, nonCommanderLevelIncrease)
        self._processSkills(skillEfficiencies, commonLevelIncrease, nonCommanderLevelIncrease)
        self._factorsDirty = False

    def _calculateSkillEfficiencies(self, commonLevelIncrease, nonCommanderLevelIncrease):
        skills = self._skills
        activityFlags = self._activityFlags
        isFire = self._isFire
        commanderIdx = self._commanderIdx
        MAX_SKILL_LEVEL = tankmen.MAX_SKILL_LEVEL
        skillsConfig = tankmen.getSkillsConfig()
        skillEfficiencies = []
        universalistAddition = 0
        numInactive = activityFlags.count(False)
        if numInactive and activityFlags[commanderIdx]:
            level = skills.get('commander_universalist')
            if level is not None:
                level = level[0][1]
                universalistAddition = (level + commonLevelIncrease) / numInactive
                universalistAddition *= skillsConfig['commander_universalist']['efficiency']
        applier = self._mainSkillQualifiersApplier
        for skillName in tankmen.ROLES:
            if isFire:
                efficiency = 0.0
                baseAvgLevel = 0.0
            else:
                skillData = skills[skillName]
                baseSummLevel, summLevel, numInactive = self._computeSummSkillLevel(skillData, nonCommanderLevelIncrease=nonCommanderLevelIncrease, commanderLevelIncrease=commonLevelIncrease)
                summLevel += numInactive * universalistAddition
                avgLevel = summLevel / len(skillData)
                avgUpdatedLevel = applier[CREW_ROLE.ALL](avgLevel)
                avgUpdatedLevel = applier[skillName](avgUpdatedLevel)
                efficiency = avgUpdatedLevel / MAX_SKILL_LEVEL
                baseAvgLevel = baseSummLevel / len(skillData)
            skillEfficiencies.append((skillName, efficiency, baseAvgLevel))

        for skillName in ('repair', 'fireFighting', 'camouflage'):
            skillData = skills.get(skillName)
            if skillData is None or isFire and skillName != 'fireFighting':
                efficiency = 0.0
                baseAvgLevel = 0.0
            else:
                baseSummLevel, summLevel, numInactive = self._computeSummSkillLevel(skillData, nonCommanderLevelIncrease=nonCommanderLevelIncrease, commanderLevelIncrease=commonLevelIncrease)
                efficiency = summLevel / (len(self._crewCompactDescrs) * MAX_SKILL_LEVEL)
                baseAvgLevel = baseSummLevel / len(skillData)
            skillEfficiencies.append((skillName, efficiency, baseAvgLevel))

        return skillEfficiencies

    def _processSkills(self, skillEfficiencies, commonLevelIncrease, nonCommanderLevelIncrease):
        skills = self._skills
        isFire = self._isFire
        skillsConfig = tankmen.getSkillsConfig()
        skillToBoost = set(self._boostedSkills.iterkeys())
        for skillName, efficiency, baseAvgLevel in skillEfficiencies:
            factor = 0.57 + 0.43 * efficiency
            skillToBoost.discard(skillName)
            self.callSkillProcessor(skillName, factor, baseAvgLevel)

        ROLES_AND_COMMON_SKILLS = tankmen.ROLES_AND_COMMON_SKILLS
        for skillName, skillData in skills.iteritems():
            if skillName in ROLES_AND_COMMON_SKILLS:
                continue
            bestTankman = self._findBestTankmanForSkill(skillData, nonCommanderLevelIncrease=nonCommanderLevelIncrease, commanderLevelIncrease=commonLevelIncrease)
            if bestTankman is None:
                continue
            skillToBoost.discard(skillName)
            idxInCrew, level, levelIncrease, isActive = bestTankman
            self.callSkillProcessor(skillName, idxInCrew, level, levelIncrease, isActive, isFire, skillsConfig[skillName])

        for skillName in skillToBoost:
            self.callSkillProcessor(skillName, None, 0, 0, True, False, skillsConfig[skillName])

        return

    def _updateCommanderFactors(self, factor, baseAvgLevel):
        self._factors['circularVisionRadius'] = factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('commander', factor, baseAvgLevel))

    def _updateRadiomanFactors(self, factor, baseAvgLevel):
        self._factors['radio/distance'] = factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('radioman', factor, baseAvgLevel))

    def _updateDriverFactors(self, factor, baseAvgLevel):
        factor = 1.0 / factor
        r = self._terrainResistanceFactors
        r[0] *= factor
        r[1] *= factor
        r[2] *= factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('driver', factor, baseAvgLevel))

    def _updateLoaderFactors(self, factor, baseAvgLevel):
        self._factors['gun/reloadTime'] = 1.0 / factor
        if self._stunFactors is not None:
            self._factors['gun/reloadTime'] *= self._stunFactors['reloadTime']
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('loader', factor, baseAvgLevel))
        return

    def _updateGunnerFactors(self, factor, baseAvgLevel):
        factors = self._factors
        factors['turret/rotationSpeed'] = factor
        factors['gun/rotationSpeed'] = factor
        factors['gun/aimingTime'] = 1.0 / factor
        self._shotDispFactor = 1.0 / factor
        if self._stunFactors is not None:
            sf = self._stunFactors
            factors['turret/rotationSpeed'] *= sf['turretRotationSpeed']
            factors['gun/rotationSpeed'] *= sf['gunRotationSpeed']
            factors['gun/aimingTime'] *= sf['aimingTime']
            self._shotDispFactor *= sf['shotDispersion']
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('gunner', factor, baseAvgLevel))
        return

    def _updateRepairFactors(self, factor, baseAvgLevel):
        self._factors['repairSpeed'] = factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('repair', factor, baseAvgLevel))

    def _updateFireFightingFactors(self, factor, baseAvgLevel):
        self._factors['healthBurnPerSecLossFraction'] = factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('fireFighting', factor, baseAvgLevel))

    def _updateCamouflageFactors(self, factor, baseAvgLevel):
        self._camouflageFactor = factor
        if _DO_DEBUG_LOG:
            LOG_DEBUG("Factor/baseAvgLevel of skill '%s': (%s, %s)" % ('camouflage', factor, baseAvgLevel))

    def _process_commander_eagleEye(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig, factorPerLevel=None):
        if not isActive or isFire:
            return
        else:
            if factorPerLevel is None:
                factorPerLevel = skillConfig['distanceFactorPerLevelWhenDeviceWorking']
            self._setFactor('circularVisionRadius', 1.0 + (level + levelIncrease) * factorPerLevel)
            if _DO_DEBUG_LOG:
                LOG_DEBUG("commander_eagleEye: factors['circularVisionRadius']: %s" % self._factors['circularVisionRadius'])
            return

    def _process_driver_virtuoso(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if not isActive or isFire:
            return
        self._setFactor('vehicle/rotationSpeed', 1.0 + (level + levelIncrease) * skillConfig['rotationSpeedFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG("driver_virtuoso: factors['vehicle/rotationSpeed']: %s" % self._factors['vehicle/rotationSpeed'])

    def _process_driver_badRoadsKing(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if not isActive or isFire:
            return
        level = level + levelIncrease
        r = self._terrainResistanceFactors
        r[1] *= max(0.001, 1.0 - level * skillConfig['mediumGroundResistanceFactorPerLevel'])
        r[2] *= max(0.001, 1.0 - level * skillConfig['softGroundResistanceFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG('driver_badRoadsKing: terrainResistanceFactors: %s' % str(self._terrainResistanceFactors))

    def _process_radioman_finder(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if not isActive or isFire:
            return
        self._setFactor('circularVisionRadius', 1.0 + (level + levelIncrease) * skillConfig['visionRadiusFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG("radioman_finder: factors['circularVisionRadius']: %s" % self._factors['circularVisionRadius'])

    def _process_radioman_inventor(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if not isActive or isFire:
            return
        self._setFactor('radio/distance', 1.0 + (level + levelIncrease) * skillConfig['radioDistanceFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG("radioman_inventor: factors['radio/distance']: %s" % self._factors['radio/distance'])

    def _findBestTankmanForSkill(self, skillData, nonCommanderLevelIncrease=0.0, commanderLevelIncrease=0.0):
        commanderIdx = self._commanderIdx
        bestActiveTankman = None
        bestInactiveTankman = None
        maxActiveLevel = 0
        maxInactiveLevel = 0
        for idxInCrew, level in skillData:
            levelIncrease = commanderLevelIncrease if idxInCrew == commanderIdx else nonCommanderLevelIncrease
            if self._activityFlags[idxInCrew]:
                if level + levelIncrease > maxActiveLevel:
                    bestActiveTankman = (idxInCrew,
                     level,
                     levelIncrease,
                     True)
                    maxActiveLevel = level + levelIncrease
            if level + levelIncrease > maxInactiveLevel:
                bestInactiveTankman = (idxInCrew,
                 level,
                 levelIncrease,
                 False)
                maxInactiveLevel = level + levelIncrease

        return bestActiveTankman or bestInactiveTankman

    def _isPerkActive(self, skillName):
        for idxInCrew, level in self._skills.get(skillName, ()):
            if self._activityFlags[idxInCrew]:
                return True

        return False

    def _setFactor(self, name, value):
        self._factors[name] = self._factors.get(name, 1.0) * value

    def _validateAndComputeCrew(self):

        def makeError(err):
            return '%s: %s, %s' % (err, repr(crewCompactDescrs), repr(vehicleDescr.name))

        crewCompactDescrs = self._crewCompactDescrs
        vehicleDescr = self._vehicleDescr
        vehicleType = vehicleDescr.type
        crewRoles = vehicleType.crewRoles
        vehicleNationID = vehicleType.id[0]
        MAX_SKILL_LEVEL = tankmen.MAX_SKILL_LEVEL
        PERKS = tankmen.PERKS
        if len(crewCompactDescrs) != len(crewRoles):
            raise Exception(makeError('wrong number or tankmen'))
        res = {}
        idxInCrew = 0
        for compactDescr, roles in zip(crewCompactDescrs, crewRoles):
            descr = tankmen.TankmanDescr(compactDescr, True)
            if descr.nationID != vehicleNationID:
                raise Exception(makeError('wrong tankman nation'))
            if descr.role != roles[0]:
                raise Exception(makeError('wrong tankman role'))
            factor, addition = descr.efficiencyOnVehicle(vehicleDescr)
            activeSkills = set()
            level = descr.roleLevel * factor + addition
            for skillName in roles:
                res.setdefault(skillName, []).append((idxInCrew, level))
                activeSkills.update(tankmen.SKILLS_BY_ROLES[skillName])

            for skillName, level in descr.skillLevels:
                if skillName not in activeSkills:
                    continue
                if skillName not in PERKS:
                    level = level * factor + addition
                    res.setdefault(skillName, []).append((idxInCrew, level))
                if level == MAX_SKILL_LEVEL:
                    res.setdefault(skillName, []).append((idxInCrew, level))

            idxInCrew += 1

        return res

    def _computeSummSkillLevel(self, skillData, nonCommanderLevelIncrease=0.0, commanderLevelIncrease=0.0):
        summLevel = 0.0
        baseSummLevel = 0.0
        numInactive = 0
        for idx, level in skillData:
            if not self._activityFlags[idx]:
                numInactive += 1
                continue
            baseSummLevel += level
            summLevel += level
            summLevel += nonCommanderLevelIncrease if idx != self._commanderIdx else commanderLevelIncrease

        return (baseSummLevel, summLevel, numInactive)

    _skillProcessors = {'commander': _updateCommanderFactors,
     'radioman': _updateRadiomanFactors,
     'driver': _updateDriverFactors,
     'gunner': _updateGunnerFactors,
     'loader': _updateLoaderFactors,
     'repair': _updateRepairFactors,
     'fireFighting': _updateFireFightingFactors,
     'camouflage': _updateCamouflageFactors,
     'commander_universalist': None,
     'commander_tutor': None,
     'commander_expert': None,
     'commander_sixthSense': None,
     'commander_eagleEye': _process_commander_eagleEye,
     'driver_tidyPerson': None,
     'driver_smoothDriving': None,
     'driver_virtuoso': _process_driver_virtuoso,
     'driver_badRoadsKing': _process_driver_badRoadsKing,
     'driver_rammingMaster': None,
     'gunner_smoothTurret': None,
     'gunner_gunsmith': None,
     'gunner_sniper': None,
     'gunner_rancorous': None,
     'loader_pedant': None,
     'loader_desperado': None,
     'loader_intuition': None,
     'radioman_finder': _process_radioman_finder,
     'radioman_inventor': _process_radioman_inventor,
     'radioman_lastEffort': None,
     'radioman_retransmitter': None}

    def __getUniqueArenaID(self):
        return -1 if not hasattr(self, '_vehicle') else self._vehicle.arenaUniqueID

    def __getVehicleID(self):
        return -1 if not hasattr(self, '_vehicle') else self._vehicle.id
