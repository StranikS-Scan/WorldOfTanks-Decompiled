# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/descr_modify_attrs.py
import inspect
from copy import copy
from functools import partial
from math import tan, atan, radians, degrees
from weakref import proxy
from typing import TYPE_CHECKING
from constants import IS_CELLAPP
from debug_utils import LOG_WARNING, LOG_CURRENT_EXCEPTION
from descr_modify_attrs_allowed import DESCR_MODIFY_ATTRS_ALLOWED, DESCR_MODIFY_ATTRS_TYPE, IS_ARRAY
from items.attributes_helpers import DESCR_MODIFY_ATTR_PREFIX, MODIFIER_TYPE
from items.components.component_constants import HP_TO_WATTS, KMH_TO_MS
if TYPE_CHECKING:
    import items.vehicle_items as vehicle_items
    from items.components.gun_components import GunShot
    from items.components.shared_components import DeviceHealth
    from items.components.shell_components import ShellType, HighExplosiveImpactParams
    from items.components.component_constants import TwinGun, AutoShoot, DualGun, DualAccuracy
    from items.vehicles import VehicleType, VehicleDescriptor

class AttrDict(dict):

    def __init__(self, vehDescrWrapper, parentDict):
        super(AttrDict, self).__init__(parentDict)
        self.__dict__ = self

        def finalizer():
            self.__dict__ = {}

        vehDescrWrapper.finalizers.append(finalizer)


class ItemWrapper(object):
    _setters = {}

    def __init__(self, item):
        self.__dict__['item'] = item

    def isSetter(self, attrName):
        setters = self._setters.get(self.__class__)
        if not setters:
            setters = set()
            for name, member in inspect.getmembers(self.__class__):
                if isinstance(member, property) and member.fset is not None:
                    setters.add(name)

            self._setters[self.__class__] = setters
        return attrName in setters

    def __getattr__(self, attrName):
        return getattr(self.item, attrName)

    def __setattr__(self, attrName, value):
        if self.isSetter(attrName):
            return super(ItemWrapper, self).__setattr__(attrName, value)
        try:
            setattr(self.item, attrName, value)
        except AttributeError:
            super(ItemWrapper, self).__setattr__(attrName, value)


class cached_property(object):

    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        elif self.name in instance.__dict__:
            return instance.__dict__[self.name]
        else:
            res = instance.__dict__[self.name] = self.func(instance)
            return res


class cached_property_namedtuple(object):

    def __init__(self, func, name=None):
        self.func = func
        self.__doc__ = getattr(func, '__doc__')
        self.name = name or func.__name__

    def __get__(self, instance, type=None):
        if instance is None:
            return self
        elif self.name in instance.__dict__:
            return instance.__dict__[self.name]
        else:
            namedTuple = self.func(instance)
            res = instance.__dict__[self.name] = AttrDict(instance, namedTuple._asdict())

            def finalizer():
                setattr(instance.gun, self.name, namedTuple._replace(**res))

            instance.finalizers.append(finalizer)
            return res


class GunWrapper(ItemWrapper):

    def __init__(self, gun):
        super(GunWrapper, self).__init__(gun)

    @property
    def shotDispersionRadius(self):
        return tan(self.item.shotDispersionAngle) * 100.0

    @shotDispersionRadius.setter
    def shotDispersionRadius(self, value):
        if value < 0.01:
            value = 0.01
        self.item.shotDispersionAngle = atan(value / 100.0)


