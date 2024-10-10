# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/vehicle_items.py
import functools
import Math
import nations
from constants import SHELL_TYPES, ATTACK_REASON
from items import ITEM_TYPES, ITEM_TYPE_NAMES, makeIntCompactDescrByID
from items.basic_item import BasicItem
from items.components import chassis_components
from items.components import component_constants
from items.components import gun_components
from items.components import shared_components
from items.components import shell_components
from items.components import sound_components
from soft_exception import SoftException
from wrapped_reflection_framework import ReflectionMetaclass

class VEHICLE_ITEM_STATUS(object):
    UNDEFINED = 0
    EMPTY = 1
    SHARED = 2
    LOCAL = 3


class CHASSIS_ITEM_TYPE(object):
    MONOLITHIC = 0
    TRACK_WITHIN_TRACK = 1
    MULTITRACK_SEQUENT = 2
    MULTITRACK_PARALLEL = 3
    MONOLITHIC_TAG = 'monolithic'
    TRACK_WITHIN_TRACK_TAG = 'trackWithinTrack'
    MULTITRACK_SEQUENT_TAG = 'multiTrackSequent'
    MULTITRACK_PARALLEL_TAG = 'multiTrackParallel'
    TRACK_TYPE_MAP = {MONOLITHIC: MONOLITHIC_TAG,
     TRACK_WITHIN_TRACK: TRACK_WITHIN_TRACK_TAG,
     MULTITRACK_SEQUENT: MULTITRACK_SEQUENT_TAG,
     MULTITRACK_PARALLEL: MULTITRACK_PARALLEL_TAG}


class _ShallowCopyWrapper(object):
    __slots__ = ('__exclude',)

    def __init__(self, *exclude):
        super(_ShallowCopyWrapper, self).__init__()
        self.__exclude = exclude

    def __call__(self, clazz):
        fields = getattr(clazz, '__slots__', None)
        method = getattr(clazz, 'copy', None)
        if method is None or not callable(method):
            raise ValueError('Method "copy" is not found in {}'.format(clazz))

        def wrapCopy(func):

            @functools.wraps(func)
            def wrapper(source, *args, **kwargs):
                destination = func(source, *args, **kwargs)
                for name in fields:
                    if name not in self.__exclude:
                        setattr(destination, name, getattr(source, name))

                return destination

            return wrapper

        clazz.copy = wrapCopy(clazz.copy)
        return clazz


def add_shallow_copy(*exclude):
    return _ShallowCopyWrapper(*exclude)


@add_shallow_copy('status')
class VehicleItem(BasicItem):
    __slots__ = ('level', 'status')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1, status=VEHICLE_ITEM_STATUS.UNDEFINED):
        super(VehicleItem, self).__init__(typeID, componentID, componentName, compactDescr)
        self.level = level
        self.status = status

    def __repr__(self):
        return '{}(id={}, name={}, level={}, status={})'.format(self.__class__.__name__, self.id, self.name, self.level, self.status)


@add_shallow_copy('unlocks')
class InstallableItem(VehicleItem):
    __slots__ = ('weight', 'modelsSets', 'models', 'materials', 'hitTesterManager', 'unlocks', 'armorHomogenization', 'camouflage', 'healthParams', 'sounds', 'soundsSets', 'emblemSlots', 'slotsAnchors')
    __metaclass__ = ReflectionMetaclass

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(InstallableItem, self).__init__(typeID, componentID, componentName, compactDescr, level=level, status=VEHICLE_ITEM_STATUS.EMPTY)
        self.weight = component_constants.ZERO_FLOAT
        self.unlocks = component_constants.EMPTY_TUPLE
        self.healthParams = shared_components.DEFAULT_DEVICE_HEALTH
        self.armorHomogenization = component_constants.DEFAULT_ARMOR_HOMOGENIZATION
        self.materials = None
        self.hitTesterManager = None
        self.modelsSets = None
        self.models = None
        self.camouflage = shared_components.EMPTY_CAMOUFLAGE
        self.sounds = None
        self.soundsSets = None
        self.emblemSlots = component_constants.EMPTY_TUPLE
        self.slotsAnchors = component_constants.EMPTY_TUPLE
        return

    @property
    def hitTester(self):
        return self.hitTesterManager.activeHitTester

    @property
    def maxHealth(self):
        return self.healthParams.maxHealth

    @property
    def repairCost(self):
        return self.healthParams.repairCost

    @property
    def maxRegenHealth(self):
        return self.healthParams.maxRegenHealth

    @property
    def healthRegenPerSec(self):
        return self.healthParams.healthRegenPerSec

    @property
    def healthBurnPerSec(self):
        return self.healthParams.healthBurnPerSec

    @property
    def chanceToHit(self):
        return self.healthParams.chanceToHit

    @property
    def hysteresisHealth(self):
        return self.healthParams.hysteresisHealth

    @property
    def maxRepairCost(self):
        return self.healthParams.maxRepairCost

    @property
    def repairSpeedLimiter(self):
        return self.healthParams.repairSpeedLimiter

    @property
    def repairTime(self):
        return self.healthParams.repairTime


