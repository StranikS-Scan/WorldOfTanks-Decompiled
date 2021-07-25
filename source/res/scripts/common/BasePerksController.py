# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BasePerksController.py
from collections import defaultdict
from operator import mul
from typing import Union, List, Dict, Tuple, Callable, Optional, Hashable
from PerkPlanHolder import PCPlanHolder
from debug_utils import LOG_DEBUG_DEV, LOG_DEBUG, LOG_ERROR
from data_structures import DynamicFactorCollectorKeyError
from constants import IS_DEVELOPMENT, CREW_CRIT_FACTOR_MOD_SUFFIX, CommonSkillFactors
from items import tankmen
_DO_DEBUG_LOG = False
PERK_SHOT_DISPERSION_FACTOR = 'perkShotDispersion'
PERK_SHOT_DISPERSION_WHILE_GUN_DAMAGED_MOD = 'perkShotDispersionWhileGunDamagedMod'
PERK_SHOT_DISPERSION_FACTORS = (PERK_SHOT_DISPERSION_FACTOR, PERK_SHOT_DISPERSION_WHILE_GUN_DAMAGED_MOD)

class BasePerksController(object):
    _multiplicativeAttributeFactors = {'gun/aimingTime',
     'repairSpeed',
     'gun/shotDispersionFactors/turretRotation',
     'chassis/shotDispersionFactors/movement',
     'chassis/shotDispersionFactors/rotation',
     'crewChanceToHitFactor',
     'engine/fireStartingChance',
     'camouflageFactor',
     'radio/distance',
     'turret/rotationSpeed',
     'healthBurnPerSecLossFraction',
     'vehicle/rotationSpeed',
     'engine/power',
     'xRayFactor',
     'foliageInvisibilityFactor',
     'circularVisionRadius',
     'gun/reloadTime',
     'gun/rotationSpeed',
     'invisibilityFactorAtShot',
     'demaskMovingFactor',
     'demaskFoliageFactor',
     'tankAcceleration',
     'reverseEnginePower',
     'gun/changeShell/reloadFactor'}
    _additiveAttributeFactors = {'crewMasteryFactor',
     'radioDistanceFactor',
     'stunResistanceEffect',
     'stunResistanceDuration'}
    _multiplicativeDynamicFactors = {'ammoBayHealthFactor',
     'engineHealthFactor',
     'fuelTankHealthFactor',
     'turretRotatorHealthFactor',
     'radioHealthFactor',
     'engineCritPenaltyReduce',
     'ammoBayCritPenaltyReduce',
     'explosiveDamageResistanceFactor',
     'trackRammingDamageFactor',
     'turretRotatorCritPenaltyReduce'}
    _additiveDynamicFactors = {'criticalHitChanceBoost',
     'damageDistributionLowerBound',
     'piercingDistributionLowerBound',
     'damageDistributionUpperBound',
     'piercingDistributionUpperBound',
     'sixthSenseTimeDelay',
     'rammingDamageBonus',
     'minStunDuration',
     'rammingDamageReduction',
     'fallDamageReductionPercent',
     'damageChanceToInnerModules',
     'rancorousTimeDelay',
     'decreaseOwnSpottingTime',
     'postMortemVision'}

    def __init__(self, owner, scopedPerks):
        LOG_DEBUG_DEV('ABILITY_SYSTEM DEBUG scopedPerks: {} '.format(scopedPerks))
        self._owner = owner
        self._scopedPerks = scopedPerks
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))
        self._attrFactorCollectors = {}
        self.dynamicFactorCollectors = {}
        self._buildAttributeFactorsCollectorMap()
        self._buildDynamicFactorsCollectorMap()
        self._scopedPerksToFactors = defaultdict(lambda : defaultdict(set))
        self._planHolder = None
        self._scheduledPlans = defaultdict(list)
        return

    @property
    def vehicleID(self):
        return self._owner.id

    def init(self, isAutoStart=False, contextCreator=None):
        self._planHolder = PCPlanHolder(self._scopedPerks)
        self._planHolder.loadPlan(contextCreator, self._owner, isAutoStart)

    def start(self):
        self._planHolder.start()

    def clean(self):
        self._scopedPerks = ()
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))
        self._planHolder.clean()

    def destroy(self):
        self._destroyPlanHolder()
        self._attrFactorCollectors = {}
        self.dynamicFactorCollectors = {}
        self._scopedPerks = ()
        self._owner = None
        return

    def modifyFactor(self, factor, scopeID, perkID, value):
        self._modifiedFactors[factor][scopeID].append((perkID, value))
        self._scopedPerksToFactors[scopeID][perkID].add(factor)

    def removeNumFactorModifiers(self, factor, scopeID, perkID, numMods):
        mods = self._modifiedFactors[factor][scopeID]
        for mod in reversed(mods):
            if mod[0] == perkID:
                mods.remove(mod)
                numMods -= 1
                if numMods == 0:
                    return

    def dropFactorModifiers(self, factor, scopeID, perkID):
        mods = self._modifiedFactors[factor][scopeID]
        mods[:] = filter(lambda t: t[0] != perkID, mods)

    def dropAllPerkModifiers(self, scopeID, perkID):
        for scopes in self._modifiedFactors.values():
            scope = scopes[scopeID]
            scope[:] = filter(lambda t: t[0] != perkID, scope)

        return self._scopedPerksToFactors[scopeID].pop(perkID, set())

    def triggerVSPlanEvent(self, event):
        self._planHolder.triggerVSPlanEvent(event)

    def collectDynamicFactor(self, factorName):
        if factorName not in self.dynamicFactorCollectors:
            raise DynamicFactorCollectorKeyError(factorName)
        return self.dynamicFactorCollectors[factorName](factorName)

    def onCollectFactors(self, factors):
        if _DO_DEBUG_LOG and IS_DEVELOPMENT:
            oldFactors = factors.copy()
        for factorName in factors.iterkeys():
            try:
                collector = self._attrFactorCollectors[factorName]
            except KeyError:
                if factorName in self._modifiedFactors:
                    LOG_ERROR('ABILITY_SYSTEM ERROR factor {} was modified but does not have a collector.'.format(factorName))
                continue

            collector(factorName, factors)

        if _DO_DEBUG_LOG and IS_DEVELOPMENT:
            LOG_DEBUG('ABILITY_SYSTEM DEBUG onCollectFactors, factors diff: {}'.format([ '{} {} -> {}'.format(k, oldFactors[k], factors[k]) for k in self._modifiedFactors if k in factors and oldFactors[k] != factors[k] ]))

    def onCollectShotDispersionFactors(self, factors):
        factors[0] *= self._collectModifiersMulScopes(self._modifiedFactors[PERK_SHOT_DISPERSION_FACTOR])

    def getCrewFactors(self):
        return {f:self.collectAddivieModsForFactor(f) for f in CommonSkillFactors.ALL if f in self._modifiedFactors}

    def collectShotDispersionWhileGunDamagedFactor(self):
        return self._collectModifiersAddScopes(self._modifiedFactors[PERK_SHOT_DISPERSION_WHILE_GUN_DAMAGED_MOD])

    def addMultiplicativeCollector(self, key):
        self.dynamicFactorCollectors[key] = self.collectMultiplicativeModsForFactor

    def addAdditiveCollector(self, key):
        self.dynamicFactorCollectors[key] = self.collectAddivieModsForFactor

    def collectMultiplicativeModsForFactor(self, key):
        return self._collectModifiersMulScopes(self._modifiedFactors[key])

    def collectAddivieModsForFactor(self, key):
        return self._collectModifiersAddScopes(self._modifiedFactors[key])

    def startPerkNotify(self, scopeId, perkId):
        if scopeId not in self._scheduledPlans or perkId not in self._scheduledPlans[scopeId]:
            return
        self._scheduledPlans[scopeId].remove(perkId)
        if not self._scheduledPlans[scopeId]:
            self._scheduledPlans.pop(scopeId)
        if self._allPerksLoaded():
            self._planHolder.setReady()

    def _destroyPlanHolder(self):
        if self._planHolder is not None:
            self._planHolder.destroy()
            self._planHolder = None
        return

    def _buildAttributeFactorsCollectorMap(self):
        self._attrFactorCollectors.update({key:self._collectMultiplicativeAttributeFactor for key in self._multiplicativeAttributeFactors})
        self._attrFactorCollectors.update({key:self._collectAdditiveAttributeFactor for key in self._additiveAttributeFactors})
        self._attrFactorCollectors.update({'chassis/terrainResistance': self._collectTerrainResistance,
         'invisibility': self._collectInvisibility,
         'damageMonitoringDelay': self._collectDamageMonitoringDelay})

    def _buildDynamicFactorsCollectorMap(self):
        self.dynamicFactorCollectors.update({key:self.collectMultiplicativeModsForFactor for key in self._multiplicativeDynamicFactors})
        self.dynamicFactorCollectors.update({key:self.collectAddivieModsForFactor for key in self._additiveDynamicFactors})
        self.dynamicFactorCollectors.update({role + CREW_CRIT_FACTOR_MOD_SUFFIX:self.collectAddivieModsForFactor for role in tankmen.ROLES})

    def _collectModifiersMulScopes(self, scopes):
        return reduce(mul, (1 + sum((v[1] for v in mods)) for mods in scopes.itervalues()), 1.0)

    def _collectModifiersAddScopes(self, scopes):
        return sum((sum((v[1] for v in mods)) for mods in scopes.itervalues()))

    def _collectMultiplicativeAttributeFactor(self, key, factors):
        factors[key] *= self._collectModifiersMulScopes(self._modifiedFactors[key])

    def _collectAdditiveAttributeFactor(self, key, factors):
        factors[key] += self._collectModifiersAddScopes(self._modifiedFactors[key])

    def _collectInvisibility(self, invisibilityKey, factors):
        invisibility = factors[invisibilityKey]
        invisibility[0] += self._collectModifiersAddScopes(self._modifiedFactors['invisibilityAdd'])
        invisibility[1] *= self._collectModifiersMulScopes(self._modifiedFactors['invisibilityMul'])

    def _collectDamageMonitoringDelay(self, key, factors):
        scopes = self._modifiedFactors.get(key)
        if not scopes:
            return
        minV = factors[key]
        for mods in scopes.itervalues():
            if mods:
                minV = min(minV, min((x[1] for x in mods)))

        factors[key] = min(factors[key], minV)

    def _collectTerrainResistance(self, terrainResKey, factors):
        terrainResistance = factors[terrainResKey]
        for scope in self._modifiedFactors[terrainResKey].itervalues():
            tmp = [1] * 3
            for _, mod in scope:
                tmp[0] += mod[0]
                tmp[1] += mod[1]
                tmp[2] += mod[2]

            terrainResistance[0] *= tmp[0]
            terrainResistance[1] *= tmp[1]
            terrainResistance[2] *= tmp[2]

    def _schedulePlans(self):
        self._scheduledPlans = defaultdict(list)
        for scopeId, scopeData in self._scopedPerks.items():
            for perkId, _ in scopeData:
                self._scheduledPlans[scopeId].append(perkId)

    def _allPerksLoaded(self):
        return not self._scheduledPlans