class EngineWrapper(ItemWrapper):

    def __init__(self, engine, vehDescrWrapper):
        super(EngineWrapper, self).__init__(engine)
        self.vehDescrWrapper = proxy(vehDescrWrapper)

    @property
    def power(self):
        return self.item.power / HP_TO_WATTS

    @power.setter
    def power(self, value):
        self.item.power = value * HP_TO_WATTS
        xphysicsEngine = self.vehDescrWrapper.xphysicsEngine
        if xphysicsEngine:
            self.vehDescrWrapper.xphysicsEngine.smplEnginePower = value

    @property
    def maxSpeedForward(self):
        return self.vehDescrWrapper.type.speedLimits[0] / KMH_TO_MS

    @maxSpeedForward.setter
    def maxSpeedForward(self, value):
        value *= KMH_TO_MS
        self.__setSpeedLimits(0, value)
        xphysicsEngine = self.vehDescrWrapper.xphysicsEngine
        if xphysicsEngine:
            self.vehDescrWrapper.xphysicsEngine.smplFwMaxSpeed = value

    @property
    def maxSpeedBack(self):
        return self.vehDescrWrapper.type.speedLimits[1] / KMH_TO_MS

    @maxSpeedBack.setter
    def maxSpeedBack(self, value):
        value *= KMH_TO_MS
        self.__setSpeedLimits(1, value)
        xphysicsEngine = self.vehDescrWrapper.xphysicsEngine
        if xphysicsEngine:
            self.vehDescrWrapper.xphysicsEngine.smplBkMaxSpeed = value

    def __setSpeedLimits(self, index, value):
        type = self.vehDescrWrapper.type
        if isinstance(type.speedLimits, tuple):
            type.speedLimits = list(type.speedLimits)

            def finalizer():
                type.speedLimits = tuple(type.speedLimits)

            self.vehDescrWrapper.finalizers.append(finalizer)
        type.speedLimits[index] = value


class ChassisWrapper(ItemWrapper):

    def __init__(self, chassis, vehDescrWrapper):
        super(ChassisWrapper, self).__init__(chassis)
        self.vehDescrWrapper = proxy(vehDescrWrapper)

    @property
    def rotationSpeedDegrees(self):
        return degrees(self.item.rotationSpeed)

    @rotationSpeedDegrees.setter
    def rotationSpeedDegrees(self, value):
        self.item.rotationSpeed = radians(value)
        if IS_CELLAPP:
            physicsChassis = self.vehDescrWrapper.xphysicsChassis
            prevValue = physicsChassis.gimletGoalWOnSpot
            if prevValue < 1e-07:
                LOG_WARNING('Rotation Speed cant change', self.vehDescrWrapper.vehDescr.name)
                return
            currentValue = physicsChassis.gimletGoalWOnSpot = self.item.rotationSpeed
            koef = currentValue / prevValue
            physicsChassis.gimletGoalWOnMove *= koef
            physicsChassis.angVelocityFactor *= koef
            physicsChassis.angVelocityFactor0 *= koef


class TurretWrapper(ItemWrapper):

    def __init__(self, turret):
        super(TurretWrapper, self).__init__(turret)

    @property
    def rotationSpeedDegrees(self):
        return degrees(self.item.rotationSpeed)

    @rotationSpeedDegrees.setter
    def rotationSpeedDegrees(self, value):
        self.item.rotationSpeed = radians(value)


class XPhysics(object):

    def __init__(self, vehDescrWrapper):
        self.vehDescrWrapper = proxy(vehDescrWrapper)
        self.vehDescr = vehDescrWrapper.vehDescr

    @cached_property
    def __xphysics(self):
        if not self.vehDescr.type.xphysics:
            return None
        else:
            type = self.vehDescrWrapper.type
            xphysics = type.xphysics = copy(type.xphysics)
            if 'detailed' in xphysics:
                xphysics = type.xphysics['detailed'] = copy(xphysics['detailed'])
            return xphysics

    @property
    def engine(self):
        if self.__xphysics:
            self.__xphysics['engines'] = copy(self.__xphysics['engines'])
            return self.__item(self.vehDescr.engine.name, self.__xphysics['engines'])

    @property
    def chassis(self):
        if self.__xphysics:
            self.__xphysics['chassis'] = copy(self.__xphysics['chassis'])
            return self.__item(self.vehDescr.chassis.name, self.__xphysics['chassis'])

    def __item(self, itemName, itemSection):
        itemSection[itemName] = AttrDict(self.vehDescrWrapper, itemSection[itemName])
        return itemSection[itemName]