@add_shallow_copy()
class Chassis(InstallableItem):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('hullPosition', 'topRightCarryingPoint', 'navmeshGirth', 'minPlaneNormalY', 'specificFriction', 'rotationSpeed', 'rotationSpeedLimit', 'rotationIsAroundCenter', 'shotDispersionFactors', 'terrainResistance', 'bulkHealthFactor', 'carryingTriangles', 'drivingWheelsSizes', 'chassisLodDistance', 'traces', 'tracks', 'wheels', 'trackPairs', 'bboxManager', 'groundNodes', 'trackNodes', 'trackSplineParams', 'splineDesc', 'leveredSuspension', 'suspensionSpringsLength', 'hullAimingSound', 'effects', 'customEffects', 'AODecals', 'brakeForce', 'physicalTracks', 'customizableVehicleAreas', 'generalWheelsAnimatorConfig', 'wheelHealthParams', 'wheelsArmor', '_chassisType', 'prefabs')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Chassis, self).__init__(typeID, componentID, componentName, compactDescr, level=level)
        self.hullPosition = None
        self.topRightCarryingPoint = None
        self.navmeshGirth = component_constants.ZERO_FLOAT
        self.minPlaneNormalY = component_constants.ZERO_FLOAT
        self.specificFriction = component_constants.DEFAULT_SPECIFIC_FRICTION
        self.rotationSpeed = component_constants.ZERO_FLOAT
        self.rotationSpeedLimit = None
        self.rotationIsAroundCenter = False
        self.shotDispersionFactors = component_constants.EMPTY_TUPLE
        self.brakeForce = component_constants.ZERO_FLOAT
        self.terrainResistance = component_constants.EMPTY_TUPLE
        self.bulkHealthFactor = component_constants.ZERO_FLOAT
        self.drivingWheelsSizes = component_constants.EMPTY_TUPLE
        self.carryingTriangles = component_constants.EMPTY_TUPLE
        self.traces = None
        self.tracks = None
        self.wheels = None
        self.trackPairs = component_constants.EMPTY_TUPLE
        self.bboxManager = None
        self.chassisLodDistance = None
        self.generalWheelsAnimatorConfig = None
        self.groundNodes = None
        self.trackNodes = None
        self.trackSplineParams = None
        self.splineDesc = None
        self.leveredSuspension = None
        self.hullAimingSound = None
        self.suspensionSpringsLength = None
        self.effects = None
        self.customEffects = None
        self.AODecals = component_constants.EMPTY_TUPLE
        self.physicalTracks = None
        self.customizableVehicleAreas = None
        self.wheelHealthParams = {}
        self.wheelsArmor = {}
        self._chassisType = None
        self.prefabs = component_constants.EMPTY_TUPLE
        return

    @property
    def chassisType(self):
        if self._chassisType is not None:
            return self._chassisType
        else:
            if CHASSIS_ITEM_TYPE.TRACK_WITHIN_TRACK_TAG in self.tags:
                self._chassisType = CHASSIS_ITEM_TYPE.TRACK_WITHIN_TRACK
            elif CHASSIS_ITEM_TYPE.MULTITRACK_SEQUENT_TAG in self.tags:
                self._chassisType = CHASSIS_ITEM_TYPE.MULTITRACK_SEQUENT
            elif CHASSIS_ITEM_TYPE.MULTITRACK_PARALLEL_TAG in self.tags:
                self._chassisType = CHASSIS_ITEM_TYPE.MULTITRACK_PARALLEL
            else:
                self._chassisType = CHASSIS_ITEM_TYPE.MONOLITHIC
            return self._chassisType

    @property
    def isTrackWithinTrack(self):
        return self.chassisType == CHASSIS_ITEM_TYPE.TRACK_WITHIN_TRACK

    @property
    def isMultiTrack(self):
        return self.chassisType in (CHASSIS_ITEM_TYPE.MULTITRACK_PARALLEL, CHASSIS_ITEM_TYPE.MULTITRACK_SEQUENT)

    @property
    def totalBBox(self):
        return self.bboxManager.activeBBox


