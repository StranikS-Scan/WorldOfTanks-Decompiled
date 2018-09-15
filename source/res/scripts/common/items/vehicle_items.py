# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/vehicle_items.py
import functools
import Math
from ModelHitTester import ModelHitTester
from constants import SHELL_TYPES
from items import ITEM_TYPES, ITEM_TYPE_NAMES, makeIntCompactDescrByID
from items.basic_item import BasicItem
from items.components import component_constants
from items.components import chassis_components
from items.components import gun_components
from items.components import shared_components
from items.components import shell_components
from items.components import sound_components

class VEHICLE_ITEM_STATUS(object):
    UNDEFINED = 0
    EMPTY = 1
    SHARED = 2
    LOCAL = 3


class _ShallowCopyWrapper(object):
    __slots__ = ('__exclude',)

    def __init__(self, *exclude):
        super(_ShallowCopyWrapper, self).__init__()
        self.__exclude = exclude

    def __call__(self, clazz):
        fields = getattr(clazz, '__slots__', None)
        if fields is None:
            raise ValueError('Slots are not defined in {}'.format(clazz))
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
    """Decorator wraps method "copy" of desired class. This method returns new object and
    then inserts references into it to the objects found in the original
    by iterating __slots__ in wrapped class only.
    :param exclude: sequence of properties that are excluded in copy process.
    :return: instance of _ShallowCopyWrapper.
    """
    return _ShallowCopyWrapper(*exclude)


@add_shallow_copy('status')
class VehicleItem(BasicItem):
    """Class provides basic information about vehicle/its component."""
    __slots__ = ('level', 'status')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1, status=VEHICLE_ITEM_STATUS.UNDEFINED):
        super(VehicleItem, self).__init__(typeID, componentID, componentName, compactDescr)
        self.level = level
        self.status = status

    def __repr__(self):
        return '{}(id={}, name={}, level={}, status={})'.format(self.__class__.__name__, self.id, self.name, self.level, self.status)


@add_shallow_copy('unlocks')
class InstallableItem(VehicleItem):
    """Class provides configuration of installable vehicle's item."""
    __slots__ = ('weight', 'models', 'materials', 'hitTester', 'unlocks', 'armorHomogenization', 'camouflage', 'healthParams', 'sounds', 'emblemSlots')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(InstallableItem, self).__init__(typeID, componentID, componentName, compactDescr, level=level, status=VEHICLE_ITEM_STATUS.EMPTY)
        self.weight = component_constants.ZERO_FLOAT
        self.unlocks = component_constants.EMPTY_TUPLE
        self.healthParams = shared_components.DEFAULT_DEVICE_HEALTH
        self.armorHomogenization = component_constants.DEFAULT_ARMOR_HOMOGENIZATION
        self.materials = None
        self.hitTester = None
        self.models = None
        self.camouflage = shared_components.DEFAULT_CAMOUFLAGE
        self.sounds = None
        self.emblemSlots = component_constants.EMPTY_TUPLE
        return

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


@add_shallow_copy()
class Chassis(InstallableItem):
    """Class provides configuration of vehicle's chassis."""
    __slots__ = ('hullPosition', 'topRightCarryingPoint', 'navmeshGirth', 'minPlaneNormalY', 'maxLoad', 'specificFriction', 'rotationSpeed', 'rotationSpeedLimit', 'rotationIsAroundCenter', 'shotDispersionFactors', 'terrainResistance', 'bulkHealthFactor', 'carryingTriangles', 'drivingWheelsSizes', 'traces', 'tracks', 'wheels', 'groundNodes', 'trackNodes', 'trackParams', 'splineDesc', 'leveredSuspension', 'suspensionSpringsLength', 'hullAimingSound', 'effects', 'customEffects', 'AODecals', 'brakeForce')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Chassis, self).__init__(typeID, componentID, componentName, compactDescr, level=level)
        self.hullPosition = None
        self.topRightCarryingPoint = None
        self.navmeshGirth = component_constants.ZERO_FLOAT
        self.minPlaneNormalY = component_constants.ZERO_FLOAT
        self.maxLoad = component_constants.ZERO_FLOAT
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
        self.groundNodes = None
        self.trackNodes = None
        self.trackParams = None
        self.splineDesc = None
        self.leveredSuspension = None
        self.hullAimingSound = None
        self.suspensionSpringsLength = None
        self.effects = None
        self.customEffects = None
        self.AODecals = component_constants.EMPTY_TUPLE
        return


@add_shallow_copy()
class Engine(InstallableItem):
    """Class provides configuration of vehicle's engine."""
    __slots__ = ('power', 'fireStartingChance', 'minFireStartingDamage', 'rpm_min', 'rpm_max')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Engine, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.power = component_constants.ZERO_FLOAT
        self.fireStartingChance = component_constants.ZERO_FLOAT
        self.minFireStartingDamage = component_constants.ZERO_FLOAT
        self.rpm_min = component_constants.ZERO_INT
        self.rpm_max = component_constants.ZERO_INT


class FuelTank(InstallableItem):
    """Class provides configuration of vehicle's fuel tanks."""
    __slots__ = ()

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(FuelTank, self).__init__(typeID, componentID, componentName, compactDescr, level)


