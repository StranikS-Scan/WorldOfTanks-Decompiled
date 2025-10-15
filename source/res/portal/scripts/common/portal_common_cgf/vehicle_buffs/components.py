# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: portal/scripts/common/portal_common_cgf/vehicle_buffs/components.py
import CGF
from cgf_script.component_meta_class import ComponentProperty, CGFMetaTypes, registerComponent

class BuffComponent(object):
    pass


@registerComponent
class PeriodicHealthChangeComponent(BuffComponent):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'Periodic Health Change'
    healthChange = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Health Change', value=1.0)


@registerComponent
class MovementBlockedComponent(BuffComponent):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'Movement Blocked'


factorComponentClasses = {}

class FactorRegisterMeta(type):

    def __init__(cls, name, bases, attrs):
        super(FactorRegisterMeta, cls).__init__(name, bases, attrs)
        factorComponentClasses[cls.__name__] = cls


class BaseFactorComponent(BuffComponent):
    __metaclass__ = FactorRegisterMeta
    domain = CGF.DomainOption.DomainAll
    category = 'Vehicle Factors'
    editorTitle = 'Base Factor Component'
    factorName = 'baseFactor'
    factorValue = ComponentProperty(type=CGFMetaTypes.FLOAT, editorName='Factor Value', value=1.0)


def createFactorComponentClass(className, factorName, factorType=CGFMetaTypes.FLOAT, factorValue=1.0):
    classAttrs = {'editorTitle': className,
     'factorName': factorName,
     'factorValue': ComponentProperty(type=factorType, editorName='Factor Value', value=factorValue)}
    return FactorRegisterMeta(className, (BaseFactorComponent,), classAttrs)