@add_shallow_copy()
class Engine(InstallableItem):
    __slots__ = ('power', 'fireStartingChance', 'minFireStartingDamage', 'rpm_min', 'rpm_max')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Engine, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.power = component_constants.ZERO_FLOAT
        self.fireStartingChance = component_constants.ZERO_FLOAT
        self.minFireStartingDamage = component_constants.ZERO_FLOAT
        self.rpm_min = component_constants.ZERO_INT
        self.rpm_max = component_constants.ZERO_INT


class FuelTank(InstallableItem):
    __slots__ = ()

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(FuelTank, self).__init__(typeID, componentID, componentName, compactDescr, level)


@add_shallow_copy()
class Radio(InstallableItem):
    __slots__ = ('distance', 'radarRadius', 'radarCooldown')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Radio, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.distance = component_constants.ZERO_FLOAT
        self.radarRadius = component_constants.ZERO_FLOAT
        self.radarCooldown = component_constants.ZERO_FLOAT


@add_shallow_copy()
class Turret(InstallableItem):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('gunPosition', 'gunJointPitch', 'rotationSpeed', 'turretRotatorHealth', 'surveyingDeviceHealth', 'invisibilityFactor', 'primaryArmor', 'ceilless', 'showEmblemsOnGun', 'guns', 'turretRotatorSoundManual', 'turretRotatorSoundGear', 'AODecals', 'turretDetachmentEffects', 'physicsShape', 'circularVisionRadius', 'customizableVehicleAreas', 'multiGun', 'prefabs', 'multiGunState')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Turret, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.gunPosition = None
        self.gunJointPitch = None
        self.rotationSpeed = component_constants.ZERO_FLOAT
        self.turretRotatorHealth = None
        self.surveyingDeviceHealth = None
        self.invisibilityFactor = component_constants.DEFAULT_INVISIBILITY_FACTOR
        self.guns = None
        self.circularVisionRadius = None
        self.multiGun = None
        self.primaryArmor = component_constants.EMPTY_TUPLE
        self.physicsShape = None
        self.ceilless = False
        self.showEmblemsOnGun = False
        self.turretRotatorSoundManual = None
        self.turretRotatorSoundGear = None
        self.AODecals = None
        self.turretDetachmentEffects = None
        self.customizableVehicleAreas = None
        self.prefabs = component_constants.EMPTY_TUPLE
        self.multiGunState = None
        return

    @property
    def isGunCarriage(self):
        return 'gunCarriage' in self.tags


@add_shallow_copy('__weakref__')
class Gun(InstallableItem):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('rotationSpeed', 'reloadTime', 'aimingTime', 'forcedReloadTime', 'maxAmmo', 'invisibilityFactorAtShot', 'effects', 'burstStartEffects', 'reloadEffect', 'reloadEffectSets', 'impulse', 'recoil', 'animateEmblemSlots', 'shotOffset', 'turretYawLimits', 'pitchLimits', 'staticTurretYaw', 'staticPitch', 'shotDispersionAngle', 'shotDispersionFactors', 'burst', 'clip', 'shots', 'shootImpulses', 'autoreload', 'autoreloadHasBoost', 'drivenJoints', 'customizableVehicleAreas', 'dualGun', 'autoShoot', 'spin', 'edgeByVisualModel', 'prefabs', 'spinEffect', 'temperature', '__weakref__', 'shootImpulses', 'dualAccuracy')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Gun, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.rotationSpeed = component_constants.ZERO_FLOAT
        self.reloadTime = component_constants.ZERO_FLOAT
        self.aimingTime = component_constants.ZERO_FLOAT
        self.forcedReloadTime = component_constants.ZERO_FLOAT
        self.maxAmmo = component_constants.ZERO_INT
        self.invisibilityFactorAtShot = component_constants.ZERO_FLOAT
        self.turretYawLimits = None
        self.shotOffset = None
        self.pitchLimits = None
        self.staticTurretYaw = None
        self.staticPitch = None
        self.shotDispersionAngle = component_constants.ZERO_FLOAT
        self.shotDispersionFactors = None
        self.autoreload = component_constants.DEFAULT_GUN_AUTORELOAD
        self.autoreloadHasBoost = False
        self.burst = component_constants.DEFAULT_GUN_BURST
        self.clip = component_constants.DEFAULT_GUN_CLIP
        self.shots = component_constants.EMPTY_TUPLE
        self.dualGun = component_constants.DEFAULT_GUN_DUALGUN
        self.dualAccuracy = component_constants.DEFAULT_GUN_DUAL_ACCURACY
        self.autoShoot = component_constants.DEFAULT_GUN_AUTOSHOOT
        self.spin = component_constants.DEFAULT_SPIN_GUN
        self.drivenJoints = None
        self.effects = None
        self.burstStartEffects = None
        self.reloadEffect = None
        self.reloadEffectSets = None
        self.impulse = component_constants.ZERO_FLOAT
        self.recoil = None
        self.spinEffect = None
        self.animateEmblemSlots = True
        self.customizableVehicleAreas = None
        self.edgeByVisualModel = True
        self.prefabs = component_constants.EMPTY_TUPLE
        self.shootImpulses = component_constants.EMPTY_TUPLE
        self.temperature = None
        return