@add_shallow_copy()
class Radio(InstallableItem):
    """Class provides configuration of vehicle's radio."""
    __slots__ = ('distance',)

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Radio, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.distance = component_constants.ZERO_FLOAT


@add_shallow_copy()
class Turret(InstallableItem):
    """Class provides configuration of vehicle's turret."""
    __slots__ = ('gunPosition', 'rotationSpeed', 'turretRotatorHealth', 'surveyingDeviceHealth', 'invisibilityFactor', 'primaryArmor', 'ceilless', 'showEmblemsOnGun', 'guns', 'turretRotatorSoundManual', 'turretRotatorSoundGear', 'AODecals', 'turretDetachmentEffects', 'physicsShape', 'circularVisionRadius')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Turret, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.gunPosition = None
        self.rotationSpeed = component_constants.ZERO_FLOAT
        self.turretRotatorHealth = None
        self.surveyingDeviceHealth = None
        self.invisibilityFactor = component_constants.DEFAULT_INVISIBILITY_FACTOR
        self.guns = None
        self.circularVisionRadius = None
        self.primaryArmor = component_constants.EMPTY_TUPLE
        self.physicsShape = None
        self.ceilless = False
        self.showEmblemsOnGun = False
        self.turretRotatorSoundManual = None
        self.turretRotatorSoundGear = None
        self.AODecals = None
        self.turretDetachmentEffects = None
        return


@add_shallow_copy()
class Gun(InstallableItem):
    """Class provides configuration of vehicle's gun."""
    __slots__ = ('rotationSpeed', 'reloadTime', 'aimingTime', 'maxAmmo', 'invisibilityFactorAtShot', 'effects', 'reloadEffect', 'impulse', 'recoil', 'animateEmblemSlots', 'turretYawLimits', 'pitchLimits', 'staticTurretYaw', 'staticPitch', 'shotDispersionAngle', 'shotDispersionFactors', 'burst', 'clip', 'shots', 'drivenJoints', 'combinedPitchLimits')

    def __init__(self, typeID, componentID, componentName, compactDescr, level=1):
        super(Gun, self).__init__(typeID, componentID, componentName, compactDescr, level)
        self.rotationSpeed = component_constants.ZERO_FLOAT
        self.reloadTime = component_constants.ZERO_FLOAT
        self.aimingTime = component_constants.ZERO_FLOAT
        self.maxAmmo = component_constants.ZERO_INT
        self.invisibilityFactorAtShot = component_constants.ZERO_FLOAT
        self.turretYawLimits = None
        self.pitchLimits = None
        self.staticTurretYaw = None
        self.staticPitch = None
        self.shotDispersionAngle = component_constants.ZERO_FLOAT
        self.shotDispersionFactors = None
        self.burst = component_constants.DEFAULT_GUN_BURST
        self.clip = component_constants.DEFAULT_GUN_CLIP
        self.shots = component_constants.EMPTY_TUPLE
        self.drivenJoints = None
        self.combinedPitchLimits = None
        self.effects = None
        self.reloadEffect = None
        self.impulse = component_constants.ZERO_FLOAT
        self.recoil = None
        self.animateEmblemSlots = True
        return


@add_shallow_copy('variantName')
class Hull(BasicItem):
    """Class contains configuration of hull for each vehicle separately.
    This class is extended from BasicItem to unify access to properties."""
    __slots__ = ('variantName', 'hitTester', 'materials', 'weight', 'maxHealth', 'ammoBayHealth', 'armorHomogenization', 'turretPositions', 'turretHardPoints', 'variantMatch', 'fakeTurrets', 'emblemSlots', 'models', 'swinging', 'customEffects', 'AODecals', 'camouflage', 'hangarShadowTexture', 'primaryArmor')

    def __init__(self):
        super(Hull, self).__init__(component_constants.UNDEFINED_ITEM_TYPE_ID, component_constants.ZERO_INT, component_constants.EMPTY_STRING, component_constants.ZERO_INT)
        self.variantName = component_constants.EMPTY_STRING
        self.hitTester = None
        self.materials = None
        self.weight = component_constants.ZERO_FLOAT
        self.maxHealth = component_constants.ZERO_INT
        self.ammoBayHealth = None
        self.turretPositions = component_constants.EMPTY_TUPLE
        self.variantMatch = component_constants.DEFAULT_HULL_VARIANT_MATCH
        self.fakeTurrets = component_constants.DEFAULT_FAKE_TURRETS
        self.armorHomogenization = component_constants.DEFAULT_ARMOR_HOMOGENIZATION
        self.primaryArmor = component_constants.EMPTY_TUPLE
        self.turretHardPoints = component_constants.EMPTY_TUPLE
        self.emblemSlots = component_constants.EMPTY_TUPLE
        self.models = None
        self.swinging = None
        self.customEffects = component_constants.EMPTY_TUPLE
        self.AODecals = component_constants.EMPTY_TUPLE
        self.camouflage = shared_components.DEFAULT_CAMOUFLAGE
        self.hangarShadowTexture = None
        return

    def copy(self):
        return Hull()