components = [('EnginePowerFactorComponent', 'engine/power'),
 ('EnginePowerReverseFactorComponent', 'reverseEnginePower'),
 ('EngineFireChanceFactorComponent', 'engine/fireStartingChance'),
 ('EngineReduceFineFactorComponent', 'engineReduceFineFactor'),
 ('VehicleRotationSpeedFactorComponent', 'vehicle/rotationSpeed'),
 ('MaxSpeedFactorComponent', 'vehicle/maxSpeed'),
 ('MaxSpeedForwardFactorComponent', 'vehicle/maxSpeed/forward'),
 ('MaxSpeedBackwardFactorComponent', 'vehicle/maxSpeed/backward'),
 ('FwMaxSpeedBonusComponent',
  'vehicle/fwMaxSpeedBonus',
  CGFMetaTypes.FLOAT,
  0.0),
 ('BkMaxSpeedBonusComponent',
  'vehicle/bkMaxSpeedBonus',
  CGFMetaTypes.FLOAT,
  0.0),
 ('TankAccelerationComponent', 'tankAcceleration'),
 ('TerrainResistanceFactorComponent',
  'chassis/terrainResistance',
  CGFMetaTypes.FLOAT_LIST,
  [1.0, 1.0, 1.0]),
 ('GunReloadTimeFactorComponent', 'gun/reloadTime'),
 ('GunAimingTimeFactorComponent', 'gun/aimingTime'),
 ('GunRotationSpeedFactorComponent', 'gun/rotationSpeed'),
 ('GunPiercingFactorComponent', 'gun/piercing'),
 ('GunClipTimeBetweenShotsComponent', 'gun/clipTimeBetweenShots'),
 ('GunChangeShellReloadFactorComponent', 'gun/changeShell/reloadFactor'),
 ('CanShootComponent',
  'gun/canShoot',
  CGFMetaTypes.BOOL,
  True),
 ('MultShotDispersionFactorComponent', 'multShotDispersionFactor'),
 ('TurretRotationSpeedFactorComponent', 'turret/rotationSpeed'),
 ('CircularVisionRadiusFactorComponent', 'circularVisionRadius'),
 ('XRayFactorComponent', 'xRayFactor'),
 ('InvisibilityFactorComponent',
  'invisibility',
  CGFMetaTypes.FLOAT_LIST,
  [0.0, 1.0]),
 ('InvisibilityFactorAtShotComponent', 'invisibilityFactorAtShot'),
 ('DemaskMovingFactorComponent', 'demaskMovingFactor'),
 ('DemaskFoliageFactorComponent', 'demaskFoliageFactor'),
 ('FoliageInvisibilityFactorComponent', 'foliageInvisibilityFactor'),
 ('InvisibilityAdditiveTermComponent',
  'invisibilityAdditiveTerm',
  CGFMetaTypes.FLOAT,
  0.0),
 ('InvisibilityMultFactorComponent', 'invisibilityMultFactor'),
 ('ChassisShotDispersionMovementFactorComponent', 'chassis/shotDispersionFactors/movement'),
 ('ChassisShotDispersionRotationFactorComponent', 'chassis/shotDispersionFactors/rotation'),
 ('BrokenTrackComponent',
  'brokenTrack',
  CGFMetaTypes.INT,
  0),
 ('GunShotDispersionTurretRotationFactorComponent', 'gun/shotDispersionFactors/turretRotation'),
 ('DamageFactorComponent', 'damageFactor'),
 ('ModuleDamageFactorComponent', 'moduleDamageFactor'),
 ('EngineAndFuelTanksDamageFactorComponent', 'engineAndFuelTanksDamageFactor'),
 ('RadioDistanceFactorComponent', 'radio/distance'),
 ('RadioDistanceBonusComponent',
  'radioDistanceFactor',
  CGFMetaTypes.FLOAT,
  0.0),
 ('RepairSpeedFactorComponent', 'repairSpeed'),
 ('AdditiveShotDispersionFactorComponent', 'additiveShotDispersionFactor'),
 ('HealthFactorComponent', 'healthFactor'),
 ('HealthBurnPerSecLossFractionComponent',
  'healthBurnPerSecLossFraction',
  CGFMetaTypes.FLOAT,
  0.57),
 ('CrewLevelIncreaseComponent',
  'crewLevelIncrease',
  CGFMetaTypes.INT,
  0),
 ('CrewChanceToHitFactorComponent', 'crewChanceToHitFactor'),
 ('CrewRolesFactorComponent', 'crewRolesFactor'),
 ('StunResistanceEffectComponent',
  'stunResistanceEffect',
  CGFMetaTypes.FLOAT,
  0.0),
 ('StunResistanceDurationComponent',
  'stunResistanceDuration',
  CGFMetaTypes.FLOAT,
  0.0),
 ('RepeatedStunDurationFactorComponent', 'repeatedStunDurationFactor'),
 ('RammingFactorComponent', 'ramming'),
 ('DeathZoneSensitivityFactorComponent', 'deathZones/sensitivityFactor'),
 ('DamageMonitoringDelayComponent',
  'damageMonitoringDelay',
  CGFMetaTypes.FLOAT,
  float('inf')),
 ('ArtNotificationDelayComponent',
  'artNotificationDelay',
  CGFMetaTypes.FLOAT,
  float('inf')),
 ('AmmoBayReduceFineFactorComponent', 'ammoBayReduceFineFactor'),
 ('CanBeDamagedComponent',
  'vehicle/canBeDamaged',
  CGFMetaTypes.BOOL,
  True),
 ('CanBeRammedComponent',
  'vehicle/canBeRammed',
  CGFMetaTypes.BOOL,
  True)]
for componentArgs in components:
    componentClass = createFactorComponentClass(*componentArgs)
    registerComponent(componentClass)

@registerComponent
class PortalAuraComponent(object):
    domain = CGF.DomainOption.DomainAll
    category = 'Portal'
    editorTitle = 'Portal Aura Component'
    applyAlliesComponents = {}
    applyEnemiesComponents = {}

    def __init__(self):
        self.enterReactionID = None
        self.exitReactionID = None
        return


@registerComponent
class AuraGOFollower(object):
    domain = CGF.DomainOption.DomainServer | CGF.DomainOption.DomainEditor
    category = 'Portal'
    editorTitle = 'Aura GO Follower'
    target = ComponentProperty(type=CGFMetaTypes.LINK, editorName='Target', value=CGF.GameObject)

    def __init__(self):
        self.owner = None
        return
