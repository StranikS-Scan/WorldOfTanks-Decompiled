# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BasePerksController.py
from collections import defaultdict
import weakref
from operator import mul
from typing import Union, List, Dict, Tuple, TYPE_CHECKING, Optional, Hashable, Set, Any
from PerkPlanHolder import PCPlanHolder
from debug_utils import LOG_DEBUG_DEV, LOG_ERROR, LOG_DEBUG, LOG_WARNING
from data_structures import DynamicFactorCollectorKeyError
from constants import IS_DEVELOPMENT
from perks.PerksLoadStrategy import LoadType
if TYPE_CHECKING:
    from constants import PerkData
_DO_DEBUG_LOG = False
PERK_SHOT_DISPERSION_FACTOR = 'perkShotDispersion'
PERK_SHOT_DISPERSION_WHILE_GUN_DAMAGED_MOD = 'perkShotDispersionWhileGunDamagedMod'
PERK_SHOT_DISPERSION_FACTORS = (PERK_SHOT_DISPERSION_FACTOR, PERK_SHOT_DISPERSION_WHILE_GUN_DAMAGED_MOD)

def creatorTemplate(context, impl, controllerRef):

    def creator(*args):
        return context(impl, controllerRef, *args)

    return creator


class BasePerksController(object):
    _multiplicativeAttributeFactors = {'gun/aimingTime',
     'repairSpeed',
     'gun/shotDispersionFactors/turretRotation',
     'chassis/shotDispersionFactors/movement',
     'chassis/shotDispersionFactors/rotation',
     'crewChanceToHitFactor',
     'engine/fireStartingChance',
     'radio/distance',
     'turret/rotationSpeed',
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
     'gun/changeShell/reloadFactor',
     'crewRolesFactor'}
    _additiveAttributeFactors = {'crewLevelIncrease',
     'healthBurnPerSecLossFraction',
     'stunResistanceEffect',
     'stunResistanceDuration',
     'radioDistanceFactor',
     'vehicle/bkMaxSpeedBonus',
     'vehicle/fwMaxSpeedBonus'}
    _multiplicativeDynamicFactors = {'ammoBayHealthFactor',
     'engineHealthFactor',
     'fuelTankHealthFactor',
     'turretRotatorHealthFactor',
     'radioHealthFactor',
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
     'decreaseOwnSpottingTime',
     'rancorousTimeDelay'}
    _scopeContextMap = {}

    def __init__(self, owner, scopedPerks):
        LOG_DEBUG_DEV('ABILITY_SYSTEM DEBUG scopedPerks: {} '.format(scopedPerks))
        self._owner = owner
        self._scopedPerks = self._assignContextsToScopes(scopedPerks)
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))
        self._attrFactorCollectors = {}
        self.dynamicFactorCollectors = {}
        self._buildAttributeFactorsCollectorMap()
        self._buildDynamicFactorsCollectorMap()
        self._scopedPerksToFactors = defaultdict(lambda : defaultdict(set))
        self._planHolder = None
        return

    @property
    def vehicleID(self):
        return self._owner.id

    def init(self, loadType=LoadType.DEFAULT):
        self._planHolder = PCPlanHolder(self._scopedPerks, self._owner, loadType)
        self._planHolder.loadPlans()

    def start(self):
        self._planHolder.start()

    def beforeBattleStart(self):
        self._planHolder.beforeBattleStart()

    def clean(self):
        self._scopedPerks = ()
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))

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

    def rebuildDynamicFactorCollectorMap(self):
        self.dynamicFactorCollectors = {}
        self._buildDynamicFactorsCollectorMap()

    def updateScopedPerks(self, newScopedPerks):
        newScopedPerks = self._assignContextsToScopes(newScopedPerks)
        self._planHolder.setScopedPerks(newScopedPerks)
        for scope in self._scopeContextMap.iterkeys():
            oldScope = self._scopedPerks.get(scope)
            newScope = newScopedPerks.get(scope)
            oldPerks = self._getPerkIDs(oldScope)
            newPerks = self._getPerkIDs(newScope)
            addedPerks = newPerks - oldPerks
            self._logUpdatedPerks('updateScopedPerks. VehicleID = {}. Scope = {}. Added perks = {}', self.vehicleID, scope, addedPerks)
            for perkID in addedPerks:
                self._planHolder.loadPlan(self._owner, scope, perkID, isAutostart=True)

            removedPerks = oldPerks - newPerks
            self._logUpdatedPerks('updateScopedPerks. VehicleID: {}. Scope: {}. Removed perks: {}', self.vehicleID, scope, removedPerks)
            for perkID in removedPerks:
                self.dropAllPerkModifiers(scope, perkID)
                self._planHolder.unloadPlan(perkID)

            changedPerks = self._findChangedPerks(oldScope, newScope, oldPerks.intersection(newPerks))
            self._logUpdatedPerks('updateScopedPerks. VehicleID = {}. Scope = {}. Changed perks = {}', self.vehicleID, scope, changedPerks)
            if newScope is not None:
                perksTuple, context = newScope
                for perkTuple in perksTuple:
                    perkID, perkData = perkTuple
                    if perkID not in changedPerks:
                        continue
                    self.dropAllPerkModifiers(scope, perkID)
                    isReadyForUse = self._planHolder.isReadyForUse
                    if isReadyForUse:
                        plan = self._planHolder.getPlan(scope, perkID)
                        plan.stop()
                        plan.setContextArgs(perkData.args)
                        plan.start()

        self._scopedPerks = newScopedPerks
        return

    @classmethod
    def _getPerkIDs(cls, scopedPerks):
        perkIDs = set()
        if scopedPerks is None:
            return perkIDs
        else:
            perksTuple, contextCreator = scopedPerks
            if not perksTuple:
                return perkIDs
            for perkTuple in perksTuple:
                perkID, perkData = perkTuple
                perkIDs.add(perkID)

            return perkIDs

    def _logUpdatedPerks(self, message, vehID, scope, perks):
        if not perks:
            return
        LOG_DEBUG_DEV(message.format(vehID, scope, perks))

    @classmethod
    def _findChangedPerks(cls, oldScopedPerks, newScopedPerks, perksToCheck):
        changedPerks = set()
        if not perksToCheck:
            return changedPerks
        perksTuple0, creator0 = oldScopedPerks
        perksTuple1, creator1 = newScopedPerks
        for perkTuple0 in perksTuple0:
            perkID0, perkData0 = perkTuple0
            if perkID0 not in perksToCheck:
                continue
            for perkTuple1 in perksTuple1:
                perkID1, perkData1 = perkTuple1
                if perkID0 != perkID1:
                    continue
                skillData0 = perkData0.args.skillData
                skillData1 = perkData1.args.skillData
                if len(skillData0) != len(skillData1):
                    changedPerks.add(perkID0)
                    break

        return changedPerks

    def _assignContextsToScopes(self, scopedPerks):
        controllerWeakRef = weakref.proxy(self)
        return {scopeId:(scopeData, self._scopeContextMap[scopeId](controllerWeakRef)) for scopeId, scopeData in scopedPerks.iteritems()}

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
         'damageMonitoringDelay': self._collectMinAttributeFactor,
         'artNotificationDelay': self._collectMinAttributeFactor})

    def _buildDynamicFactorsCollectorMap(self):
        self.dynamicFactorCollectors.update({key:self.collectMultiplicativeModsForFactor for key in self._multiplicativeDynamicFactors})
        self.dynamicFactorCollectors.update({key:self.collectAddivieModsForFactor for key in self._additiveDynamicFactors})

    def _collectModifiersMulScopes(self, scopes):
        return reduce(mul, (1 + sum((v[1] for v in mods)) for mods in scopes.itervalues()), 1.0)

    def _collectModifiersAddScopes(self, scopes):
        return sum((sum((v[1] for v in mods)) for mods in scopes.itervalues()))

    def _collectMultiplicativeAttributeFactor(self, key, factors):
        factors[key] *= self._collectModifiersMulScopes(self._modifiedFactors[key])

    def _collectAdditiveAttributeFactor(self, key, factors):
        factors[key] += self._collectModifiersAddScopes(self._modifiedFactors[key])

    def _collectMinAttributeFactor(self, key, factors):
        scopes = self._modifiedFactors.get(key)
        if not scopes:
            return
        minV = factors[key]
        for mods in scopes.itervalues():
            for v in mods:
                minV = min(minV, v[1])

        factors[key] = min(factors[key], minV)

    def _collectInvisibility(self, invisibilityKey, factors):
        invisibility = factors[invisibilityKey]
        invisibility[0] += self._collectModifiersAddScopes(self._modifiedFactors['invisibilityAdd'])
        invisibility[1] *= self._collectModifiersMulScopes(self._modifiedFactors['invisibilityMul'])

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
