# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/BasePerksController.py
from collections import defaultdict
from operator import mul, add
from typing import Union, List, Dict, Tuple
from PerkPlanHolder import PCPlanHolder
from debug_utils import LOG_DEBUG_DEV
from constants import IS_DEVELOPMENT
_DO_DEBUG_LOG = False

class BasePerksController(object):

    def __init__(self, owner, scopedPerks):
        LOG_DEBUG_DEV('ABILITY_SYSTEM DEBUG scopedPerks: {} '.format(scopedPerks))
        self._owner = owner
        self._scopedPerks = scopedPerks
        self._modifiedFactors = None
        self._planHolder = None
        return

    def init(self, isAutoStart=False):
        self._modifiedFactors = defaultdict(lambda : defaultdict(list))
        self._planHolder = PCPlanHolder(self._scopedPerks)
        self._planHolder.loadPlan(self._owner, isAutoStart)

    def start(self):
        self._planHolder.start()

    def destroy(self):
        self._destroyPlanHolder()
        self._owner = None
        return

    def modifyFactor(self, factor, scopeID, perkID, value):
        self._modifiedFactors[factor][scopeID].append((perkID, value))

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

    def triggerVSPlanEvent(self, event):
        self._planHolder.triggerVSPlanEvent(event)

    def onCollectFactors(self, factors):
        if IS_DEVELOPMENT:
            oldFactors = factors.copy()
        factors['crewRolesFactor'] *= self._collectModifiersMulScopes(self._modifiedFactors['crewRolesFactor'])
        factors['circularVisionRadius'] *= self._collectModifiersMulScopes(self._modifiedFactors['circularVisionRadius'])
        factors['radio/distance'] *= self._collectModifiersMulScopes(self._modifiedFactors['radio/distance'])
        factors['gun/reloadTime'] *= self._collectModifiersMulScopes(self._modifiedFactors['gun/reloadTime'])
        factors['turret/rotationSpeed'] *= self._collectModifiersMulScopes(self._modifiedFactors['turret/rotationSpeed'])
        factors['gun/rotationSpeed'] *= self._collectModifiersMulScopes(self._modifiedFactors['gun/rotationSpeed'])
        factors['gun/aimingTime'] *= self._collectModifiersMulScopes(self._modifiedFactors['gun/aimingTime'])
        factors['gun/shotDispersionFactors/turretRotation'] *= self._collectModifiersMulScopes(self._modifiedFactors['gun/shotDispersionFactors/turretRotation'])
        factors['chassis/shotDispersionFactors/movement'] *= self._collectModifiersMulScopes(self._modifiedFactors['chassis/shotDispersionFactors/movement'])
        factors['repairSpeed'] *= self._collectModifiersMulScopes(self._modifiedFactors['repairSpeed'])
        factors['crewChanceToHitFactor'] *= self._collectModifiersMulScopes(self._modifiedFactors['crewChanceToHitFactor'])
        factors['engine/fireStartingChance'] *= self._collectModifiersMulScopes(self._modifiedFactors['engine/fireStartingChance'])
        factors['healthBurnPerSecLossFraction'] *= self._collectModifiersMulScopes(self._modifiedFactors['healthBurnPerSecLossFraction'])
        factors['vehicle/rotationSpeed'] *= self._collectModifiersMulScopes(self._modifiedFactors['vehicle/rotationSpeed'])
        factors['engine/power'] *= self._collectModifiersMulScopes(self._modifiedFactors['engine/power'])
        invisibility = factors['invisibility']
        invisibility[0] += self._collectModifiersAddScopes(self._modifiedFactors['invisibilityAdd'])
        invisibility[1] *= self._collectModifiersMulScopes(self._modifiedFactors['invisibilityMul'])
        factors['stunResistanceDuration'] += self._collectModifiersAddScopes(self._modifiedFactors['stunResistanceDuration'])
        factors['stunResistanceEffect'] += self._collectModifiersAddScopes(self._modifiedFactors['stunResistanceEffect'])
        if _DO_DEBUG_LOG:
            if IS_DEVELOPMENT:
                LOG_DEBUG_DEV('ABILITY_SYSTEM DEBUG onCollectFactors, factors diff: {}'.format([ '{} {} -> {}'.format(k, oldFactors[k], factors[k]) for k in self._modifiedFactors if k in factors and oldFactors[k] != factors[k] ]))

    def _collectModifiersMulScopes(self, scopes):
        return reduce(mul, (1.0 + reduce(lambda acc, v: acc + v[1], mods, 0) for mods in scopes.itervalues()), 1)

    def _collectModifiersAddScopes(self, scopes):
        return reduce(add, (reduce(lambda acc, v: acc + v[1], mods, 0) for mods in scopes.itervalues()), 0)

    def _destroyPlanHolder(self):
        if self._planHolder is not None:
            self._planHolder.destroy()
            self._planHolder = None
        return