class VehDescrWrapper(object):

    def __init__(self, vehDescr):
        self.vehDescr = vehDescr
        self.finalizers = []

    def finalize(self):
        for finalizer in self.finalizers:
            finalizer()

        self.finalizers = []
        del self.__dict__

    @cached_property
    def type(self):
        self.vehDescr.type = copy(self.vehDescr.type)
        return self.vehDescr.type

    @cached_property
    def hullAimingParamsPitch(self):
        self.type.hullAimingParams = copy(self.type.hullAimingParams)
        self.type.hullAimingParams['pitch'] = AttrDict(self, self.type.hullAimingParams['pitch'])
        return self.type.hullAimingParams['pitch']

    @cached_property
    def typeCollisionEffectVelocities(self):
        ret = self.type.collisionEffectVelocities = AttrDict(self, self.type.collisionEffectVelocities)
        return ret

    @cached_property
    def typeDamageByStaticsChances(self):
        ret = self.type.damageByStaticsChances = AttrDict(self, self.type.damageByStaticsChances)
        return ret

    @cached_property
    def typeInvisibilityDeltas(self):
        ret = self.type.invisibilityDeltas = AttrDict(self, self.type.invisibilityDeltas)
        return ret

    @cached_property
    def siegeModeParams(self):
        if self.type.siegeModeParams is None:
            return
        else:
            self.type.siegeModeParams = AttrDict(self, self.type.siegeModeParams)
            return self.type.siegeModeParams

    @cached_property
    def hull(self):
        self.vehDescr.hull = copy(self.vehDescr.hull)
        return self.vehDescr.hull

    def __appendActiveGunFinalizer(self):

        def finalizer():
            self.vehDescr.activeTurretPosition = 0

        self.finalizers.append(finalizer)

    @cached_property
    def turret(self):
        turret, gun = self.vehDescr.turrets[0]
        turret = copy(turret)
        self.vehDescr.turrets = [(turret, gun)] + self.vehDescr.turrets[1:]
        self.__appendActiveGunFinalizer()
        return TurretWrapper(turret)

    @cached_property
    def gun(self):
        turret, gun = self.vehDescr.turrets[0]
        gun = copy(gun)
        self.vehDescr.turrets = [(turret, gun)] + self.vehDescr.turrets[1:]
        self.__appendActiveGunFinalizer()
        return GunWrapper(gun)

    @cached_property
    def gunPitchLimits(self):
        self.gun.pitchLimits = AttrDict(self, self.gun.pitchLimits)
        return self.gun.pitchLimits

    @cached_property
    def gunShotDispersionFactors(self):
        self.gun.shotDispersionFactors = AttrDict(self, self.gun.shotDispersionFactors)
        return self.gun.shotDispersionFactors

    @cached_property_namedtuple
    def twinGun(self):
        return self.gun.twinGun

    @cached_property_namedtuple
    def dualGun(self):
        return self.gun.dualGun

    @cached_property_namedtuple
    def dualAccuracy(self):
        return self.gun.dualAccuracy

    @cached_property_namedtuple
    def autoShoot(self):
        return self.gun.autoShoot

    @cached_property
    def chassis(self):
        self.vehDescr.chassis = copy(self.vehDescr.chassis)
        return ChassisWrapper(self.vehDescr.chassis, self)

    @cached_property
    def chassisShotDispersionFactors(self):
        self.chassis.shotDispersionFactors = self.chassis.shotDispersionFactors
        return self.chassis.shotDispersionFactors

    @cached_property
    def engine(self):
        self.vehDescr.engine = copy(self.vehDescr.engine)
        return EngineWrapper(self.vehDescr.engine, self)

    @cached_property
    def fuelTank(self):
        self.vehDescr.fuelTank = copy(self.vehDescr.fuelTank)
        return self.vehDescr.fuelTank

    @cached_property
    def radio(self):
        self.vehDescr.radio = copy(self.vehDescr.radio)
        return self.vehDescr.radio

    @cached_property
    def ammoBayHealth(self):
        res = self.hull.ammoBayHealth = copy(self.hull.ammoBayHealth)
        return res

    @cached_property
    def gunShotsLen(self):
        return len(self.vehDescr.gun.shots)

    @cached_property
    def shots(self):
        self.gun.shots = list(self.gun.shots)

        def finalizer():
            self.gun.shots = tuple(self.gun.shots)

        self.finalizers.append(finalizer)
        return self.gun.shots

    @cached_property
    def shot0(self):
        self.shots[0] = copy(self.shots[0])
        return self.shots[0]

    @cached_property
    def shot1(self):
        if self.gunShotsLen < 2:
            return None
        else:
            self.shots[1] = copy(self.shots[1])
            return self.shots[1]

    @cached_property
    def shot2(self):
        if self.gunShotsLen < 3:
            return None
        else:
            self.shots[2] = copy(self.shots[2])
            return self.shots[2]

    @cached_property
    def shell0(self):
        self.shot0.shell = copy(self.shot0.shell)
        return self.shot0.shell

    @cached_property
    def shell1(self):
        if self.gunShotsLen < 2:
            return None
        else:
            self.shot1.shell = copy(self.shot1.shell)
            return self.shot1.shell

    @cached_property
    def shell2(self):
        if self.gunShotsLen < 3:
            return None
        else:
            self.shot2.shell = copy(self.shot2.shell)
            return self.shot2.shell

    @cached_property
    def shellType0(self):
        self.shot0.shell.type = copy(self.shot0.shell.type)
        return self.shot0.shell.type

    @cached_property
    def shellType1(self):
        if self.gunShotsLen < 2:
            return None
        else:
            self.shot1.shell.type = copy(self.shot1.shell.type)
            return self.shot1.shell.type

    @cached_property
    def shellType2(self):
        if self.gunShotsLen < 3:
            return None
        else:
            self.shot2.shell.type = copy(self.shot2.shell.type)
            return self.shot2.shell.type

    def __hasArmorSpalls(self, ind):
        return None if self.gunShotsLen < ind + 1 else hasattr(self.vehDescr.gun.shots[ind].shell.type, 'armorSpalls')

    @cached_property
    def shellTypeArmorSpalls0(self):
        if not self.__hasArmorSpalls(0):
            return None
        else:
            self.shellType0.armorSpalls = copy(self.shellType0.armorSpalls)
            return self.shellType0.armorSpalls

    @cached_property
    def shellTypeArmorSpalls1(self):
        if not self.__hasArmorSpalls(1):
            return None
        else:
            self.shellType1.armorSpalls = copy(self.shellType1.armorSpalls)
            return self.shellType1.armorSpalls

    @cached_property
    def shellTypeArmorSpalls2(self):
        if not self.__hasArmorSpalls(2):
            return None
        else:
            self.shellType2.armorSpalls = copy(self.shellType2.armorSpalls)
            return self.shellType2.armorSpalls

    @cached_property
    def __xphysics(self):
        return XPhysics(self)

    @cached_property
    def xphysicsEngine(self):
        return self.__xphysics.engine

    @cached_property
    def xphysicsChassis(self):
        return self.__xphysics.chassis

    __projectileSpeedFactor = None

    @classmethod
    def projectileSpeedFactor(cls):
        if cls.__projectileSpeedFactor is None:
            from items import vehicles
            cls.__projectileSpeedFactor = vehicles.g_cache.commonConfig['miscParams']['projectileSpeedFactor']
        return cls.__projectileSpeedFactor


