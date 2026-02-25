# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/shell_components.py
from constants import SHELL_TYPES, DamageAbsorptionTypeToLabel, SHELL_MECHANICS_TYPE
from items.components.component_constants import DEFAULT_ENABLE_TRACE_RICOCHET, ZERO_FLOAT, ZERO_TUPLE2
from typing import Set, Optional, Tuple, Union

class ShellType(object):
    __slots__ = ('name',)

    def __init__(self, name):
        super(ShellType, self).__init__()
        self.name = name

    def __repr__(self):
        return '{}()'.format(self.__class__.__name__)


class ArmorPiercingType(ShellType):
    __slots__ = ('normalizationAngle', 'ricochetAngleCos', 'protectFromDirectHits', 'mechanics', 'nonPiercingArmorDamage', 'enableTraceRicochet')

    def __init__(self, name):
        super(ArmorPiercingType, self).__init__(name)
        self.normalizationAngle = ZERO_FLOAT
        self.ricochetAngleCos = ZERO_FLOAT
        self.enableTraceRicochet = DEFAULT_ENABLE_TRACE_RICOCHET
        self.protectFromDirectHits = set()
        self.mechanics = SHELL_MECHANICS_TYPE.LEGACY
        self.nonPiercingArmorDamage = ZERO_FLOAT

    def __repr__(self):
        return 'ArmorPiercingType(normalizationAngle={}, ricochetAngleCos={}, protectFromDirectHits = {})'.format(self.normalizationAngle, self.ricochetAngleCos, self.protectFromDirectHits)


class HollowChargeType(ShellType):
    __slots__ = ('piercingPowerLossFactorByDistance', 'ricochetAngleCos', 'protectFromDirectHits', 'mechanics', 'nonPiercingArmorDamage', 'enableTraceRicochet')

    def __init__(self, name):
        super(HollowChargeType, self).__init__(name)
        self.piercingPowerLossFactorByDistance = ZERO_FLOAT
        self.ricochetAngleCos = ZERO_FLOAT
        self.enableTraceRicochet = DEFAULT_ENABLE_TRACE_RICOCHET
        self.protectFromDirectHits = set()
        self.mechanics = SHELL_MECHANICS_TYPE.LEGACY
        self.nonPiercingArmorDamage = ZERO_FLOAT

    def __repr__(self):
        return 'HollowChargeType(piercingPowerLossFactorByDistance={}, ricochetAngleCos={}, protectFromDirectHits={})'.format(self.piercingPowerLossFactorByDistance, self.ricochetAngleCos, self.protectFromDirectHits)


class HighExplosiveImpactParams(object):
    __slots__ = ('radius', 'armorDamage', 'deviceDamage', 'coneAngleCos', 'piercingSpalls', 'damageAbsorptionType', 'isActive', 'hasSplash')

    def __init__(self):
        self.radius = ZERO_FLOAT
        self.armorDamage = ZERO_TUPLE2
        self.deviceDamage = ZERO_TUPLE2
        self.coneAngleCos = None
        self.piercingSpalls = None
        self.damageAbsorptionType = None
        self.hasSplash = True
        self.isActive = True
        return

    def __repr__(self):
        return 'HighExplosiveImpactParams(radius={}, armorDamage={}, deviceDamage={}, coneAngleCos={}, piersingSpalls={}, damageAbsorption={})'.format(self.radius, self.armorDamage, self.deviceDamage, self.coneAngleCos, self.piercingSpalls, DamageAbsorptionTypeToLabel[self.damageAbsorptionType] if self.damageAbsorptionType else None)


