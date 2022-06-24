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
        collectModifiersMulScopes = self._collectModifiersMulScopes
        collectModifiersAddScopes = self._collectModifiersAddScopes
        modifiedFactors = self._modifiedFactors
        factors['crewRolesFactor'] *= collectModifiersMulScopes(modifiedFactors['crewRolesFactor'])
        factors['circularVisionRadius'] *= collectModifiersMulScopes(modifiedFactors['circularVisionRadius'])
        factors['radio/distance'] *= collectModifiersMulScopes(modifiedFactors['radio/distance'])
        factors['gun/reloadTime'] *= collectModifiersMulScopes(modifiedFactors['gun/reloadTime'])
        factors['turret/rotationSpeed'] *= collectModifiersMulScopes(modifiedFactors['turret/rotationSpeed'])
        factors['gun/rotationSpeed'] *= collectModifiersMulScopes(modifiedFactors['gun/rotationSpeed'])
        factors['gun/aimingTime'] *= collectModifiersMulScopes(modifiedFactors['gun/aimingTime'])
        factors['gun/shotDispersionFactors/turretRotation'] *= collectModifiersMulScopes(modifiedFactors['gun/shotDispersionFactors/turretRotation'])
        factors['chassis/shotDispersionFactors/movement'] *= collectModifiersMulScopes(modifiedFactors['chassis/shotDispersionFactors/movement'])
        factors['repairSpeed'] *= collectModifiersMulScopes(modifiedFactors['repairSpeed'])
        factors['crewChanceToHitFactor'] *= collectModifiersMulScopes(modifiedFactors['crewChanceToHitFactor'])
        factors['engine/fireStartingChance'] *= collectModifiersMulScopes(modifiedFactors['engine/fireStartingChance'])
        factors['healthBurnPerSecLossFraction'] *= collectModifiersMulScopes(modifiedFactors['healthBurnPerSecLossFraction'])
        factors['vehicle/rotationSpeed'] *= collectModifiersMulScopes(modifiedFactors['vehicle/rotationSpeed'])
        factors['engine/power'] *= collectModifiersMulScopes(modifiedFactors['engine/power'])
        invisibility = factors['invisibility']
        invisibility[0] += collectModifiersAddScopes(modifiedFactors['invisibilityAdd'])
        invisibility[1] *= collectModifiersMulScopes(modifiedFactors['invisibilityMul'])
        factors['stunResistanceDuration'] += collectModifiersAddScopes(modifiedFactors['stunResistanceDuration'])
        factors['stunResistanceEffect'] += collectModifiersAddScopes(modifiedFactors['stunResistanceEffect'])
        if _DO_DEBUG_LOG:
            if IS_DEVELOPMENT:
                LOG_DEBUG_DEV('ABILITY_SYSTEM DEBUG onCollectFactors, factors diff: {}'.format([ '{} {} -> {}'.format(k, oldFactors[k], factors[k]) for k in modifiedFactors if k in factors and oldFactors[k] != factors[k] ]))

    def _collectModifiersMulScopes(self, scopes):
        return reduce(mul, (1.0 + reduce(lambda acc, v: acc + v[1], mods, 0) for mods in scopes.itervalues()), 1)

    def _collectModifiersAddScopes(self, scopes):
        return reduce(add, (reduce(lambda acc, v: acc + v[1], mods, 0) for mods in scopes.itervalues()), 0)

    def _destroyPlanHolder(self):
        if self._planHolder is not None:
            self._planHolder.destroy()
            self._planHolder = None
        return
