# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/shell_components.py
from constants import SHELL_TYPES, DamageAbsorptionTypeToLabel, SHELL_MECHANICS_TYPE, StunTypes, HAS_EXPLOSION_EFFECT
from items.components import component_constants
from typing import Set, Optional, Tuple, Union

class ShellType(object):
    __slots__ = ('name',)

    def __init__(self, name):
        super(ShellType, self).__init__()
        self.name = name

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class ArmorPiercingType(ShellType):
    __slots__ = ('normalizationAngle', 'ricochetAngleCos', 'protectFromDirectHits', 'mechanics', 'guaranteedDamages', 'protectFromDestroy')

    def __init__(self, name):
        super(ArmorPiercingType, self).__init__(name)
        self.normalizationAngle = component_constants.ZERO_FLOAT
        self.ricochetAngleCos = component_constants.ZERO_FLOAT
        self.protectFromDirectHits = set()
        self.protectFromDestroy = set()
        self.mechanics = SHELL_MECHANICS_TYPE.LEGACY
        self.guaranteedDamages = component_constants.EMPTY_TUPLE

    def __repr__(self):
        return 'ArmorPiercingType(normalizationAngle={}, ricochetAngleCos={}, protectFromDirectHits = {}, protectFromDestroy = {})'.format(self.normalizationAngle, self.ricochetAngleCos, self.protectFromDirectHits, self.protectFromDestroy)


class HollowChargeType(ShellType):
    __slots__ = ('piercingPowerLossFactorByDistance', 'ricochetAngleCos', 'protectFromDirectHits', 'mechanics', 'guaranteedDamages', 'protectFromDestroy')

    def __init__(self, name):
        super(HollowChargeType, self).__init__(name)
        self.piercingPowerLossFactorByDistance = component_constants.ZERO_FLOAT
        self.ricochetAngleCos = component_constants.ZERO_FLOAT
        self.protectFromDirectHits = set()
        self.protectFromDestroy = set()
        self.mechanics = SHELL_MECHANICS_TYPE.LEGACY
        self.guaranteedDamages = component_constants.EMPTY_TUPLE

    def __repr__(self):
        return 'HollowChargeType(piercingPowerLossFactorByDistance={}, ricochetAngleCos={}, protectFromDirectHits={}, protectFromDestroy={})'.format(self.piercingPowerLossFactorByDistance, self.ricochetAngleCos, self.protectFromDirectHits, self.protectFromDestroy)


class HighExplosiveImpactParams(object):
    __slots__ = ('radius', 'damages', 'coneAngleCos', 'piercingSpalls', 'damageAbsorptionType', 'isActive')

    def __init__(self):
        self.radius = component_constants.ZERO_FLOAT
        self.damages = component_constants.EMPTY_TUPLE
        self.coneAngleCos = None
        self.piercingSpalls = None
        self.damageAbsorptionType = None
        self.isActive = True
        return

    def __repr__(self):
        return 'HighExplosiveImpactParams(radius={}, damages={}, coneAngleCos={}, piersingSpalls={}, damageAbsorption={})'.format(self.radius, self.damages, self.coneAngleCos, self.piercingSpalls, DamageAbsorptionTypeToLabel[self.damageAbsorptionType] if self.damageAbsorptionType else None)