@add_shallow_copy('variantName')
class Hull(BasicItem):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('variantName', 'hitTesterManager', 'materials', 'weight', 'maxHealth', 'ammoBayHealth', 'armorHomogenization', 'turretPositions', 'turretPitches', 'turretHardPoints', 'variantMatch', 'fakeTurrets', 'emblemSlots', 'slotsAnchors', 'modelsSets', 'models', 'swinging', 'customEffects', 'AODecals', 'camouflage', 'hangarShadowTexture', 'primaryArmor', 'customizableVehicleAreas', 'burnoutAnimation', 'prefabs')

    def __init__(self):
        super(Hull, self).__init__(component_constants.UNDEFINED_ITEM_TYPE_ID, component_constants.ZERO_INT, component_constants.EMPTY_STRING, component_constants.ZERO_INT)
        self.variantName = component_constants.EMPTY_STRING
        self.hitTesterManager = None
        self.materials = None
        self.weight = component_constants.ZERO_FLOAT
        self.maxHealth = component_constants.ZERO_INT
        self.ammoBayHealth = None
        self.turretPositions = component_constants.EMPTY_TUPLE
        self.turretPitches = component_constants.EMPTY_TUPLE
        self.variantMatch = component_constants.DEFAULT_HULL_VARIANT_MATCH
        self.fakeTurrets = component_constants.DEFAULT_FAKE_TURRETS
        self.armorHomogenization = component_constants.DEFAULT_ARMOR_HOMOGENIZATION
        self.primaryArmor = component_constants.EMPTY_TUPLE
        self.turretHardPoints = component_constants.EMPTY_TUPLE
        self.emblemSlots = component_constants.EMPTY_TUPLE
        self.slotsAnchors = component_constants.EMPTY_TUPLE
        self.modelsSets = None
        self.models = None
        self.swinging = None
        self.customEffects = component_constants.EMPTY_TUPLE
        self.AODecals = component_constants.EMPTY_TUPLE
        self.camouflage = shared_components.EMPTY_CAMOUFLAGE
        self.hangarShadowTexture = component_constants.EMPTY_STRING
        self.customizableVehicleAreas = None
        self.burnoutAnimation = None
        self.prefabs = component_constants.EMPTY_TUPLE
        return

    @property
    def hitTester(self):
        return self.hitTesterManager.activeHitTester

    def copy(self):
        return Hull()


