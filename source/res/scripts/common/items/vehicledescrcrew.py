# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/VehicleDescrCrew.py
from __future__ import division
from decimal import Decimal, ROUND_DOWN, ROUND_UP
from items import tankmen
from constants import CREW_CRIT_FACTOR_MOD_SUFFIX, CommonSkillFactors
from floating_point_utils import isclose
_BASE_EFFICIENCY = 0.57
_BONUS_EFFICIENCY = 0.43
_COMMANDER_BONUS_DIGIT_SHIFT = 1

class _EmptyPerksControllerForCrew(object):

    def getCrewFactors(self):
        return {}

    def getCrewMasteryIgnored(self):
        return False


class VehicleDescrCrew(object):

    def __init__(self, vehTypeDescriptor, perksController=None, activityFlags=None, isFire=False):
        self._perksController = perksController or _EmptyPerksControllerForCrew()
        crewRoles = vehTypeDescriptor.type.crewRoles
        self._numTankmen = len(crewRoles)
        if activityFlags is None:
            activityFlags = [True] * self._numTankmen
        self._activityFlags = activityFlags
        self._isFire = isFire
        roleTankmanIdxs = {role:[] for role in tankmen.ROLES}
        crewTankmanIdxs = {role:[] for role in tankmen.ROLES}
        for idxInCrew, roles in enumerate(crewRoles):
            for skillName in roles:
                roleTankmanIdxs[skillName].append(idxInCrew)

            crewTankmanIdxs[roles[0]].append(idxInCrew)

        self._commanderIdx = roleTankmanIdxs['commander'][0]
        self._roleTankmanIdxs = roleTankmanIdxs
        self._crewTankmanIdxs = crewTankmanIdxs
        self._cachedFactors = {}
        self._shotDispFactor = 1.0
        self._terrainResistanceFactor = 1.0
        self._miscAttrsCrewMastery = vehTypeDescriptor.miscAttrs['crewMasteryFactor']
        self._affectingFactors = {'crewMasteryFactor': 0.0,
         'crewRolesFactor': 1.0,
         'radioDistanceFactor': 0.0}
        self._rolePenaltyFactors = {}
        self._factorsDirty = True
        return

    @property
    def roleTankmanIdxs(self):
        return self._roleTankmanIdxs

    @property
    def crewTankmanIdxs(self):
        return self._crewTankmanIdxs

    def onCollectShotDispersionFactors(self, factors):
        if self._factorsDirty:
            self._buildFactors()
        factors[0] *= self._shotDispFactor

    def onCollectFactors(self, factors, dynamicFactors):
        for key, factor in self._affectingFactors.iteritems():
            if not isclose(factors[key], factor):
                self._affectingFactors.update(((k, factors[k]) for k in self._affectingFactors.iterkeys()))
                self._factorsDirty = True
                break

        rolePenaltyFactors = {role:dynamicFactors[role + CREW_CRIT_FACTOR_MOD_SUFFIX] for role in tankmen.ROLES}
        if self._factorsDirty or _floatValDictChanged(self._rolePenaltyFactors, rolePenaltyFactors):
            self._rolePenaltyFactors = rolePenaltyFactors
            self._factorsDirty = True
        if self._factorsDirty:
            self._buildFactors()
        for key, value in self._cachedFactors.iteritems():
            factors[key] *= value

        r = factors['chassis/terrainResistance']
        for i, _ in enumerate(r):
            r[i] *= self._terrainResistanceFactor

    def _buildFactors(self):
        crewMasteryFactor = 1 + self._affectingFactors['crewMasteryFactor'] + self._miscAttrsCrewMastery
        commanderBonusMod = _calcCommanderBonus(crewMasteryFactor)
        crewRolesFactor = self._affectingFactors['crewRolesFactor']
        for role in tankmen.ROLES:
            efficiency = _BASE_EFFICIENCY
            if not self._isFire:
                tmenWithSkill = self._roleTankmanIdxs[role]
                numTmenWithSkill = len(tmenWithSkill)
                numActive = sum((self._activityFlags[idx] for idx in tmenWithSkill))
                penaltyFactor = self._rolePenaltyFactors[role]
                activityFactor = 1 - (1 - numActive / numTmenWithSkill) * (1 - penaltyFactor)
                commanderBonusFactor = commanderBonusMod
                if self._commanderIdx in tmenWithSkill:
                    if numActive == 0:
                        commanderBonusFactor *= (numTmenWithSkill - 1) / numTmenWithSkill
                    elif self._activityFlags[self._commanderIdx]:
                        if numActive == 1:
                            commanderBonusFactor = 0
                        else:
                            commanderBonusFactor *= (numTmenWithSkill - 1) / numTmenWithSkill
                efficiency += _BONUS_EFFICIENCY * (crewMasteryFactor + commanderBonusFactor) * activityFactor
            efficiency *= crewRolesFactor
            self._factorUpdaters[role](self, efficiency)

        commonSkillMods = self._perksController.getCrewFactors()
        for factor in CommonSkillFactors.ALL:
            efficiency = _BASE_EFFICIENCY
            if factor in commonSkillMods and (not self._isFire or factor == CommonSkillFactors.FIREFIGHTING):
                numActive = sum(self._activityFlags)
                activityFactor = numActive / self._numTankmen
                commanderBonusFactor = commanderBonusMod
                if self._activityFlags[self._commanderIdx]:
                    if numActive == 1:
                        commanderBonusFactor = 0
                    else:
                        commanderBonusFactor *= (self._numTankmen - 1) / self._numTankmen
                efficiency += _BONUS_EFFICIENCY * (crewMasteryFactor + commanderBonusFactor) * activityFactor * commonSkillMods[factor]
            efficiency *= crewRolesFactor
            self._factorUpdaters[factor](self, efficiency)

        self._factorsDirty = False

    def _updateCommanderFactors(self, modifier):
        self._cachedFactors['circularVisionRadius'] = modifier

    def _updateRadiomanFactors(self, modifier):
        self._cachedFactors['radio/distance'] = modifier * (1.0 + self._affectingFactors['radioDistanceFactor'])

    def _updateDriverFactors(self, modifier):
        self._terrainResistanceFactor = 1 / modifier

    def _updateGunnerFactors(self, modifier):
        self._cachedFactors['turret/rotationSpeed'] = modifier
        self._cachedFactors['gun/rotationSpeed'] = modifier
        self._cachedFactors['gun/aimingTime'] = 1 / modifier
        self._shotDispFactor = 1 / modifier

    def _updateLoaderFactors(self, modifier):
        self._cachedFactors['gun/reloadTime'] = 1 / modifier

    def _updateCamouflage(self, modifier):
        self._cachedFactors['camouflageFactor'] = modifier

    def _updateFirefighting(self, modifier):
        self._cachedFactors['healthBurnPerSecLossFraction'] = modifier

    def _updateRepairSpeed(self, modifier):
        self._cachedFactors['repairSpeed'] = modifier

    _factorUpdaters = {'commander': _updateCommanderFactors,
     'radioman': _updateRadiomanFactors,
     'driver': _updateDriverFactors,
     'gunner': _updateGunnerFactors,
     'loader': _updateLoaderFactors,
     CommonSkillFactors.CAMOUFLAGE: _updateCamouflage,
     CommonSkillFactors.FIREFIGHTING: _updateFirefighting,
     CommonSkillFactors.REPAIR: _updateRepairSpeed}


def _floatValDictChanged(old, new):
    if old.viewkeys() ^ new.viewkeys():
        return True
    cmp = isclose
    for k in old.iterkeys():
        if not cmp(old[k], new[k]):
            return True

    return False


def _calcCommanderBonus(crewMastery):
    s = '{}'.format(crewMastery)
    trunc = Decimal(s).quantize(Decimal((0, (1,), -6)), rounding=ROUND_DOWN)
    return float(trunc.shift(-_COMMANDER_BONUS_DIGIT_SHIFT).quantize(Decimal('0.01'), rounding=ROUND_UP))