class HighExplosiveType(ShellType):
    __slots__ = ('explosionRadius', 'explosionDamageFactor', 'explosionDamageAbsorptionFactor', 'explosionEdgeDamageFactor', 'mechanics', 'blastWave', 'shellFragments', 'armorSpalls', 'shellFragmentsDamageAbsorptionFactor', 'obstaclePenetration', 'shieldPenetration', 'maxDamage', 'protectFromDirectHits', 'protectFromIndirectHits', 'protectFromDestroy', 'explosionDisableDamageFalloff')

    def __init__(self, name):
        super(HighExplosiveType, self).__init__(name)
        self.explosionRadius = component_constants.ZERO_FLOAT
        self.explosionDamageFactor = component_constants.ZERO_FLOAT
        self.explosionDamageAbsorptionFactor = component_constants.ZERO_FLOAT
        self.explosionEdgeDamageFactor = component_constants.ZERO_FLOAT
        self.shellFragmentsDamageAbsorptionFactor = component_constants.ZERO_FLOAT
        self.explosionDisableDamageFalloff = component_constants.ZERO_FLOAT
        self.mechanics = SHELL_MECHANICS_TYPE.LEGACY
        self.obstaclePenetration = None
        self.shieldPenetration = None
        self.blastWave = None
        self.shellFragments = None
        self.armorSpalls = None
        self.protectFromDirectHits = set()
        self.protectFromIndirectHits = set()
        self.protectFromDestroy = set()
        self.maxDamage = None
        return

    def __repr__(self):
        return 'HighExplosiveType(explosionRadius={}, explosionDamageFactor={}, explosionDamageAbsorptionFactor={}, explosionEdgeDamageFactor={}, mechanics={}, obstaclePenetration={}, shieldPenetration={}, blastWave={}, shellFragments={}, armorSpalls={}, shellFragmentsDamageAbsorptionFactor={}, protectFromDirectHits = {}, protectFromIndirectHits = {}, protectFromDestroy = {}, explosionDisableDamageFalloff = {}, '.format(self.explosionRadius, self.explosionDamageFactor, self.explosionDamageAbsorptionFactor, self.explosionEdgeDamageFactor, self.mechanics, self.obstaclePenetration, self.shieldPenetration, self.blastWave, self.shellFragments, self.armorSpalls, self.shellFragmentsDamageAbsorptionFactor, self.protectFromDirectHits, self.protectFromIndirectHits, self.protectFromDestroy, self.explosionDisableDamageFalloff)


class SmokeType(ShellType):
    __slots__ = ()

    def __init__(self, name):
        super(SmokeType, self).__init__(name)

    def __repr__(self):
        pass


class Stun(object):
    __slots__ = ('stunRadius', 'stunDuration', 'stunType', 'stunFactor', 'guaranteedStunDuration', 'damageDurationCoeff', 'guaranteedStunEffect', 'damageEffectCoeff', 'stunInPoint')

    def __init__(self):
        super(Stun, self).__init__()
        self.stunRadius = component_constants.ZERO_FLOAT
        self.stunDuration = component_constants.ZERO_FLOAT
        self.stunType = StunTypes.DEFAULT
        self.stunInPoint = False
        self.stunFactor = component_constants.ZERO_FLOAT
        self.guaranteedStunDuration = component_constants.ZERO_FLOAT
        self.damageDurationCoeff = component_constants.ZERO_FLOAT
        self.guaranteedStunEffect = component_constants.ZERO_FLOAT
        self.damageEffectCoeff = component_constants.ZERO_FLOAT

    def __repr__(self):
        return 'Stun(radius={}, duration={}, guaranteedDuration={}, damageDurationCoeff={} guaranteedSEffect={}, damageEffectCoeff={}, stunInPoint={})'.format(self.stunRadius, self.stunDuration, self.guaranteedStunDuration, self.damageDurationCoeff, self.guaranteedStunEffect, self.damageEffectCoeff, self.stunInPoint)


def createShellType(typeName):
    shellType = None
    if typeName in (SHELL_TYPES.ARMOR_PIERCING,
     SHELL_TYPES.ARMOR_PIERCING_HE,
     SHELL_TYPES.ARMOR_PIERCING_FSDS,
     SHELL_TYPES.ARMOR_PIERCING_CR):
        shellType = ArmorPiercingType(typeName)
    elif typeName == SHELL_TYPES.HOLLOW_CHARGE:
        shellType = HollowChargeType(typeName)
    elif typeName in HAS_EXPLOSION_EFFECT:
        shellType = HighExplosiveType(typeName)
    elif typeName == SHELL_TYPES.SMOKE:
        shellType = SmokeType(typeName)
    return shellType