class Shell(BasicItem):
    """Class provides configuration of vehicle's shell."""
    __slots__ = ('caliber', 'isTracer', 'damage', 'damageRandomization', 'piercingPowerRandomization', 'icon', 'isGold', 'type', 'stun', 'effectsIndex')

    def __init__(self, typeID, componentID, componentName, compactDescr):
        super(Shell, self).__init__(typeID, componentID, componentName, compactDescr)
        self.caliber = component_constants.ZERO_FLOAT
        self.isTracer = False
        self.damage = component_constants.EMPTY_TUPLE
        self.damageRandomization = component_constants.DEFAULT_DAMAGE_RANDOMIZATION
        self.piercingPowerRandomization = component_constants.DEFAULT_PIERCING_POWER_RANDOMIZATION
        self.stun = None
        self.type = None
        self.effectsIndex = component_constants.ZERO_INT
        self.isGold = False
        self.icon = None
        return

    @property
    def kind(self):
        """Gets kind of shell. Available values of kind are in SHELL_TYPES_LIST."""
        return self.type.name

    @property
    def hasStun(self):
        """Does shell have stun effect?"""
        return self.stun is not None

    @property
    def isAmmoPercingType(self):
        return self.kind in (SHELL_TYPES.ARMOR_PIERCING, SHELL_TYPES.ARMOR_PIERCING_HE, SHELL_TYPES.ARMOR_PIERCING_CR)


_TYPE_ID_TO_CLASS = {ITEM_TYPES.vehicleChassis: Chassis,
 ITEM_TYPES.vehicleTurret: Turret,
 ITEM_TYPES.vehicleGun: Gun,
 ITEM_TYPES.vehicleEngine: Engine,
 ITEM_TYPES.vehicleFuelTank: FuelTank,
 ITEM_TYPES.vehicleRadio: Radio}

def createInstallableItem(itemTypeID, nationID, itemID, name):
    """ Creates vehicle's item by ID of type.
    :param itemTypeID: integer containing index of ITEM_TYPE.
    :param nationID: integer containing ID of nation.
    :param itemID: integer containing unique ID of item in nation scope.
    :param name: string containing name of component.
    :return: instance of item.
    """
    if itemTypeID in _TYPE_ID_TO_CLASS:
        clazz = _TYPE_ID_TO_CLASS[itemTypeID]
        return clazz(itemTypeID, (nationID, itemID), name, makeIntCompactDescrByID(ITEM_TYPE_NAMES[itemTypeID], nationID, itemID))
    raise ValueError('Item can not be created by type {}'.format(itemTypeID))


def createChassis(nationID, componentID, name):
    """ Creates vehicle's chassis.
    :param nationID: integer containing ID of nation.
    :param componentID: integer containing ID of chassis in nation scope.
    :param name: string containing name of chassis.
    :return: instance of Chassis.
    """
    return createInstallableItem(ITEM_TYPES.vehicleChassis, nationID, componentID, name)


def createTurret(nationID, componentID, name):
    """ Creates vehicle's chassis.
    :param nationID: integer containing ID of nation.
    :param componentID: integer containing ID of turret in nation scope.
    :param name: string containing name of turret.
    :return: instance of Turret.
    """
    return createInstallableItem(ITEM_TYPES.vehicleTurret, nationID, componentID, name)


def createGun(nationID, componentID, name):
    """ Creates vehicle's gun.
    :param nationID: integer containing ID of nation.
    :param componentID: integer containing ID of gun in nation scope.
    :param name: string containing name of gun.
    :return: instance of Gun.
    """
    return createInstallableItem(ITEM_TYPES.vehicleGun, nationID, componentID, name)


def createEngine(nationID, componentID, name):
    """ Creates vehicle's engine.
    :param nationID: integer containing ID of nation.
    :param componentID: integer containing ID of engine in nation scope.
    :param name: string containing name of engine.
    :return: instance of Engine.
    """
    return createInstallableItem(ITEM_TYPES.vehicleEngine, nationID, componentID, name)


def createFuelTank(nationID, componentID, name):
    """ Creates vehicle's fuel tanks.
    :param nationID: integer containing ID of nation.
    :param componentID: integer containing ID of fuel tanks in nation scope.
    :param name: string containing name of engine.
    :return: instance of FuelTank.
    """
    return createInstallableItem(ITEM_TYPES.vehicleFuelTank, nationID, componentID, name)


def createRadio(nationID, componentID, name):
    """ Creates vehicle's radio.
    :param nationID: integer containing ID of nation.
    :param componentID: integer containing ID of radio in nation scope.
    :param name: string containing name of radio.
    :return: instance of Radio.
    """
    return createInstallableItem(ITEM_TYPES.vehicleRadio, nationID, componentID, name)


def createShell(nationID, componentID, name):
    """Creates vehicle's shell.
    :param nationID: integer containing ID of nation.
    :param componentID: integer containing ID of shell in nation scope.
    :param name: string containing name of shell.
    :return: instance of Shell.
    """
    return Shell(ITEM_TYPES.shell, (nationID, componentID), name, makeIntCompactDescrByID('shell', nationID, componentID))