class Shell(BasicItem):
    __slots__ = ('caliber', 'isTracer', 'isForceTracer', 'damage', 'damageRandomization', 'piercingPowerRandomization', 'icon', 'iconName', 'isGold', 'type', 'stun', 'effectsIndex', 'tags', 'secondaryAttackReason', 'useAltDamageRandomization', 'dynamicEffectsIndexes', 'hitDeviceChanceMultiplier', 'hitCrewChanceMultiplier', 'maxDistanceInsideVehicle', 'damagedDevicesLimit', 'engineFireFactor', 'distanceDmg', 'skipSelfDamage')

    def __init__(self, typeID, componentID, componentName, compactDescr):
        super(Shell, self).__init__(typeID, componentID, componentName, compactDescr)
        self.caliber = component_constants.ZERO_FLOAT
        self.isTracer = False
        self.isForceTracer = False
        self.damage = component_constants.EMPTY_TUPLE
        self.damageRandomization = component_constants.DEFAULT_DAMAGE_RANDOMIZATION
        self.piercingPowerRandomization = component_constants.DEFAULT_PIERCING_POWER_RANDOMIZATION
        self.stun = None
        self.type = None
        self.effectsIndex = component_constants.ZERO_INT
        self.dynamicEffectsIndexes = component_constants.EMPTY_TUPLE
        self.skipSelfDamage = False
        self.isGold = False
        self.icon = None
        self.iconName = None
        self.secondaryAttackReason = ATTACK_REASON.NONE
        self.useAltDamageRandomization = False
        self.hitDeviceChanceMultiplier = component_constants.DEFAULT_SHELL_HIT_EXTRAS_CHANCE_MULTIPLIER
        self.hitCrewChanceMultiplier = component_constants.DEFAULT_SHELL_HIT_EXTRAS_CHANCE_MULTIPLIER
        self.maxDistanceInsideVehicle = None
        self.damagedDevicesLimit = None
        self.engineFireFactor = None
        self.distanceDmg = None
        return

    def __repr__(self):
        nationId, shellId = self.id
        return 'Shell(nation = {}, shellId = {}, shellName={})'.format(nations.NAMES[nationId], shellId, self.name)

    @property
    def kind(self):
        return self.type.name

    @property
    def avgDamage(self):
        return self.distanceDmg.avgDamage if self.distanceDmg is not None else self.damage[0]

    @property
    def dmgLimits(self):
        if self.distanceDmg is not None:
            dmg = self.distanceDmg.damage
            minDamage = dmg.min
            maxDamage = dmg.max
        else:
            damage = self.damage[0]
            minDamage = damage
            maxDamage = damage
        return (minDamage, maxDamage)

    @property
    def randomizationDmgLimits(self):
        minDamage, maxDamage = self.dmgLimits
        minDamageRand = minDamage * (1.0 - self.damageRandomization)
        maxDamageRand = maxDamage * (1.0 + self.damageRandomization)
        return (minDamageRand, maxDamageRand)

    @property
    def hasStun(self):
        return self.stun is not None

    @property
    def isAmmoPercingType(self):
        return self.kind in (SHELL_TYPES.ARMOR_PIERCING,
         SHELL_TYPES.ARMOR_PIERCING_HE,
         SHELL_TYPES.ARMOR_PIERCING_CR,
         SHELL_TYPES.ARMOR_PIERCING_FSDS)

    @property
    def prereqEffectIndexes(self):
        return (self.effectsIndex,) + tuple((item.effectsIndex for item in self.dynamicEffectsIndexes))


_TYPE_ID_TO_CLASS = {ITEM_TYPES.vehicleChassis: Chassis,
 ITEM_TYPES.vehicleTurret: Turret,
 ITEM_TYPES.vehicleGun: Gun,
 ITEM_TYPES.vehicleEngine: Engine,
 ITEM_TYPES.vehicleFuelTank: FuelTank,
 ITEM_TYPES.vehicleRadio: Radio}

def createInstallableItem(itemTypeID, nationID, itemID, name):
    if itemTypeID in _TYPE_ID_TO_CLASS:
        clazz = _TYPE_ID_TO_CLASS[itemTypeID]
        return clazz(itemTypeID, (nationID, itemID), name, makeIntCompactDescrByID(ITEM_TYPE_NAMES[itemTypeID], nationID, itemID))
    raise SoftException('Item can not be created by type {}'.format(itemTypeID))


def createChassis(nationID, componentID, name):
    return createInstallableItem(ITEM_TYPES.vehicleChassis, nationID, componentID, name)


def createTurret(nationID, componentID, name):
    return createInstallableItem(ITEM_TYPES.vehicleTurret, nationID, componentID, name)


def createGun(nationID, componentID, name):
    return createInstallableItem(ITEM_TYPES.vehicleGun, nationID, componentID, name)


def createEngine(nationID, componentID, name):
    return createInstallableItem(ITEM_TYPES.vehicleEngine, nationID, componentID, name)


def createFuelTank(nationID, componentID, name):
    return createInstallableItem(ITEM_TYPES.vehicleFuelTank, nationID, componentID, name)


def createRadio(nationID, componentID, name):
    return createInstallableItem(ITEM_TYPES.vehicleRadio, nationID, componentID, name)


def createShell(nationID, componentID, name):
    return Shell(ITEM_TYPES.shell, (nationID, componentID), name, makeIntCompactDescrByID('shell', nationID, componentID))
