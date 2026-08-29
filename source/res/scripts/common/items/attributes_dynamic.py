# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/attributes_dynamic.py
from items.attributes_helpers import CommonFactorsHelper, MODIFIER_TYPE
ALLOWED_DYNAMIC_ATTRS = ['additiveShotDispersionFactor',
 'armorSpallsDamageFactor',
 'deviceDamageFactor',
 'armorDamageFactor',
 'spallsDeviceDamageFactor',
 'chassis/shotDispersionFactors/movement',
 'chassis/shotDispersionFactors/rotation',
 'circularVisionRadius',
 'crewChanceToHitFactor',
 'crewLevelIncrease',
 'crewRolesFactor',
 ('damageFactor', MODIFIER_TYPE.MUL),
 'deathZones/sensitivityFactor',
 'engine/fireStartingChance',
 'engine/power',
 'enginePowerFactor',
 'gun/aimingTime',
 'gun/changeShell/reloadFactor',
 'gun/piercing',
 'gun/maxDistanceFactor',
 'gun/shellSpeedFactor',
 'gun/reloadTime',
 'gun/rotationSpeed',
 ('gun/shotDispersionFactors/afterShot', MODIFIER_TYPE.MUL),
 'gun/shotDispersionFactors/turretRotation',
 'gun/temperature/heatingFactor',
 'healthBurnPerSecLossFraction',
 'healthFactor',
 'multShotDispersionFactor',
 'radio/distance',
 'ramming',
 'repairSpeed',
 'repeatedStunDurationFactor',
 'stunResistanceDuration',
 'stunResistanceEffect',
 'turret/rotationSpeed',
 'vehicle/maxSpeed',
 'vehicle/maxSpeed/forward',
 'vehicle/maxSpeed/backward',
 'vehicle/rotationSpeed',
 'vehicle/bkMaxSpeedBonus',
 'vehicle/fwMaxSpeedBonus',
 'moduleDamageFactor',
 'engineAndFuelTanksDamageFactor',
 'gun/chargeTimeBonus',
 'gun/reloadLockTimeBonus',
 'gun/loadShellIntoDualGunBonus']

class DynamicFactorsHelper(CommonFactorsHelper):
    ALLOWED_ATTRS = ALLOWED_DYNAMIC_ATTRS
    PREFIX = 'dynAttrs/'


attributes_dynamic_factory = DynamicFactorsHelper()
