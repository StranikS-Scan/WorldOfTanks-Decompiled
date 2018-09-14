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
        skills, femaleCount = self._validateAndComputeCrew()
        self._skills = skills
        if _DO_DEBUG_LOG:
            items = skills.iteritems()
            for skillName, skillData in sorted(items, cmp=lambda x, y: cmp(x[0], y[0])):
                LOG_DEBUG("TankmanIdxs/levels with skill '%s': %s" % (skillName, str(skillData)))

        self._commanderIdx = skills['commander'][0][0]
        self.__factorsDirty = True
        self._levelIncreaseByVehicle = 0.0
        skillData = skills.get('brotherhood')
        if not (skillData is None or len(skillData) != len(crewCompactDescrs)):
            self._levelIncreaseByBrotherhood = 0 < femaleCount < len(skillData) and 0.0
        else:
            self._levelIncreaseByBrotherhood = tankmen.getSkillsConfig()['brotherhood']['crewLevelIncrease']
        self._camouflageFactor = 1.0
        return

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
        skills = self._skills
        activityFlags = self._activityFlags
        isFire = self._isFire
        crewCompactDescrs = self._crewCompactDescrs
        commanderIdx = self._commanderIdx
        MAX_SKILL_LEVEL = tankmen.MAX_SKILL_LEVEL
        skillsConfig = tankmen.getSkillsConfig()
        commonLevelIncrease = self._levelIncreaseByBrotherhood + self._levelIncreaseByVehicle
        if _DO_DEBUG_LOG:
            LOG_DEBUG('Crew level increase by vehicle={}, by brotherhood={}'.format(self._levelIncreaseByVehicle, self._levelIncreaseByBrotherhood))
        nonCommanderLevelIncrease = self._calcLeverIncreaseForNonCommander(commonLevelIncrease)
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
            else:
                skillData = skills[skillName]
                summLevel, numInactive = self._computeSummSkillLevel(skillData, nonCommanderLevelIncrease=nonCommanderLevelIncrease, commanderLevelIncrease=commonLevelIncrease)
                summLevel += numInactive * universalistAddition
                avgLevel = summLevel / len(skillData)
                avgUpdatedLevel = applier[CREW_ROLE.ALL](avgLevel)
                avgUpdatedLevel = applier[skillName](avgUpdatedLevel)
                efficiency = avgUpdatedLevel / MAX_SKILL_LEVEL
            skillEfficiencies.append((skillName, efficiency))

        for skillName in ('repair', 'fireFighting', 'camouflage'):
            skillData = skills.get(skillName)
            if skillData is None or isFire and skillName != 'fireFighting':
                efficiency = 0.0
            else:
                summLevel, numInactive = self._computeSummSkillLevel(skillData, nonCommanderLevelIncrease=nonCommanderLevelIncrease, commanderLevelIncrease=commonLevelIncrease)
                efficiency = summLevel / (len(crewCompactDescrs) * MAX_SKILL_LEVEL)
            skillEfficiencies.append((skillName, efficiency))

        skillProcessors = self._skillProcessors
        for skillName, efficiency in skillEfficiencies:
            factor = 0.57 + 0.43 * efficiency
            if _DO_DEBUG_LOG:
                LOG_DEBUG("Efficiency/factor of skill '%s': (%s, %s)" % (skillName, efficiency, factor))
            skillProcessors[skillName](self, factor)

        markers = {}
        ROLES_AND_COMMON_SKILLS = tankmen.ROLES_AND_COMMON_SKILLS
        for skillName, skillData in skills.iteritems():
            if skillName in ROLES_AND_COMMON_SKILLS:
                continue
            try:
                for idxInCrew, level in skillData:
                    processor = skillProcessors[skillName]
                    if processor is not None:
                        levelIncrease = commonLevelIncrease if idxInCrew == commanderIdx else nonCommanderLevelIncrease
                        processor(self, idxInCrew, level, levelIncrease, activityFlags[idxInCrew], isFire, skillsConfig[skillName], markers)

            except:
                LOG_ERROR('Failed to compute skill (arenaUniqueID, vehicleID, skillName, skillData):', self.__getUniqueArenaID(), self.__getVehicleID(), skillName, skillData, stack=True)
                LOG_CURRENT_EXCEPTION()

        self._factorsDirty = False
        return

    def _updateCommanderFactors(self, factor):
        self._factors['circularVisionRadius'] = factor

    def _updateRadiomanFactors(self, factor):
        self._factors['radio/distance'] = factor

    def _updateDriverFactors(self, factor):
        factor = 1.0 / factor
        r = self._terrainResistanceFactors
        r[0] *= factor
        r[1] *= factor
        r[2] *= factor

    def _updateLoaderFactors(self, factor):
        self._factors['gun/reloadTime'] = 1.0 / factor
        if self._stunFactors is not None:
            self._factors['gun/reloadTime'] *= self._stunFactors['reloadTime']
        return

    def _updateGunnerFactors(self, factor):
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
        return

    def _updateRepairFactors(self, factor):
        self._factors['repairSpeed'] = factor

    def _updateFireFightingFactors(self, factor):
        self._factors['healthBurnPerSecLossFraction'] = factor

    def _updateCamouflageFactors(self, factor):
        self._camouflageFactor = factor

    def _process_commander_eagleEye(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig, markers, factorPerLevel=None):
        if not isActive or isFire:
            return
        else:
            if factorPerLevel is None:
                factorPerLevel = skillConfig['distanceFactorPerLevelWhenDeviceWorking']
            self._setFactor('circularVisionRadius', 1.0 + (level + levelIncrease) * factorPerLevel)
            if _DO_DEBUG_LOG:
                LOG_DEBUG("commander_eagleEye: factors['circularVisionRadius']: %s" % self._factors['circularVisionRadius'])
            return

    def _process_driver_virtuoso(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig, markers):
        if not isActive or isFire:
            return
        self._setFactor('vehicle/rotationSpeed', 1.0 + (level + levelIncrease) * skillConfig['rotationSpeedFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG("driver_virtuoso: factors['vehicle/rotationSpeed']: %s" % self._factors['vehicle/rotationSpeed'])

    def _process_driver_badRoadsKing(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig, markers):
        if not isActive or isFire:
            return
        level = level + levelIncrease
        r = self._terrainResistanceFactors
        r[1] *= max(0.001, 1.0 - level * skillConfig['mediumGroundResistanceFactorPerLevel'])
        r[2] *= max(0.001, 1.0 - level * skillConfig['softGroundResistanceFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG('driver_badRoadsKing: terrainResistanceFactors: %s' % str(self._terrainResistanceFactors))

    def _process_radioman_finder(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig, markers):
        if isFire or 'radioman_finder' in markers:
            return
        maxLevel = self._getMaxActiveSkillLevelAndSetMarker('radioman_finder', levelIncrease, markers)
        if not maxLevel:
            return
        self._setFactor('circularVisionRadius', 1.0 + maxLevel * skillConfig['visionRadiusFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG("radioman_finder: factors['circularVisionRadius']: %s" % self._factors['circularVisionRadius'])

    def _process_radioman_inventor(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig, markers):
        if isFire or 'radioman_inventor' in markers:
            return
        maxLevel = self._getMaxActiveSkillLevelAndSetMarker('radioman_inventor', levelIncrease, markers)
        if not maxLevel:
            return
        self._setFactor('radio/distance', 1.0 + maxLevel * skillConfig['radioDistanceFactorPerLevel'])
        if _DO_DEBUG_LOG:
            LOG_DEBUG("radioman_inventor: factors['radio/distance']: %s" % self._factors['radio/distance'])

    def _getMaxActiveSkillLevelAndSetMarker(self, skillName, levelIncrease, markers):
        maxLevel = 0
        skillHolders = self._skills[skillName]
        if len(skillHolders) > 1:
            markers[skillName] = True
        for idxInCrew, level in skillHolders:
            level = level + levelIncrease
            if level > maxLevel and self._activityFlags[idxInCrew]:
                maxLevel = level

        return maxLevel

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
        femaleCount = 0
        for compactDescr, roles in zip(crewCompactDescrs, crewRoles):
            descr = tankmen.TankmanDescr(compactDescr, True)
            if descr.nationID != vehicleNationID:
                raise Exception(makeError('wrong tankman nation'))
            if descr.role != roles[0]:
                raise Exception(makeError('wrong tankman role'))
            femaleCount += int(descr.isFemale)
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

        return (res, femaleCount)

    def _computeSummSkillLevel(self, skillData, nonCommanderLevelIncrease=0.0, commanderLevelIncrease=0.0):
        summLevel = 0.0
        numInactive = 0
        for idx, level in skillData:
            if not self._activityFlags[idx]:
                numInactive += 1
                continue
            summLevel += level
            summLevel += nonCommanderLevelIncrease if idx != self._commanderIdx else commanderLevelIncrease

        return (summLevel, numInactive)

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
     'gunner_woodHunter': None,
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