APPLIERS = {MODIFIER_TYPE.ADD: lambda obj, value: obj + value,
 MODIFIER_TYPE.MUL: lambda obj, value: obj * value,
 MODIFIER_TYPE.SET: lambda obj, value: value}
MERGERS = {MODIFIER_TYPE.ADD: lambda obj, value: obj + value,
 MODIFIER_TYPE.MUL: lambda obj, value: obj + value - 1,
 MODIFIER_TYPE.SET: lambda obj, value: value}

def arrayItemApplyerDegrees(arr, index, value, applier):
    degreesVal = degrees(arr[index])
    arr[index] = radians(applier(degreesVal, value))


gunPitchLimitsNameMap = {'maxPitchDegrees': 'maxPitch',
 'minPitchDegrees': 'minPitch'}

def processValue(obj, valueName, index, operation, attrName, value):
    valueObj = getattr(obj, valueName, None)
    if valueObj is None:
        return
    else:
        valueObjType = valueObj.__class__
        applier = APPLIERS[operation]
        if index is not None:
            isArray = True
        else:
            isArray = DESCR_MODIFY_ATTRS_TYPE.get(attrName)
        if isArray:
            nextObj = list(valueObj)
            if index is None:
                indexes = range(len(nextObj))
            else:
                indexes = [index]
            for ind in indexes:
                if ind >= len(nextObj):
                    LOG_WARNING('[DESCR_MODIFY] Index out of range', attrName, operation, nextObj, index)
                    break
                valueType = nextObj[ind].__class__
                nextObj[ind] = valueType(applier(nextObj[ind], value))

            setattr(obj, valueName, valueObjType(nextObj))
        else:
            setattr(obj, valueName, valueObjType(applier(valueObj, value)))
        return