class HighExplosiveType(ShellType):
    __slots__ = ('explosionRadius', 'explosionDamageFactor', 'explosionDamageAbsorptionFactor', 'explosionEdgeDamageFactor', 'mechanics', 'blastWave', 'shellFragments', 'armorSpalls', 'shellFragmentsDamageAbsorptionFactor', 'obstaclePenetration', 'shieldPenetration', 'maxDamage', 'protectFromDirectHits', 'protectFromIndirectHits')

    def __init__(self, name):
        super(HighExplosiveType, self).__init__(name)
        self.explosionRadius = ZERO_FLOAT
        self.explosionDamageFactor = ZERO_FLOAT
        self.explosionDamageAbsorptionFactor = ZERO_FLOAT
        self.explosionEdgeDamageFactor = ZERO_FLOAT
        self.shellFragmentsDamageAbsorptionFactor = ZERO_FLOAT
        self.mechanics = SHELL_MECHANICS_TYPE.LEGACY
        self.obstaclePenetration = None
        self.shieldPenetration = None
        self.blastWave = None
        self.shellFragments = None
        self.armorSpalls = None
        self.protectFromDirectHits = set()
        self.protectFromIndirectHits = set()
        self.maxDamage = None
        return

    def __repr__(self):
        return 'HighExplosiveType(explosionRadius={}, explosionDamageFactor={}, explosionDamageAbsorptionFactor={}, explosionEdgeDamageFactor={}, mechanics={}, obstaclePenetration={}, shieldPenetration={}, blastWave={}, shellFragments={}, armorSpalls={}, shellFragmentsDamageAbsorptionFactor={}, protectFromDirectHits = {}, protectFromIndirectHits = {}, '.format(self.explosionRadius, self.explosionDamageFactor, self.explosionDamageAbsorptionFactor, self.explosionEdgeDamageFactor, self.mechanics, self.obstaclePenetration, self.shieldPenetration, self.blastWave, self.shellFragments, self.armorSpalls, self.shellFragmentsDamageAbsorptionFactor, self.protectFromDirectHits, self.protectFromIndirectHits)

    @property
    def impacts(self):
        return (self.blastWave, self.shellFragments, self.armorSpalls)


class SmokeType(ShellType):
    __slots__ = ()

    def __init__(self, name):
        super(SmokeType, self).__init__(name)

    def __repr__(self):
        pass


class Stun(object):
    __slots__ = ('stunRadius', 'stunDuration', 'stunFactor', 'guaranteedStunDuration', 'damageDurationCoeff', 'guaranteedStunEffect', 'damageEffectCoeff')

    def __init__(self, stunRadius=ZERO_FLOAT, stunDuration=ZERO_FLOAT, stunFactor=ZERO_FLOAT, guaranteedStunDuration=ZERO_FLOAT, damageDurationCoeff=ZERO_FLOAT, guaranteedStunEffect=ZERO_FLOAT, damageEffectCoeff=ZERO_FLOAT):
        super(Stun, self).__init__()
        self.stunRadius = stunRadius
        self.stunDuration = stunDuration
        self.stunFactor = stunFactor
        self.guaranteedStunDuration = guaranteedStunDuration
        self.damageDurationCoeff = damageDurationCoeff
        self.guaranteedStunEffect = guaranteedStunEffect
        self.damageEffectCoeff = damageEffectCoeff

    def __repr__(self):
        return 'Stun(radius={}, duration={}, guaranteedDuration={}, damageDurationCoeff={} guaranteedSEffect={}, damageEffectCoeff={})'.format(self.stunRadius, self.stunDuration, self.guaranteedStunDuration, self.damageDurationCoeff, self.guaranteedStunEffect, self.damageEffectCoeff)


def createShellType(typeName):
    shellType = None
    if typeName in (SHELL_TYPES.ARMOR_PIERCING, SHELL_TYPES.ARMOR_PIERCING_HE, SHELL_TYPES.ARMOR_PIERCING_CR):
        shellType = ArmorPiercingType(typeName)
    elif typeName == SHELL_TYPES.HOLLOW_CHARGE:
        shellType = HollowChargeType(typeName)
    elif typeName == SHELL_TYPES.HIGH_EXPLOSIVE:
        shellType = HighExplosiveType(typeName)
    elif typeName == SHELL_TYPES.SMOKE:
        shellType = SmokeType(typeName)
    return shellType