def gunPitchLimitsProcessor(obj, valueName, index, operation, attrName, value, vehDescrWrapper):
    valueName = gunPitchLimitsNameMap[valueName]
    valueObj = obj[valueName]
    if isinstance(valueObj, tuple):
        valueObj = obj[valueName] = list(valueObj)
        for ind in xrange(len(valueObj)):
            valueObj[ind] = list(valueObj[ind])

        def finalize():
            for ind in xrange(len(valueObj)):
                valueObj[ind] = tuple(valueObj[ind])

            obj['absolute'] = (min([ key for _, key in obj['minPitch'] ]), max([ key for _, key in obj['maxPitch'] ]))
            obj[valueName] = tuple(valueObj)

        vehDescrWrapper.finalizers.append(finalize)
    if index is None:
        indexes = range(len(valueObj))
    else:
        indexes = [index]
    applier = APPLIERS[operation]
    for ind in indexes:
        arrayItemApplyerDegrees(valueObj[ind], 1, value, applier)

    return True


def gunTurretYawLimitsDegrees(obj, valueName, index, operation, attrName, value, vehDescrWrapper):
    valueObj = obj.turretYawLimits
    if valueObj is None:
        return True
    else:
        if isinstance(valueObj, tuple):

            def finalize():
                obj.turretYawLimits = tuple(valueObj)

            valueObj = obj.turretYawLimits = list(valueObj)
            vehDescrWrapper.finalizers.append(finalize)
        applier = APPLIERS[operation]
        if index is None:
            firstvalue = value if operation == 'mul' else -value
            arrayItemApplyerDegrees(valueObj, 0, firstvalue, applier)
            arrayItemApplyerDegrees(valueObj, 1, value, applier)
        else:
            arrayItemApplyerDegrees(valueObj, index, value, applier)
        return True


def armorSpallProcessor(spallValueName, obj, valueName, index, operation, attrName, value, vehDescrWrapper):
    obj = getattr(vehDescrWrapper, spallValueName, None)
    if not obj:
        return False
    else:
        attrName = '{}/{}'.format(spallValueName, valueName)
        if operation == 'add' or operation == 'set':
            value *= 0.5
        processValue(obj, valueName, index, operation, attrName, value)
        return False


def shotSpeedProcessor(obj, valueName, index, operation, attrName, value, vehDescrWrapper):
    value *= vehDescrWrapper.projectileSpeedFactor()
    processValue(obj, valueName, index, operation, attrName, value)
    return True


customValueProcessors = {'gunPitchLimits/maxPitchDegrees': gunPitchLimitsProcessor,
 'gunPitchLimits/minPitchDegrees': gunPitchLimitsProcessor,
 'gun/turretYawLimitsDegrees': gunTurretYawLimitsDegrees,
 'shell0/armorDamage': partial(armorSpallProcessor, 'shellTypeArmorSpalls0'),
 'shell1/armorDamage': partial(armorSpallProcessor, 'shellTypeArmorSpalls1'),
 'shell2/armorDamage': partial(armorSpallProcessor, 'shellTypeArmorSpalls2'),
 'shell0/deviceDamage': partial(armorSpallProcessor, 'shellTypeArmorSpalls0'),
 'shell1/deviceDamage': partial(armorSpallProcessor, 'shellTypeArmorSpalls1'),
 'shell2/deviceDamage': partial(armorSpallProcessor, 'shellTypeArmorSpalls2'),
 'shot0/speed': shotSpeedProcessor,
 'shot1/speed': shotSpeedProcessor,
 'shot2/speed': shotSpeedProcessor}

def parseValue(attrName):
    attrs = attrName.split('/')
    objName, valueName = attrs[:2]
    index = None
    try:
        if len(attrs) == 3:
            index = int(attrs[2])
    except ValueError:
        return (None, None, None)

    return (objName, valueName, index)


def checkAttrName(attrName):
    objName, valueName, index = parseValue(attrName)
    if objName is None:
        return False
    else:
        attrNameOnly = '{}/{}'.format(objName, valueName)
        if attrNameOnly not in DESCR_MODIFY_ATTRS_ALLOWED:
            return False
        modType = DESCR_MODIFY_ATTRS_TYPE[attrNameOnly]
        return index is None if modType != IS_ARRAY else True


opOrder = {'mul': 1,
 'add': 2,
 'set': 3}

def mergeDescrModifyAttrs(modifiersList, filter):
    attrs = {}
    for modifiers in modifiersList:
        for opType, attrType, attrName, value, modifierFilter in modifiers:
            if attrType != DESCR_MODIFY_ATTR_PREFIX:
                continue
            if filter and modifierFilter not in filter:
                continue
            key = (attrName, opType)
            currentValue = attrs.get(key)
            if currentValue is None:
                currentValue = attrs[key] = 1.0 if opType == MODIFIER_TYPE.MUL else 0
            attrs[key] = MERGERS[opType](currentValue, value)

    return attrs


def applyDescrModifyAttrs(vehDescr, modifiersList, filter):
    try:
        attrs = mergeDescrModifyAttrs(modifiersList, filter)
        if not attrs:
            return False
        applyMergedDescrModifyAttrs(vehDescr, attrs)
    except:
        LOG_CURRENT_EXCEPTION()

    return True


def applyMergedDescrModifyAttrs(vehDescr, attrs):
    vehDescrWrapper = VehDescrWrapper(vehDescr)
    items = [ (parseValue(attrName),
     opType,
     attrName,
     value) for (attrName, opType), value in attrs.iteritems() ]
    items.sort(key=lambda value: opOrder[value[1]])
    for (objName, valueName, index), operation, attrName, value in items:
        if objName is None:
            LOG_WARNING('Unknown attribute for descr modification', attrName)
            continue
        obj = getattr(vehDescrWrapper, objName)
        if obj is None:
            continue
        processor = customValueProcessors.get('/'.join([objName, valueName]))
        if processor:
            if processor(obj, valueName, index, operation, attrName, value, vehDescrWrapper):
                continue
        processValue(obj, valueName, index, operation, attrName, value)

    vehDescrWrapper.finalize()
    return


def getAttrValue(vehDescr, attrName):
    vehDescrWrapper = VehDescrWrapper(vehDescr)
    objName, valueName, index = parseValue(attrName)
    obj = getattr(vehDescrWrapper, objName, None)
    return None if obj is None else getattr(obj, valueName, None)
