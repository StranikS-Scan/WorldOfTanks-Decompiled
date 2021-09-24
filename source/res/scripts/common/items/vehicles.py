# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/vehicles.py
import string
import typing
from items import ItemsPrices
from items.components.supply_slot_categories import LevelsFactor
from math_common import ceilTo
from soft_exception import SoftException
from collections import namedtuple
from math import radians, cos, tan, atan, pi, isnan, degrees
from functools import partial
import struct
import itertools
import copy
import os
from typing import List, Optional, Tuple, Dict, Any, TYPE_CHECKING, Union, Generator
import BigWorld
from Math import Vector2, Vector3
import nation_change
import nations
import items
from items import _xml, makeIntCompactDescrByID, parseIntCompactDescr, ITEM_TYPES
from items.attributes_helpers import onCollectAttributes, STATIC_ATTR_PREFIX
from items.components import component_constants, shell_components, chassis_components, skills_constants
from items.components.shell_components import HighExplosiveImpactParams
from items.components import shared_components
from items.components.c11n_constants import ApplyArea, MATCHING_TAGS_SUFFIX, CamouflageTilingType, CamouflageTilingTypeNameToType
from items.components.post_progression_components import PostProgressionCache, getActiveModifications
from items.readers import chassis_readers
from items.readers import gun_readers
from items.readers import shared_readers
from items.readers import sound_readers
from items.readers import json_vehicle_reader
from items.writers import shared_writers
from items.writers import chassis_writers
from items.writers import gun_writers
from items.writers import sound_writers
from items import vehicle_items
from items._xml import cachedFloat
from constants import IS_BOT, IS_WEB, ITEM_DEFS_PATH, SHELL_TYPES, VEHICLE_SIEGE_STATE, VEHICLE_MODE
from constants import IGR_TYPE, IS_RENTALS_ENABLED, IS_CELLAPP, IS_BASEAPP, IS_CLIENT, IS_EDITOR
from constants import ACTION_LABEL_TO_TYPE, ROLE_LABEL_TO_TYPE, ROLE_TYPE, DamageAbsorptionLabelToType, ROLE_LEVELS, ROLE_TYPE_TO_LABEL
from debug_utils import LOG_WARNING, LOG_ERROR, LOG_CURRENT_EXCEPTION
from items.stun import g_cfg as stunConfig
from items import common_extras, decodeEnum
from string import upper
from constants import SHELL_MECHANICS_TYPE
from wrapped_reflection_framework import ReflectionMetaclass
from collector_vehicle import CollectorVehicleConsts
from material_kinds import IDS_BY_NAMES
if IS_EDITOR:
    import meta_objects.items.vehicles_meta as meta
    from meta_objects.items.vehicle_items_meta.utils import getEffectNameByEffect
    from combined_data_section import CombinedDataSection
    from reflection import ReflectedObject
    from wrapped_reflection_framework import reflectedNamedTuple
    import Math
    import Editor
if IS_CLIENT or IS_EDITOR:
    import ResMgr
else:
    from realm_utils import ResMgr
if IS_CELLAPP or IS_CLIENT or IS_BOT or IS_EDITOR:
    from ModelHitTester import HitTesterManager
if IS_CELLAPP or IS_CLIENT or IS_EDITOR or IS_WEB:
    import material_kinds
    from material_kinds import EFFECT_MATERIALS
if IS_CLIENT or IS_EDITOR:
    from helpers import i18n
    from helpers import EffectsList
    from CustomEffect import SelectorDescFactory, CustomEffectsDescriptor, ExhaustEffectDescriptor
    import ReloadEffect
    import Vehicular
elif IS_WEB:
    from web_stubs import *
if IS_CELLAPP:
    from vehicle_constants import OVERMATCH_MECHANICS_VER
if TYPE_CHECKING:
    from ResMgr import DataSection
    from items.artefacts import OptionalDevice, Equipment
    from items.components.supply_slots_components import SupplySlotsCache, SupplySlot
    from helpers.EntityExtra import EntityExtra
VEHICLE_CLASS_TAGS = frozenset(('lightTank',
 'mediumTank',
 'heavyTank',
 'SPG',
 'AT-SPG'))
VEHICLE_LEVEL_EARN_CRYSTAL = 10
MODES_WITHOUT_CRYSTAL_EARNINGS = set(('bob',
 'fallout',
 'event_battles',
 'battle_royale',
 'clanWarsBattles'))

class VEHICLE_PHYSICS_TYPE():
    TANK = 0
    WHEELED_TECH = 1


VEHICLE_DEVICE_TYPE_NAMES = ('engine',
 'ammoBay',
 'fuelTank',
 'radio',
 'track',
 'gun',
 'turretRotator',
 'surveyingDevice',
 'STUN_PLACEHOLDER',
 'wheel')
VEHICLE_TANKMAN_TYPE_NAMES = ('commander',
 'driver',
 'radioman',
 'gunner',
 'loader')
VEHICLE_DEVICE_INDICES = {deviceName:index for index, deviceName in enumerate(VEHICLE_DEVICE_TYPE_NAMES)}

def _makeExtraNames(tankmanNames):
    retVal = {}
    extraSuffix = 'Health'
    edgeCases = {'track': ['leftTrack' + extraSuffix, 'rightTrack' + extraSuffix],
     'radioman': ['radioman1' + extraSuffix, 'radioman2' + extraSuffix],
     'gunner': ['gunner1' + extraSuffix, 'gunner2' + extraSuffix],
     'loader': ['loader1' + extraSuffix, 'loader2' + extraSuffix]}
    for name in tankmanNames:
        retVal[name] = edgeCases.get(name, [name + extraSuffix])

    return retVal


DEVICE_TANKMAN_NAMES_TO_VEHICLE_EXTRA_NAMES = _makeExtraNames(VEHICLE_DEVICE_TYPE_NAMES + VEHICLE_TANKMAN_TYPE_NAMES)
PREMIUM_IGR_TAGS = frozenset(('premiumIGR',))
MAX_OPTIONAL_DEVICES_SLOTS = 4
NUM_SHELLS_SLOTS = 3
EQUIPMENT_TYPES_ORDER = (items.EQUIPMENT_TYPES.regular, items.EQUIPMENT_TYPES.battleBoosters)
CAMOUFLAGE_KINDS = {'winter': 0,
 'summer': 1,
 'desert': 2}
CAMOUFLAGE_KIND_INDICES = dict(((v, k) for k, v in CAMOUFLAGE_KINDS.iteritems()))
NATIONAL_EMBLEMS = set()
VEHICLE_MODE_FILE_SUFFIX = {VEHICLE_MODE.DEFAULT: '',
 VEHICLE_MODE.SIEGE: '_siege_mode'}
NUM_INSCRIPTION_COLORS = 16
_ITEM_STATUS = vehicle_items.VEHICLE_ITEM_STATUS
g_list = None
g_cache = None
_VEHICLE_TYPE_XML_PATH = ITEM_DEFS_PATH + 'vehicles/'
_DEFAULT_HEALTH_BURN_PER_SEC_LOSS_FRACTION = 0.0875
_CUSTOMIZATION_EPOCH = 1306886400
_CUSTOMIZATION_XML_PATH = ITEM_DEFS_PATH + 'customization/'
_readTags = shared_readers.readAllowedTags
EmblemSlot = namedtuple('EmblemSlot', ['rayStart',
 'rayEnd',
 'rayUp',
 'size',
 'hideIfDamaged',
 'type',
 'isMirrored',
 'isUVProportional',
 'emblemId'])
VEHICLE_MISC_ATTRIBUTE_FACTOR_NAMES = ('fuelTankHealthFactor',
 'repairSpeedFactor',
 'additiveShotDispersionFactor',
 'antifragmentationLiningFactor',
 'circularVisionRadiusFactor',
 'gunReloadTimeFactor',
 'gunAimingTimeFactor',
 'ammoBayHealthFactor',
 'engineHealthFactor',
 'chassisHealthFactor',
 'vehicleByChassisDamageFactor',
 'fuelTankHealthFactor',
 'crewLevelIncrease',
 'crewChanceToHitFactor',
 'stunResistanceEffect',
 'stunResistanceDuration',
 'repeatedStunDurationFactor',
 'healthFactor',
 'damageFactor',
 'enginePowerFactor',
 'radioHealthFactor',
 'turretRotatorHealthFactor',
 'surveyingDeviceHealthFactor',
 'gunHealthFactor',
 'increaseEnemySpottingTime',
 'decreaseOwnSpottingTime',
 'demaskFoliageFactor',
 'demaskMovingFactor',
 'chassisRepairSpeedFactor',
 'turretRotationSpeed',
 'invisibilityAdditiveTerm',
 'forwardMaxSpeedKMHTerm',
 'backwardMaxSpeedKMHTerm',
 'onStillRotationSpeedFactor',
 'onMoveRotationSpeedFactor',
 'fireStartingChanceFactor',
 'multShotDispersionFactor',
 'chassisHealthAfterHysteresisFactor',
 'centerRotationFwdSpeedFactor',
 'receivedDamageFactor',
 'proofHealth')
VEHICLE_MISC_ATTRIBUTE_FACTOR_INDICES = dict(((value, index) for index, value in enumerate(VEHICLE_MISC_ATTRIBUTE_FACTOR_NAMES)))

class EnhancementItem(object):
    __slots__ = ('name', 'value', 'op')
    _operations = {'mul': lambda x, y: x * y,
     'sum': lambda x, y: x + y}
    _OPERATION_NAMES = _operations.keys()
    _OPERATION_IDS_TO_NAMES = {i:name for i, name in enumerate(_OPERATION_NAMES)}
    _OPERATION_NAMES_TO_IDS = {name:i for i, name in enumerate(_OPERATION_NAMES)}

    def __init__(self, name, value, op):
        self.name = name
        self.value = value
        self.op = op

    def getOpIndex(self):
        return self._OPERATION_NAMES_TO_IDS[self.op]

    @classmethod
    def getOpName(cls, opIdx):
        return cls._OPERATION_IDS_TO_NAMES[opIdx]

    def applyFactor(self, factor):
        func = self._operations[self.op]
        return func(factor, self.value)


def vehicleAttributeFactors():
    return {'engine/power': 1.0,
     'turret/rotationSpeed': 1.0,
     'circularVisionRadius': 1.0,
     'invisibility': [0.0, 1.0],
     'radio/distance': 1.0,
     'gun/rotationSpeed': 1.0,
     'chassis/shotDispersionFactors/movement': 1.0,
     'chassis/shotDispersionFactors/rotation': 1.0,
     'gun/shotDispersionFactors/turretRotation': 1.0,
     'gun/reloadTime': 1.0,
     'gun/aimingTime': 1.0,
     'gun/piercing': 1.0,
     'gun/canShoot': True,
     'engine/fireStartingChance': 1.0,
     'healthBurnPerSecLossFraction': 1.0,
     'repairSpeed': 1.0,
     'additiveShotDispersionFactor': 1.0,
     'brokenTrack': 0,
     'vehicle/rotationSpeed': 1.0,
     'vehicle/maxSpeed': 1.0,
     'chassis/terrainResistance': [1.0, 1.0, 1.0],
     'ramming': 1.0,
     'crewLevelIncrease': 0.0,
     'crewChanceToHitFactor': 1.0,
     'crewRolesFactor': 1.0,
     'stunResistanceEffect': 0.0,
     'stunResistanceDuration': 0.0,
     'repeatedStunDurationFactor': 1.0,
     'healthFactor': 1.0,
     'damageFactor': 1.0,
     'receivedDamageFactor': 1.0,
     'enginePowerFactor': 1.0,
     'deathZones/sensitivityFactor': 1.0,
     'multShotDispersionFactor': 1.0,
     'gun/changeShell/reloadFactor': 1.0,
     'demaskMovingFactor': 1.0,
     'demaskFoliageFactor': 1.0,
     'invisibilityAdditiveTerm': 0.0,
     'engineReduceFineFactor': 1.0,
     'ammoBayReduceFineFactor': 1.0,
     'proofHealth': 0}


WHEEL_SIZE_COEF = 2.2
_g_prices = None

class CamouflageBonus():
    MIN = 1.0
    MAX = 0.0


def init(preloadEverything, pricesToCollect):
    global g_cache
    global _g_prices
    global g_list
    if IS_CLIENT or IS_CELLAPP or IS_BOT:
        import vehicle_extras
    _g_prices = pricesToCollect
    g_list = VehicleList()
    g_cache = Cache()
    if preloadEverything:
        g_cache.optionalDevices()
        g_cache.equipments()
        g_cache.playerEmblems()
        for nationID in xrange(len(nations.NAMES)):
            g_cache.customization(nationID)
            for vehicleTypeID in g_list.getList(nationID).iterkeys():
                g_cache.vehicle(nationID, vehicleTypeID)

        g_cache.customization20()
        g_cache.supplySlots()
        g_cache.postProgression()
        _g_prices = None
    return


def reload(full=True):
    import vehicle_extras
    vehicle_extras.reload()
    from sys import modules
    import __builtin__
    __builtin__.reload(modules[reload.__module__])
    init(full, None)
    return


class VehicleDescriptor(object):
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('enhancements', 'turret', 'gun', 'hull', 'engine', 'fuelTank', 'radio', 'chassis', 'turrets', 'optionalDevices', 'shot', 'supplySlots', 'camouflages', 'playerEmblems', 'playerInscriptions', 'type', 'name', 'level', 'extras', 'extrasDict', 'miscAttrs', 'physics', 'visibilityCheckPoints', 'observerPosOnChassis', 'observerPosOnTurret', '_customRoleSlotTypeId', '_modifications', '_optDevSlotsMap', '_maxHealth', '__activeTurretPos', '__activeGunShotIdx', '__activeGunShotPosition', '__boundingRadius')

    def __init__(self, compactDescr=None, typeID=None, typeName=None, vehMode=VEHICLE_MODE.DEFAULT, xmlPath=None, extData=None):
        self.enhancements = []
        vehType = None
        if compactDescr is None:
            vehicleItem = None
            if typeID is not None:
                nationID, vehicleTypeID = typeID
            elif typeName is not None:
                nationID, vehicleTypeID = g_list.getIDsByName(typeName)
            elif xmlPath is not None:
                nation, vehicleType = _deduceNamesFromTankXmlPath(xmlPath)
                typeName = nation + ':' + vehicleType
                try:
                    nationID, vehicleTypeID = g_list.getIDsByName(typeName)
                    vehicleItem = g_list.getList(nationID)[vehicleTypeID]
                except Exception as e:
                    nationID = nations.INDICES[nation]
                    vehicleTypeID = 255

            if xmlPath is None:
                type = g_cache.vehicle(nationID, vehicleTypeID)
            else:
                if vehicleItem is None:
                    vehicleItem = vehicle_items.VehicleItem(ITEM_TYPES['vehicle'], vehicleTypeID, typeName, makeIntCompactDescrByID('vehicle', nationID, vehicleTypeID))
                if vehMode != VEHICLE_MODE.DEFAULT:
                    xmlName, xmlExt = os.path.splitext(xmlPath)
                    xmlPath = xmlName + VEHICLE_MODE_FILE_SUFFIX[vehMode] + xmlExt
                type = VehicleType(nationID, vehicleItem, xmlPath, vehMode)
                vehType = type
            if IS_EDITOR:
                ReflectedObject(type).edVisible = True if vehMode is VEHICLE_MODE.DEFAULT else False
            turretDescr = type.turrets[0][0]
            header = items.ITEM_TYPES.vehicle + (nationID << 4)
            compactDescr = struct.pack('<2B6HB', header, vehicleTypeID, type.chassis[0].id[1], type.engines[0].id[1], type.fuelTanks[0].id[1], type.radios[0].id[1], turretDescr.id[1], turretDescr.guns[0].id[1], 0)
        self.__initFromCompactDescr(compactDescr, vehMode, vehType)
        self.__applyExternalData(extData or {})
        self.__updateAttributes()
        return

    @property
    def maxHealth(self):
        if IS_BASEAPP:
            self.__updateAttributes(onAnyApp=True)
        return self._maxHealth

    def getShot(self, shotIdx=None):
        return self.shot if shotIdx is None else self.gun.shots[shotIdx]

    def __set_activeTurretPos(self, turretPosition):
        self.turret, self.gun = self.turrets[turretPosition]
        self.__activeTurretPos = turretPosition
        self.activeGunShotPosition = self.turret.gunPosition + self.gun.shotOffset
        self.activeGunShotIndex = 0

    activeTurretPosition = property(lambda self: self.__activeTurretPos, __set_activeTurretPos)

    def __set_activeGunShotIndex(self, shotIndex):
        self.shot = self.gun.shots[shotIndex]
        self.__activeGunShotIdx = shotIndex

    activeGunShotIndex = property(lambda self: self.__activeGunShotIdx, __set_activeGunShotIndex)

    def __set_activeGunShotPosition(self, gunShotPos):
        self.__activeGunShotPosition = gunShotPos

    activeGunShotPosition = property(lambda self: self.__activeGunShotPosition, __set_activeGunShotPosition)
    modifications = property(lambda self: self._modifications)
    customRoleSlotTypeId = property(lambda self: self._customRoleSlotTypeId)
    hasSiegeMode = property(lambda self: self.type.hasSiegeMode)
    hasAutoSiegeMode = property(lambda self: self.type.hasAutoSiegeMode)
    isWheeledVehicle = property(lambda self: self.type.isWheeledVehicle)
    isDualgunVehicle = property(lambda self: 'dualGun' in self.gun.tags)
    hasTurboshaftEngine = property(lambda self: self.type.hasTurboshaftEngine)
    hasHydraulicChassis = property(lambda self: self.type.hasHydraulicChassis)
    hasBurnout = property(lambda self: self.type.hasBurnout)
    hasCharge = property(lambda self: self.type.hasCharge)
    role = property(lambda self: self.type.role)
    isPitchHullAimingAvailable = property(lambda self: self.type.hullAimingParams['pitch']['isAvailable'])
    isYawHullAimingAvailable = property(lambda self: self.type.hullAimingParams['yaw']['isAvailable'])

    def __getIsHullAimingAvailable(self):
        hap = self.type.hullAimingParams
        return hap['yaw']['isAvailable'] or hap['pitch']['isAvailable']

    isHullAimingAvailable = property(__getIsHullAimingAvailable)

    def onSiegeStateChanged(self, siegeMode):
        pass

    def __get_boundingRadius(self):
        radius = getattr(self, '_VehicleDescriptor__boundingRadius', None)
        if radius is None:
            chassisDescr = self.chassis
            hullDescr = self.hull
            hullOnChassisOffsetZ = chassisDescr.hullPosition.z
            turretOnHullOffsetZ = hullDescr.turretPositions[0].z
            gunOnTurretOffsetZ = self.turret.gunPosition.z
            chassisBbox = chassisDescr.hitTester.bbox
            hullBbox = hullDescr.hitTester.bbox
            bboxMin = Vector2(min(chassisBbox[0].x, hullBbox[0].x), min(chassisBbox[0].z, hullBbox[0].z + hullOnChassisOffsetZ))
            bboxMax = Vector2(max(chassisBbox[1].x, hullBbox[1].x), max(chassisBbox[1].z, hullBbox[1].z + hullOnChassisOffsetZ))
            gunOnTurretMaxZ = gunOnTurretOffsetZ + self.gun.hitTester.bbox[1].z
            radius = max(bboxMin.length, bboxMax.length, abs(hullOnChassisOffsetZ + turretOnHullOffsetZ + gunOnTurretMaxZ), abs(hullOnChassisOffsetZ + turretOnHullOffsetZ - gunOnTurretMaxZ))
            self.__boundingRadius = radius
        return radius

    boundingRadius = property(__get_boundingRadius)

    def __applyExternalData(self, extData):

        def getValue(key, defaultValue):
            if isinstance(extData, dict):
                return extData.get(key, defaultValue)
            else:
                return getattr(extData, key, defaultValue)

        self._customRoleSlotTypeId = 0
        self._modifications = []
        self.installCustomRoleSlot(getValue('customRoleSlotTypeId', 0), False)
        modificationIDs = getActiveModifications(getValue('vehPostProgression', []), g_cache.postProgression())
        self.installModifications(modificationIDs, False)

    def installCustomRoleSlot(self, customRoleSlotTypeId, rebuildAttrs=True):
        self._customRoleSlotTypeId = customRoleSlotTypeId
        self._updateSupplySlots()
        self._rebuildOptDevSlotsMap()
        if rebuildAttrs:
            self.__updateAttributes()

    def installModifications(self, modificationIDs, rebuildAttrs=True):
        self._modifications = modificationIDs
        if rebuildAttrs:
            self.__updateAttributes()

    def setCamouflage(self, position, camouflageID, startTime, durationDays):
        p = self.camouflages
        if camouflageID is None:
            startTime = _CUSTOMIZATION_EPOCH
            durationDays = 0
            p[position]
        else:
            descr = g_cache.customization(self.type.customizationNationID)['camouflages'][camouflageID]
            if position is None:
                position = descr['kind']
            elif position != descr['kind']:
                raise SoftException('wrong camouflage kind = %d' % position)
            cd = self.type.compactDescr
            if cd in descr['deny'] or descr['allow'] and cd not in descr['allow']:
                raise SoftException('camouflage = %d is incompatible with vehicle' % cd)
            startTime = int(startTime / 60) * 60
            if startTime < _CUSTOMIZATION_EPOCH:
                raise SoftException('wrong camouflage start time = %d' % startTime)
            durationDays = int(durationDays)
            if not 0 <= durationDays <= 255:
                raise SoftException('wrong camouflage duration = %d' % durationDays)
        self.camouflages = p[:position] + ((camouflageID, startTime, durationDays),) + p[position + 1:]
        return

    def setPlayerEmblem(self, position, emblemID, startTime, durationDays):
        p = self.playerEmblems
        p[position]
        defEmblemID = self.type.defaultPlayerEmblemID
        if emblemID is None or emblemID == defEmblemID:
            emblemID = defEmblemID
            startTime = _CUSTOMIZATION_EPOCH
            durationDays = 0
        else:
            groups, emblems, names = g_cache.playerEmblems()
            emblem = emblems[emblemID]
            groupName = emblem[0]
            group = groups[groupName]
            nations = group[3]
            if nations is not None and self.type.customizationNationID not in nations:
                raise SoftException('emblem nation mismatch')
            allow, deny = group[4:6]
            cd = self.type.compactDescr
            if cd in deny:
                raise SoftException('emblem is incompatible with vehicle')
            if allow and cd not in allow:
                raise SoftException('emblem is incompatible with vehicle')
            startTime = int(startTime / 60) * 60
            if startTime < _CUSTOMIZATION_EPOCH:
                raise SoftException('wrong emblem start time')
            durationDays = int(durationDays)
            if not 0 <= durationDays <= 255:
                raise SoftException('wrong emblem duration')
        self.playerEmblems = p[:position] + ((emblemID, startTime, durationDays),) + p[position + 1:]
        return

    def setPlayerInscription(self, position, inscriptionID, startTime, durationDays, color):
        if IS_CLIENT:
            LOG_WARNING('This method cannot be executed on client')
            return
        else:
            p = self.playerInscriptions
            p[position]
            if inscriptionID is None:
                startTime = _CUSTOMIZATION_EPOCH
                durationDays = 0
                color = 0
            else:
                customization = g_cache.customization(self.type.customizationNationID)
                groupName = customization['inscriptions'][inscriptionID][0]
                customization['inscriptionColors'][color]
                allow, deny = customization['inscriptionGroups'][groupName][3:5]
                cd = self.type.compactDescr
                if cd in deny:
                    raise SoftException('inscription is incompatible with vehicle')
                if allow and cd not in allow:
                    raise SoftException('inscription is incompatible with vehicle')
                startTime = int(startTime / 60) * 60
                if startTime < _CUSTOMIZATION_EPOCH:
                    raise SoftException('wrong inscription start time')
                durationDays = int(durationDays)
                if not 0 <= durationDays <= 255:
                    raise SoftException('wrong inscription duration')
            self.playerInscriptions = p[:position] + ((inscriptionID,
              startTime,
              durationDays,
              color),) + p[position + 1:]
            return

    def getComponentsByType(self, itemTypeName, positionIndex=0):
        if itemTypeName == 'vehicleChassis':
            return (self.chassis, self.type.chassis)
        if itemTypeName == 'vehicleEngine':
            return (self.engine, self.type.engines)
        if itemTypeName == 'vehicleRadio':
            return (self.radio, self.type.radios)
        if itemTypeName == 'vehicleFuelTank':
            return (self.fuelTank, self.type.fuelTanks)
        if itemTypeName == 'vehicleTurret':
            return (self.turrets[positionIndex][0], self.type.turrets[positionIndex])
        if itemTypeName == 'vehicleGun':
            turretDescr, gunDescr = self.turrets[positionIndex]
            return (gunDescr, turretDescr.guns)

    def mayInstallTurret(self, turretCompactDescr, gunCompactDescr, positionIndex=0):
        selfType = self.type
        selfTurrets = self.turrets
        itemTypeID, nationID, turretID = parseIntCompactDescr(turretCompactDescr)
        if items.ITEM_TYPE_NAMES[itemTypeID] != 'vehicleTurret':
            return (False, 'wrong item type')
        elif nationID != selfType.id[0]:
            return (False, 'wrong nation')
        else:
            if gunCompactDescr == 0:
                gunID = selfTurrets[positionIndex][1].id[1]
            else:
                itemTypeID, nationID, gunID = parseIntCompactDescr(gunCompactDescr)
                if items.ITEM_TYPE_NAMES[itemTypeID] != 'vehicleGun':
                    return (False, 'wrong item type')
                if nationID != selfType.id[0]:
                    return (False, 'wrong nation')
            newTurretDescr = _findDescrByID(selfType.turrets[positionIndex], turretID)
            if newTurretDescr is None:
                return (False, 'not for this vehicle type')
            newGunDescr = _findDescrByID(newTurretDescr.guns, gunID)
            if newGunDescr is None:
                if gunCompactDescr not in selfType.installableComponents:
                    return (False, 'not for this vehicle type')
                return (False, 'not for current vehicle')
            setter = partial(selfTurrets.__setitem__, positionIndex, (newTurretDescr, newGunDescr))
            restorer = partial(selfTurrets.__setitem__, positionIndex, selfTurrets[positionIndex])
            if len(selfType.hulls) > 1:
                turrets = list(selfTurrets)
                turrets[positionIndex] = (newTurretDescr, newGunDescr)
                hullDescr = self.__selectBestHull(turrets, self.chassis)
                if hullDescr is not self.hull:
                    setter = partial(self.__setHullAndCall, hullDescr, setter)
                    restorer = partial(self.__setHullAndCall, self.hull, restorer)
            try:
                prevWeight = self.__computeWeight()
                setter()
                for device in self.optionalDevices:
                    if device is not None and not device.checkCompatibilityWithVehicle(self):
                        return (False, 'not for current vehicle')

                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                    return (False, 'too heavy')
            finally:
                restorer()

            return (True, None)

    def installTurret(self, turretCompactDescr, gunCompactDescr, positionIndex=0):
        turretID = parseIntCompactDescr(turretCompactDescr)[2]
        if gunCompactDescr == 0:
            gunID = self.turrets[positionIndex][1].id[1]
        else:
            gunID = parseIntCompactDescr(gunCompactDescr)[2]
        prevTurretDescr, prevGunDescr = self.turrets[positionIndex]
        newTurretDescr = _descrByID(self.type.turrets[positionIndex], turretID)
        newGunDescr = _descrByID(newTurretDescr.guns, gunID)
        self.turrets[positionIndex] = (newTurretDescr, newGunDescr)
        if len(self.type.hulls) > 1:
            self.hull = self.__selectBestHull(self.turrets, self.chassis)
        self.__updateAttributes()
        if self.__activeTurretPos == positionIndex:
            self.activeTurretPosition = positionIndex
        removed = [prevTurretDescr.compactDescr]
        if gunCompactDescr != 0:
            removed.append(prevGunDescr.compactDescr)
        return removed

    def installEnhancements(self, enhancements, rebuildAttrs=True):
        for modsInSlot in enhancements.itervalues():
            for mod in modsInSlot.itervalues():
                for attr in mod['attributes']:
                    self.enhancements.append(EnhancementItem(attr['name'], attr['value'], attr['operation']))

        if rebuildAttrs:
            self.__updateAttributes()

    def mayInstallComponent(self, compactDescr, positionIndex=0):
        itemTypeID, nationID, compID = parseIntCompactDescr(compactDescr)
        itemTypeName = items.ITEM_TYPE_NAMES[itemTypeID]
        selfType = self.type
        if nationID != selfType.id[0]:
            return (False, 'wrong nation')
        else:
            if itemTypeName == 'vehicleGun':
                hullDescr = self.hull
                turretDescr = self.turrets[positionIndex][0]
                newDescr = _findDescrByID(turretDescr.guns, compID)
                if newDescr is None and positionIndex in hullDescr.fakeTurrets['lobby']:
                    newDescr, turretDescr, hullDescr = self.__selectTurretForGun(compID, positionIndex)
                setter = partial(self.turrets.__setitem__, positionIndex, (turretDescr, newDescr))
                restorer = partial(self.turrets.__setitem__, positionIndex, self.turrets[positionIndex])
                if hullDescr is not self.hull:
                    setter = partial(self.__setHullAndCall, hullDescr, setter)
                    restorer = partial(self.__setHullAndCall, self.hull, restorer)
            elif itemTypeName == 'vehicleChassis':
                newDescr = _findDescrByID(selfType.chassis, compID)
                setter = partial(setattr, self, 'chassis', newDescr)
                restorer = partial(setattr, self, 'chassis', self.chassis)
                if len(selfType.hulls) > 1:
                    hullDescr = self.__selectBestHull(self.turrets, newDescr)
                    if hullDescr is not self.hull:
                        setter = partial(self.__setHullAndCall, hullDescr, setter)
                        restorer = partial(self.__setHullAndCall, self.hull, restorer)
            elif itemTypeName == 'vehicleEngine':
                newDescr = _findDescrByID(selfType.engines, compID)
                setter = partial(setattr, self, 'engine', newDescr)
                restorer = partial(setattr, self, 'engine', self.engine)
            elif itemTypeName == 'vehicleRadio':
                newDescr = _findDescrByID(selfType.radios, compID)
                setter = partial(setattr, self, 'radio', newDescr)
                restorer = partial(setattr, self, 'radio', self.radio)
            elif itemTypeName == 'vehicleFuelTank':
                newDescr = _findDescrByID(selfType.fuelTanks, compID)
                setter = partial(setattr, self, 'fuelTank', newDescr)
                restorer = partial(setattr, self, 'fuelTank', self.fuelTank)
            else:
                return (False, 'wrong item type')
            if newDescr is None:
                if compactDescr not in selfType.installableComponents:
                    return (False, 'not for this vehicle type')
                return (False, 'not for current vehicle')
            try:
                prevWeight = self.__computeWeight()
                setter()
                for device in self.optionalDevices:
                    if device is not None and not device.checkCompatibilityWithVehicle(self):
                        return (False, 'not for current vehicle')

                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                    return (False, 'too heavy')
            finally:
                restorer()

            return (True, None)

    def rebuildAttrs(self):
        return self.__updateAttributes()

    def installComponent(self, compactDescr, positionIndex=0):
        itemTypeID, nationID, compID = parseIntCompactDescr(compactDescr)
        itemTypeName = items.ITEM_TYPE_NAMES[itemTypeID]
        if nationID != self.type.id[0]:
            raise SoftException('incompatible nation of component')
        if itemTypeName == 'vehicleGun':
            return self.__installGun(compID, positionIndex)
        if itemTypeName == 'vehicleChassis':
            attrName = 'chassis'
            compList = self.type.chassis
        elif itemTypeName == 'vehicleEngine':
            attrName = 'engine'
            compList = self.type.engines
        elif itemTypeName == 'vehicleRadio':
            attrName = 'radio'
            compList = self.type.radios
        elif itemTypeName == 'vehicleFuelTank':
            attrName = 'fuelTank'
            compList = self.type.fuelTanks
        prevDescr = getattr(self, attrName)
        newDescr = _descrByID(compList, compID)
        setattr(self, attrName, newDescr)
        if attrName == 'chassis' and len(self.type.hulls) > 1:
            self.hull = self.__selectBestHull(self.turrets, self.chassis)
        self.__updateAttributes()
        return (prevDescr.compactDescr,)

    def mayInstallOptionalDevice(self, compactDescr, slotIdx):
        itemTypeID, _, deviceID = parseIntCompactDescr(compactDescr)
        if items.ITEM_TYPE_NAMES[itemTypeID] != 'optionalDevice':
            return (False, 'wrong item type')
        else:
            device = g_cache.optionalDevices()[deviceID]
            prevDevices = self.optionalDevices
            prevOptDevSlotMap = self._optDevSlotsMap
            if device in prevDevices:
                return (False, 'already installed')
            if slotIdx >= self.supplySlots.getAmountForType(ITEM_TYPES.optionalDevice):
                return (False, 'Wrong slotIDx ({})'.format(slotIdx))
            for idx, installedDevice in enumerate(self.optionalDevices):
                if idx != slotIdx and installedDevice and not device.checkCompatibilityWithOther(installedDevice):
                    return (False, 'similar device already installed')

            devices = list(prevDevices)
            self.optionalDevices = devices
            try:
                prevWeight = self.__computeWeight()
                devices[slotIdx] = None
                res = device.checkCompatibilityWithVehicle(self)
                if not res[0]:
                    return res
                devices[slotIdx] = device
                self._rebuildOptDevSlotsMap()
                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                    return (False, 'too heavy')
            finally:
                self.optionalDevices = prevDevices
                self._optDevSlotsMap = prevOptDevSlotMap

            return (True, None)

    def mayInstallOptDevsSequence(self, optDevSequence):
        result, errorStr = self.supplySlots.checkLayoutCompatibility(ITEM_TYPES.optionalDevice, optDevSequence)
        if not result:
            return (False, errorStr)
        else:
            prevDevices = self.optionalDevices
            prevOptDevSlotMap = self._optDevSlotsMap
            optDevs = [ (getItemByCompactDescr(cd) if cd != 0 else None) for cd in optDevSequence ]
            prevWeights = self.__computeWeight()
            try:
                optDevsLen = len(optDevs)
                for i in range(0, optDevsLen):
                    device = optDevs[i]
                    if device is None:
                        continue
                    result, errorStr = device.checkCompatibilityWithVehicle(self)
                    if not result:
                        return (False, errorStr)
                    for j in range(i + 1, optDevsLen):
                        otherDevice = optDevs[j]
                        if otherDevice is not None and not device.checkCompatibilityWithOther(otherDevice):
                            return (False, 'Similar devices in sequence')

                self.optionalDevices = optDevs
                self._rebuildOptDevSlotsMap()
                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeights):
                    return (False, 'Devices are too heavy for vehicle')
            finally:
                self.optionalDevices = prevDevices
                self._optDevSlotsMap = prevOptDevSlotMap

            return (True, None)

    def installOptDevsSequence(self, optDevSequence):
        optDevs = [ (getItemByCompactDescr(cd) if cd != 0 else None) for cd in optDevSequence ]
        self.optionalDevices = optDevs
        self._rebuildOptDevSlotsMap()
        self.__updateAttributes()
        return

    def installOptionalDevice(self, compactDescr, slotIdx, rebuildAttrs=True):
        device = g_cache.optionalDevices()[parseIntCompactDescr(compactDescr)[2]]
        devices = self.optionalDevices
        prevDevice = devices[slotIdx]
        devices[slotIdx] = device
        self._optDevSlotsMap[compactDescr] = self.supplySlots.getSlotByIdxInItemType(ITEM_TYPES.optionalDevice, slotIdx)
        if rebuildAttrs:
            self.__updateAttributes()
        if prevDevice is None:
            return (component_constants.EMPTY_TUPLE, component_constants.EMPTY_TUPLE)
        else:
            return ((prevDevice.compactDescr,), component_constants.EMPTY_TUPLE) if prevDevice.removable else (component_constants.EMPTY_TUPLE, (prevDevice.compactDescr,))

    def mayRemoveOptionalDevice(self, slotIdx):
        prevDevices = self.optionalDevices
        devices = list(prevDevices)
        self.optionalDevices = devices
        try:
            prevWeight = self.__computeWeight()
            devices[slotIdx] = None
            if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                return (False, 'too heavy')
        finally:
            self.optionalDevices = prevDevices

        return (True, None)

    def removeOptionalDevice(self, slotIdx, rebuildAttrs=True):
        device = self.optionalDevices[slotIdx]
        if device is None:
            return (component_constants.EMPTY_TUPLE, component_constants.EMPTY_TUPLE)
        else:
            self.optionalDevices[slotIdx] = None
            self._optDevSlotsMap.pop(device.compactDescr)
            if rebuildAttrs:
                self.__updateAttributes()
            return ((device.compactDescr,), component_constants.EMPTY_TUPLE) if device.removable else (component_constants.EMPTY_TUPLE, (device.compactDescr,))

    def maySwapOptionalDevice(self, leftID, rightID):
        if leftID >= self.supplySlots.getAmountForType(ITEM_TYPES.optionalDevice):
            return (False, 'Wrong slotIDx ({})'.format(leftID))
        elif rightID >= self.supplySlots.getAmountForType(ITEM_TYPES.optionalDevice):
            return (False, 'Wrong slotIDx ({})'.format(leftID))
        else:
            prevDevices = self.optionalDevices
            devices = list(prevDevices)
            self.optionalDevices = devices
            try:
                prevWeight = self.__computeWeight()
                devices[leftID], devices[rightID] = devices[rightID], devices[leftID]
                if not _isWeightAllowedToChange(self.__computeWeight(), prevWeight):
                    return (False, 'too heavy')
            finally:
                self.optionalDevices = prevDevices

            return (True, None)

    def swapOptionalDevice(self, leftID, rightID):
        devices = self.optionalDevices
        leftDevice, rightDevice = devices[leftID], devices[rightID]
        devices[leftID], devices[rightID] = rightDevice, leftDevice
        if leftDevice:
            self._optDevSlotsMap[leftDevice.compactDescr] = self.supplySlots.getSlotByIdxInItemType(ITEM_TYPES.optionalDevice, rightID)
        if rightDevice:
            self._optDevSlotsMap[rightDevice.compactDescr] = self.supplySlots.getSlotByIdxInItemType(ITEM_TYPES.optionalDevice, leftID)
        self.__updateAttributes()

    def iterOptDevsWithSlots(self):
        optDevSlotIDs = self.supplySlots.getSlotIDsByType(ITEM_TYPES.optionalDevice)
        for optDev, slotID in itertools.izip(self.optionalDevices, optDevSlotIDs):
            slot = g_cache.supplySlots().getSlotDescr(slotID)
            yield (optDev, slot)

    def _rebuildOptDevSlotsMap(self):
        self._optDevSlotsMap = {}
        for optDev, slot in self.iterOptDevsWithSlots():
            if optDev is not None:
                self._optDevSlotsMap[optDev.compactDescr] = slot

        return

    def getOptDevSupplySlot(self, optDevCompDescr):
        return self._optDevSlotsMap.get(optDevCompDescr, None)

    def _updateSupplySlots(self):
        supplySlotIDs = list(self.type.supplySlots.slotIDs)
        if self._customRoleSlotTypeId:
            for slotIdx, slotID in enumerate(supplySlotIDs):
                slotDescr = g_cache.supplySlots().getSlotDescr(slotID)
                if slotDescr.itemType == ITEM_TYPES.optionalDevice and not slotDescr.categories:
                    supplySlotIDs[slotIdx] = self._customRoleSlotTypeId
                    break

        self.supplySlots = g_cache.supplySlotsStorage().getStorage(supplySlotIDs)

    def makeCompactDescr(self):
        type = self.type
        pack = struct.pack
        components = pack('<4H', self.chassis.id[1], self.engine.id[1], self.fuelTank.id[1], self.radio.id[1])
        for n in xrange(len(type.turrets)):
            turretDescr, gunDescr = self.turrets[n]
            components += pack('<2H', turretDescr.id[1], gunDescr.id[1])

        optDevSlots = self.supplySlots.getAmountForType(ITEM_TYPES.optionalDevice)
        if len(self.optionalDevices) != optDevSlots:
            raise SoftException('Optional devices num ({}) is incorrect. Should be equal to {}'.format(len(self.optionalDevices), optDevSlots))
        optionalDevices = ''
        optionalDeviceSlots = 0
        for device in self.optionalDevices:
            optionalDeviceSlots <<= 1
            if device is not None:
                optionalDevices = pack('<H', device.id[1]) + optionalDevices
                optionalDeviceSlots |= 1

        enhancements = ''
        if self.enhancements:
            enhancements = pack('<B', len(self.enhancements))
            for enhancement in self.enhancements:
                enhancements += pack('<BfB', VEHICLE_MISC_ATTRIBUTE_FACTOR_INDICES[enhancement.name], enhancement.value * 1000, enhancement.getOpIndex())

        emblemPositions = 0
        emblems = ''
        for idx, item in enumerate(self.playerEmblems):
            if item[0] is not None and item[0] != type.defaultPlayerEmblemID:
                emblemPositions |= 1 << idx
                emblems += _packIDAndDuration(*item)

        inscriptions = ''
        for idx, item in enumerate(self.playerInscriptions):
            if item[0] is not None:
                emblemPositions |= 1 << idx + 4
                inscriptions += _packIDAndDuration(item[0], item[1], item[2]) + chr(item[3])

        camouflages = ''
        for item in self.camouflages:
            if item[0] is not None:
                camouflages += _packIDAndDuration(*item)

        return _combineVehicleCompactDescr(type, components, optionalDeviceSlots, optionalDevices, enhancements, emblemPositions, emblems, inscriptions, camouflages)

    def getCost(self, itemPrices):
        type = self.type
        cost = itemPrices[type.compactDescr]
        for idx in xrange(len(self.turrets)):
            currentTurret, currentGun = self.turrets[idx]
            defaultTurret = type.turrets[idx][0]
            cost = _summPriceDiff(cost, itemPrices[currentTurret.compactDescr], itemPrices[defaultTurret.compactDescr])
            cost = _summPriceDiff(cost, itemPrices[currentGun.compactDescr], itemPrices[defaultTurret.guns[0].compactDescr])

        cost = _summPriceDiff(cost, itemPrices[self.chassis.compactDescr], itemPrices[type.chassis[0].compactDescr])
        cost = _summPriceDiff(cost, itemPrices[self.engine.compactDescr], itemPrices[type.engines[0].compactDescr])
        cost = _summPriceDiff(cost, itemPrices[self.fuelTank.compactDescr], itemPrices[type.fuelTanks[0].compactDescr])
        cost = _summPriceDiff(cost, itemPrices[self.radio.compactDescr], itemPrices[type.radios[0].compactDescr])
        for device in self.optionalDevices:
            if device is not None:
                cost = _summPriceDiff(cost, itemPrices[device.compactDescr], (0, 0))

        return cost

    def getMaxRepairCost(self):
        type = self.type
        cost = self.maxHealth * type.repairCost
        for turretDescr, gunDescr in self.turrets:
            cost += gunDescr.maxRepairCost + turretDescr.turretRotatorHealth.maxRepairCost + turretDescr.surveyingDeviceHealth.maxRepairCost

        cost += self.hull.ammoBayHealth.maxRepairCost + self.chassis.maxRepairCost * 2 + self.engine.maxRepairCost + self.fuelTank.maxRepairCost + self.radio.maxRepairCost
        return cost

    def getDevices(self):
        defComps = []
        instComps = []
        type = self.type
        instComps.append(self.chassis.compactDescr)
        defComps.append(type.chassis[0].compactDescr)
        instComps.append(self.engine.compactDescr)
        defComps.append(type.engines[0].compactDescr)
        instComps.append(self.fuelTank.compactDescr)
        defComps.append(type.fuelTanks[0].compactDescr)
        instComps.append(self.radio.compactDescr)
        defComps.append(type.radios[0].compactDescr)
        for (turretDescr, gunDescr), turrets in zip(self.turrets, type.turrets):
            instComps.append(turretDescr.compactDescr)
            defComps.append(turrets[0].compactDescr)
            instComps.append(gunDescr.compactDescr)
            defComps.append(turrets[0].guns[0].compactDescr)

        optDevices = []
        for device in self.optionalDevices:
            if device is not None:
                optDevices.append(device.compactDescr)

        return (defComps, instComps, optDevices)

    def getHitTesterManagers(self):
        hitTesters = [self.chassis.hitTesterManager, self.hull.hitTesterManager]
        for turretDescr, gunDescr in self.turrets:
            hitTesters.append(turretDescr.hitTesterManager)
            hitTesters.append(gunDescr.hitTesterManager)

        if self.isWheeledVehicle and self.chassis.generalWheelsAnimatorConfig is None:
            for wheel in self.chassis.wheels.wheels:
                hitTesters.append(wheel.hitTesterManager)

        return hitTesters

    def prerequisites(self, newPhysic=True):
        prereqs = set()
        for effGroup in self.type.effects.values():
            for keyPoints, effects, readyPrereqs in effGroup:
                if not readyPrereqs:
                    prereqs.update(effects.prerequisites())

        if self.chassis.effects is not None and not newPhysic:
            if self.chassis.effects['dust'] is not None:
                effGroup, readyPrereqs = self.chassis.effects['dust']
                if not readyPrereqs:
                    prereqs.update(self.__getChassisEffectNames(effGroup))
            if self.chassis.effects['mud'] is not None:
                effGroup, readyPrereqs = self.chassis.effects['mud']
                if not readyPrereqs:
                    prereqs.update(self.__getChassisEffectNames(effGroup))
        for turretDescr, gunDescr in self.turrets:
            detachmentEff = turretDescr.turretDetachmentEffects
            detachmentEff = itertools.chain((detachmentEff['flight'], detachmentEff['flamingOnGround']), detachmentEff['collision'].itervalues())
            for stages, effects, readyPrereqs in detachmentEff:
                if not readyPrereqs:
                    prereqs.update(effects.prerequisites())

            if gunDescr.effects is not None:
                if isinstance(gunDescr.effects, list):
                    for effect in gunDescr.effects:
                        keyPoints, effects, readyPrereqs = effect
                        if not readyPrereqs:
                            prereqs.update(effects.prerequisites())

                else:
                    keyPoints, effects, readyPrereqs = gunDescr.effects
                    if not readyPrereqs:
                        prereqs.update(effects.prerequisites())
            for shotDescr in gunDescr.shots:
                effectsDescr = g_cache.shotEffects[shotDescr.shell.effectsIndex]
                if not effectsDescr['prereqs']:
                    projectileModel, projectileOwnShotModel, effects = effectsDescr['projectile']
                    prereqs.add(projectileModel)
                    prereqs.add(projectileOwnShotModel)
                    prereqs.update(effects.prerequisites())
                    for materialName in EFFECT_MATERIALS:
                        prereqs.update(effectsDescr[materialName + 'Hit'][1].prerequisites())

                    prereqs.update(effectsDescr['shallowWaterHit'][1].prerequisites())
                    prereqs.update(effectsDescr['deepWaterHit'][1].prerequisites())
                    prereqs.update(effectsDescr['armorResisted'][1].prerequisites())
                    prereqs.update(effectsDescr['armorBasicRicochet'][1].prerequisites())
                    prereqs.update(effectsDescr['armorRicochet'][1].prerequisites())
                    prereqs.update(effectsDescr['armorHit'][1].prerequisites())
                    prereqs.update(effectsDescr['armorCriticalHit'][1].prerequisites())

        if self.type._prereqs is None and not newPhysic:
            prereqs.update(self.hull['exhaust'].prerequisites())
            for extra in self.extras:
                prereqs.update(extra.prerequisites())

        for elem in copy.copy(prereqs):
            if elem in g_cache.requestOncePrereqs:
                prereqs.remove(elem)

        return list(prereqs)

    def keepPrereqs(self, prereqs):
        if not prereqs:
            return
        else:
            for effGroup in self.type.effects.values():
                for keyPoints, effects, readyPrereqs in effGroup:
                    if not readyPrereqs:
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))

            for turretDescr, gunDescr in self.turrets:
                detachmentEff = turretDescr.turretDetachmentEffects
                detachmentEff = itertools.chain((detachmentEff['flight'], detachmentEff['flamingOnGround']), detachmentEff['collision'].itervalues())
                for stages, effects, readyPrereqs in detachmentEff:
                    if not readyPrereqs:
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))

                if isinstance(gunDescr.effects, list):
                    for gunEffect in gunDescr.effects:
                        keyPoints, effects, readyPrereqs = gunEffect
                        if not readyPrereqs:
                            readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))

                else:
                    keyPoints, effects, readyPrereqs = gunDescr.effects
                    if not readyPrereqs:
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))
                for shotDescr in gunDescr.shots:
                    effectsDescr = g_cache.shotEffects[shotDescr.shell.effectsIndex]
                    readyPrereqs = effectsDescr['prereqs']
                    if not readyPrereqs:
                        projectileModel, projectileOwnShotModel, effects = effectsDescr['projectile']
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, (projectileModel, projectileOwnShotModel)))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effects.prerequisites()))
                        for materialName in EFFECT_MATERIALS:
                            readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr[materialName + 'Hit'][1].prerequisites()))

                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['shallowWaterHit'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['deepWaterHit'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorResisted'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorBasicRicochet'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorRicochet'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorHit'][1].prerequisites()))
                        readyPrereqs.update(_extractNeededPrereqs(prereqs, effectsDescr['armorCriticalHit'][1].prerequisites()))

            if self.type._prereqs is None:
                resourceNames = []
                for extra in self.extras:
                    resourceNames += extra.prerequisites()

                self.type._prereqs = _extractNeededPrereqs(prereqs, resourceNames)
            return

    def computeBaseInvisibility(self, crewFactor, camouflageId):
        if not camouflageId:
            camouflageBonus = 0.0
        else:
            camouflageBonus = self.type.invisibilityDeltas['camouflageBonus'] * g_cache.customization20().camouflages[camouflageId].invisibilityFactor
        vehicleFactor = self.miscAttrs['invisibilityFactor']
        invMoving, invStill = self.type.invisibility
        return (invMoving * crewFactor * vehicleFactor + camouflageBonus, invStill * crewFactor * vehicleFactor + camouflageBonus)

    def __getChassisEffectNames(self, effectGroup):
        ret = []
        for v in effectGroup.values():
            if isinstance(v, list):
                for s in v:
                    ret.append(s)

            ret.append(v)

        return ret

    def __installGun(self, gunID, turretPositionIdx):
        turretDescr, prevGunDescr = self.turrets[turretPositionIdx]
        newGunDescr = _findDescrByID(turretDescr.guns, gunID)
        hullDescr = self.hull
        if newGunDescr is None and turretPositionIdx in self.hull.fakeTurrets['lobby']:
            newGunDescr, turretDescr, hullDescr = self.__selectTurretForGun(gunID, turretPositionIdx)
        if newGunDescr is None:
            raise SoftException
        self.turrets[turretPositionIdx] = (turretDescr, newGunDescr)
        self.hull = hullDescr
        self.__updateAttributes()
        if self.__activeTurretPos == turretPositionIdx:
            self.activeTurretPosition = turretPositionIdx
        return (prevGunDescr.compactDescr,)

    def __selectBestHull(self, turrets, chassis):
        turretIDs = [ descr[0].id[1] for descr in turrets ]
        chassisID = chassis.id[1]
        hulls = self.type.hulls
        bestHull = hulls[0]
        bestMatchWeight = 0
        for hull in hulls[1:]:
            match = hull.variantMatch
            matchWeight = 0
            if match[0] is not None:
                if match[0] != chassisID:
                    continue
                matchWeight = 100
            for turretID, turretToMatchID in zip(turretIDs, match[1:]):
                if turretToMatchID is None:
                    continue
                if turretID == turretToMatchID:
                    matchWeight += 1
                matchWeight = -1
                break

            if bestMatchWeight < matchWeight:
                bestMatchWeight = matchWeight
                bestHull = hull

        return bestHull

    def __selectTurretForGun(self, gunID, turretPositionIdx):
        hullDescr = self.hull
        for turretDescr in self.type.turrets[turretPositionIdx]:
            gunDescr = _findDescrByID(turretDescr.guns, gunID)
            if gunDescr is not None:
                if len(self.type.hulls) > 1:
                    turrets = list(self.turrets)
                    turrets[turretPositionIdx] = (turretDescr, gunDescr)
                    hullDescr = self.__selectBestHull(turrets, self.chassis)
                return (gunDescr, turretDescr, hullDescr)

        return (None, None, None)

    def __setHullAndCall(self, hullDescr, callable):
        self.hull = hullDescr
        callable()

    def __initFromCompactDescr(self, compactDescr, vehMode, vehType=None):
        unpack = struct.unpack
        try:
            type, components, optionalDeviceSlots, optionalDevices, enhancements, emblemPositions, emblems, inscriptions, camouflages = _splitVehicleCompactDescr(compactDescr, vehMode, vehType)
            custNationID = type.customizationNationID
            customization = g_cache.customization(custNationID)
            self.type = type
            self.name = type.name
            self.level = type.level
            if IS_CLIENT or IS_EDITOR or IS_CELLAPP or IS_BOT:
                self.extras = type.extras
                self.extrasDict = type.extrasDict
            chassisID, engineID, fuelTankID, radioID = unpack('<4H', components[:8])
            self.chassis = _descrByID(type.chassis, chassisID)
            self.engine = _descrByID(type.engines, engineID)
            self.fuelTank = _descrByID(type.fuelTanks, fuelTankID)
            self.radio = _descrByID(type.radios, radioID)
            turrets = []
            for idx in xrange(len(type.turrets)):
                turretID, gunID = unpack('<2H', components[8 + idx * 4:12 + idx * 4])
                turret = _descrByID(type.turrets[idx], turretID)
                turrets.append((turret, _descrByID(turret.guns, gunID)))

            self.turrets = turrets
            self.activeTurretPosition = 0
            if len(type.hulls) == 1:
                self.hull = type.hulls[0]
            else:
                self.hull = self.__selectBestHull(self.turrets, self.chassis)
            self.supplySlots = self.type.supplySlots
            optDevSlots = self.supplySlots.getAmountForType(ITEM_TYPES.optionalDevice)
            self.optionalDevices = [None] * optDevSlots
            self._optDevSlotsMap = {}
            optDevsCache = g_cache.optionalDevices()
            idx = optDevSlots - 1
            while optionalDeviceSlots:
                if optionalDeviceSlots & 1:
                    self.optionalDevices[idx] = optDevsCache[unpack('<H', optionalDevices[:2])[0]]
                    optionalDevices = optionalDevices[2:]
                optionalDeviceSlots >>= 1
                idx -= 1

            self._rebuildOptDevSlotsMap()
            if enhancements:
                enhancements = enhancements[1:]
                for idx in xrange(0, len(enhancements), 6):
                    attrId, value, opIdx = unpack('<BfB', enhancements[idx:idx + 6])
                    self.enhancements.append(EnhancementItem(VEHICLE_MISC_ATTRIBUTE_FACTOR_NAMES[attrId], value / 1000, EnhancementItem.getOpName(opIdx)))

            if IS_CLIENT:
                self.playerEmblems = _EMPTY_EMBLEMS
                self.playerInscriptions = _EMPTY_INSCRIPTIONS
                self.camouflages = _EMPTY_CAMOUFLAGES
            else:
                if not emblemPositions & 15:
                    self.playerEmblems = type._defEmblems
                else:
                    emblemCache = g_cache.playerEmblems()[1]
                    slots = [None,
                     None,
                     None,
                     None]
                    for idx in _RANGE_4:
                        if emblemPositions & 1 << idx:
                            slots[idx] = _unpackIDAndDuration(emblems[:6])
                            emblems = emblems[6:]
                            emblemCache[slots[idx][0]]
                        slots[idx] = type._defEmblem

                    self.playerEmblems = tuple(slots)
                if not emblemPositions & 240:
                    self.playerInscriptions = _EMPTY_INSCRIPTIONS
                else:
                    slots = [None,
                     None,
                     None,
                     None]
                    for idx in _RANGE_4:
                        if emblemPositions & 1 << idx + 4:
                            slots[idx] = _unpackIDAndDuration(inscriptions[:6]) + (ord(inscriptions[6]),)
                            inscriptions = inscriptions[7:]
                            customization['inscriptions'][slots[idx][0]]
                            customization['inscriptionColors'][slots[idx][3]]
                        slots[idx] = _EMPTY_INSCRIPTION

                    self.playerInscriptions = tuple(slots)
                if not camouflages:
                    self.camouflages = _EMPTY_CAMOUFLAGES
                else:
                    slots = list(_EMPTY_CAMOUFLAGES)
                    while camouflages:
                        item = _unpackIDAndDuration(camouflages[:6])
                        camouflages = camouflages[6:]
                        idx = customization['camouflages'][item[0]]['kind']
                        if slots[idx][0] is not None:
                            LOG_WARNING('Second camouflage of same kind', custNationID, item[0], slots[idx][0])
                        slots[idx] = item

                    self.camouflages = tuple(slots)
        except Exception:
            LOG_ERROR('(compact descriptor to XML mismatch?)', compactDescr)
            raise

        return

    def __computeWeight(self):
        maxWeight = self.chassis.maxLoad
        weight = self.hull.weight + self.chassis.weight + self.engine.weight + self.fuelTank.weight + self.radio.weight
        for turretDescr, gunDescr in self.turrets:
            weight += turretDescr.weight + gunDescr.weight

        vehWeightFraction = 0.0
        vehWeightAddition = 0.0
        for device in self.optionalDevices:
            if device is not None:
                fraction, addition, maxWeightChange = device.weightOnVehicle(self)
                vehWeightFraction += fraction
                vehWeightAddition += addition
                maxWeight += maxWeightChange

        return (weight * (1.0 + vehWeightFraction) + vehWeightAddition, maxWeight)

    def isWeightConsistent(self):
        weight, maxWeight = self.__computeWeight()
        return weight <= maxWeight

    def applyOptionalDevicesMiscAttrs(self):
        for optDev in self.optionalDevices:
            if optDev is not None:
                optDev.updateVehicleDescrAttrs(self)

        return

    def applyOptDevFactorsForAspect(self, factors, aspect):
        for optDev in self.optionalDevices:
            if optDev is not None:
                optDev.updateVehicleAttrFactorsForAspect(self, factors, aspect)

        return

    def applyModificationsAttrs(self):
        vppCache = g_cache.postProgression()
        items = iter((vppCache.modifications[modificationID].modifiers for modificationID in self._modifications))
        onCollectAttributes(self.miscAttrs, items, STATIC_ATTR_PREFIX, True)

    @property
    def shootExtraName(self):
        return 'shoot' if not self.isDualgunVehicle else 'dualShoot'

    def __updateAttributes(self, onAnyApp=False):
        self.miscAttrs = None
        self.physics = None
        type = self.type
        chassis = self.chassis
        chassisShotDispersionFactors = chassis.shotDispersionFactors
        gunShotDispersionFactors = self.gun.shotDispersionFactors
        self._maxHealth = self.hull.maxHealth
        for turretDescr, gunDescr in self.turrets:
            self._maxHealth += turretDescr.maxHealth

        weight, maxWeight = self.__computeWeight()
        self.miscAttrs = {'maxWeight': maxWeight,
         'repairSpeedFactor': 1.0,
         'additiveShotDispersionFactor': 1.0,
         'antifragmentationLiningFactor': 1.0,
         'circularVisionRadiusFactor': 1.0,
         'circularVisionRadiusBaseFactor': 1.0,
         'gunReloadTimeFactor': 1.0,
         'gunAimingTimeFactor': 1.0,
         'vehicleByChassisDamageFactor': 1.0,
         'crewLevelIncrease': 0.0,
         'crewChanceToHitFactor': 1.0,
         'stunResistanceEffect': 0.0,
         'stunResistanceDuration': 0.0,
         'repeatedStunDurationFactor': 1.0,
         'healthFactor': 1.0,
         'damageFactor': 1.0,
         'receivedDamageFactor': 1.0,
         'enginePowerFactor': 1.0,
         'armorSpallsDamageDevicesFactor': 1.0,
         'increaseEnemySpottingTime': 0.0,
         'decreaseOwnSpottingTime': 0.0,
         'demaskFoliageFactor': 1.0,
         'chassisRepairSpeedFactor': 1.0,
         'turretRotationSpeed': 1.0,
         'invisibilityAdditiveTerm': 0.0,
         'invisibilityBaseAdditive': 0.0,
         'forwardMaxSpeedKMHTerm': 0.0,
         'backwardMaxSpeedKMHTerm': 0.0,
         'onStillRotationSpeedFactor': 1.0,
         'onMoveRotationSpeedFactor': 1.0,
         'fireStartingChanceFactor': 1.0,
         'multShotDispersionFactor': 1.0,
         'chassisHealthAfterHysteresisFactor': 1.0,
         'ammoBayHealthFactor': 1.0,
         'engineHealthFactor': 1.0,
         'chassisHealthFactor': 1.0,
         'fuelTankHealthFactor': 1.0,
         'turretRotatorHealthFactor': 1.0,
         'radioHealthFactor': 1.0,
         'surveyingDeviceHealthFactor': 1.0,
         'gunHealthFactor': 1.0,
         'demaskMovingFactor': 1.0,
         'centerRotationFwdSpeedFactor': 1.0,
         'deathZones/sensitivityFactor': 1.0,
         'rammingFactor': 1.0,
         'rollingFrictionFactor': 1.0,
         'chassis/shotDispersionFactors/movement': chassisShotDispersionFactors[0],
         'chassis/shotDispersionFactors/rotation': chassisShotDispersionFactors[1],
         'invisibilityFactorAtShot': self.gun.invisibilityFactorAtShot,
         'gun/shotDispersionFactors/afterShot': gunShotDispersionFactors['afterShot'],
         'gun/shotDispersionFactors/turretRotation': gunShotDispersionFactors['turretRotation'],
         'gun/shotDispersionFactors/whileGunDamaged': gunShotDispersionFactors['whileGunDamaged'],
         'ammoBayReduceFineFactor': 1.0,
         'engineReduceFineFactor': 1.0,
         'proofHealth': 0}
        if IS_CLIENT or IS_EDITOR or IS_CELLAPP or IS_WEB or IS_BOT or onAnyApp:
            trackCenterOffset = chassis.topRightCarryingPoint[0]
            self.physics = {'weight': weight,
             'enginePower': self.engine.power,
             'specificFriction': chassis.specificFriction,
             'minPlaneNormalY': chassis.minPlaneNormalY,
             'trackCenterOffset': trackCenterOffset,
             'rotationIsAroundCenter': chassis.rotationIsAroundCenter,
             'speedLimits': self.type.speedLimits,
             'navmeshGirth': chassis.navmeshGirth,
             'carryingTriangles': chassis.carryingTriangles,
             'brakeForce': chassis.brakeForce,
             'terrainResistance': chassis.terrainResistance,
             'rollingFrictionFactors': [1.0, 1.0, 1.0]}
            self.applyModificationsAttrs()
            self.applyOptionalDevicesMiscAttrs()
            physics = self.physics
            rff = physics['rollingFrictionFactors']
            rollingFrictionFactor = self.miscAttrs['rollingFrictionFactor']
            physics['rollingFrictionFactors'] = list((rffi * rollingFrictionFactor for rffi in rff))
            defWeight = type.hulls[0].weight + chassis.weight + type.engines[0].weight + type.fuelTanks[0].weight + type.radios[0].weight
            for turretList in type.turrets:
                defWeight += turretList[0].weight + turretList[0].guns[0].weight

            defResistance = chassis.terrainResistance[0]
            rotationEnergy = type.engines[0].power * (weight / defWeight) / (chassis.rotationSpeed * defResistance)
            rotationSpeedLimit = physics['enginePower'] / (rotationEnergy * physics['terrainResistance'][0])
            if not chassis.rotationIsAroundCenter:
                rotationEnergy -= trackCenterOffset * weight * chassis.specificFriction / defResistance
                if rotationEnergy <= 0.0:
                    raise SoftException('wrong parameters of rotation of ' + type.name)
            if chassis.rotationSpeedLimit is not None:
                rotationSpeedLimit = min(rotationSpeedLimit, chassis.rotationSpeedLimit)
            physics['rotationSpeedLimit'] = rotationSpeedLimit
            physics['rotationEnergy'] = rotationEnergy
            physics['massRotationFactor'] = defWeight / weight
            if IS_CELLAPP or IS_CLIENT or IS_EDITOR or IS_BOT:
                invisibilityFactor = 1.0
                for turretDescr, _ in self.turrets:
                    invisibilityFactor *= turretDescr.invisibilityFactor

                self.miscAttrs['invisibilityFactor'] = invisibilityFactor
        if IS_CELLAPP:
            hullPos = self.chassis.hullPosition
            hullBboxMin, hullBboxMax, _ = self.hull.hitTester.bbox
            turretPosOnHull = self.hull.turretPositions[0]
            turretLocalTopY = max(hullBboxMax.y, turretPosOnHull.y + self.turret.hitTester.bbox[1].y)
            gunPosOnHull = turretPosOnHull + self.turret.gunPosition
            hullLocalCenterY = (hullBboxMin.y + hullBboxMax.y) / 2.0
            hullLocalPt1 = Vector3(0.0, hullLocalCenterY, hullBboxMax.z)
            hullLocalPt2 = Vector3(0.0, hullLocalCenterY, hullBboxMin.z)
            hullLocalCenterZ = (hullBboxMin.z + hullBboxMax.z) / 2.0
            hullLocalPt3 = Vector3(hullBboxMax.x, gunPosOnHull.y, hullLocalCenterZ)
            hullLocalPt4 = Vector3(hullBboxMin.x, gunPosOnHull.y, hullLocalCenterZ)
            self.visibilityCheckPoints = (Vector3(0.0, hullPos.y + turretLocalTopY, 0.0),
             hullPos + gunPosOnHull,
             hullPos + hullLocalPt1,
             hullPos + hullLocalPt2,
             hullPos + hullLocalPt3,
             hullPos + hullLocalPt4)
            self.observerPosOnChassis = Vector3(0, hullPos.y + turretLocalTopY, 0)
            self.observerPosOnTurret = self.turret.gunPosition
        for attribute in self.enhancements:
            self.miscAttrs[attribute.name] = attribute.applyFactor(self.miscAttrs[attribute.name])

        if self.miscAttrs['healthFactor'] != 1.0:
            self._maxHealth = int(ceilTo(self._maxHealth * self.miscAttrs['healthFactor'], VEHICLE_HEALTH_DECIMALS))
        return


class CompositeVehicleDescriptor(object):
    defaultVehicleDescr = property(lambda self: self.__vehicleDescr)
    siegeVehicleDescr = property(lambda self: self.__siegeDescr)
    vehicleMode = property(lambda self: self.__vehicleMode)
    currentDescr = property(lambda self: self.__siegeDescr if self.__vehicleMode == VEHICLE_MODE.SIEGE else self.__vehicleDescr)

    def __init__(self, vehicleDescr, siegeDescr):
        self.__dict__['_CompositeVehicleDescriptor__vehicleDescr'] = vehicleDescr
        self.__dict__['_CompositeVehicleDescriptor__siegeDescr'] = siegeDescr
        self.__dict__['_CompositeVehicleDescriptor__vehicleMode'] = VEHICLE_MODE.DEFAULT
        if IS_CLIENT:
            self.__siegeDescr.chassis.hitTesterManager = self.__vehicleDescr.chassis.hitTesterManager
            self.__siegeDescr.hull.hitTesterManager = self.__vehicleDescr.hull.hitTesterManager
            self.__siegeDescr.turret.hitTesterManager = self.__vehicleDescr.turret.hitTesterManager
            self.__siegeDescr.gun.hitTesterManager = self.__vehicleDescr.gun.hitTesterManager
            self.__siegeDescr.type.extras = self.__vehicleDescr.type.extras
            self.__siegeDescr.type.extrasDict = self.__vehicleDescr.type.extrasDict

    def __getattr__(self, item):
        return getattr(self.__siegeDescr, item) if self.__vehicleMode == VEHICLE_MODE.SIEGE else getattr(self.__vehicleDescr, item)

    def __setattr__(self, key, value):
        setattr(self.__siegeDescr, key, value)
        setattr(self.__vehicleDescr, key, value)

    def onSiegeStateChanged(self, siegeMode):
        if siegeMode == VEHICLE_SIEGE_STATE.ENABLED:
            self.__dict__['_CompositeVehicleDescriptor__vehicleMode'] = VEHICLE_MODE.SIEGE
        elif self.__vehicleMode == VEHICLE_MODE.SIEGE:
            self.__dict__['_CompositeVehicleDescriptor__vehicleMode'] = VEHICLE_MODE.DEFAULT

    def installComponent(self, compactDescr, positionIndex=0):
        self.__siegeDescr.installComponent(compactDescr, positionIndex)
        return self.__vehicleDescr.installComponent(compactDescr, positionIndex)

    def installEnhancements(self, enhancements, rebuildAttrs=True):
        self.__siegeDescr.installEnhancements(enhancements, rebuildAttrs)
        return self.__vehicleDescr.installEnhancements(enhancements, rebuildAttrs)

    def installModifications(self, modificationIDs, rebuildAttrs=True):
        self.__siegeDescr.installModifications(modificationIDs, rebuildAttrs)
        return self.__vehicleDescr.installModifications(modificationIDs, rebuildAttrs)

    def installOptionalDevice(self, compactDescr, slotIdx, rebuildAttrs=True):
        self.__siegeDescr.installOptionalDevice(compactDescr, slotIdx, rebuildAttrs)
        return self.__vehicleDescr.installOptionalDevice(compactDescr, slotIdx, rebuildAttrs)

    def installOptDevsSequence(self, optDevSequence):
        self.__siegeDescr.installOptDevsSequence(optDevSequence)
        return self.__vehicleDescr.installOptDevsSequence(optDevSequence)

    def installTurret(self, turretCompactDescr, gunCompactDescr, positionIndex=0):
        self.__siegeDescr.installTurret(turretCompactDescr, gunCompactDescr, positionIndex)
        return self.__vehicleDescr.installTurret(turretCompactDescr, gunCompactDescr, positionIndex)

    def removeOptionalDevice(self, slotIdx, rebuildAttrs=True):
        self.__siegeDescr.removeOptionalDevice(slotIdx, rebuildAttrs)
        return self.__vehicleDescr.removeOptionalDevice(slotIdx, rebuildAttrs)

    def rebuildAttrs(self):
        self.__siegeDescr.rebuildAttrs()
        return self.__vehicleDescr.rebuildAttrs()

    def __installGun(self, gunID, turretPositionIdx):
        self.__siegeDescr.__installGun(gunID, turretPositionIdx)
        return self.__vehicleDescr.__installGun(gunID, turretPositionIdx)


def VehicleDescr(compactDescr=None, typeID=None, typeName=None, xmlPath=None, extData=None):
    defaultDescriptor = VehicleDescriptor(compactDescr, typeID, typeName, xmlPath=xmlPath, extData=extData)
    if not defaultDescriptor.hasSiegeMode:
        return defaultDescriptor
    siegeDescriptor = VehicleDescriptor(compactDescr, typeID, typeName, VEHICLE_MODE.SIEGE, xmlPath=xmlPath, extData=extData)
    return CompositeVehicleDescriptor(defaultDescriptor, siegeDescriptor)


def isVehicleDescr(descr):
    return isinstance(descr, VehicleDescriptor) or isinstance(descr, CompositeVehicleDescriptor)


VehicleDescrType = Union[VehicleDescriptor, CompositeVehicleDescriptor]

class NoneVehicleSelector(list):

    def matches(self, vehTypeOrDescr=None, vehName=None):
        return False

    def match(self, tags=(), excludedTags=()):
        return self


class VehicleSelector(NoneVehicleSelector):
    ANY = ('', '*')
    ctags = property(lambda self: self.__tags & VEHICLE_CLASS_TAGS)
    vtags = property(lambda self: self.__tags - VEHICLE_CLASS_TAGS)
    etags = property(lambda self: self.__etags - VEHICLE_CLASS_TAGS)

    def __init__(self, ns=(), levels=(), vehClasses=(), vehTags=(), excludedVehTags=()):
        self.__nations = {str(n) for n in ns if str(n) in nations.NAMES} if ns else nations.NAMES
        self.__levels = {int(l) for l in levels} if levels else set(range(1, 11))
        self.__tags = {str(vc) for vc in vehClasses if vc in VEHICLE_CLASS_TAGS} if vehClasses else VEHICLE_CLASS_TAGS
        vtags = set(items.getTypeInfoByName('vehicle')['tags']) - VEHICLE_CLASS_TAGS
        self.__tags |= {str(vt) for vt in vehTags if vt in vtags}
        self.__etags = {str(vt) for vt in excludedVehTags if vt in vtags}

    def match(self, tags=(), excludedTags=()):
        tags = frozenset(tags)
        excludedTags = frozenset(excludedTags)
        if not self:
            nset, levels, vtags, vetags = (self.__nations,
             self.__levels,
             self.__tags,
             self.__etags)
            tags |= vtags
            excludedTags |= vetags
            self.extend((vdict.compactDescr for nn in nset for vdict in g_list.getList(nations.INDICES[nn]).itervalues() if self.matches(vehTypeOrDescr=vdict.compactDescr)))
        return self

    def matches(self, vehTypeOrDescr=None, vehName=None):
        if not bool(vehTypeOrDescr) ^ bool(vehName):
            raise SoftException('Value Error')
        if vehTypeOrDescr is not None:
            _, nid, vnid = parseIntCompactDescr(vehTypeOrDescr)
        elif vehName is not None:
            nid, vnid = g_list.getIDsByName(vehName)
        vdata = g_list.getList(nid)[vnid]
        vct, vt, vet = self.ctags, self.vtags, self.etags
        return (not self.__nations or nations.MAP[nid] in self.__nations) and (not self.__levels or vdata.level in self.__levels) and not (vct and vdata.tags.isdisjoint(vct)) and not (vt and not vdata.tags >= vt) and not (vet and vdata.tags >= vet)

    def __repr__(self):
        return super(VehicleSelector, self).__repr__() if self else ':'.join(('|'.join(self.__nations),
         '|'.join((str(l) for l in self.__levels)),
         '|'.join(self.ctags),
         '&'.join(self.vtags | {'~{}'.format(et) for et in self.etags})))

    @staticmethod
    def fromString(vstr):
        try:
            nset, levels, ctags, tags = itertools.islice(itertools.chain(string.split(vstr, ':', 3), iter(str, -1)), 4)
            nset = VehicleSelector.predicateAsSet(nset, nations.NAMES, str)
            levels = VehicleSelector.predicateAsSet(levels, range(1, 11), int)
            vehClasses = VehicleSelector.predicateAsSet(ctags, VEHICLE_CLASS_TAGS, str)
            tags = tags.split('&')
            vehTags = {t for t in tags if not (t in VEHICLE_CLASS_TAGS or t.startswith('~'))}
            excludedVehTags = {t[1:] for t in tags if t and t[1:] not in VEHICLE_CLASS_TAGS and t.startswith('~')}
        except ValueError:
            LOG_ERROR('Unable to match any vehicle by {}'.format(vstr))
            return NoneVehicleSelector()

        return VehicleSelector(nset, levels, vehClasses, vehTags, excludedVehTags)

    @staticmethod
    def predicateAsSet(predicate, dom, fun=lambda _: _):
        result = set()
        dom = frozenset(dom)
        for p in str(predicate).split('|'):
            try:
                if p.startswith('~'):
                    result |= dom - {fun(p[1:])} if fun(p[1:]) in dom else set()
                else:
                    result.add(fun(p)) if fun(p) in dom else None
            except ValueError:
                pass

        return result or dom


class VehicleType(object):
    currentReadingVeh = None
    __metaclass__ = ReflectionMetaclass
    __slots__ = ('name',
     'id',
     'compactDescr',
     'mode',
     'tags',
     'level',
     'hasSiegeMode',
     'hasAutoSiegeMode',
     'isWheeledVehicle',
     'isDualgunVehicleType',
     'hasCustomDefaultCamouflage',
     'customizationNationID',
     'baseColorID',
     'speedLimits',
     'repairCost',
     'crewXpFactor',
     'premiumVehicleXPFactor',
     'xpFactor',
     'creditsFactor',
     'freeXpFactor',
     'healthBurnPerSec',
     'healthBurnPerSecLossFraction',
     'invisibility',
     'invisibilityDeltas',
     'crewRoles',
     'extras',
     'extrasDict',
     'devices',
     'tankmen',
     'damageByStaticsChances',
     'i18nInfo',
     'balanceByClass',
     'balanceByComponentLevels',
     'damageStickersLodDist',
     'heavyCollisionEffectVelocities',
     'effects',
     'camouflage',
     'emblemsLodDist',
     'emblemsAlpha',
     '_prereqs',
     'clientAdjustmentFactors',
     'defaultPlayerEmblemID',
     '_defEmblem',
     '_defEmblems',
     'unlocks',
     'chassis',
     'engines',
     'fuelTanks',
     'radios',
     'turrets',
     'hulls',
     'installableComponents',
     'unlocksDescrs',
     'autounlockedItems',
     'collisionEffectVelocities',
     'isRotationStill',
     'useHullZSize',
     'useHullZOffset',
     'siegeModeParams',
     'hullAimingParams',
     'overmatchMechanicsVer',
     'xphysics',
     'repaintParameters',
     'rollerExtras',
     'hasBurnout',
     'hasCharge',
     'role',
     'actionsGroup',
     'actions',
     'builtins',
     'nationChangeGroupId',
     'isCollectorVehicle',
     'hasTurboshaftEngine',
     'hasHydraulicChassis',
     'supplySlots',
     'optDevsOverrides',
     'postProgressionTree',
     'customRoleSlotOptions',
     'armorMaxHealth',
     '__weakref__')

    def __init__(self, nationID, basicInfo, xmlPath, vehMode=VEHICLE_MODE.DEFAULT):
        self.name = basicInfo.name
        self.id = (nationID, basicInfo.id)
        self.compactDescr = basicInfo.compactDescr
        self.mode = vehMode
        self.nationChangeGroupId = nation_change.findVehicleNationGroupId(self.name)
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        xmlCtx = (None, xmlPath)
        self.tags = basicInfo.tags
        self.level = basicInfo.level
        self.hasSiegeMode = 'siegeMode' in self.tags
        self.hasHydraulicChassis = 'hydraulicChassis' in self.tags
        self.hasAutoSiegeMode = 'autoSiege' in self.tags
        self.isWheeledVehicle = 'wheeledVehicle' in self.tags
        self.isDualgunVehicleType = 'dualgun' in self.tags
        self.hasTurboshaftEngine = 'turboshaftEngine' in self.tags
        self.hasCharge = 'charger' in self.tags
        self.builtins = {t.split('_user')[0] for t in self.tags if t.startswith('builtin')}
        self.hasBurnout = 'burnout' in self.tags
        self.isCollectorVehicle = CollectorVehicleConsts.COLLECTOR_VEHICLES_TAG in self.tags
        self.role = self.__getRoleFromTags() if self.level in ROLE_LEVELS else ROLE_TYPE.NOT_DEFINED
        self.actions = self.__getActionsFromRole(self.role)
        VehicleType.currentReadingVeh = self
        self.baseColorID = section.readInt('baseColorID', 0)
        self.hasCustomDefaultCamouflage = section.readBool('customDefaultCamouflage', False)
        customizationNation = section.readString('customizationNation')
        if not customizationNation:
            self.customizationNationID = nationID
        else:
            self.customizationNationID = nations.INDICES.get(customizationNation)
            if self.customizationNationID is None:
                _xml.raiseWrongXml(xmlCtx, 'customizationNation', 'unknown nation name:' + customizationNation)
        self.speedLimits = (component_constants.KMH_TO_MS * _xml.readPositiveFloat(xmlCtx, section, 'speedLimits/forward'), component_constants.KMH_TO_MS * _xml.readPositiveFloat(xmlCtx, section, 'speedLimits/backward'))
        if IS_EDITOR:
            self.speedLimits = list(self.speedLimits)
        self.repairCost = _xml.readNonNegativeFloat(xmlCtx, section, 'repairCost')
        self.crewXpFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'crewXpFactor')
        self.premiumVehicleXPFactor = component_constants.DEFAULT_PREMIUM_VEHICLE_XP_FACTOR
        if section.has_key('premiumVehicleXPFactor'):
            self.premiumVehicleXPFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'premiumVehicleXPFactor')
        self.premiumVehicleXPFactor = max(self.premiumVehicleXPFactor, 0.0)
        supplySlotIDs = _xml.readTupleOfInts(xmlCtx, section, 'supplySlots')
        self.supplySlots = g_cache.supplySlotsStorage().getStorage(supplySlotIDs)
        if section.has_key('postProgressionTree'):
            treeName = _xml.readString(xmlCtx, section, 'postProgressionTree')
            treeID = g_cache.postProgression().treeIDs.get(treeName)
            if treeID is None:
                _xml.raiseWrongXml(xmlCtx, 'postProgressionTree', 'Unknown postProgression tree: {}'.format(treeName))
            self.postProgressionTree = treeID
        else:
            self.postProgressionTree = None
        if self.role == ROLE_TYPE.NOT_DEFINED and self.postProgressionTree is not None:
            LOG_ERROR('Vehicle {} must have role'.format(self.name))
        if section.has_key('customRoleSlotOptions'):
            self.customRoleSlotOptions = _xml.readTupleOfInts(xmlCtx, section, 'customRoleSlotOptions')
            intersection = set(supplySlotIDs) & set(self.customRoleSlotOptions)
            if intersection:
                _xml.raiseWrongXml(xmlCtx, 'customRoleSlotOptions', 'Duplicate custom slots: {}'.format(intersection))
        else:
            self.customRoleSlotOptions = ()
        if not IS_CLIENT and not IS_BOT:
            self.xpFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'xpFactor')
            self.creditsFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'creditsFactor')
            self.freeXpFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'freeXpFactor')
            self.healthBurnPerSec = _xml.readNonNegativeFloat(xmlCtx, section, 'healthBurnPerSec')
            self.healthBurnPerSecLossFraction = _DEFAULT_HEALTH_BURN_PER_SEC_LOSS_FRACTION
        self.invisibility = (_xml.readFraction(xmlCtx, section, 'invisibility/moving'), _xml.readFraction(xmlCtx, section, 'invisibility/still'))
        camouflageBonus = _xml.readFraction(xmlCtx, section, 'invisibility/camouflageBonus')
        CamouflageBonus.MIN = min(CamouflageBonus.MIN, camouflageBonus)
        CamouflageBonus.MAX = max(CamouflageBonus.MAX, camouflageBonus)
        self.invisibilityDeltas = {'camouflageBonus': camouflageBonus,
         'firePenalty': _xml.readFraction(xmlCtx, section, 'invisibility/firePenalty')}
        self.optDevsOverrides = _readOptDevsOverrides(xmlCtx, section['optDevsOverrides'])
        self.crewRoles = _readCrew(xmlCtx, section, 'crew')
        commonConfig = g_cache.commonConfig
        if IS_CLIENT or IS_EDITOR or IS_CELLAPP or IS_BOT:
            _id = lambda args: args
            copyMethod = copy.copy if section.has_key('extras') else _id
            self.extras = copyMethod(commonConfig['extras'])
            self.extrasDict = copyMethod(commonConfig['extrasDict'])
            self.devices = copyMethod(commonConfig['_devices'])
            self.tankmen = _selectCrewExtras(self.crewRoles, self.extrasDict)
            self.armorMaxHealth = _xml.readIntOrNone(xmlCtx, section, 'armorMaxHealth')
        if IS_CLIENT or IS_WEB:
            self.i18nInfo = basicInfo.i18n
        if IS_CLIENT or IS_EDITOR:
            self.damageStickersLodDist = commonConfig['miscParams']['damageStickersLodDist']
            collisionVelCfg = commonConfig['miscParams']['collisionEffectVelocities']
            self.heavyCollisionEffectVelocities = {'hull': collisionVelCfg['hull'][1],
             'track': collisionVelCfg['track'][1],
             'waterContact': collisionVelCfg['waterContact'][1]}
            if not IS_EDITOR:
                self.effects = _readVehicleEffects(xmlCtx, section, 'effects', commonConfig['defaultVehicleEffects'], useOverride=True)
            else:
                self.effects, self.editorData.damagedStateGroup = _readVehicleEffects(xmlCtx, section, 'effects', commonConfig['defaultVehicleEffects'][0], useOverride=True)
                if self.editorData.damagedStateGroup is None:
                    self.editorData.damagedStateGroup = commonConfig['defaultDamagedStateGroup']
            self.camouflage = shared_readers.readCamouflage(xmlCtx, section, 'camouflage')
            self.emblemsLodDist = shared_readers.readLodDist(xmlCtx, section, 'emblems/lodDist', g_cache)
            self.emblemsAlpha = _xml.readFraction(xmlCtx, section, 'emblems/alpha')
            self._prereqs = None
            self.clientAdjustmentFactors = _readClientAdjustmentFactors(xmlCtx, section)
        if IS_CELLAPP or IS_CLIENT or IS_EDITOR:
            collisionVelCfg = commonConfig['miscParams']['collisionEffectVelocities']
            self.collisionEffectVelocities = {'hull': collisionVelCfg['hull'][0],
             'track': collisionVelCfg['track'][0],
             'waterContact': collisionVelCfg['waterContact'][0],
             'ramming': collisionVelCfg['ramming']}
        g_cache.playerEmblems()
        self.defaultPlayerEmblemID = _xml.readNonNegativeInt(xmlCtx, section, 'emblems/default')
        NATIONAL_EMBLEMS.add(self.defaultPlayerEmblemID)
        self._defEmblem = (self.defaultPlayerEmblemID, _CUSTOMIZATION_EPOCH, 0)
        self._defEmblems = (self._defEmblem,
         self._defEmblem,
         self._defEmblem,
         self._defEmblem)
        pricesDest = _g_prices
        if pricesDest is not None:
            pricesDest['vehicleCamouflagePriceFactors'][self.compactDescr] = _xml.readNonNegativeFloat(xmlCtx, section, 'camouflage/priceFactor')
        unlocksDescrs = []
        self.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs)
        defHull = _readHull((xmlCtx, 'hull'), _xml.getSubsection(xmlCtx, section, 'hull'))
        self.damageByStaticsChances = _readDamageByStaticsChances(xmlCtx, section, 'damageByStaticsChances')
        self.chassis = _readInstallableComponents(xmlCtx, section, 'chassis', nationID, _readChassis, _readChassisLocals, g_cache.chassis(nationID), g_cache.chassisIDs(nationID), unlocksDescrs)
        self.engines = _readInstallableComponents(xmlCtx, section, 'engines', nationID, _readEngine, _readEngineLocal, g_cache.engines(nationID), g_cache.engineIDs(nationID), unlocksDescrs)
        self.fuelTanks = _readInstallableComponents(xmlCtx, section, 'fuelTanks', nationID, _readFuelTank, _defaultLocalReader, g_cache.fuelTanks(nationID), g_cache.fuelTankIDs(nationID), unlocksDescrs)
        self.radios = _readInstallableComponents(xmlCtx, section, 'radios', nationID, _readRadio, _defaultLocalReader, g_cache.radios(nationID), g_cache.radioIDs(nationID), unlocksDescrs)
        turretsList = []
        for n in xrange(len(defHull.turretPositions)):
            turrets = _readInstallableComponents(xmlCtx, section, 'turrets' + repr(n), nationID, _readTurret, _readTurretLocals, g_cache.turrets(nationID), g_cache.turretIDs(nationID), unlocksDescrs)
            turretsList.append(turrets)

        self.turrets = tuple(turretsList)
        self.hulls = (defHull,)
        if section.has_key('hull/variants'):
            self.hulls += _readHullVariants((xmlCtx, 'hull/variants'), section['hull/variants'], defHull, self.chassis, self.turrets)
        compactDescrs = set()
        _collectComponents(compactDescrs, self.chassis)
        _collectComponents(compactDescrs, self.engines)
        _collectComponents(compactDescrs, self.fuelTanks)
        _collectComponents(compactDescrs, self.radios)
        for turrets in self.turrets:
            _collectComponents(compactDescrs, turrets)
            for turret in turrets:
                _collectComponents(compactDescrs, turret.guns)

        self.installableComponents = compactDescrs
        self.unlocksDescrs = self.__convertAndValidateUnlocksDescrs(unlocksDescrs)
        self.autounlockedItems = self.__collectDefaultUnlocks()
        self.isRotationStill = section.readBool('isRotationStill', False)
        self.useHullZSize = section.readBool('useHullZSize', False)
        self.useHullZOffset = section.readBool('useHullZOffset', False)
        self.siegeModeParams = _readSiegeModeParams(xmlCtx, section, self)
        self.hullAimingParams = _readHullAimingParams(xmlCtx, section)
        if IS_CELLAPP:
            overmatchVer = _xml.readIntOrNone(xmlCtx, section, 'overmatchMechanicsVer')
            if overmatchVer is None:
                overmatchVer = OVERMATCH_MECHANICS_VER.DEFAULT
            self.overmatchMechanicsVer = overmatchVer
            try:
                self.xphysics = _readXPhysics(xmlCtx, section, 'physics')
            except:
                LOG_CURRENT_EXCEPTION()
                self.xphysics = None

        elif IS_CLIENT:
            self.xphysics = _readXPhysicsClient(xmlCtx, section, 'physics', self.isWheeledVehicle)
        elif IS_EDITOR:
            self.xphysics = _readXPhysicsEditor(xmlCtx, section, 'physics', self.isWheeledVehicle)
        else:
            self.xphysics = None
        if (IS_CLIENT or IS_EDITOR) and section.has_key('repaintParameters'):
            self.repaintParameters = _readRepaintParams(xmlCtx, _xml.getSubsection(xmlCtx, section, 'repaintParameters'))
        if (IS_CLIENT or IS_EDITOR or IS_CELLAPP or IS_BOT) and section.has_key('extras'):
            _readExtraLocals(self, (xmlCtx, 'extras'), section)
        if IS_CELLAPP:
            self.rollerExtras = [ extra for extra in self.devices if extra.isTrack and getattr(extra, 'isWheel', False) == self.isWheeledVehicle ]
            self.rollerExtras.sort(key=lambda extra: extra.name)
            if self.isWheeledVehicle:
                for chassis in self.chassis:
                    for wheel in chassis.wheels.wheels:
                        for matKind, matInfo in wheel.materials.items():
                            if matInfo.multipleExtra:
                                wheel.materials[matKind] = matInfo._replace(extra=self.extrasDict[matInfo.extra])

        if IS_CLIENT or IS_EDITOR:
            self.__checkMatchingTags()
        VehicleType.currentReadingVeh = None
        section = None
        ResMgr.purge(xmlPath, True)
        return

    def retrieveSectionToSave(self, mainXmlPath, useSharedSections=True):
        mainSection = ResMgr.openSection(mainXmlPath)
        if mainSection is None:
            _xml.raiseWrongXml(None, mainXmlPath, 'can not open or read')
        _writeCamouflageSettings(mainSection, 'camouflage', self.camouflage)
        _xml.rewriteFloat(mainSection, 'speedLimits/forward', self.speedLimits[0] * component_constants.MS_TO_KMH)
        _xml.rewriteFloat(mainSection, 'speedLimits/backward', self.speedLimits[1] * component_constants.MS_TO_KMH)
        _xml.rewriteFloat(mainSection, 'emblems/alpha', self.emblemsAlpha)
        _xml.rewriteString(mainSection, 'effects/damagedStateGroup', self.editorData.damagedStateGroup)
        sharedSections = {}
        nationID = self.id[0]
        nationName = nations.NAMES[nationID]
        if useSharedSections:
            for componentId in ITEM_TYPES.values():
                if componentId in Cache.NATION_ITEM_SOURCE:
                    compsXmlPath = '{vehcilePath}{nationName}{componentsPath}{componentSource}'.format(vehcilePath=_VEHICLE_TYPE_XML_PATH, nationName=nationName, componentsPath=Cache.NATION_COMPONENTS_SECTION, componentSource=Cache.NATION_ITEM_SOURCE[componentId])
                    section = ResMgr.openSection(compsXmlPath)
                    if section is None:
                        _xml.raiseWrongXml(None, compsXmlPath, "Can't open shared section")
                    sharedSections[componentId] = section

        _writeHulls(self.hulls, mainSection)
        _writeInstallableComponents(self.chassis, mainSection, 'chassis', _writeChassis, g_cache.chassisIDs(nationID), sharedSections)
        defHull = self.hulls[0]
        for n in xrange(len(defHull.turretPositions)):
            _writeInstallableComponents(self.turrets[n], mainSection, 'turrets' + repr(n), _writeTurret, g_cache.turretIDs(nationID), sharedSections)

        for id, section in sharedSections.items():
            section.save()

        return mainSection

    @staticmethod
    def saveCustomization():
        from items.writers import c11n_writers
        customizationCache = g_cache.customization20(False)
        if customizationCache is not None:
            c11n_writers.saveCustomizationItems(customizationCache, _CUSTOMIZATION_XML_PATH)
        return

    @property
    def userString(self):
        return self.i18nInfo.userString

    @property
    def shortUserString(self):
        return self.i18nInfo.shortString

    @property
    def description(self):
        return self.i18nInfo.description

    @property
    def shortDescriptionSpecial(self):
        return self.i18nInfo.shortDescriptionSpecial

    @property
    def longDescriptionSpecial(self):
        return self.i18nInfo.longDescriptionSpecial

    @property
    def isCustomizationLocked(self):
        return 'lockOutfit' in self.tags

    @property
    def progressionDecalsOnly(self):
        return 'lockExceptProgression' in self.tags

    @property
    def isEquipmentLocked(self):
        return 'lockEquipment' in self.tags

    @property
    def isOptionalDevicesLocked(self):
        return 'lockOptionalDevices' in self.tags

    def update(self, data):
        if json_vehicle_reader:
            json_vehicle_reader.readVehicle(self, data)
        else:
            LOG_WARNING('Json vehicle reader is not found')

    def getGuns(self):
        res = []
        for data in self.turrets:
            for turret in data:
                for gun in turret.guns:
                    res.append(gun)

        return res

    def getVehicleClass(self):
        return getVehicleClassFromVehicleType(self)

    def __getRoleFromTags(self):
        roles = g_cache.roles()
        suitableRoles = [ tag for tag in roles if ROLE_TYPE_TO_LABEL[tag] in self.tags ]
        if not suitableRoles:
            LOG_WARNING('All vehicles from levels %s must have role, vehicle: %s(CD:%s)' % (ROLE_LEVELS, self.name, self.compactDescr))
            return ROLE_TYPE.NOT_DEFINED
        if len(suitableRoles) > 1:
            raise SoftException("There are several roles for vehicle '%s': '%s'" % (self.name, suitableRoles))
        return suitableRoles[0]

    def __getActionsFromRole(self, role):
        actionsByRoles = g_cache.roles()
        return actionsByRoles.get(role, None)

    def __convertAndValidateUnlocksDescrs(self, srcList):
        nationID = self.id[0]
        destList = []
        reqItems = {}
        for descr in srcList:
            itemTypeName = descr[1]
            itemName = descr[2]
            itemID = None
            try:
                if itemTypeName == 'vehicle':
                    itemID = g_list.getIDsByName(nations.NAMES[nationID] + ':' + itemName)[1]
                if itemTypeName == 'vehicleChassis':
                    itemID = g_cache.chassisIDs(nationID)[itemName]
                if itemTypeName == 'vehicleTurret':
                    itemID = g_cache.turretIDs(nationID)[itemName]
                if itemTypeName == 'vehicleGun':
                    itemID = g_cache.gunIDs(nationID)[itemName]
                if itemTypeName == 'vehicleEngine':
                    itemID = g_cache.engineIDs(nationID)[itemName]
                if itemTypeName == 'vehicleFuelTank':
                    itemID = g_cache.fuelTankIDs(nationID)[itemName]
                if itemTypeName == 'vehicleRadio':
                    itemID = g_cache.radioIDs(nationID)[itemName]
            except Exception:
                LOG_CURRENT_EXCEPTION()
                raise SoftException("wrong name '%s' in <unlocks> of '%s'" % (itemName, self.name))

            compactDescr = makeIntCompactDescrByID(itemTypeName, nationID, itemID)
            if itemTypeName != 'vehicle' and compactDescr not in self.installableComponents:
                raise SoftException("component '%s' in <unlocks> is not for '%s'" % (itemName, self.name))
            reqItems.setdefault(compactDescr, set()).update(descr[3:])
            destList.append((descr[0], compactDescr))

        for descr in reqItems.itervalues():
            for compactDescr in tuple(descr):
                _collectReqItemsRecursively(descr, tuple(reqItems.get(compactDescr, ())), reqItems)

        for idx in xrange(len(destList)):
            descr = destList[idx]
            destList[idx] = descr + tuple(reqItems[descr[1]])

        return destList

    def __collectDefaultUnlocks(self):
        autounlocks = []
        autounlocks.append(self.chassis[0].compactDescr)
        autounlocks.append(self.engines[0].compactDescr)
        autounlocks.append(self.fuelTanks[0].compactDescr)
        autounlocks.append(self.radios[0].compactDescr)
        for posIndex, turrets in enumerate(self.turrets):
            turret = turrets[0]
            autounlocks.append(turret.compactDescr)
            autounlocks.append(turret.guns[0].compactDescr)
            if posIndex in self.hulls[0].fakeTurrets['lobby']:
                for turret in turrets[1:]:
                    autounlocks.append(turret.compactDescr)

        return autounlocks

    def __checkMatchingTags(self):
        hullsMatchingTags = set()
        for hull in self.hulls:
            hullsMatchingTags = self.____checkPartMatchingTags(hull, hullsMatchingTags)

        turretsMatchingTags = set()
        gunsMatchingTags = set()
        for turrets in self.turrets:
            for turret in turrets:
                turretsMatchingTags = self.____checkPartMatchingTags(turret, turretsMatchingTags)
                gunMatchingTags = set()
                for gun in turret.guns:
                    gunMatchingTags = self.____checkPartMatchingTags(gun, gunMatchingTags)

                gunsMatchingTags |= gunMatchingTags

        repeatingTags = hullsMatchingTags & gunsMatchingTags | hullsMatchingTags & turretsMatchingTags | gunsMatchingTags & turretsMatchingTags
        if repeatingTags:
            LOG_ERROR('repeating matching tags: {} for {}'.format(','.join(repeatingTags), self.name))

    def ____checkPartMatchingTags(self, part, partTags):
        tags = set()
        projectionDecalSlots = [ slot for slot in part.slotsAnchors if slot.type == 'projectionDecal' ]
        for slot in projectionDecalSlots:
            matchingTags = [ tag for tag in slot.tags if tag.endswith(MATCHING_TAGS_SUFFIX) ]
            if len(matchingTags) > 1:
                LOG_ERROR('several matching tags for slot ID%i' % slot.slotId)
            for tag in matchingTags:
                if tag not in tags:
                    tags.add(tag)
                LOG_ERROR('repeating matching tags: {} for {}'.format(tag, self.name))

        repeatingTags = tags & partTags
        if repeatingTags:
            LOG_ERROR('repeating matching tags: {} for {}'.format(','.join(repeatingTags), self.name))
        return tags | partTags


class SupplySlotsStorageCache(object):
    __slots__ = ('__cache',)

    def __init__(self):
        self.__cache = {}

    def getStorage(self, slotIDs):
        slotIDs = tuple(slotIDs)
        if slotIDs not in self.__cache:
            self.__cache[slotIDs] = SupplySlotsStorage(slotIDs)
        return self.__cache[slotIDs]


class SupplySlotsStorage(object):
    __slots__ = ('_slotIDs', '_slotsByType')
    ALL_IDS_KEY = -1

    def __init__(self, slotIDs):
        super(SupplySlotsStorage, self).__init__()
        self._slotIDs = slotIDs
        self._slotsByType = {}
        for slotID in slotIDs:
            slotDescr = g_cache.supplySlots().getSlotDescr(slotID)
            subType = slotDescr.getSubType()
            itemTypeStorage = self._slotsByType.setdefault(slotDescr.itemType, dict())
            itemTypeStorage.setdefault(SupplySlotsStorage.ALL_IDS_KEY, list()).append(slotID)
            if subType is not None:
                itemTypeStorage.setdefault(subType, list()).append(slotID)

        self._checkRestrictions()
        return

    def getSlotIDsByType(self, itemType, subItemType=None):
        return self._slotsByType.get(itemType, {}).get(SupplySlotsStorage.ALL_IDS_KEY, []) if subItemType is None else self._slotsByType.get(itemType, {}).get(subItemType, [])

    def getAmountForType(self, itemType, *subItemTypes):
        if len(subItemTypes) == 0:
            return len(self.getSlotIDsByType(itemType))
        res = 0
        for subType in subItemTypes:
            res += len(self.getSlotIDsByType(itemType, subType))

        return res

    def getSlotByIdxInItemType(self, itemType, inItemTypeIdx):
        slotIDs = self.getSlotIDsByType(itemType)
        return g_cache.supplySlots().getSlotDescr(slotIDs[inItemTypeIdx]) if inItemTypeIdx < len(slotIDs) else None

    @property
    def slotIDs(self):
        return self._slotIDs

    def checkLayoutCompatibility(self, itemType, itemLayout):
        slotIDs = self.getSlotIDsByType(itemType)
        if len(itemLayout) > len(slotIDs):
            return (False, 'Cannot apply layout for itemType {}, exceed allowed number of supply ({} > {})'.format(itemType, len(itemLayout), len(slotIDs)))
        else:
            for slotID, itemCompDescr in zip(slotIDs, itemLayout):
                if itemCompDescr == 0:
                    continue
                slotDescr = g_cache.supplySlots().getSlotDescr(slotID)
                res = slotDescr.checkSlotCompatibility(compDescr=itemCompDescr)
                if not res[0]:
                    return res

            return (True, None)

    def _checkRestrictions(self):
        optDevs = self.getSlotIDsByType(ITEM_TYPES.optionalDevice)
        if len(optDevs) > MAX_OPTIONAL_DEVICES_SLOTS:
            raise SoftException('Number of optional devices ({}) must be less that MAX_OPTIONAL_DEVICES_SLOTS({})'.format(len(optDevs), MAX_OPTIONAL_DEVICES_SLOTS))
        shellSlots = self.getAmountForType(ITEM_TYPES.shell)
        if shellSlots != NUM_SHELLS_SLOTS:
            raise SoftException('Number of shells ({}) must be equal to NUM_SHELLS_SLOTS({}) now'.format(shellSlots, NUM_SHELLS_SLOTS))


class Cache(object):
    __slots__ = ('__vehicles', '__commonConfig', '__chassis', '__engines', '__fuelTanks', '__radios', '__turrets', '__guns', '__shells', '__optionalDevices', '__optionalDeviceIDs', '__equipments', '__equipmentIDs', '__chassisIDs', '__engineIDs', '__fuelTankIDs', '__radioIDs', '__turretIDs', '__gunIDs', '__shellIDs', '__customization', '__playerEmblems', '__shotEffects', '__shotEffectsIndexes', '__damageStickers', '__vehicleEffects', '__gunEffects', '__gunReloadEffects', '__gunRecoilEffects', '__turretDetachmentEffects', '__customEffects', '__requestOncePrereqs', '__customization20', '__roles', '__supplySlots', '__supplySlotsStorages', '__moduleKind', '__postProgression')
    NATION_COMPONENTS_SECTION = '/components/'
    NATION_ITEM_SOURCE = {ITEM_TYPES.vehicleChassis: 'chassis.xml',
     ITEM_TYPES.vehicleEngine: 'engines.xml',
     ITEM_TYPES.vehicleFuelTank: 'fuelTanks.xml',
     ITEM_TYPES.vehicleRadio: 'radios.xml',
     ITEM_TYPES.vehicleGun: 'guns.xml',
     ITEM_TYPES.vehicleTurret: 'turrets.xml'}

    def __init__(self):
        self.__vehicles = {}
        self.__commonConfig = None
        self.__chassis = [ None for i in nations.NAMES ]
        self.__engines = [ None for i in nations.NAMES ]
        self.__fuelTanks = [ None for i in nations.NAMES ]
        self.__radios = [ None for i in nations.NAMES ]
        self.__turrets = [ None for i in nations.NAMES ]
        self.__guns = [ None for i in nations.NAMES ]
        self.__shells = [ None for i in nations.NAMES ]
        self.__optionalDevices = None
        self.__optionalDeviceIDs = None
        self.__equipments = None
        self.__equipmentIDs = None
        self.__chassisIDs = [ None for i in nations.NAMES ]
        self.__engineIDs = [ None for i in nations.NAMES ]
        self.__fuelTankIDs = [ None for i in nations.NAMES ]
        self.__radioIDs = [ None for i in nations.NAMES ]
        self.__turretIDs = [ None for i in nations.NAMES ]
        self.__gunIDs = [ None for i in nations.NAMES ]
        self.__shellIDs = [ None for i in nations.NAMES ]
        self.__customization20 = None
        self.__customization = [ None for i in nations.NAMES ]
        self.__playerEmblems = None
        self.__shotEffects = None
        self.__shotEffectsIndexes = None
        self.__damageStickers = None
        self.__roles = None
        self.__supplySlots = None
        self.__supplySlotsStorages = None
        self.__moduleKind = {}
        self.__postProgression = None
        if IS_CLIENT or IS_EDITOR:
            self.__vehicleEffects = None
            self.__gunEffects = None
            self.__gunReloadEffects = None
            self.__gunRecoilEffects = None
            self.__turretDetachmentEffects = None
            self.__customEffects = None
            self.__requestOncePrereqs = set()
        return

    @property
    def requestOncePrereqs(self):
        return self.__requestOncePrereqs

    def clearPrereqs(self):
        pass

    def vehicle(self, nationID, vehicleTypeID, vehMode=VEHICLE_MODE.DEFAULT):
        if vehMode == VEHICLE_MODE.DEFAULT:
            id = (nationID, vehicleTypeID)
        else:
            id = (nationID, vehicleTypeID, vehMode)
        vt = self.__vehicles.get(id)
        if vt:
            return vt
        nation = nations.NAMES[nationID]
        basicInfo = g_list.getList(nationID)[vehicleTypeID]
        xmlName = basicInfo.name.split(':')[1] + VEHICLE_MODE_FILE_SUFFIX[vehMode]
        xmlPath = _VEHICLE_TYPE_XML_PATH + nation + '/' + xmlName + '.xml'
        vt = VehicleType(nationID, basicInfo, xmlPath, vehMode)
        self.__vehicles[id] = vt
        return vt

    def chassis(self, nationID):
        return self.__getList(nationID, 'chassis')

    def chassisIDs(self, nationID):
        return self.__getList(nationID, 'chassisIDs')

    def engines(self, nationID):
        return self.__getList(nationID, 'engines')

    def engineIDs(self, nationID):
        return self.__getList(nationID, 'engineIDs')

    def fuelTanks(self, nationID):
        return self.__getList(nationID, 'fuelTanks')

    def fuelTankIDs(self, nationID):
        return self.__getList(nationID, 'fuelTankIDs')

    def radios(self, nationID):
        return self.__getList(nationID, 'radios')

    def radioIDs(self, nationID):
        return self.__getList(nationID, 'radioIDs')

    def turrets(self, nationID):
        return self.__getList(nationID, 'turrets')

    def turretIDs(self, nationID):
        return self.__getList(nationID, 'turretIDs')

    def guns(self, nationID):
        return self.__getList(nationID, 'guns')

    def gunIDs(self, nationID):
        return self.__getList(nationID, 'gunIDs')

    def shells(self, nationID):
        return self.__getList(nationID, 'shells')

    def shellIDs(self, nationID):
        return self.__getList(nationID, 'shellIDs')

    def customization20(self, createNew=True):
        if self.__customization20 is None and createNew:
            from items.components.c11n_components import CustomizationCache
            from items.readers.c11n_readers import readCustomizationCacheFromXml
            self.__customization20 = CustomizationCache()
            readCustomizationCacheFromXml(self.__customization20, _CUSTOMIZATION_XML_PATH)
        return self.__customization20

    def supplySlots(self):
        from items.components.supply_slots_components import SupplySlotsCache
        if self.__supplySlots is None:
            self.__supplySlots = SupplySlotsCache(_VEHICLE_TYPE_XML_PATH + 'common/supply_slot_types.xml')
        return self.__supplySlots

    def supplySlotsStorage(self):
        if self.__supplySlotsStorages is None:
            self.__supplySlotsStorages = SupplySlotsStorageCache()
        return self.__supplySlotsStorages

    def postProgression(self):
        _POST_PROGRESSION_XML_ROOT = _VEHICLE_TYPE_XML_PATH + 'common/post_progression/'
        if self.__postProgression is None:
            self.__postProgression = PostProgressionCache(_POST_PROGRESSION_XML_ROOT + 'features.xml', _POST_PROGRESSION_XML_ROOT + 'modifications.xml', _POST_PROGRESSION_XML_ROOT + 'pairs.xml', _POST_PROGRESSION_XML_ROOT + 'trees.xml')
        return self.__postProgression

    def customization(self, nationID):
        descr = self.__customization[nationID]
        if descr is None:
            nationName = nations.NAMES[nationID]
            descr = {}
            if nationName in nations.AVAILABLE_NAMES:
                commonDescr = _readCustomization(_VEHICLE_TYPE_XML_PATH + 'common/customization.xml', nationID, idsRange=(5001, 65535))
                customDescr = _readCustomization(_VEHICLE_TYPE_XML_PATH + nationName + '/customization.xml', nationID, idsRange=(1, 5000))
                descr = _joinCustomizationParams(nationID, commonDescr, customDescr)
            self.__customization[nationID] = descr
        return descr

    def playerEmblems(self):
        if IS_CLIENT:
            descr = ({}, {}, {})
            return descr
        else:
            descr = self.__playerEmblems
            if descr is None:
                descr = self.__playerEmblems = _readPlayerEmblems(_VEHICLE_TYPE_XML_PATH + 'common/player_emblems.xml')
            return descr

    def optionalDevices(self):
        descr = self.__optionalDevices
        if descr is None:
            from items import artefacts
            self.__optionalDevices, self.__optionalDeviceIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/optional_devices.xml')
            descr = self.__optionalDevices
        return descr

    def optionalDeviceIDs(self):
        descr = self.__optionalDeviceIDs
        if descr is None:
            from items import artefacts
            self.__optionalDevices, self.__optionalDeviceIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/optional_devices.xml')
            descr = self.__optionalDeviceIDs
        return descr

    def equipments(self):
        descr = self.__equipments
        if descr is None:
            from items import artefacts
            self.__equipments, self.__equipmentIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/equipments.xml')
            descr = self.__equipments
        return descr

    def equipmentIDs(self):
        descr = self.__equipmentIDs
        if descr is None:
            from items import artefacts
            self.__equipments, self.__equipmentIDs = _readArtefacts(_VEHICLE_TYPE_XML_PATH + 'common/equipments.xml')
            descr = self.__equipmentIDs
        return descr

    def roles(self):
        roles = self.__roles
        if roles is None:
            self.__roles = _readVehicleRoles(_VEHICLE_TYPE_XML_PATH + 'common/roleExp/roles.xml')
            roles = self.__roles
        return roles

    @property
    def shotEffects(self):
        descr = self.__shotEffects
        if descr is None:
            self.__shotEffectsIndexes, self.__shotEffects = _readShotEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/shot_effects.xml')
            descr = self.__shotEffects
        return descr

    @property
    def shotEffectsIndexes(self):
        descr = self.__shotEffectsIndexes
        if descr is None:
            self.__shotEffectsIndexes, self.__shotEffects = _readShotEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/shot_effects.xml')
            descr = self.__shotEffectsIndexes
        return descr

    @property
    def damageStickers(self):
        descr = self.__damageStickers
        if descr is None:
            descr = self.__damageStickers = _readDamageStickers(_VEHICLE_TYPE_XML_PATH + 'common/damage_stickers.xml')
        return descr

    @property
    def commonConfig(self):
        descr = self.__commonConfig
        if descr is None:
            commonXmlPath = _VEHICLE_TYPE_XML_PATH + 'common/vehicle.xml'
            commonXml = ResMgr.openSection(commonXmlPath)
            if commonXml is None:
                _xml.raiseWrongXml(None, commonXmlPath, 'can not open or read')
            descr = self.__commonConfig = _readCommonConfig((None, commonXmlPath), commonXml)
            commonXml = None
            ResMgr.purge(commonXmlPath, True)
        return descr

    def getGunRecoilEffects(self, effectName):
        return self._gunRecoilEffects.get(effectName, None)

    def getVehicleEffect(self, effectID):
        return self._vehicleEffects.get(effectID)

    @property
    def _vehicleEffects(self):
        if self.__vehicleEffects is None:
            self.__vehicleEffects = _readEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/vehicle_effects.xml', True)
        return self.__vehicleEffects

    @property
    def _gunEffects(self):
        if self.__gunEffects is None:
            self.__gunEffects = _readEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/gun_effects.xml')
        return self.__gunEffects

    @property
    def _gunReloadEffects(self):
        if self.__gunReloadEffects is None:
            self.__gunReloadEffects = _readReloadEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/gun_reload_effects.xml')
        return self.__gunReloadEffects

    @property
    def _gunRecoilEffects(self):
        if self.__gunRecoilEffects is None:
            self.__gunRecoilEffects = _readRecoilEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/gun_recoil_effects.xml')
        return self.__gunRecoilEffects

    @property
    def _customEffects(self):
        if self.__customEffects is None:
            self.__customEffects = dict()
            self.__customEffects['slip'] = _readCustomEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/trackSlip_effects.xml')
            self.__customEffects['exhaust'] = _readCustomEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/exhaust_effects.xml')
        return self.__customEffects

    @property
    def _turretDetachmentEffects(self):
        if self.__turretDetachmentEffects is None:
            self.__turretDetachmentEffects = _readEffectGroups(_VEHICLE_TYPE_XML_PATH + 'common/turret_effects.xml')
        return self.__turretDetachmentEffects

    def __getList(self, nationID, listName):
        nations = getattr(self, '_Cache__' + listName)
        if nations[nationID] is None:
            self.__readNation(nationID)
        return nations[nationID]

    def _readModulesLists(self, xmlPath):
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        for key in ('tankmen', 'internal', 'external'):
            self.__moduleKind[key] = _xml.readString(xmlPath, section, 'moduleKind/' + key).split()
            moduleName = self.__moduleKind[key]
            modules = set()
            for module in moduleName:
                moduleID = IDS_BY_NAMES.get(module)
                if not moduleID:
                    _xml.raiseWrongXml((_VEHICLE_TYPE_XML_PATH + 'common', 'vehicle_common.xml'), 'moduleKind/' + key, 'module is not existing in system/data/vehicle_common.xml')
                modules.add(moduleID)

            self.__moduleKind[key] = modules

        return

    @property
    def _moduleKind(self):
        if not self.__moduleKind:
            self._readModulesLists(_VEHICLE_TYPE_XML_PATH + 'common/vehicle_common.xml')
        return self.__moduleKind

    def __readNation(self, nationID):
        nationName = nations.NAMES[nationID]
        if nationName not in nations.AVAILABLE_NAMES:
            emptyDict = {}
            self.__chassis[nationID], self.__chassisIDs[nationID] = emptyDict, emptyDict
            self.__engines[nationID], self.__engineIDs[nationID] = emptyDict, emptyDict
            self.__fuelTanks[nationID], self.__fuelTankIDs[nationID] = emptyDict, emptyDict
            self.__radios[nationID], self.__radioIDs[nationID] = emptyDict, emptyDict
            self.__turrets[nationID], self.__turretIDs[nationID] = emptyDict, emptyDict
            self.__guns[nationID], self.__gunIDs[nationID] = emptyDict, emptyDict
            self.__shells[nationID], self.__shellIDs[nationID] = emptyDict, emptyDict
            return
        compsXmlPath = _VEHICLE_TYPE_XML_PATH + nationName + self.NATION_COMPONENTS_SECTION
        self.__chassis[nationID], self.__chassisIDs[nationID] = _readComponents(compsXmlPath + self.NATION_ITEM_SOURCE[ITEM_TYPES.vehicleChassis], _readChassis, nationID, ITEM_TYPES.vehicleChassis)
        self.__engines[nationID], self.__engineIDs[nationID] = _readComponents(compsXmlPath + self.NATION_ITEM_SOURCE[ITEM_TYPES.vehicleEngine], _readEngine, nationID, ITEM_TYPES.vehicleEngine)
        self.__fuelTanks[nationID], self.__fuelTankIDs[nationID] = _readComponents(compsXmlPath + self.NATION_ITEM_SOURCE[ITEM_TYPES.vehicleFuelTank], _readFuelTank, nationID, ITEM_TYPES.vehicleFuelTank)
        self.__radios[nationID], self.__radioIDs[nationID] = _readComponents(compsXmlPath + self.NATION_ITEM_SOURCE[ITEM_TYPES.vehicleRadio], _readRadio, nationID, ITEM_TYPES.vehicleRadio)
        self.__shells[nationID], self.__shellIDs[nationID] = _readShells(compsXmlPath + 'shells.xml', nationID)
        self.__guns[nationID], self.__gunIDs[nationID] = _readComponents(compsXmlPath + self.NATION_ITEM_SOURCE[ITEM_TYPES.vehicleGun], _readGun, nationID, ITEM_TYPES.vehicleGun)
        self.__turrets[nationID], self.__turretIDs[nationID] = _readComponents(compsXmlPath + self.NATION_ITEM_SOURCE[ITEM_TYPES.vehicleTurret], _readTurret, nationID, ITEM_TYPES.vehicleTurret)


class VehicleList(object):

    def __init__(self):
        self.__ids = {}
        self.__categories = {}
        typeCompDescrsByLevel = {level:[] for level in range(1, 11)}
        list = []
        for nation in nations.NAMES:
            if nation not in nations.AVAILABLE_NAMES:
                list.append({})
                continue
            xmlPath = _VEHICLE_TYPE_XML_PATH + nation + '/list.xml'
            section = ResMgr.openSection(xmlPath)
            if section is None:
                _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
            descrs = self.__readVehicleList(nation, section, xmlPath)
            list.append(descrs)
            nationID = nations.INDICES[nation]
            for d in descrs.itervalues():
                self.__categories.setdefault((nationID, (set(d.tags) & VEHICLE_CLASS_TAGS).pop(), d.level), 0)
                self.__categories[(nationID, (set(d.tags) & VEHICLE_CLASS_TAGS).pop(), d.level)] += 1

            self.__ids.update(dict(((d.name, (nationID, d.id)) for d in descrs.itervalues())))
            for descr in descrs.itervalues():
                typeCompDescrsByLevel[descr.level].append(descr.compactDescr)

            ResMgr.purge(xmlPath, True)

        self.__nations = tuple(list)
        self.__typeCompDescrsByLevel = {level:frozenset(vehTypeCompDescrs) for level, vehTypeCompDescrs in typeCompDescrsByLevel.iteritems()}
        return

    def getList(self, nationID):
        return self.__nations[nationID] if nationID < len(self.__nations) else None

    def getCategories(self, nationID=None, vehClass=None, level=None, excluded=()):
        result = copy.copy(self.__categories)
        for tcd in excluded:
            if parseIntCompactDescr(tcd)[0] != ITEM_TYPES.vehicle:
                continue
            category = (lambda vt: (vt.id[0], (set(vt.tags) & VEHICLE_CLASS_TAGS).pop(), vt.level))(getVehicleType(tcd))
            result[category] = count = result[category] - 1
            if count < 1:
                result.pop(category, None)

        return {args for args in result if (nationID is None or args[0] == nationID) and (vehClass is None or args[1] == vehClass) and (level is None or args[2] == level)}

    def getTypeCompDescrsByLevel(self, level):
        return self.__typeCompDescrsByLevel[level]

    def isVehicleExisting(self, name):
        return name in self.__ids

    def isVehicleExistingByType(self, nationID, vehicleTypeID):
        nation = self.getList(nationID)
        return nation is not None and nation.get(vehicleTypeID) is not None

    def isVehicleExistingByCD(self, vehTypeCompDescr):
        itemTypeID, nationID, innationID = parseIntCompactDescr(vehTypeCompDescr)
        return itemTypeID == items.ITEM_TYPES.vehicle and innationID in self.getList(nationID)

    def getIDsByVehName(self, name):
        for nation in nations.NAMES:
            fullName = '%s:%s' % (nation, name)
            if fullName in self.__ids:
                return self.__ids[fullName]

        raise SoftException("unknown vehicle name '%s'" % name)

    def getIDsByName(self, name):
        ids = self.__ids.get(name)
        if ids is None:
            raise SoftException("unknown vehicle type name '%s'" % name)
        return ids

    def __readVehicleList(self, nation, section, xmlPath):
        res = {}
        ids = {}
        nationID = nations.INDICES[nation]
        pricesDest = _g_prices
        if pricesDest is not None:
            if IS_CLIENT or IS_WEB:
                SELL_PRICE_FACTOR = 0.5
            else:
                from server_constants import SELL_PRICE_FACTOR
        for vname, vsection in section.items():
            if 'xmlns:xmlref' == vname or 0 == len(vsection):
                continue
            ctx = (None, xmlPath + '/' + vname)
            if vname in ids:
                _xml.raiseWrongXml(ctx, '', 'vehicle type name is not unique')
            innationID = _xml.readInt(ctx, vsection, 'id', 0, 255)
            if innationID in res:
                _xml.raiseWrongXml(ctx, 'id', 'is not unique')
            compactDescr = makeIntCompactDescrByID('vehicle', nationID, innationID)
            ids[vname] = innationID
            item = vehicle_items.VehicleItem(ITEM_TYPES['vehicle'], innationID, '{}:{}'.format(nation, vname), compactDescr, level=_readLevel(ctx, vsection))
            tags = _readTags(ctx, vsection, 'tags', 'vehicle')
            if 1 != len(tags & VEHICLE_CLASS_TAGS):
                _xml.raiseWrongXml(ctx, 'tags', 'vehicle class tag is missing or is multiple')
            if item.level == VEHICLE_LEVEL_EARN_CRYSTAL and 'earn_crystals' not in tags and len(set(tags) & MODES_WITHOUT_CRYSTAL_EARNINGS) == 0:
                _xml.raiseWrongXml(ctx, 'tags', 'vehicle %s with level %s does not have tag earn_crystals' % (vname, item.level))
            item.tags = tags
            res[innationID] = item
            if IS_CLIENT or IS_WEB:
                item.i18n = shared_readers.readUserText(vsection)
            price = _xml.readPrice(ctx, vsection, 'price')
            if 'gold' in price:
                item.tags |= frozenset(('premium',))
            if pricesDest is not None:
                pricesDest['itemPrices'][compactDescr] = price
                if vsection.readBool('notInShop', False):
                    pricesDest['notInShopItems'].add(compactDescr)
                if IS_RENTALS_ENABLED and vsection.readBool('cannotBeBought', False):
                    pricesDest['vehiclesNotToBuy'].add(compactDescr)
                sellPriceFactor = vsection.readFloat('sellPriceFactor', SELL_PRICE_FACTOR)
                if abs(sellPriceFactor - SELL_PRICE_FACTOR) > 0.001:
                    pricesDest['vehicleSellPriceFactors'][compactDescr] = sellPriceFactor
                if 'gold' in price and vsection.readBool('sellForGold', False):
                    pricesDest['vehiclesToSellForGold'].add(compactDescr)
                rentPrice = _xml.readRentPrice(ctx, vsection, 'rent') if IS_RENTALS_ENABLED else {}
                pricesDest['vehiclesRentPrices'][compactDescr] = rentPrice

        return res


def parseVehicleCompactDescr(compactDescr):
    header, vehicleTypeID = struct.unpack('2B', compactDescr[0:2])
    return (header >> 4 & 15, vehicleTypeID)


__ITEM_TYPE_VEHICLE = items.ITEM_TYPES.vehicle

def getVehicleTypeCompactDescr(compactDescr):
    nationID, vehicleTypeID = parseVehicleCompactDescr(compactDescr)
    return __ITEM_TYPE_VEHICLE + (nationID << 4) + (vehicleTypeID << 8)


def makeVehicleTypeCompDescrByName(name):
    nationID, innationID = g_list.getIDsByName(name)
    return makeIntCompactDescrByID('vehicle', nationID, innationID)


def getItemByCompactDescr(compactDescr):
    try:
        itemTypeID, nationID, compTypeID = parseIntCompactDescr(compactDescr)
        return _itemGetters[itemTypeID](nationID, compTypeID)
    except Exception:
        LOG_CURRENT_EXCEPTION()
        LOG_ERROR('(compact description to XML mismatch?)', compactDescr)
        raise


def isItemWithCompactDescrExist(compactDescr):
    try:
        itemTypeID, nationID, compTypeID = parseIntCompactDescr(compactDescr)
        return _itemGetters[itemTypeID](nationID, compTypeID) is not None
    except Exception:
        return False

    return None


_itemGetters = {ITEM_TYPES.vehicle: lambda nationID, compTypeID: g_cache.vehicle(nationID, compTypeID),
 ITEM_TYPES.shell: lambda nationID, compTypeID: g_cache.shells(nationID)[compTypeID],
 ITEM_TYPES.equipment: lambda nationID, compTypeID: g_cache.equipments()[compTypeID],
 ITEM_TYPES.optionalDevice: lambda nationID, compTypeID: g_cache.optionalDevices()[compTypeID],
 ITEM_TYPES.vehicleGun: lambda nationID, compTypeID: g_cache.guns(nationID)[compTypeID],
 ITEM_TYPES.vehicleTurret: lambda nationID, compTypeID: g_cache.turrets(nationID)[compTypeID],
 ITEM_TYPES.vehicleEngine: lambda nationID, compTypeID: g_cache.engines(nationID)[compTypeID],
 ITEM_TYPES.vehicleRadio: lambda nationID, compTypeID: g_cache.radios(nationID)[compTypeID],
 ITEM_TYPES.vehicleChassis: lambda nationID, compTypeID: g_cache.chassis(nationID)[compTypeID],
 ITEM_TYPES.vehicleFuelTank: lambda nationID, compTypeID: g_cache.fuelTanks(nationID)[compTypeID],
 ITEM_TYPES.customizationItem: lambda cType, compTypeID: g_cache.customization20().itemTypes[cType][compTypeID],
 ITEM_TYPES.slot: lambda _, compTypeID: g_cache.supplySlots().getSlotDescr(compTypeID)}
VEHICLE_ITEM_TYPES = _itemGetters.keys()

def isVehicleTypeCompactDescr(vehDescr):
    cdType = type(vehDescr)
    return True if cdType is int or cdType is long else False


def getEquipmentByName(name):
    eqID = g_cache.equipmentIDs()[name]
    return g_cache.equipments()[eqID]


def getOptionalDeviceByName(name):
    optDevID = g_cache.optionalDeviceIDs()[name]
    return g_cache.optionalDevices()[optDevID]


def getVehicleType(compactDescr):
    if isVehicleTypeCompactDescr(compactDescr):
        nationID = compactDescr >> 4 & 15
        vehicleTypeID = compactDescr >> 8 & 65535
    else:
        header, vehicleTypeID = struct.unpack('2B', compactDescr[0:2])
        nationID = header >> 4 & 15
    return g_cache.vehicle(nationID, vehicleTypeID)


def getVehicleClass(compactDescr):
    return getVehicleClassFromVehicleType(getVehicleType(compactDescr))


def getVehicleClassFromVehicleType(vehicleType):
    for vehClass in VEHICLE_CLASS_TAGS & vehicleType.tags:
        return vehClass


def makeCompactDescrBy(*args, **kwargs):
    if 'intCD' in kwargs:
        vehDescr = VehicleDescr(typeID=parseIntCompactDescr(kwargs['intCD'])[1:])
    else:
        vehDescr = VehicleDescr(**kwargs)
    return vehDescr.makeCompactDescr()


def stripCustomizationFromVehicleCompactDescr(compactDescr, stripEmblems=True, stripInscriptions=True, stripCamouflages=True, keepInfinite=False):
    type, components, optionalDevicesSlots, optionalDevices, enhancements, emblemSlots, emblems, inscriptions, camouflages = _splitVehicleCompactDescr(compactDescr)
    resEmblems = {}
    if stripEmblems and emblems:
        remainedEmblems = ''
        for pos in _RANGE_4:
            if emblemSlots & 1 << pos:
                emblemInfo = _unpackIDAndDuration(emblems[:6])
                if keepInfinite and emblemInfo[2] == 0:
                    remainedEmblems += emblems[:6]
                else:
                    resEmblems[pos] = emblemInfo
                    emblemSlots &= ~(1 << pos)
                emblems = emblems[6:]

        emblems = remainedEmblems
    resInscrs = {}
    if stripInscriptions and inscriptions:
        remainedInscriptions = ''
        for pos in _RANGE_4:
            if emblemSlots & 1 << pos + 4:
                inscrInfo = _unpackIDAndDuration(inscriptions[:6]) + (ord(inscriptions[6]),)
                if keepInfinite and inscrInfo[2] == 0:
                    remainedInscriptions += inscriptions[:7]
                else:
                    resInscrs[pos] = inscrInfo
                    emblemSlots &= ~(1 << pos + 4)
                inscriptions = inscriptions[7:]

        inscriptions = remainedInscriptions
    resCams = {}
    if stripCamouflages and camouflages:
        remainedCamouflages = ''
        pos = 0
        while camouflages:
            camInfo = _unpackIDAndDuration(camouflages[:6])
            if keepInfinite and camInfo[2] == 0:
                remainedCamouflages += camouflages[:6]
            else:
                resCams[pos] = camInfo
            camouflages = camouflages[6:]
            pos += 1

        camouflages = remainedCamouflages
    compactDescr = _combineVehicleCompactDescr(type, components, optionalDevicesSlots, optionalDevices, enhancements, emblemSlots, emblems, inscriptions, camouflages)
    return (compactDescr,
     resEmblems,
     resInscrs,
     resCams)


def stripPrivateInfoFromVehicleCompactDescr(compactDescr):
    type, components, optionalDevicesSlots, optionalDevices, enhancements, emblemSlots, emblems, inscriptions, camouflages = _splitVehicleCompactDescr(compactDescr)
    optionalDevices = ''
    optionalDevicesSlots = 0
    enhancements = ''
    compactDescr = _combineVehicleCompactDescr(type, components, optionalDevicesSlots, optionalDevices, enhancements, emblemSlots, emblems, inscriptions, camouflages)
    return compactDescr


def stripOptionalDeviceFromVehicleCompactDescr(compactDescr):
    vehType, components, optionalDevicesSlots, optionalDevices, enhancements, emblemSlots, emblems, inscriptions, camouflages = _splitVehicleCompactDescr(compactDescr)
    optionalDevices = ''
    optionalDevicesSlots = 0
    return _combineVehicleCompactDescr(vehType, components, optionalDevicesSlots, optionalDevices, enhancements, emblemSlots, emblems, inscriptions, camouflages)


def isShellSuitableForGun(shellCompactDescr, gunDescr):
    itemTypeID, nationID, shellTypeID = parseIntCompactDescr(shellCompactDescr)
    shellID = (nationID, shellTypeID)
    for shotDescr in gunDescr.shots:
        if shotDescr.shell.id == shellID:
            return True

    return False


def getEmptyAmmoForGun(gunDescr):
    ammo = []
    for shot in gunDescr.shots:
        ammo.append(shot.shell.compactDescr)
        ammo.append(0)

    if not ammo:
        ammo.append(gunDescr.shots[0].shell.compactDescr)
        ammo.append(0)
    return ammo


def getDefaultAmmoForGun(gunDescr):
    return _getAmmoForGun(gunDescr, None)


def getUniformAmmoForGun(gunDescr):
    shots = len(gunDescr.shots)
    defaultPortion = 1.0 / shots if shots else 1.0
    return _getAmmoForGun(gunDescr, defaultPortion)


def getSpecificAmmoForGun(gunDescr, ammoProperties):
    ammo = []
    usedShellKinds = set()
    maxCount = gunDescr.maxAmmo
    for shot in gunDescr.shots:
        shellKind = shot.shell.kind
        percentage = ammoProperties.get(shellKind, None)
        if percentage is not None and shellKind not in usedShellKinds:
            ammo.append(shot.shell.compactDescr)
            ammo.append(int(percentage * maxCount))
            usedShellKinds.add(shellKind)

    return ammo


def calculateCarryingTriangles(carryingPoint):
    v = carryingPoint
    topLeft = Vector2(-v.x, v.y)
    bottomLeft = Vector2(-v.x, -v.y)
    topRight = Vector2(v.x, v.y)
    bottomRight = Vector2(v.x, -v.y)
    return (((topLeft + bottomLeft) / 2.0, topRight, bottomRight), ((topRight + bottomRight) / 2.0, bottomLeft, topLeft))


def _getAmmoForGun(gunDescr, defaultPortion=None):
    ammo = []
    maxCount = gunDescr.maxAmmo
    clipSize = gunDescr.clip[0]
    currCount = 0
    for shot in gunDescr.shots:
        if defaultPortion is None:
            portion = shot.defaultPortion
        else:
            portion = defaultPortion
        shotCount = int(portion * maxCount / clipSize + 0.5) * clipSize
        if currCount + shotCount > maxCount:
            shotCount = maxCount - currCount
        currCount += shotCount
        ammo.append(shot.shell.compactDescr)
        ammo.append(shotCount)

    return ammo


def getBuiltinEqsForVehicle(vehType):
    result = []
    for eqName in vehType.builtins:
        eq = getEquipmentByName(eqName)
        result.append(eq.compactDescr)

    return sorted(result)


def getUnlocksSources():
    res = {}
    for nationID in xrange(len(nations.NAMES)):
        for vehicleTypeID in g_list.getList(nationID).iterkeys():
            vehicleType = g_cache.vehicle(nationID, vehicleTypeID)
            for descr in vehicleType.unlocksDescrs:
                cd = descr[1]
                res.setdefault(cd, set()).add(vehicleType)

    return res


def getRolesActions():
    return g_cache.roles()


def getActionsByRole(role):
    actionsByRoles = getRolesActions()
    if role in actionsByRoles:
        return actionsByRoles[role]
    LOG_ERROR("actionsByRoles doesn't contain role={}".format(role))


def isRestorable(vehTypeCD, gameParams):
    if vehTypeCD in gameParams['items']['vehiclesToSellForGold']:
        return False
    vehicleTags = getVehicleType(vehTypeCD).tags
    for tag in ('unrecoverable', CollectorVehicleConsts.COLLECTOR_VEHICLES_TAG):
        if bool(tag in vehicleTags):
            return False

    isPremium = bool('premium' in vehicleTags)
    notInShop = bool(vehTypeCD in gameParams['items']['notInShopItems'])
    return isPremium or notInShop


def hasAnyOfTags(vehTypeCD, tags=()):
    vehicleType = getVehicleType(vehTypeCD)
    return bool(vehicleType.tags.intersection(tags))


def _readComponents(xmlPath, reader, nationID, itemTypeID):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    descrs = {}
    ids = {}
    for name in _xml.getSubsection(xmlCtx, section, 'ids').keys():
        name = intern(name)
        componentID = _xml.readInt(xmlCtx, section, 'ids/' + name, 0, 65535)
        if componentID in descrs:
            _xml.raiseWrongXml(xmlCtx, 'ids/' + name, 'name or ID is not unique')
        ids[name] = componentID
        descrs[componentID] = vehicle_items.createInstallableItem(itemTypeID, nationID, componentID, name)

    for name, subsection in _xml.getChildren(xmlCtx, section, 'shared'):
        ctx = (xmlCtx, 'shared')
        if name not in ids:
            _xml.raiseWrongXml(ctx, name, 'unknown name')
        descr = descrs[ids[name]]
        if descr.status != _ITEM_STATUS.EMPTY:
            _xml.raiseWrongXml(ctx, name, 'already defined')
        reader((ctx, name), subsection, descr)
        descr.status = _ITEM_STATUS.SHARED

    ResMgr.purge(xmlPath, True)
    return (descrs, ids)


def _readInstallableComponents(xmlCtx, section, subsectionName, nationID, reader, localReader, cachedDescrs, cachedIDs, unlocksDescrs, parentItem=None, **kwargs):
    res = []
    for sname, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        ctx = (xmlCtx, subsectionName + '/' + sname)
        id = cachedIDs.get(sname)
        if id is None:
            _xml.raiseWrongXml(ctx, '', 'unknown name')
        descr = cachedDescrs[id]
        if VehicleType.currentReadingVeh.mode == VEHICLE_MODE.DEFAULT:
            if subsection.asString == 'shared':
                if descr.status != _ITEM_STATUS.SHARED:
                    _xml.raiseWrongXml(ctx, sname, 'the component is not shared')
                res.append(localReader(ctx, subsection, descr, unlocksDescrs, parentItem, **kwargs))
            else:
                if descr.status != _ITEM_STATUS.EMPTY:
                    if IS_EDITOR:
                        descr = descr.copy()
                    else:
                        _xml.raiseWrongXml(ctx, '', 'the component is already defined somewhere')
                descr.status = _ITEM_STATUS.LOCAL
                reader(ctx, subsection, descr, unlocksDescrs, parentItem, **kwargs)
                res.append(descr)
        if descr.status == _ITEM_STATUS.SHARED:
            res.append(localReader(ctx, subsection, descr, unlocksDescrs, parentItem, **kwargs))
        modeDescr = descr.copy()
        modeDescr.status = _ITEM_STATUS.LOCAL
        reader(ctx, subsection, modeDescr, unlocksDescrs, parentItem, **kwargs)
        res.append(modeDescr)

    if not res:
        _xml.raiseWrongXml(xmlCtx, subsectionName, 'should be at least one subsection')
    return tuple(res)


def _writeInstallableComponents(components, section, subsectionName, writer, cachedIDs, sharedSections, **kwargs):
    cachedNames = {id:name for name, id in cachedIDs.iteritems()}
    for component in components:
        item_type_id, nation_id, item_id_within_nation = parseIntCompactDescr(component.compactDescr)
        componentName = cachedNames[item_id_within_nation]
        sharedComponentSection = None
        if sharedSections:
            sharedSection = sharedSections[item_type_id]
            sharedComponentSection = sharedSection['shared/{}'.format(componentName)]
        mainComponentSection = section['{}/{}'.format(subsectionName, componentName)]
        if mainComponentSection is None:
            _xml.raiseWrongXml(None, subsectionName, 'can not open main components section')
            return
        sectionsToWrite = [mainComponentSection]
        if sharedComponentSection:
            sectionsToWrite.append(sharedComponentSection)
        combinedSection = CombinedDataSection(sectionsToWrite)
        writer(component, combinedSection, sharedSections)

    return


def _writeMultiGun(item, section):
    multiGunSection = section['multiGun']
    if multiGunSection is None or item.multiGun is None:
        return
    else:
        children = multiGunSection.values()
        index = 0
        for child in children:
            value = item.multiGun[index]
            _xml.rewriteVector3(child, 'position', value.position)
            _xml.rewriteVector3(child, 'shotOffset', value.shotOffset)
            index += 1

        return


def _readLevel(xmlCtx, section):
    level = section.readInt('level', 1)
    if not 1 <= level <= 10:
        _xml.raiseWrongSection(xmlCtx, 'level')
    return level


def _readIGRType(xmlCtx, section):
    igrType = section.readInt('igrType', IGR_TYPE.NONE)
    if not IGR_TYPE.NONE <= igrType <= IGR_TYPE.PREMIUM:
        _xml.raiseWrongSection(xmlCtx, 'igrType')
    return igrType


def _readNations(xmlCtx, section):
    if not section.has_key('nations'):
        return
    else:
        values = section.readString('nations').split()
        result = []
        for nation in values:
            index = nations.INDICES.get(nation, None)
            if index is None:
                _xml.raiseWrongSection(xmlCtx, 'nations')
            result.append(index)

        return tuple(result)


def _readFakeGearBox(xmlCtx, section):
    res = {'fwdgears': {'switchSpeed': (2, 5, 15),
                  'switchHysteresis': (1, 2, 3),
                  'lowRpm': (0.2, 0.2, 0.2),
                  'highRpm': (0.9, 0.9, 0.9)},
     'bkwdgears': {'switchSpeed': (2, 5, 15),
                   'switchHysteresis': (1, 2, 3),
                   'lowRpm': (0.2, 0.2, 0.2),
                   'highRpm': (0.9, 0.9, 0.9)}}
    fakeGeadBoxSection = section['fakegearbox']
    if fakeGeadBoxSection is None:
        return res
    else:
        fwdGears = dict()
        fwdGearsSection = fakeGeadBoxSection['fwdgears']
        fwdGears['switchSpeed'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, fwdGearsSection, 'switchSpeed')
        fwdGears['switchHysteresis'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, fwdGearsSection, 'switchHysteresis')
        fwdGears['lowRpm'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, fwdGearsSection, 'lowRpm')
        fwdGears['highRpm'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, fwdGearsSection, 'highRpm')
        bkwdGears = dict()
        bkwdGearsSection = fakeGeadBoxSection['bkwdgears']
        bkwdGears['switchSpeed'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, bkwdGearsSection, 'switchSpeed')
        bkwdGears['switchHysteresis'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, bkwdGearsSection, 'switchHysteresis')
        bkwdGears['lowRpm'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, bkwdGearsSection, 'lowRpm')
        bkwdGears['highRpm'] = _xml.readTupleOfNonNegativeFloats(xmlCtx, bkwdGearsSection, 'highRpm')
        if not len(fwdGears['switchSpeed']) == len(fwdGears['switchHysteresis']) == len(fwdGears['lowRpm']) == len(fwdGears['highRpm']):
            _xml.raiseWrongSection(xmlCtx, 'fwdGears')
        if not len(bkwdGears['switchSpeed']) == len(bkwdGears['switchHysteresis']) == len(bkwdGears['lowRpm']) == len(bkwdGears['highRpm']):
            _xml.raiseWrongSection(xmlCtx, 'bkwdGears')
        res['fwdgears'] = fwdGears
        res['bkwdgears'] = bkwdGears
        return res


def _readHull(xmlCtx, section):
    item = vehicle_items.Hull()
    item.hitTesterManager = _readHitTester(xmlCtx, section, 'hitTester')
    item.materials = _readArmor(xmlCtx, section, 'armor')
    item.weight = _xml.readNonNegativeFloat(xmlCtx, section, 'weight')
    item.maxHealth = _xml.readInt(xmlCtx, section, 'maxHealth', 1)
    item.ammoBayHealth = shared_readers.readDeviceHealthParams(xmlCtx, section, 'ammoBayHealth', False)
    item.customizableVehicleAreas = _readCustomizableAreas(xmlCtx, section, 'customization')
    if not IS_CLIENT and not IS_BOT:
        item.armorHomogenization = _xml.readPositiveFloat(xmlCtx, section, 'armorHomogenization')
    v = []
    for s in _xml.getSubsection(xmlCtx, section, 'turretPositions').values():
        v.append(_xml.readVector3((xmlCtx, 'turretPositions'), s, ''))

    if not v:
        _xml.raiseWrongSection(xmlCtx, 'turretPositions')
    item.turretPositions = tuple(v)
    numTurrets = len(item.turretPositions)
    item.turretPitches = __readTurretPitches(xmlCtx, section, numTurrets)
    if IS_CLIENT or IS_EDITOR:
        item.turretHardPoints = __readTurretHardPoints(section, numTurrets)
    if numTurrets == 1:
        item.variantMatch = component_constants.DEFAULT_HULL_VARIANT_MATCH
    else:
        item.variantMatch = (None,) * (1 + numTurrets)
    if not section.has_key('fakeTurrets'):
        item.fakeTurrets = component_constants.DEFAULT_FAKE_TURRETS
    else:
        item.fakeTurrets = {'lobby': _readFakeTurretIndices(xmlCtx, section, 'fakeTurrets/lobby', numTurrets),
         'battle': _readFakeTurretIndices(xmlCtx, section, 'fakeTurrets/battle', numTurrets)}
    if IS_CLIENT or IS_EDITOR or IS_BOT or IS_BASEAPP:
        if section.has_key('emblemSlots'):
            if not IS_BASEAPP:
                item.emblemSlots, item.slotsAnchors = shared_readers.readEmblemSlots(xmlCtx, section, 'emblemSlots')
        elif section.has_key('customizationSlots'):
            item.emblemSlots, item.slotsAnchors = shared_readers.readCustomizationSlots(xmlCtx, section, 'customizationSlots')
    if IS_CLIENT or IS_EDITOR:
        item.modelsSets = shared_readers.readModelsSets(xmlCtx, section, 'models')
        item.models = item.modelsSets['default']
        item.swinging = shared_readers.readSwingingSettings(xmlCtx, section, g_cache)
        item.customEffects = (__readExhaustEffect(xmlCtx, section),)
        item.AODecals = _readAODecals(xmlCtx, section, 'AODecals')
        if section.has_key('camouflage'):
            item.camouflage = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=shared_components.DEFAULT_CAMOUFLAGE)
        if section.has_key('hangarShadowTexture'):
            item.hangarShadowTexture = _xml.readString(xmlCtx, section, 'hangarShadowTexture')
        else:
            item.hangarShadowTexture = None
        item.burnoutAnimation = __readBurnoutAnimation(xmlCtx, section)
    if IS_CLIENT or IS_EDITOR or IS_WEB or IS_CELLAPP:
        item.primaryArmor = _readPrimaryArmor(xmlCtx, section, 'primaryArmor', item.materials)
    return item


def _writeHulls(hulls, section):
    section = _xml.getSubsection(None, section, 'hull')
    item = hulls[0]
    _writeHitTester(item.hitTesterManager, None, section, 'hitTester')
    _writeArmor(item.materials, None, section, 'armor')
    _xml.rewriteFloat(section, 'weight', item.weight)
    _xml.rewriteInt(section, 'maxHealth', item.maxHealth)
    __writeTurretPitches(section, item.turretPitches)
    _writeCamouflageSettings(section, 'camouflage', item.camouflage)
    slots = item.emblemSlots + item.slotsAnchors
    shared_writers.writeCustomizationSlots(slots, section, 'customizationSlots')
    shared_writers.writeModelsSets(item.modelsSets, section['models'])
    shared_writers.writeSwingingSettings(item.swinging, section['swinging'])
    __writeExhaustEffect(item.customEffects[0], section)
    _xml.rewriteString(section, 'hangarShadowTexture', item.hangarShadowTexture)
    _writeCustomizableAreas(item.customizableVehicleAreas, section)
    _writeHullVariants(hulls, section)
    return


def __readExhaustEffect(xmlCtx, section):
    effectDescriptors = {}
    effectDescriptors['default'] = CustomEffectsDescriptor.getDescriptor(section, g_cache._customEffects['exhaust'], xmlCtx, 'exhaust/pixie')
    tagsSection = _xml.getSubsection(xmlCtx, section, 'exhaust/tags', False)
    if tagsSection:
        for key in tagsSection.keys():
            effectDescriptors[key] = CustomEffectsDescriptor.getDescriptor(tagsSection, g_cache._customEffects['exhaust'], xmlCtx, key)

    effect = ExhaustEffectDescriptor(section, xmlCtx, effectDescriptors, 'exhaust/nodes')
    return effect


def __writeExhaustEffect(effect, section):
    effectDescriptors = effect._ExhaustEffectDescriptor__descriptors
    defaultEffect = effectDescriptors['default']
    effectName = None
    for name, effect in g_cache._customEffects['exhaust'].iteritems():
        if defaultEffect == effect:
            effectName = name
            break

    _xml.rewriteString(section, 'exhaust/pixie', effectName)
    return


BurnoutAnimationConfig = namedtuple('BurnoutAnimationConfig', ('accumImpulseMag', 'dischargeImpulseMag', 'timeToAccumImpulse'))

def __readBurnoutAnimation(xmlCtx, section):
    burnoutSection = _xml.getSubsection(xmlCtx, section, 'burnoutAnimation', False)
    if burnoutSection is None:
        return
    else:
        accumImpulseMag = _xml.readFloat(xmlCtx, burnoutSection, 'accumulationImpulse')
        dischargeImpulseMag = _xml.readFloat(xmlCtx, burnoutSection, 'dischargeImpulse')
        timeToAccumImpulse = _xml.readFloat(xmlCtx, burnoutSection, 'timeToAccumulationImpulse')
        return BurnoutAnimationConfig(accumImpulseMag, dischargeImpulseMag, timeToAccumImpulse)


def __readTurretPitches(xmlCtx, section, numTurrets):
    if not section.has_key('turretPitches'):
        return [0.0] * numTurrets
    values = []
    for s in _xml.getSubsection(xmlCtx, section, 'turretPitches').values():
        values.append(radians(_xml.readFloat((xmlCtx, 'turretPitches'), s, '')))

    result = tuple(values)
    return result


def __writeTurretPitches(section, pitches):
    with _xml.ListRewriter(section, 'turretPitches/turret') as listRewriter:
        for pitch, child in zip(pitches, listRewriter):
            child.writeFloat('', degrees(pitch))


def __readTurretHardPoints(section, numTurrets):
    thpSection = section['turretHardPoints']
    defaultJointHP = intern('HP_turretJoint')
    resultSeq = None
    if thpSection is None:
        resultSeq = (defaultJointHP for x in xrange(numTurrets))
    else:
        resultSeq = (intern(node.asString) for node in thpSection.values())
    result = tuple(resultSeq)
    return result


def _readHullVariants(xmlCtx, section, defHull, chassis, turrets):
    res = []
    numTurrets = len(defHull.turretPositions)
    for variantName, section in section.items():
        ctx = (xmlCtx, variantName)
        for prevVariant in res:
            if prevVariant.variantName == variantName:
                _xml.raiseWrongXml(xmlCtx, variantName, 'duplicate variant name')

        variantBase = defHull
        if section.has_key('base'):
            variantBaseName = section['base'].asString
            for prevVariant in res:
                if prevVariant.variantName == variantBaseName:
                    variantBase = prevVariant
                    break
            else:
                _xml.raiseWrongXml(ctx, 'base', 'unknown hull variant name "%s"' % variantBaseName)

        variant = variantBase.copy()
        variant.variantName = variantName
        variantMatch = variant.variantMatch = [None] * (1 + numTurrets)
        res.append(variant)
        isNonEmptyMatch = False
        for name in section.keys():
            if name == 'base':
                continue
            if name == 'models':
                variant.modelsSets = shared_readers.readModelsSets(ctx, section, 'models')
                variant.models = variant.modelsSets['default']
                continue
            if name == 'exhaust':
                if IS_CLIENT:
                    variant.customEffects = (__readExhaustEffect(ctx, section),)
                continue
            if name == 'hitTester':
                variant.hitTesterManager = _readHitTester(ctx, section, 'hitTester')
                continue
            if name == 'armor':
                variant.materials = _readArmor(ctx, section, 'armor')
                continue
            if name == 'primaryArmor':
                if IS_CLIENT:
                    variant.primaryArmor = _readPrimaryArmor(ctx, section, 'primaryArmor', variant.materials)
                continue
            if name == 'armorHomogenization':
                if not IS_CLIENT and not IS_BOT:
                    variant.armorHomogenization = _xml.readPositiveFloat(ctx, section, 'armorHomogenization')
                continue
            if name == 'weight':
                variant.weight = _xml.readNonNegativeFloat(ctx, section, 'weight')
                continue
            if name == 'maxHealth':
                variant.maxHealth = _xml.readInt(ctx, section, 'maxHealth', 1)
                continue
            if name == 'ammoBayHealth':
                variant.ammoBayHealth = shared_readers.readDeviceHealthParams(ctx, section, 'ammoBayHealth', False)
                continue
            if name == 'turretPositions':
                v = []
                for s in _xml.getSubsection(ctx, section, 'turretPositions').values():
                    v.append(_xml.readVector3((ctx, 'turretPositions'), s, ''))

                if len(v) != numTurrets:
                    _xml.raiseWrongSection(ctx, 'turretPositions')
                variant.turretPositions = tuple(v)
                continue
            if name == 'turretHardPoints':
                if IS_CLIENT or IS_EDITOR:
                    variant.turretHardPoints = __readTurretHardPoints(section, numTurrets)
                continue
            if name == 'emblemSlots':
                if IS_CLIENT or IS_EDITOR:
                    variant.emblemSlots, variant.slotsAnchors = shared_readers.readEmblemSlots(xmlCtx, section, 'emblemSlots')
                continue
            if name == 'customizationSlots':
                if IS_CLIENT or IS_EDITOR or IS_BOT or IS_BASEAPP:
                    variant.emblemSlots, variant.slotsAnchors = shared_readers.readCustomizationSlots(xmlCtx, section, 'customizationSlots')
                continue
            if name == 'camouflage':
                if IS_CLIENT or IS_EDITOR:
                    variant.camouflage = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=shared_components.DEFAULT_CAMOUFLAGE)
                continue
            if name == 'chassis':
                if variantMatch[0] is not None:
                    _xml.raiseWrongXml(ctx, 'chassis', 'duplicate attr "chassis"')
                itemName = section['chassis'].asString
                for descr in chassis:
                    if descr.name == itemName:
                        variantMatch[0] = descr.id[1]
                        isNonEmptyMatch = True
                        break
                else:
                    _xml.raiseWrongXml(ctx, 'chassis', 'unknown chassis "%s"' % itemName)

                continue
            if name.startswith('turret'):
                turretIndex = -1
                try:
                    turretIndex = int(name[len('turret'):])
                except:
                    pass

                if not 0 <= turretIndex < numTurrets:
                    _xml.raiseWrongXml(ctx, name, 'unsupported parameter')
                if variantMatch[1 + turretIndex] is not None:
                    _xml.raiseWrongXml(ctx, name, 'duplicate attr "%s"' % name)
                itemName = section[name].asString
                for descr in turrets[turretIndex]:
                    if descr.name == itemName:
                        variantMatch[1 + turretIndex] = descr.id[1]
                        isNonEmptyMatch = True
                        break
                else:
                    _xml.raiseWrongXml(ctx, name, 'unknown turret "%s"' % itemName)

                continue
            _xml.raiseWrongXml(ctx, name, 'unsupported parameter')

        if not isNonEmptyMatch:
            _xml.raiseWrongXml(xmlCtx, variantName, 'no chassis or turret match specified')

    return tuple(res)


def _writeHullVariants(hulls, section):
    if len(hulls) < 2:
        return
    else:
        section = _xml.getSubsection(None, section, 'variants')
        defHull = hulls[0]
        for i in range(1, len(hulls)):
            hull = hulls[i]
            subsectionName = hull.variantName
            subsection = _xml.getSubsection(None, section, subsectionName)
            if hull.models == defHull.models:
                subsection.deleteSection('models')
            else:
                shared_writers.writeModelsSets(hull.modelsSets, subsection['models'])
            if hull.hitTesterManager == defHull.hitTesterManager:
                subsection.deleteSection('hitTester')
            else:
                _writeHitTester(hull.hitTesterManager, None, subsection, 'hitTester')
            slots = hull.emblemSlots + hull.slotsAnchors
            defSlots = defHull.emblemSlots + defHull.slotsAnchors
            shared_writers.writeCustomizationSlots(slots if slots != defSlots else None, subsection, 'customizationSlots')
            _xml.rewriteFloat(subsection, 'weight', hull.weight, defHull.weight)

        return


def _readChassis(xmlCtx, section, item, unlocksDescrs=None, _=None):
    item.tags = _readTags(xmlCtx, section, 'tags', 'vehicleChassis')
    item.level = _readLevel(xmlCtx, section)
    item.hullPosition = _xml.readVector3(xmlCtx, section, 'hullPosition')
    item.hitTesterManager = _readHitTester(xmlCtx, section, 'hitTester')
    item.topRightCarryingPoint = _xml.readPositiveVector2(xmlCtx, section, 'topRightCarryingPoint')
    item.navmeshGirth = _xml.readPositiveFloat(xmlCtx, section, 'navmeshGirth')
    item.minPlaneNormalY = cos(radians(_xml.readPositiveFloat(xmlCtx, section, 'maxClimbAngle')))
    item.materials = _readArmor(xmlCtx, section, 'armor', optional=True)
    item.weight = _xml.readPositiveFloat(xmlCtx, section, 'weight')
    item.maxLoad = _xml.readPositiveFloat(xmlCtx, section, 'maxLoad')
    item.specificFriction = component_constants.DEFAULT_SPECIFIC_FRICTION
    item.rotationSpeed = radians(_xml.readPositiveFloat(xmlCtx, section, 'rotationSpeed'))
    item.rotationIsAroundCenter = _xml.readBool(xmlCtx, section, 'rotationIsAroundCenter')
    item.customizableVehicleAreas = _readCustomizableAreas(xmlCtx, section, 'customization')
    if section.has_key('rotationSpeedLimit'):
        item.rotationSpeedLimit = radians(_xml.readPositiveFloat(xmlCtx, section, 'rotationSpeedLimit'))
    item.shotDispersionFactors = (_xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionFactors/vehicleMovement') / component_constants.KMH_TO_MS, degrees(_xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionFactors/vehicleRotation')))
    v = _xml.readVector3(xmlCtx, section, 'terrainResistance').tuple()
    if not 0.0 < v[0] <= v[1] <= v[2]:
        _xml.raiseWrongSection(xmlCtx, 'terrainResistance')
    item.terrainResistance = v
    if not IS_CLIENT and not IS_BOT:
        item.armorHomogenization = component_constants.DEFAULT_ARMOR_HOMOGENIZATION
        item.bulkHealthFactor = _xml.readPositiveFloat(xmlCtx, section, 'bulkHealthFactor')
    item.healthParams = shared_readers.readDeviceHealthParams(xmlCtx, section)
    if IS_CLIENT or IS_EDITOR or IS_BOT or IS_BASEAPP:
        if section.has_key('emblemSlots'):
            if not IS_BASEAPP:
                item.emblemSlots, item.slotsAnchors = shared_readers.readEmblemSlots(xmlCtx, section, 'emblemSlots')
        elif section.has_key('customizationSlots'):
            item.emblemSlots, item.slotsAnchors = shared_readers.readCustomizationSlots(xmlCtx, section, 'customizationSlots')
    if section.has_key('wheelsHealth'):
        for name, subsection in section['wheelsHealth'].items():
            subctx = ((xmlCtx, 'wheelsHealth'), name)
            wheelNumber = int(name[-2:]) if name[-2:].isdigit() else int(name[-1])
            item.wheelHealthParams[wheelNumber] = shared_readers.readDeviceHealthParams(subctx, subsection)

    if IS_CLIENT or IS_EDITOR or IS_CELLAPP or IS_WEB or IS_BOT:
        item.carryingTriangles = calculateCarryingTriangles(item.topRightCarryingPoint)
    if IS_CLIENT or IS_EDITOR or IS_CELLAPP:
        drivingWheelNames = section.readString('drivingWheels').split()
        if len(drivingWheelNames) != 2:
            _xml.raiseWrongSection(xmlCtx, 'drivingWheels')
        if IS_EDITOR and hasattr(item, 'editorData'):
            item.editorData.frontDrivingWheelName = drivingWheelNames[0]
            item.editorData.rearDrivingWheelName = drivingWheelNames[1]
        frontWheelSize = None
        rearWheelSize = None
        if (IS_CLIENT or IS_EDITOR) and _xml.readBool(xmlCtx, section, 'wheels/generalWheels', False):
            item.generalWheelsAnimatorConfig = Vehicular.GeneralWheelsAnimatorConfig(section)
            radius = item.generalWheelsAnimatorConfig.getRadius(drivingWheelNames[0])
            frontWheelSize = radius * WHEEL_SIZE_COEF
            radius = item.generalWheelsAnimatorConfig.getRadius(drivingWheelNames[1])
            rearWheelSize = radius * WHEEL_SIZE_COEF
        if frontWheelSize is None or IS_EDITOR:
            wheelGroups, wheels = chassis_readers.readWheelsAndGroups(xmlCtx, section)
            for wheel in wheels:
                if wheel.nodeName == drivingWheelNames[0]:
                    frontWheelSize = wheel.radius * WHEEL_SIZE_COEF
                if wheel.nodeName == drivingWheelNames[1]:
                    rearWheelSize = wheel.radius * WHEEL_SIZE_COEF
                if frontWheelSize is not None and rearWheelSize is not None:
                    break
            else:
                _xml.raiseWrongXml(xmlCtx, 'drivingWheels', 'unknown wheel name(s)')

            item.wheels = chassis_components.WheelsConfig(wheelGroups, wheels)
        if IS_CLIENT:
            _, wheels = chassis_readers.readWheelsAndGroups(xmlCtx, section)
            for wheel in wheels:
                if wheel.materials:
                    item.wheelsArmor[wheel.nodeName] = wheel.materials.values()[0]

        item.drivingWheelsSizes = (frontWheelSize, rearWheelSize)
    _readPriceForItem(xmlCtx, section, item.compactDescr)
    if IS_CLIENT or IS_WEB:
        item.i18n = shared_readers.readUserText(section)
    if IS_CLIENT or IS_EDITOR:
        groundGroups, groundNodes, groundNodesActivePostmortem, lodSettings = chassis_readers.readGroundNodesAndGroups(xmlCtx, section, g_cache)
        trackNodes = chassis_readers.readTrackNodes(xmlCtx, section)
        if section.has_key('camouflage'):
            item.camouflage = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=shared_components.DEFAULT_CAMOUFLAGE)
        item.modelsSets = shared_readers.readModelsSets(xmlCtx, section, 'models')
        item.models = item.modelsSets['default']
        item.traces = chassis_readers.readTraces(xmlCtx, section, item.topRightCarryingPoint[0], g_cache)
        item.tracks = chassis_readers.readTrackBasicParams(xmlCtx, section, g_cache)
        item.groundNodes = shared_components.NodesAndGroups(nodes=groundNodes, groups=groundGroups, activePostmortem=groundNodesActivePostmortem, lodSettings=lodSettings)
        item.trackNodes = shared_components.NodesAndGroups(nodes=trackNodes, groups=component_constants.EMPTY_TUPLE, activePostmortem=False, lodSettings=None)
        item.trackSplineParams = chassis_readers.readTrackSplineParams(xmlCtx, section)
        item.splineDesc = chassis_readers.readSplineConfig(xmlCtx, section, g_cache)
        item.leveredSuspension = chassis_readers.readLeveredSuspension(xmlCtx, section, g_cache)
        item.hullAimingSound = sound_readers.readHullAimingSound(xmlCtx, section, g_cache)
        item.effects = {'lodDist': shared_readers.readLodDist(xmlCtx, section, 'effects/lodDist', g_cache)}
        sounds = sound_readers.readWWTripleSoundConfig(section)
        if sounds.isEmpty():
            raise SoftException('chassis sound tags are wrong for vehicle ' + item.name)
        item.sounds = sounds
        item.physicalTracks = physicalTracksDict = {}
        physicalTracksSection = section['physicalTracks']
        if physicalTracksSection is not None:
            physicalTracksDict['left'] = shared_readers.readBuilders(xmlCtx, physicalTracksSection, 'left', Vehicular.PhysicalTrackBuilder)
            physicalTracksDict['right'] = shared_readers.readBuilders(xmlCtx, physicalTracksSection, 'right', Vehicular.PhysicalTrackBuilder)
        item.chassisLodDistance = shared_readers.readLodDist(xmlCtx, section, 'wheels/lodDist', g_cache)
        item.customEffects = (CustomEffectsDescriptor.getDescriptor(section, g_cache._customEffects['slip'], xmlCtx, 'effects/mud'),)
        item.AODecals = _readAODecals(xmlCtx, section, 'AODecals')
    item.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, item.compactDescr)
    return


def _writeChassis(item, section, *args):
    _writeHitTester(item.hitTesterManager, None, section, 'hitTester')
    _xml.rewriteFloat(section, 'weight', item.weight)
    _xml.rewriteFloat(section, 'rotationSpeed', degrees(item.rotationSpeed))
    _writeArmor(item.materials, None, section, 'armor', optional=True)
    slots = item.emblemSlots + item.slotsAnchors
    shared_writers.writeCustomizationSlots(slots, section, 'customizationSlots')
    chassis_writers.writeWheelsAndGroups(item.wheels, section)
    shared_writers.writeModelsSets(item.modelsSets, section['models'])
    chassis_writers.writeSplineDesc(item.splineDesc, section, g_cache)
    chassis_writers.writeTraces(item.traces, section, g_cache)
    chassis_writers.writeTrackBasicParams(item.tracks, section, g_cache)
    chassis_writers.writeTrackSplineParams(item.trackSplineParams, section)
    chassis_writers.writeTrackNodes(item.trackNodes.nodes, section)
    chassis_writers.writeGroundNodes(item.groundNodes.groups, section)
    sound_writers.writeHullAimingSound(item.hullAimingSound, section, g_cache)
    shared_writers.writeLodDist(item.effects['lodDist'], section, 'effects/lodDist', g_cache)
    chassis_writers.writeMudEffect(item.customEffects[0], g_cache, section, 'effects/mud')
    sound_writers.writeWWTripleSoundConfig(item.sounds, section)
    _writeCustomizableAreas(item.customizableVehicleAreas, section)
    _writeAODecals(item.AODecals, section, 'AODecals')
    if IS_EDITOR:
        editorData = item.editorData
        drivingWheelNames = ' '.join((editorData.frontDrivingWheelName, editorData.rearDrivingWheelName))
        _xml.rewriteString(section, 'drivingWheels', drivingWheelNames)
    if item.generalWheelsAnimatorConfig:
        item.generalWheelsAnimatorConfig.save(section.getPrioritySection('wheels'))
    physicalTracksSection = None
    if section.has_key('physicalTracks'):
        physicalTracksSection = section['physicalTracks']
    elif bool(item.physicalTracks):
        physicalTracksSection = section.createSection('physicalTracks')
        physicalTracksSection.createSection('left')
        physicalTracksSection.createSection('right')
    if physicalTracksSection is not None:
        if 'left' in item.physicalTracks:
            shared_writers.writeBuilders(item.physicalTracks['left'], physicalTracksSection, 'left')
        if 'right' in item.physicalTracks:
            shared_writers.writeBuilders(item.physicalTracks['right'], physicalTracksSection, 'right')
    leveredSuspensionSection = section['leveredSuspension']
    if leveredSuspensionSection is not None and item.leveredSuspension is not None:
        for leverSectionName, leverSection in leveredSuspensionSection.items():
            if leverSectionName != 'lever':
                continue
            leverName = _xml.readNonEmptyString(None, leverSection, 'trackNode')
            for lever in item.leveredSuspension.levers:
                if leverName == lever.trackNodeName:
                    limits = Vector2(degrees(lever.minAngle), degrees(lever.maxAngle))
                    _xml.rewriteVector2(leverSection, 'limits', limits)

    return


def _readChassisLocals(xmlCtx, section, sharedItem, unlocksDescrs, _=None):
    hasOverride = False
    cam = None
    if IS_CLIENT or IS_EDITOR:
        sharedCam = sharedItem.camouflage
        cam = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=sharedCam)
        if cam != sharedCam:
            hasOverride = True
    if not section.has_key('unlocks'):
        unlocks = sharedItem.unlocks
    else:
        hasOverride = True
        unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedItem.compactDescr)
    if not hasOverride:
        return sharedItem
    else:
        descr = sharedItem.copy()
        descr.unlocks = unlocks
        if IS_CLIENT or IS_EDITOR:
            descr.camouflage = cam
        return descr


def _readEngine(xmlCtx, section, item, unlocksDescrs=None, _=None):
    item.tags = _readTags(xmlCtx, section, 'tags', 'vehicleEngine')
    item.level = _readLevel(xmlCtx, section)
    item.power = _xml.readPositiveFloat(xmlCtx, section, 'power') * component_constants.HP_TO_WATTS
    item.weight = _xml.readPositiveFloat(xmlCtx, section, 'weight')
    item.fireStartingChance = _xml.readFraction(xmlCtx, section, 'fireStartingChance')
    item.minFireStartingDamage = g_cache.commonConfig['miscParams']['minFireStartingDamage']
    _readPriceForItem(xmlCtx, section, item.compactDescr)
    if IS_CLIENT or IS_WEB:
        item.i18n = shared_readers.readUserText(section)
    if IS_CLIENT or IS_EDITOR:
        item.rpm_min = section.readInt('rpm_min', 1000)
        item.rpm_max = section.readInt('rpm_max', 2600)
        sounds = sound_readers.readWWTripleSoundConfig(section)
        if sounds.isEmpty():
            _xml.raiseWrongXml(xmlCtx, '', 'chassis sound tags are wrong')
        item.sounds = sounds
    item.healthParams = shared_readers.readDeviceHealthParams(xmlCtx, section)
    item.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, item.compactDescr)


def _readEngineLocal(xmlCtx, section, sharedItem, unlocksDescrs, _=None):
    hasOverride = False
    if section.has_key('unlocks'):
        hasOverride = True
        unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedItem.compactDescr)
    else:
        unlocks = sharedItem.unlocks
    if section.has_key('power'):
        hasOverride = True
        power = _xml.readPositiveFloat(xmlCtx, section, 'power') * component_constants.HP_TO_WATTS
    else:
        power = sharedItem.power
    if not hasOverride:
        return sharedItem
    descr = sharedItem.copy()
    descr.unlocks = unlocks
    descr.power = power
    return descr


def _readFuelTank(xmlCtx, section, item, unlocksDescrs=None, _=None):
    item.tags = _readTags(xmlCtx, section, 'tags', 'vehicleEngine')
    item.level = _readLevel(xmlCtx, section)
    item.weight = _xml.readPositiveFloat(xmlCtx, section, 'weight')
    _readPriceForItem(xmlCtx, section, item.compactDescr)
    if IS_CLIENT or IS_WEB:
        item.i18n = shared_readers.readUserText(section)
    item.healthParams = shared_readers.readDeviceHealthParams(xmlCtx, section, '', False)
    item.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, item.compactDescr)


def _readRadio(xmlCtx, section, item, unlocksDescrs=None, _=None):
    item.tags = _readTags(xmlCtx, section, 'tags', 'vehicleEngine')
    item.level = _readLevel(xmlCtx, section)
    item.weight = _xml.readNonNegativeFloat(xmlCtx, section, 'weight')
    item.distance = _xml.readNonNegativeFloat(xmlCtx, section, 'distance')
    defaults = g_cache.commonConfig['miscParams']['radarDefaults']
    item.radarRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'radarRadius', defaults['radarRadius'])
    item.radarCooldown = _xml.readNonNegativeFloat(xmlCtx, section, 'radarCooldown', defaults['radarCooldown'])
    _readPriceForItem(xmlCtx, section, item.compactDescr)
    if IS_CLIENT or IS_WEB:
        item.i18n = shared_readers.readUserText(section)
    item.healthParams = shared_readers.readDeviceHealthParams(xmlCtx, section)
    item.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, item.compactDescr)


def _parseSectionList(ctx, section, listItemParser, listSubSectionTag=None):
    if listSubSectionTag:
        subsection = _xml.getSubsection(ctx, section, listSubSectionTag)
        ctx = (ctx, listSubSectionTag)
    else:
        subsection = section
    res = {}
    for name, sec in subsection.items():
        named_ctx = (ctx, name)
        res[intern(name)] = listItemParser(named_ctx, sec)

    return res


def _parseFloatList(ctx, sec, floatList):
    return dict(((pn, _xml.readFloat(ctx, sec, pn)) for pn in floatList))


def _tryParseFloatList(ctx, sec, nameList):
    return dict(((pn, _xml.readFloat(ctx, sec, pn)) for pn in nameList if sec.has_key(pn)))


def _parseFloatArrList(ctx, sec, floatArrList):
    return dict(((pn, _xml.readTupleOfFloats(ctx, sec, pn, sz)) for pn, sz in floatArrList))


def _xphysicsParseEngine(ctx, sec):
    res = {}
    floatParamsCommon = ('startRPM',)
    res.update(_parseFloatList(ctx, sec, floatParamsCommon))
    floatParamsDetailed = ('engineInertia', 'idleRPM', 'idleChoker')
    res.update(_parseFloatList(ctx, sec, floatParamsDetailed))
    floatArrParamsDetailed = (('engineLoses', 2), ('engineTorque', 8))
    res.update(_parseFloatArrList(ctx, sec, floatArrParamsDetailed))
    res['engineTorque'] = tuple(zip(res['engineTorque'][0::2], res['engineTorque'][1::2]))
    res['powerFactor'] = sec.readFloat('powerFactor', 1.0)
    res['rotationFactor'] = sec.readFloat('rotationFactor', 1.0)
    res['smplEnginePower'] = sec.readFloat('smplEnginePower', 600.0)
    res['smplFwMaxSpeed'] = component_constants.KMH_TO_MS * sec.readFloat('smplFwMaxSpeed', 55.0)
    res['smplBkMaxSpeed'] = component_constants.KMH_TO_MS * sec.readFloat('smplBkMaxSpeed', 15.0)
    return res


def _xphysicsReadSwingCompensator(ctx, sec):
    floatParams = ('collisionExtend', 'stiffnesFactor0', 'stiffnesFactor1', 'dampingFactor', 'maxPitchDeviation', 'maxRollDeviation', 'restitution')
    res = _tryParseFloatList(ctx, sec, floatParams)
    if sec.has_key('enable'):
        res['enable'] = sec.readBool('enable', 'true')
    if sec.has_key('stabilisationCenter'):
        res['stabilisationCenter'] = _xml.readTupleOfFloats(ctx, sec, 'stabilisationCenter')
    return res


def _xphysicsParseGround(ctx, sec):
    floatParams = ('dirtCumulationRate', 'dirtReleaseRate', 'dirtSideVelocity', 'maxDirt', 'sideFriction', 'fwdFriction', 'rollingFriction')
    res = _parseFloatList(ctx, sec, floatParams)
    res['dirtSideVelocity'] *= component_constants.KMH_TO_MS
    res['dirtCumulationRate'] *= component_constants.KMH_TO_MS
    res['hbComSideFriction'] = sec.readFloat('hbComSideFriction', 0.0)
    res['hbSideFrictionAddition'] = sec.readFloat('hbSideFrictionAddition', 0.0)
    res['rotationFactor'] = sec.readFloat('rotationFactor', 1.0)
    return res


def _xphysicsParseChassis(ctx, sec):
    res = {}
    res['grounds'] = _parseSectionList(ctx, sec, _xphysicsParseGround, 'grounds')
    floatParamsCommon = ('chassisMassFraction', 'hullCOMShiftY', 'wheelRadius', 'bodyHeight', 'clearance', 'wheelStroke', 'stiffness0', 'stiffness1', 'damping', 'movementRevertSpeed', 'comSideFriction', 'wheelInertiaFactor', 'rotationBrake', 'brake', 'angVelocityFactor')
    res.update(_parseFloatList(ctx, sec, floatParamsCommon))
    res['movementRevertSpeed'] *= component_constants.KMH_TO_MS
    res['isRotationAroundCenter'] = sec.readBool('isRotationAroundCenter', False)
    res['comFrictionYOffs'] = sec.readFloat('comFrictionYOffs', 0.7)
    res['rotFritionFactor'] = sec.readFloat('rotFritionFactor', 0.0)
    res['wheelSinkageResistFactor'] = sec.readFloat('wheelSinkageResistFactor', 0.0)
    res['gimletGoalWOnSpot'] = sec.readFloat('gimletGoalWOnSpot', sec.readFloat('wPushedRot', 0.0))
    res['gimletGoalWOnMove'] = sec.readFloat('gimletGoalWOnMove', sec.readFloat('wPushedDiag', 0.0))
    res['wPushedRot'] = res['gimletGoalWOnSpot']
    res['wPushedDiag'] = res['gimletGoalWOnMove']
    res['pushStop'] = sec.readFloat('pushStop', 0.0)
    res['gimletPushOnSpotInit'] = sec.readFloat('gimletPushOnSpotInit', sec.readFloat('pushRot', 0.0))
    res['gimletPushOnSpotFinal'] = sec.readFloat('gimletPushOnSpotFinal', sec.readFloat('pushDiag', 0.0))
    res['gimletPushOnMoveInit'] = sec.readFloat('gimletPushOnMoveInit', res['gimletPushOnSpotInit'])
    res['gimletPushOnMoveFinal'] = sec.readFloat('gimletPushOnMoveFinal', res['gimletPushOnSpotFinal'])
    gimletParams = ('gimletVelScaleMin', 'gimletVelScaleMax', 'pushRotOnSpotFixedPeriod', 'pushRotOnMoveFixedPeriod', 'pushRotOnSpotGrowPeriod', 'pushRotOnMoveGrowPeriod')
    res.update(_tryParseFloatList(ctx, sec, gimletParams))
    res['chsDmgMultiplier'] = sec.readFloat('chsDmgMultiplier', 1.0)
    if sec.has_key('hullDamageByStaticFactor'):
        res['hullDamageByStaticFactor'] = _xml.readPositiveFloat(ctx, sec, 'hullDamageByStaticFactor')
    res['wPushedMediumFactor'] = sec.readFloat('wPushedMediumFactor', 1.0)
    res['wPushedSoftFactor'] = sec.readFloat('wPushedSoftFactor', 1.0)
    res['sideFrictionConstantRatio'] = sec.readFloat('sideFrictionConstantRatio', 0.0)
    res['angVelocityFactor0'] = sec.readFloat('angVelocityFactor0', 1.0)
    axleCount = sec.readInt('axleCount', 5)
    res['axleCount'] = axleCount
    floatArrParamsCommon = (('hullCOM', 3),
     ('roadWheelPositions', axleCount),
     ('stiffnessFactors', axleCount),
     ('hullInertiaFactors', 3))
    res.update(_parseFloatArrList(ctx, sec, floatArrParamsCommon))
    floatParamsDetailed = ('centerRotationFwdSpeed', 'rotationByLockChoker', 'fwLagRatio', 'bkLagRatio')
    res.update(_parseFloatList(ctx, sec, floatParamsDetailed))
    res['centerRotationFwdSpeed'] *= component_constants.KMH_TO_MS
    return res


def _xphysicsParseWheeledChassis(ctx, sec):
    res = _xphysicsParseChassis(ctx, sec)
    axleCount = sec.readInt('axleCount', 5)
    floatArrParams = (('axleSteeringLockAngles', axleCount),
     ('axleSteeringAngles', axleCount),
     ('axleSteeringSpeed', axleCount),
     ('fwdFrictionOnAxisModifiers', axleCount),
     ('sideFrictionOnAxisModifiers', axleCount),
     ('sideFrictionConstantRatioOnAxis', axleCount),
     ('sinkageResistOnAxis', axleCount))
    res.update(_parseFloatArrList(ctx, sec, floatArrParams))
    res['axleIsLeading'] = _xml.readTupleOfBools(ctx, sec, 'axleIsLeading', axleCount)
    res['axleCanBeRised'] = _xml.readTupleOfBools(ctx, sec, 'axleCanBeRised', axleCount)
    floatParams = ('wheelRiseHeight', 'wheelRiseSpeed', 'handbrakeBrakeForce', 'noSignalBrakeForce', 'afterDeathBrakeForce', 'afterDeathMinSpeedForImpulse', 'afterDeathImpulse', 'jumpingFactor', 'jumpingMinForce', 'slowTurnChocker', 'airPitchReduction', 'wheelToHullRollTransmission', 'steeringSpeedInTurnMultiplier')
    res.update(_parseFloatList(ctx, sec, floatParams))
    res['afterDeathMinSpeedForImpulse'] *= component_constants.KMH_TO_MS
    res['brokenWheelRollingFrictionModifier'] = _xml.readFloat(ctx, sec, 'brokenWheelRollingFrictionModifier', 1.0)
    res['brokenWheelPowerLoss'], res['brokenWheelSpeedLoss'] = _readBrokenWheelLosses(ctx, sec, res['axleIsLeading'], res['axleCanBeRised'], res['wheelRiseHeight'])
    burnoutSubsection = _xml.getSubsection(ctx, sec, 'burnout')
    burnoutParams = ('preparationTime', 'activityTime', 'engineDamageMin', 'engineDamageMax', 'warningMaxHealth', 'warningMaxHealthCritEngine', 'power', 'impulse')
    res['burnout'] = _parseFloatList(ctx, burnoutSubsection, burnoutParams)
    res['enableRail'] = _xml.readBool(ctx, sec, 'enableRail')
    return res


def _readXPhysicsMode(xmlCtx, sec, subsectionName):
    subsec = sec[subsectionName]
    if subsec is None:
        return
    else:
        ctx = (xmlCtx, subsectionName)
        res = {}
        res['gravityFactor'] = subsec.readFloat('gravityFactor', 1.0)
        res['vehiclePhysicsType'] = subsec.readInt('vehiclePhysicsType', VEHICLE_PHYSICS_TYPE.TANK)
        res['fakegearbox'] = _readFakeGearBox(ctx, subsec)
        res['engines'] = _parseSectionList(ctx, subsec, _xphysicsParseEngine, 'engines')
        if subsec.has_key('swingCompensator'):
            res['swingCompensator'] = _xphysicsReadSwingCompensator(ctx, subsec['swingCompensator'])
        isTank = res['vehiclePhysicsType'] == VEHICLE_PHYSICS_TYPE.TANK
        readChassisFunc = _xphysicsParseChassis if isTank else _xphysicsParseWheeledChassis
        res['chassis'] = _parseSectionList(ctx, subsec, readChassisFunc, 'chassis')
        return res


def _readXPhysics(xmlCtx, section, subsectionName):
    xsec = section[subsectionName]
    if xsec is None:
        return
    else:
        ctx = (xmlCtx, subsectionName)
        res = {}
        res['mode'] = _xml.readInt(ctx, xsec, 'mode', 1)
        res['detailed'] = _readXPhysicsMode(ctx, xsec, 'detailed')
        return res


def _xphysicsParseGroundClient(ctx, sec):
    res = {}
    res['rollingFriction'] = sec.readFloat('rollingFriction', float('nan'))
    if isnan(res['rollingFriction']):
        _xml.raiseWrongXml(ctx, '', "'rollingFriction' is missing")
    return res


def _xphysicsParseChassisClient(ctx, sec):
    res = {}
    res['grounds'] = _parseSectionList(ctx, sec, _xphysicsParseGroundClient, 'grounds')
    return res


def _xphysicsParseWheeledChassisClient(ctx, sec):
    res = _xphysicsParseChassisClient(ctx, sec)
    axleCount = sec.readInt('axleCount', 5)
    floatArrParams = (('axleSteeringLockAngles', axleCount),)
    res.update(_parseFloatArrList(ctx, sec, floatArrParams))
    floatParams = ('wheelRiseSpeed',)
    res.update(_parseFloatList(ctx, sec, floatParams))
    return res


def _xphysicsParseEngineClient(ctx, sec):
    res = {}
    res['smplEnginePower'] = sec.readFloat('smplEnginePower', float('nan'))
    res['smplFwMaxSpeed'] = sec.readFloat('smplFwMaxSpeed', float('nan'))
    if isnan(res['smplEnginePower']):
        _xml.raiseWrongXml(ctx, '', "'smplEnginePower' is missing")
    return res


def _readXPhysicsClient(xmlCtx, section, subsectionName, isWheeledVehicle=False):
    xsec = section[subsectionName]
    if xsec is None:
        _xml.raiseWrongXml(xmlCtx, '', "subsection '%s' is missing" % subsectionName)
    ctx = (xmlCtx, subsectionName)
    res = {}
    res['engines'] = _parseSectionList(ctx, xsec, _xphysicsParseEngineClient, 'detailed/engines')
    if isWheeledVehicle:
        readFunc = _xphysicsParseWheeledChassisClient
    else:
        readFunc = _xphysicsParseChassisClient
    res['chassis'] = _parseSectionList(ctx, xsec, readFunc, 'detailed/chassis')
    return res


def _readXPhysicsEditor(xmlCtx, section, subsectionName, isWheeledVehicle=False):
    xsec = section[subsectionName]
    if xsec is None:
        return
    else:
        ctx = (xmlCtx, subsectionName)
        res = {}
        res['mode'] = _xml.readInt(ctx, xsec, 'mode', 1)
        res['detailed'] = _readXPhysicsMode(ctx, xsec, 'detailed')
        res['engines'] = _parseSectionList(ctx, xsec, _xphysicsParseEngineClient, 'detailed/engines')
        if isWheeledVehicle:
            readFunc = _xphysicsParseWheeledChassisClient
        else:
            readFunc = _xphysicsParseChassisClient
        res['chassis'] = _parseSectionList(ctx, xsec, readFunc, 'detailed/chassis')
        return res


def _readTurret(xmlCtx, section, item, unlocksDescrs=None, _=None):
    item.tags = _readTags(xmlCtx, section, 'tags', 'vehicleTurret')
    item.level = _readLevel(xmlCtx, section)
    item.hitTesterManager = _readHitTester(xmlCtx, section, 'hitTester')
    item.gunPosition = _xml.readVector3(xmlCtx, section, 'gunPosition')
    item.gunJointPitch = radians(_xml.readFloat(xmlCtx, section, 'gunJointPitch', 0.0))
    item.customizableVehicleAreas = _readCustomizableAreas(xmlCtx, section, 'customization')
    if section.has_key('multiGun'):
        item.multiGun = _readMultiGun(xmlCtx, section, 'multiGun')
    item.materials = _readArmor(xmlCtx, section, 'armor')
    item.weight = _xml.readNonNegativeFloat(xmlCtx, section, 'weight')
    item.healthParams = shared_components.DeviceHealth(_xml.readInt(xmlCtx, section, 'maxHealth', 1))
    item.rotationSpeed = cachedFloat(radians(_xml.readNonNegativeFloat(xmlCtx, section, 'rotationSpeed')))
    item.turretRotatorHealth = shared_readers.readDeviceHealthParams(xmlCtx, section, 'turretRotatorHealth')
    item.surveyingDeviceHealth = shared_readers.readDeviceHealthParams(xmlCtx, section, 'surveyingDeviceHealth')
    if not IS_CLIENT and not IS_BOT:
        item.armorHomogenization = _xml.readPositiveFloat(xmlCtx, section, 'armorHomogenization')
    if section.has_key('invisibilityFactor'):
        item.invisibilityFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'invisibilityFactor')
    else:
        item.invisibilityFactor = component_constants.DEFAULT_INVISIBILITY_FACTOR
    _readPriceForItem(xmlCtx, section, item.compactDescr)
    item.showEmblemsOnGun = section.readBool('showEmblemsOnGun', False)
    if IS_CLIENT or IS_WEB:
        item.i18n = shared_readers.readUserText(section)
    if IS_CLIENT or IS_EDITOR or IS_WEB or IS_CELLAPP:
        item.primaryArmor = _readPrimaryArmor(xmlCtx, section, 'primaryArmor', item.materials)
    if IS_CLIENT or IS_EDITOR or IS_BOT or IS_BASEAPP:
        if section.has_key('emblemSlots'):
            if not IS_BASEAPP:
                item.emblemSlots, item.slotsAnchors = shared_readers.readEmblemSlots(xmlCtx, section, 'emblemSlots')
        elif section.has_key('customizationSlots'):
            item.emblemSlots, item.slotsAnchors = shared_readers.readCustomizationSlots(xmlCtx, section, 'customizationSlots')
    if IS_CLIENT or IS_EDITOR:
        item.ceilless = section.readBool('ceilless', False)
        item.modelsSets = shared_readers.readModelsSets(xmlCtx, section, 'models')
        item.models = item.modelsSets['default']
        if section.has_key('camouflage'):
            item.camouflage = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=shared_components.DEFAULT_CAMOUFLAGE)
        item.turretRotatorSoundManual = _xml.readString(xmlCtx, section, 'wwturretRotatorSoundManual')
        item.AODecals = _readAODecals(xmlCtx, section, 'AODecals')
        commonConfig = g_cache.commonConfig
        item.turretDetachmentEffects = _readTurretDetachmentEffects(xmlCtx, section, 'turretDetachmentEffects', commonConfig['defaultTurretDetachmentEffects'])
    if IS_CELLAPP or IS_EDITOR:
        arrayStr = section.readString('physicsShape')
        strArr = arrayStr.split()
        item.physicsShape = tuple(map(float, strArr))
    v = _xml.readNonNegativeFloat(xmlCtx, section, 'circularVisionRadius')
    item.circularVisionRadius = v
    nationID = parseIntCompactDescr(item.compactDescr)[1]
    item.guns = _readInstallableComponents(xmlCtx, section, 'guns', nationID, _readGun, _readGunLocals, g_cache.guns(nationID), g_cache.gunIDs(nationID), unlocksDescrs, item.compactDescr)
    if not item.multiGun:
        pass
    item.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, item.compactDescr)


def _writeTurret(item, section, sharedSections):
    _xml.rewriteFloat(section, 'weight', item.weight)
    _xml.rewriteFloat(section, 'gunJointPitch', degrees(item.gunJointPitch), 0.0)
    _xml.rewriteBool(section, 'showEmblemsOnGun', item.showEmblemsOnGun, defaultValue=False)
    _writeHitTester(item.hitTesterManager, None, section, 'hitTester')
    _xml.rewriteString(section, 'wwturretRotatorSoundManual', item.turretRotatorSoundManual)
    _writeCamouflageSettings(section, 'camouflage', item.camouflage)
    _writeArmor(item.materials, None, section, 'armor')
    slots = item.emblemSlots + item.slotsAnchors
    shared_writers.writeCustomizationSlots(slots, section, 'customizationSlots')
    shared_writers.writeModelsSets(item.modelsSets, section['models'])
    _writeCustomizableAreas(item.customizableVehicleAreas, section)
    arrayStr = ' '.join([ '{:.3f}'.format(value) for value in item.physicsShape ])
    _xml.rewriteString(section, 'physicsShape', arrayStr)
    nationID = parseIntCompactDescr(item.compactDescr)[1]
    _writeInstallableComponents(item.guns, section, 'guns', _writeGun, g_cache.gunIDs(nationID), sharedSections)
    _writeMultiGun(item, section)
    return


def _readTurretLocals(xmlCtx, section, sharedItem, unlocksDescrs, _=None):
    hasOverride = False
    cam = None
    nationID = sharedItem.id[0]
    if not section.has_key('guns'):
        guns = sharedItem.guns
    else:
        hasOverride = True
        guns = _readInstallableComponents(xmlCtx, section, 'guns', nationID, _readGun, _readGunLocals, g_cache.guns(nationID), g_cache.gunIDs(nationID), unlocksDescrs, sharedItem.compactDescr)
    if IS_CLIENT or IS_EDITOR:
        sharedCam = sharedItem.camouflage
        cam = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=sharedCam)
        if cam != sharedCam:
            hasOverride = True
    if not section.has_key('unlocks'):
        unlocks = sharedItem.unlocks
    else:
        hasOverride = True
        unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedItem.compactDescr)
    if not hasOverride:
        return sharedItem
    else:
        descr = sharedItem.copy()
        descr.guns = guns
        descr.unlocks = unlocks
        if IS_CLIENT or IS_EDITOR:
            descr.camouflage = cam
        return descr


if IS_CLIENT or IS_EDITOR:
    MultiGunInstance = namedtuple('MultiGun', ('node',
     'gunFire',
     'position',
     'shotOffset',
     'shotPosition'))
    if IS_EDITOR:
        MultiGunInstance = reflectedNamedTuple('MultiGun', ('node',
         'gunFire',
         'position',
         'shotOffset',
         'shotPosition'))
else:
    MultiGunInstance = namedtuple('MultiGun', ('position', 'shotOffset', 'shotPosition'))

def _readMultiGun(xmlCtx, section, subsection):
    multiGun = []
    gun_tag_name = 'gun'
    for name, subsection in _xml.getChildren(xmlCtx, section, subsection):
        if name != gun_tag_name:
            _xml.raiseWrongXml(xmlCtx, 'multiGun/{}'.format(name), 'expected {}'.format(gun_tag_name))
        ctx = (xmlCtx, 'multiGun/{}'.format(gun_tag_name))
        gunPosition = _xml.readVector3(ctx, subsection, 'position')
        gunShotOffset = _xml.readVector3(ctx, subsection, 'shotOffset', defaultValue=Vector3(0.0, 0.0, 0.0))
        gunShotPosition = gunPosition + gunShotOffset
        if IS_CLIENT or IS_EDITOR:
            gunNode = _xml.readString(ctx, subsection, 'gunNode')
            gunFire = _xml.readString(ctx, subsection, 'gunFire')
            multiGun.append(MultiGunInstance(gunNode, gunFire, gunPosition, gunShotOffset, gunShotPosition))
        multiGun.append(MultiGunInstance(gunPosition, gunShotOffset, gunShotPosition))

    return multiGun


def makeMultiExtraNameTemplate(name):
    return name.replace('_', '{}', 1) if '_' in name else name + '{}'


def _readExtraLocals(vehType, xmlCtx, section):
    vehExtrasDict = vehType.extrasDict
    vehExtras = list(vehType.extras)
    extras, extrasDict = common_extras.readExtras(xmlCtx, section, 'extras', 'vehicle_extras', vehType=vehType)
    for extraName, extra in extrasDict.iteritems():
        oldExtra = vehExtrasDict.get(extraName)
        if oldExtra:
            extra.index = oldExtra.index
            vehExtras[oldExtra.index] = extra
        else:
            extra.index = len(vehExtras)
            vehExtras.append(extra)
        vehExtrasDict[extraName] = extra

    vehType.extras = tuple(vehExtras)
    vehType.tankmen = _selectCrewExtras(vehType.crewRoles, vehType.extrasDict)
    if section.has_key('deviceExtras'):
        vehDevices, _ = _readDeviceTypes(xmlCtx, section, 'deviceExtras', extrasDict)
        vehType.devices = vehType.devices.union(frozenset((vehExtras[idx] for idx in vehDevices.iterkeys())))


def _readGun(xmlCtx, section, item, unlocksDescrs=None, _=None):
    item.tags = _readTags(xmlCtx, section, 'tags', 'vehicleGun')
    item.level = _readLevel(xmlCtx, section)
    item.rotationSpeed = radians(_xml.readNonNegativeFloat(xmlCtx, section, 'rotationSpeed'))
    item.weight = _xml.readPositiveFloat(xmlCtx, section, 'weight')
    item.reloadTime = _xml.readPositiveFloat(xmlCtx, section, 'reloadTime')
    item.aimingTime = _xml.readPositiveFloat(xmlCtx, section, 'aimingTime')
    item.maxAmmo = _xml.readInt(xmlCtx, section, 'maxAmmo', 1)
    item.invisibilityFactorAtShot = _xml.readFraction(xmlCtx, section, 'invisibilityFactorAtShot')
    item.shotOffset = _xml.readVector3(xmlCtx, section, 'shotOffset', defaultValue=Vector3(0.0, 0.0, 0.0))
    _readPriceForItem(xmlCtx, section, item.compactDescr)
    if IS_CLIENT or IS_WEB:
        item.i18n = shared_readers.readUserText(section)
    if IS_CLIENT or IS_EDITOR:
        if section.has_key('models'):
            item.modelsSets = shared_readers.readModelsSets(xmlCtx, section, 'models')
            item.models = item.modelsSets['default']
        effName = _xml.readNonEmptyString(xmlCtx, section, 'effects')
        eff = g_cache._gunEffects.get(effName)
        if eff is None:
            _xml.raiseWrongXml(xmlCtx, 'effects', "unknown effect '%s'" % effName)
        item.effects = eff
        effName = _xml.readStringOrNone(xmlCtx, section, 'reloadEffect')
        if effName is not None:
            reloadEff = g_cache._gunReloadEffects.get(effName, None)
            if reloadEff is None:
                _xml.raiseWrongXml(xmlCtx, 'effects', "unknown reload effect '%s'" % effName)
            item.reloadEffect = reloadEff
        item.impulse = _xml.readNonNegativeFloat(xmlCtx, section, 'impulse')
        item.recoil = gun_readers.readRecoilEffect(xmlCtx, section, g_cache)
        if section.has_key('camouflage'):
            item.camouflage = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=shared_components.DEFAULT_CAMOUFLAGE)
        item.animateEmblemSlots = section.readBool('animateEmblemSlots', True)
        if section.has_key('emblemSlots'):
            item.emblemSlots, item.slotsAnchors = shared_readers.readEmblemSlots(xmlCtx, section, 'emblemSlots')
    if IS_CLIENT or IS_EDITOR or IS_BOT or IS_BASEAPP:
        if section.has_key('customizationSlots'):
            item.emblemSlots, item.slotsAnchors = shared_readers.readCustomizationSlots(xmlCtx, section, 'customizationSlots')
    if section.has_key('hitTester'):
        item.hitTesterManager = _readHitTester(xmlCtx, section, 'hitTester')
    if section.has_key('armor'):
        item.materials = _readArmor(xmlCtx, section, 'armor')
    if not section.has_key('turretYawLimits'):
        _xml.raiseWrongSection(xmlCtx, 'turretYawLimits')
    else:
        item.turretYawLimits = __readRotationAngleLimits(xmlCtx, section, 'turretYawLimits')
    if not section.has_key('pitchLimits'):
        _xml.raiseWrongSection(xmlCtx, 'pitchLimits')
    else:
        item.pitchLimits = _readGunPitchLimits(xmlCtx, section['pitchLimits'], False)
        _validatePitchLimits(xmlCtx, 'pitchLimits', item.pitchLimits)
    if section.has_key('staticTurretYaw'):
        item.staticTurretYaw = angle = _xml.readFloat(xmlCtx, section, 'staticTurretYaw')
        if angle is not None:
            item.staticTurretYaw = radians(angle)
    else:
        item.staticTurretYaw = None
    if section.has_key('staticPitch'):
        item.staticPitch = angle = _xml.readFloat(xmlCtx, section, 'staticPitch')
        if angle is not None:
            item.staticPitch = radians(angle)
    else:
        item.staticPitch = None
    item.healthParams = shared_readers.readDeviceHealthParams(xmlCtx, section)
    item.shotDispersionAngle = atan(_xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionRadius') / 100.0)
    item.shotDispersionFactors = _readGunShotDispersionFactors(xmlCtx, section, 'shotDispersionFactors')
    if not section.has_key('autoreload'):
        item.autoreload = component_constants.DEFAULT_GUN_AUTORELOAD
    else:
        item.autoreload, item.autoreloadHasBoost = _readGunClipAutoreload(xmlCtx, section)
    if not section.has_key('burst'):
        item.burst = component_constants.DEFAULT_GUN_BURST
    else:
        item.burst = _readGunClipBurst(xmlCtx, section, 'burst')
    if not section.has_key('clip'):
        item.clip = component_constants.DEFAULT_GUN_CLIP
    else:
        item.clip = _readGunClipBurst(xmlCtx, section, 'clip')
    if item.burst[0] > item.clip[0] > 1:
        _xml.raiseWrongXml(xmlCtx, 'burst', 'burst/count is larger than clip/count')
    if item.autoreload != component_constants.DEFAULT_GUN_AUTORELOAD and item.clip[0] <= 1:
        _xml.raiseWrongXml(xmlCtx, 'autoreload', "'autoreload' section is redundant for non-clip items")
    dualGun = None
    if section.has_key('dualGun'):
        dualGun = _readGunDualGunParams(xmlCtx, section)
        item.dualGun = dualGun
    tags = item.tags
    if item.clip[0] == 1:
        tags = tags.difference(('clip',))
    else:
        tags = tags.union(('clip',))
    if item.autoreload == component_constants.DEFAULT_GUN_AUTORELOAD:
        tags = tags.difference(('autoreload',))
    else:
        tags = tags.union(('autoreload',))
    if dualGun is None:
        tags = tags.difference(('dualGun',))
    else:
        tags = tags.union(('dualGun',))
    item.tags = tags
    nationID = parseIntCompactDescr(item.compactDescr)[1]
    v = []
    projSpeedFactor = g_cache.commonConfig['miscParams']['projectileSpeedFactor']
    for sname, subsection in _xml.getChildren(xmlCtx, section, 'shots'):
        v.append(gun_readers.readShot((xmlCtx, 'shots/' + sname), subsection, nationID, projSpeedFactor, g_cache))

    if not v:
        _xml.raiseWrongXml(xmlCtx, 'shots', 'no shots are specified')
    item.shots = tuple(v)
    item.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, item.compactDescr)
    return


if IS_EDITOR:

    def __markEditorPropertyAsOverride(object, propertyName):
        if hasattr(object, 'editorData'):
            sharedPropertiesInfo = object.editorData.sharedPropertiesInfo
            if sharedPropertiesInfo is not None:
                sharedPropertiesInfo.markAsOverride(propertyName)
        return


else:

    def __markEditorPropertyAsOverride(object, propertyName):
        pass


def _readGunLocals(xmlCtx, section, sharedItem, unlocksDescrs, turretCompactDescr):
    hasOverride = False
    sharedItem.customizableVehicleAreas = _readCustomizableAreas(xmlCtx, section, 'customization')
    if not section.has_key('turretYawLimits'):
        turretYawLimits = sharedItem.turretYawLimits
    else:
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'turretYawLimits')
        v = _xml.readVector2(xmlCtx, section, 'turretYawLimits')
        if v[0] > v[1]:
            _xml.raiseWrongSection(xmlCtx, 'turretYawLimits')
        turretYawLimits = cachedFloatTuple((radians(v[0]), radians(v[1]))) if v[0] > -179.0 or v[1] < 179.0 else None
    if section.has_key('pitchLimits'):
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'pitchLimits')
        pitchLimits = _readGunPitchLimits(xmlCtx, section['pitchLimits'], True)
    else:
        pitchLimits = sharedItem.pitchLimits
    if not section.has_key('shotOffset'):
        shotOffset = sharedItem.shotOffset
    else:
        hasOverride = True
        shotOffset = _xml.readVector3(xmlCtx, section, 'shotOffset')
    if not section.has_key('staticTurretYaw'):
        staticTurretYaw = sharedItem.staticTurretYaw
    else:
        hasOverride = True
        staticTurretYaw = radians(_xml.readFloat(xmlCtx, section, 'staticTurretYaw'))
    if not section.has_key('staticPitch'):
        staticPitch = sharedItem.staticPitch
    else:
        hasOverride = True
        staticPitch = radians(_xml.readFloat(xmlCtx, section, 'staticPitch'))
    if not section.has_key('rotationSpeed'):
        rotationSpeed = sharedItem.rotationSpeed
    else:
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'rotationSpeed')
        rotationSpeed = radians(_xml.readNonNegativeFloat(xmlCtx, section, 'rotationSpeed'))
    if not section.has_key('reloadTime'):
        reloadTime = sharedItem.reloadTime
    else:
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'reloadTime')
        reloadTime = _xml.readPositiveFloat(xmlCtx, section, 'reloadTime')
    if not section.has_key('aimingTime'):
        aimingTime = sharedItem.aimingTime
    else:
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'aimingTime')
        aimingTime = _xml.readPositiveFloat(xmlCtx, section, 'aimingTime')
    if not section.has_key('maxAmmo'):
        ammo = sharedItem.maxAmmo
    else:
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'maxAmmo')
        ammo = _xml.readInt(xmlCtx, section, 'maxAmmo', 1)
    if not section.has_key('shotDispersionRadius'):
        shotDispAngle = sharedItem.shotDispersionAngle
    else:
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'shotDispersionRadius')
        shotDispAngle = _xml.readNonNegativeFloat(xmlCtx, section, 'shotDispersionRadius') / 100.0
    if not section.has_key('shotDispersionFactors'):
        shotDispFactors = sharedItem.shotDispersionFactors
    else:
        hasOverride = True
        shotDispFactors = _readGunShotDispersionFactors(xmlCtx, section, 'shotDispersionFactors')
    if not section.has_key('autoreload'):
        autoreload = sharedItem.autoreload
    else:
        hasOverride = True
        autoreload, autoreloadHasBoost = _readGunClipAutoreload(xmlCtx, section)
    if not section.has_key('burst'):
        burst = sharedItem.burst
    else:
        hasOverride = True
        burst = _readGunClipBurst(xmlCtx, section, 'burst')
    if not section.has_key('clip'):
        clip = sharedItem.clip
    else:
        hasOverride = True
        clip = _readGunClipBurst(xmlCtx, section, 'clip')
    if burst[0] > clip[0] > 1:
        _xml.raiseWrongXml(xmlCtx, 'burst', 'burst/count is larger than clip/count')
    if autoreload != component_constants.DEFAULT_GUN_AUTORELOAD and clip[0] <= 1:
        _xml.raiseWrongXml(xmlCtx, 'autoreload', "'autoreload' section is redundant for non-clip items")
    dualGun = None
    if section.has_key('dualGun'):
        hasOverride = True
        dualGun = _readGunDualGunParams(xmlCtx, section)
    if not section.has_key('invisibilityFactorAtShot'):
        invisibilityFactorAtShot = sharedItem.invisibilityFactorAtShot
    else:
        hasOverride = True
        __markEditorPropertyAsOverride(sharedItem, 'invisibilityFactorAtShot')
        invisibilityFactorAtShot = _xml.readFraction(xmlCtx, section, 'invisibilityFactorAtShot')
    if IS_CLIENT or IS_EDITOR:
        if not section.has_key('models'):
            modelsSets = sharedItem.modelsSets
            models = sharedItem.models
            if models is None:
                _xml.raiseWrongSection(xmlCtx, 'models')
        else:
            hasOverride = True
            modelsSets = shared_readers.readModelsSets(xmlCtx, section, 'models')
            models = modelsSets['default']
        if not section.has_key('effects'):
            effects = sharedItem.effects
        else:
            hasOverride = True
            __markEditorPropertyAsOverride(sharedItem, 'effects')
            effName = _xml.readNonEmptyString(xmlCtx, section, 'effects')
            effects = g_cache._gunEffects.get(effName)
            if effects is None:
                _xml.raiseWrongXml(xmlCtx, 'effects', "unknown effect '%s'" % effName)
        if section.has_key('multiGunEffects'):
            multiGunEffects = _xml.readNonEmptyString(xmlCtx, section, 'multiGunEffects')
            effects = []
            for effName in multiGunEffects.split():
                effect = g_cache._gunEffects.get(intern(effName))
                effects.append(effect)

        if not section.has_key('recoil'):
            recoil = sharedItem.recoil
        else:
            hasOverride = True
            __markEditorPropertyAsOverride(sharedItem, 'recoil')
            recoil = gun_readers.readRecoilEffect(xmlCtx, section, g_cache)
        reloadEffect = sharedItem.reloadEffect
        if section.has_key('reloadEffect'):
            hasOverride = True
            effName = _xml.readStringOrNone(xmlCtx, section, 'reloadEffect')
            if effName is not None:
                reloadEffect = g_cache._gunReloadEffects.get(effName, None)
                if reloadEffect is None:
                    _xml.raiseWrongXml(xmlCtx, 'effects', "unknown reload effect '%s'" % effName)
        sharedCam = sharedItem.camouflage
        cam = shared_readers.readCamouflage(xmlCtx, section, 'camouflage', default=sharedCam)
        if cam != sharedCam:
            hasOverride = True
        if not section.has_key('animateEmblemSlots'):
            animateEmblemSlots = sharedItem.animateEmblemSlots
        else:
            hasOverride = True
            animateEmblemSlots = section.readBool('animateEmblemSlots', True)
        if section.has_key('drivenJoints'):
            drivenJoints = _readDrivenJoints(xmlCtx, section, 'drivenJoints')
        else:
            drivenJoints = {}
    slotsAnchors = tuple([])
    if IS_CLIENT or IS_EDITOR or IS_BOT or IS_BASEAPP:
        if not section.has_key('emblemSlots') and not section.has_key('customizationSlots'):
            if not IS_BOT and not IS_BASEAPP:
                emblemSlots = sharedItem.emblemSlots
            slotsAnchors = sharedItem.slotsAnchors
        else:
            hasOverride = True
            __markEditorPropertyAsOverride(sharedItem, 'emblemSlots')
            __markEditorPropertyAsOverride(sharedItem, 'slotsAnchors')
            if section.has_key('emblemSlots'):
                if not IS_BOT and not IS_BASEAPP:
                    emblemSlots, slotsAnchors = shared_readers.readEmblemSlots(xmlCtx, section, 'emblemSlots')
            elif section.has_key('customizationSlots'):
                emblemSlots, slotsAnchors = shared_readers.readCustomizationSlots(xmlCtx, section, 'customizationSlots')
    if IS_BASEAPP:
        htManager = None
        materials = None
    else:
        if not section.has_key('hitTester'):
            htManager = sharedItem.hitTesterManager
            if htManager is None:
                _xml.raiseWrongSection(xmlCtx, 'hitTester')
        else:
            hasOverride = True
            htManager = _readHitTester(xmlCtx, section, 'hitTester')
        if not section.has_key('armor'):
            materials = sharedItem.materials
            if materials is None:
                _xml.raiseWrongSection(xmlCtx, 'armor')
        else:
            hasOverride = True
            materials = _readArmor(xmlCtx, section, 'armor')
    if not section.has_key('unlocks'):
        unlocks = sharedItem.unlocks
    else:
        hasOverride = True
        unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedItem.compactDescr, turretCompactDescr)
    if not hasOverride:
        return sharedItem
    else:
        item = sharedItem.copy()
        item.turretYawLimits = turretYawLimits
        item.rotationSpeed = rotationSpeed
        item.reloadTime = reloadTime
        item.aimingTime = aimingTime
        item.maxAmmo = ammo
        item.shotDispersionAngle = shotDispAngle
        item.shotDispersionFactors = shotDispFactors
        item.burst = burst
        item.unlocks = unlocks
        item.hitTesterManager = htManager
        item.materials = materials
        item.staticTurretYaw = staticTurretYaw
        item.staticPitch = staticPitch
        item.shotOffset = shotOffset
        item.pitchLimits = copy.deepcopy(sharedItem.pitchLimits)
        item.pitchLimits.update(pitchLimits)
        _validatePitchLimits(xmlCtx, 'pitchLimits', item.pitchLimits)
        if clip is not sharedItem.clip:
            item.clip = clip
            tags = item.tags
            if clip[0] == 1:
                tags = tags.difference(('clip',))
            else:
                tags = tags.union(('clip',))
            item.tags = tags
        if autoreload is not sharedItem.autoreload:
            item.autoreload = autoreload
            item.autoreloadHasBoost = autoreloadHasBoost
            tags = item.tags
            if autoreload == component_constants.DEFAULT_GUN_AUTORELOAD:
                tags = tags.difference(('autoreload',))
            else:
                tags = tags.union(('autoreload',))
            item.tags = tags
        if dualGun is not None:
            item.dualGun = dualGun
            tags = item.tags
            if dualGun == component_constants.DEFAULT_GUN_DUALGUN:
                tags = tags.difference(('dualGun',))
            else:
                tags = tags.union(('dualGun',))
            item.tags = tags
        if IS_CLIENT or IS_EDITOR:
            item.modelsSets = modelsSets
            item.models = models
            item.effects = effects
            item.recoil = recoil
            item.camouflage = cam
            item.animateEmblemSlots = animateEmblemSlots
            item.emblemSlots = emblemSlots
            item.reloadEffect = reloadEffect
            item.drivenJoints = drivenJoints
        if IS_CLIENT or IS_EDITOR or IS_BOT or IS_BASEAPP:
            item.slotsAnchors = slotsAnchors
        item.invisibilityFactorAtShot = invisibilityFactorAtShot
        return item


def _writeGun(item, section, *args):
    _xml.rewriteFloat(section, 'rotationSpeed', degrees(item.rotationSpeed))
    _xml.rewriteFloat(section, 'weight', item.weight)
    _xml.rewriteFloat(section, 'reloadTime', item.reloadTime)
    _xml.rewriteFloat(section, 'aimingTime', item.aimingTime)
    _xml.rewriteInt(section, 'maxAmmo', item.maxAmmo, 1)
    _xml.rewriteFloat(section, 'shotDispersionRadius', tan(item.shotDispersionAngle) * 100.0)
    _xml.rewriteFloat(section, 'invisibilityFactorAtShot', item.invisibilityFactorAtShot)
    _xml.rewriteFloat(section, 'impulse', item.impulse)
    _xml.rewriteBool(section, 'animateEmblemSlots', item.animateEmblemSlots)
    _xml.rewriteVector3(section, 'shotOffset', item.shotOffset)
    _xml.rewriteVector2(section, 'turretYawLimits', item.editorTurretYawLimits)
    _writeGunEffectName(item, section)
    _writeCamouflageSettings(section, 'camouflage', item.camouflage)
    _writeArmor(item.materials, None, section, 'armor', optional=True)
    slots = item.emblemSlots + item.slotsAnchors
    shared_writers.writeCustomizationSlots(slots, section, 'customizationSlots')
    shared_writers.writeModelsSets(item.modelsSets, section['models'])
    gun_writers.writeRecoilEffect(item.recoil, section['recoil'], g_cache)
    _writeHitTester(item.hitTesterManager, None, section, 'hitTester')
    _writeGunPitchLimits(item.pitchLimits, section['pitchLimits'])
    _writeDrivenJoints(item.drivenJoints, section, 'drivenJoints')
    _writeCustomizableAreas(item.customizableVehicleAreas, section)
    _writeDualGun(item, section)
    return


def _writeGunEffectName(item, section):
    effects = item.effects
    effectName = None
    if isinstance(effects, list):
        for effect in effects:
            if effectName is None:
                effectName = getEffectNameByEffect(effect)
            effectName += ' ' + getEffectNameByEffect(effect)

    else:
        effectName = getEffectNameByEffect(effects)
    if item.dualGun and item.dualGun is not component_constants.DEFAULT_GUN_DUALGUN:
        _xml.rewriteString(section, 'multiGunEffects', effectName)
    else:
        _xml.rewriteString(section, 'effects', effectName)
    return


def _readGunPitchLimitsSiege(xmlCtx, section, subsectionName):
    subsec = section[subsectionName]
    res = {'minPitch': _readGunPitchConstraints(xmlCtx, subsec, 'minPitch'),
     'maxPitch': _readGunPitchConstraints(xmlCtx, subsec, 'maxPitch')}
    return res


def _readGunPitchLimits(xmlCtx, section, isLocal):
    res = {}
    if section.has_key('minPitch'):
        res['minPitch'] = _readGunPitchConstraints(xmlCtx, section, 'minPitch')
    elif not isLocal:
        _xml.raiseWrongSection(xmlCtx, 'minPitch')
    if section.has_key('maxPitch'):
        res['maxPitch'] = _readGunPitchConstraints(xmlCtx, section, 'maxPitch')
    elif not isLocal:
        _xml.raiseWrongSection(xmlCtx, 'maxPitch')
    return res


def _writeGunPitchLimits(pitchLimits, section):
    if 'minPitch' in pitchLimits:
        _writeGunPitch(pitchLimits['minPitch'], section, 'minPitch')
    if 'maxPitch' in pitchLimits:
        _writeGunPitch(pitchLimits['maxPitch'], section, 'maxPitch')


def _writeGunPitch(pitchLimit, section, subsectionName):
    points = []
    for pair in pitchLimit:
        points.append(0.5 * pair[0] / pi)
        points.append(degrees(pair[1]))

    try:
        strings = section.readString(subsectionName).split()
        oldPoints = tuple(map(float, strings))
        match = True
        for i in xrange(len(oldPoints)):
            if abs(points[i] - oldPoints[i]) > 1e-05:
                match = False
                break

        if match:
            return
    except:
        pass

    pointsStr = ' '.join([ ('{:.5f}'.format(points[i]) if i % 2 == 0 else '{:.2f}'.format(points[i])) for i in xrange(len(points)) ])
    _xml.rewriteString(section, subsectionName, pointsStr)


def _validatePitchLimits(xmlCtx, subsectionName, pitchLimits):
    minPitch = pitchLimits['minPitch']
    maxPitch = pitchLimits['maxPitch']
    pitchLimits['absolute'] = cachedFloatTuple((min([ key for _, key in minPitch ]), max([ key for _, key in maxPitch ])))
    ok = _validateMinMaxPitchLimits(minPitch, maxPitch, False) and _validateMinMaxPitchLimits(maxPitch, minPitch, True)
    if not ok:
        _xml.raiseWrongSection(xmlCtx, subsectionName)


def _validateMinMaxPitchLimits(firstLimit, secondLimit, isGreater):
    ok = True
    f = 0
    s = 1
    while f < len(firstLimit):
        firstYaw = firstLimit[f][0]
        firstPitch = firstLimit[f][1]
        f += 1
        while secondLimit[s][0] < firstYaw:
            s += 1

        t = (firstYaw - secondLimit[s - 1][0]) / (secondLimit[s][0] - secondLimit[s - 1][0])
        secondPitch = secondLimit[s - 1][1] * (1 - t) + secondLimit[s][1] * t
        if firstPitch == secondPitch:
            continue
        if not (firstPitch < secondPitch) ^ isGreater:
            ok = False
            break

    return ok


def _readGunPitchConstraints(xmlCtx, section, type):
    v = _xml.readTupleOfFloats(xmlCtx, section, type)
    if len(v) & 1 != 0:
        _xml.raiseWrongSection(xmlCtx, type)
    points = [ (2 * pi * v[2 * index], radians(v[2 * index + 1])) for index in xrange(len(v) / 2) ]
    if points[0][0] != 0 or points[-1][0] != 2 * pi or points[0][1] != points[-1][1]:
        _xml.raiseWrongSection(xmlCtx, type)
    if len(points) <= 1:
        _xml.raiseWrongSection(xmlCtx, type)
    for index in xrange(len(points) - 1):
        if points[index][0] >= points[index + 1][0]:
            _xml.raiseWrongSection(xmlCtx, type)

    return cachedFloatTuple(points)


def _readGunClipBurst(xmlCtx, section, type):
    count = _xml.readInt(xmlCtx, section, type + '/count', 1)
    interval = 60.0 / _xml.readPositiveFloat(xmlCtx, section, type + '/rate')
    return (count, interval if count > 1 else 0.0)


def _readGunClipAutoreload(xmlCtx, section):
    reloadTime = _xml.readTupleOfPositiveFloats(xmlCtx, section, 'autoreload/reloadTime')
    if not len(reloadTime):
        _xml.raiseWrongXml(xmlCtx, 'autoreload/reloadTime', "'reloadTime' must contain at least one value")
    boostStartTime = _xml.readNonNegativeFloat(xmlCtx, section, 'autoreload/boostStartTime', 0.0)
    boostResidueTime = _xml.readNonNegativeFloat(xmlCtx, section, 'autoreload/boostResidueTime', 0.0)
    fractionName = 'autoreload/boostFraction'
    boostFraction = _xml.readFraction(xmlCtx, section, fractionName) if section.has_key(fractionName) else 1.0
    hasBoost = section.has_key('autoreload/boostStartTime') and section.has_key('autoreload/boostResidueTime') and section.has_key('autoreload/boostFraction')
    return (component_constants.Autoreload(reloadTime=reloadTime, boostStartTime=boostStartTime, boostResidueTime=boostResidueTime, boostFraction=boostFraction), hasBoost)


def _readShells(xmlPath, nationID):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    icons = {}
    if IS_CLIENT or IS_EDITOR or IS_WEB:
        for name, subsection in _xml.getChildren((None, xmlPath), section, 'icons'):
            name = intern(name)
            if icons.has_key(name):
                _xml.raiseWrongXml((None, xmlPath + '/icons'), name, 'name is not unique')
            icons[name] = _xml.readIcon((None, xmlPath + '/icons'), subsection, '')

    descrs = {}
    ids = {}
    for name, subsection in section.items():
        if name in ('icons', 'xmlns:xmlref'):
            continue
        xmlCtx = (None, xmlPath + '/' + name)
        name = intern(name)
        if ids.has_key(name):
            _xml.raiseWrongXml(xmlCtx, '', 'shell type name is not unique')
        id = _xml.readInt(xmlCtx, subsection, 'id', 0, 65535)
        if descrs.has_key(id):
            _xml.raiseWrongXml(xmlCtx, 'id', 'shell type ID is not unique')
        descrs[id] = _readShell(xmlCtx, subsection, name, nationID, id, icons)
        ids[name] = id

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return (descrs, ids)


def _readShell(xmlCtx, section, name, nationID, shellTypeID, icons):
    shell = vehicle_items.createShell(nationID, shellTypeID, name)
    shell.caliber = _xml.readPositiveFloat(xmlCtx, section, 'caliber')
    shell.isTracer = section.readBool('isTracer', False)
    if shell.isTracer:
        shell.isForceTracer = section.readBool('isForceTracer', False)
    if IS_CLIENT or IS_WEB:
        shell.i18n = shared_components.I18nComponent(userStringKey=section.readString('userString'), descriptionKey=section.readString('description'), shortDescriptionSpecialKey=section.readString('shortDescriptionSpecial'), longDescriptionSpecialKey=section.readString('longDescriptionSpecial'))
        v = _xml.readNonEmptyString(xmlCtx, section, 'icon')
        if icons.get(v) is None:
            _xml.raiseWrongXml(xmlCtx, 'icon', "unknown icon '%s'" % v)
        shell.icon = icons.get(v)
        shell.iconName = os.path.splitext(os.path.basename(shell.icon[0]))[0]
    _readPriceForItem(xmlCtx, section, shell.compactDescr)
    if IS_CELLAPP or IS_WEB:
        shell.isGold = 'gold' in _xml.readPrice(xmlCtx, section, 'price') or section.readBool('improved', False)
    kind = intern(_xml.readNonEmptyString(xmlCtx, section, 'kind'))
    shellType = shell_components.createShellType(kind)
    if shellType is None:
        _xml.raiseWrongXml(xmlCtx, 'kind', "unknown shell kind '%s'" % kind)
    shell.type = shellType
    mechanics = intern(_xml.readStringWithDefaultValue(xmlCtx, section, 'mechanics', SHELL_MECHANICS_TYPE.LEGACY))
    isModernHighExplosive = mechanics == SHELL_MECHANICS_TYPE.MODERN
    shell.damage = (_readDamageValue(xmlCtx, section, 'armor', isModernHighExplosive), _readDamageValue(xmlCtx, section, 'devices', isModernHighExplosive))
    if section.has_key('deviceDamagePossibility/protectFromDirectHits'):
        shellType.protectFromDirectHits = readProtectedModules(xmlCtx, section, 'deviceDamagePossibility/protectFromDirectHits')
    if kind == 'HIGH_EXPLOSIVE' and section.has_key('deviceDamagePossibility/protectFromIndirectHits'):
        shellType.protectFromIndirectHits = readProtectedModules(xmlCtx, section, 'deviceDamagePossibility/protectFromIndirectHits')
    if not IS_CLIENT and not IS_BOT:
        if kind.startswith('ARMOR_PIERCING'):
            shellType.normalizationAngle = radians(_xml.readNonNegativeFloat(xmlCtx, section, 'normalizationAngle'))
            shellType.ricochetAngleCos = cos(radians(_xml.readNonNegativeFloat(xmlCtx, section, 'ricochetAngle')))
        elif kind == 'HOLLOW_CHARGE':
            shellType.piercingPowerLossFactorByDistance = 10.0 * _xml.readNonNegativeFloat(xmlCtx, section, 'piercingPowerLossFactorByDistance')
            shellType.ricochetAngleCos = cos(radians(_xml.readNonNegativeFloat(xmlCtx, section, 'ricochetAngle')))
    if kind == 'HIGH_EXPLOSIVE':
        shellType.mechanics = mechanics
        if isModernHighExplosive:
            shellType.obstaclePenetration = _xml.readBool(xmlCtx, section, 'obstaclePenetration', component_constants.DEFAULT_MODERN_HE_OBSTACLE_PENETRATION)
            shellType.shieldPenetration = _xml.readBool(xmlCtx, section, 'shieldPenetration', component_constants.DEFAULT_MODERN_HE_SHIELD_PENETRATION)
            blastWave = _readImpactParams(xmlCtx, section, 'blastWave')
            shellFragments = _readImpactParams(xmlCtx, section, 'shellFragments')
            armorSpalls = _readImpactParams(xmlCtx, section, 'armorSpalls')
            if not (blastWave.isActive or shellFragments.isActive or armorSpalls.isActive):
                _xml.raiseWrongXml(xmlCtx, '', 'Modern high explosive shell must contain at least one damage mechanics: blastWave, shellFragments, armorSpalls')
            shellType.blastWave = blastWave
            shellType.shellFragments = shellFragments
            shellType.armorSpalls = armorSpalls
            shellType.maxDamage = max(shellFragments.damages[0], shellFragments.damages[1], armorSpalls.damages[0], armorSpalls.damages[1], blastWave.damages[0], blastWave.damages[1])
        shellType.explosionRadius = cachedFloat(section.readFloat('explosionRadius'))
        if shellType.explosionRadius <= 0.0:
            shellType.explosionRadius = cachedFloat(shell.caliber * shell.caliber / 5555.0)
        explosionSettings = ('explosionDamageFactor', 'explosionDamageAbsorptionFactor', 'explosionEdgeDamageFactor', 'shellFragmentsDamageAbsorptionFactor')
        for f in explosionSettings:
            factor = section.readFloat(f)
            if factor <= 0:
                factor = g_cache.commonConfig['miscParams'][f]
            setattr(shellType, f, factor)

        if shellType.explosionEdgeDamageFactor > 1.0:
            _xml.raiseWrongXml(xmlCtx, 'explosionEdgeDamageFactor', 'explosionEdgeDamageFactor must be < 1')
    shell.damageRandomization = _xml.readNonNegativeFloat(xmlCtx, section, 'damageRandomization', component_constants.DEFAULT_DAMAGE_RANDOMIZATION)
    shell.piercingPowerRandomization = _xml.readNonNegativeFloat(xmlCtx, section, 'piercingPowerRandomization', component_constants.DEFAULT_PIERCING_POWER_RANDOMIZATION)
    hasStun = section.readBool('hasStun', False)
    if hasStun:
        stun = shell_components.Stun()
        if section.has_key('stunRadius'):
            stunRadius = _xml.readPositiveFloat(xmlCtx, section, 'stunRadius')
        elif kind == 'HIGH_EXPLOSIVE':
            stunRadius = shellType.explosionRadius
        else:
            _xml.raiseWrongXml(xmlCtx, 'stunRadius', 'hasStun = true, but neither explosionRadius nor stunRadius defined')
        stun.stunRadius = stunRadius
        stun.stunDuration = _xml.readPositiveFloat(xmlCtx, section, 'stunDuration') if section.has_key('stunDuration') else stunConfig.get('baseStunDuration', 30)
        stun.stunFactor = _xml.readPositiveFloat(xmlCtx, section, 'stunFactor') if section.has_key('stunFactor') else 1.0
        if stun.stunFactor > 1:
            _xml.raiseWrongXml(xmlCtx, 'stunFactor', 'stun factor cannot exceed 1')
        stun.guaranteedStunDuration = _xml.readFraction(xmlCtx, section, 'guaranteedStunDuration') if section.has_key('guaranteedStunDuration') else stunConfig['guaranteedStunDuration']
        stun.damageDurationCoeff = _xml.readFraction(xmlCtx, section, 'damageDurationCoeff') if section.has_key('damageDurationCoeff') else stunConfig['damageDurationCoeff']
        stun.guaranteedStunEffect = _xml.readFraction(xmlCtx, section, 'guaranteedStunEffect') if section.has_key('guaranteedStunEffect') else stunConfig['guaranteedStunEffect']
        stun.damageEffectCoeff = _xml.readFraction(xmlCtx, section, 'damageEffectCoeff') if section.has_key('damageEffectCoeff') else stunConfig['damageEffectCoeff']
    else:
        stun = None
    shell.stun = stun
    effName = _xml.readNonEmptyString(xmlCtx, section, 'effects')
    v = g_cache.shotEffectsIndexes.get(effName)
    if v is None:
        _xml.raiseWrongXml(xmlCtx, 'effects', "unknown effect '%s'" % effName)
    shell.effectsIndex = v
    if section.has_key('tags'):
        shell.tags = _readTags(xmlCtx, section, 'tags', 'shell')
    return shell


_shellKinds = (SHELL_TYPES.HOLLOW_CHARGE,
 SHELL_TYPES.HIGH_EXPLOSIVE,
 SHELL_TYPES.ARMOR_PIERCING,
 SHELL_TYPES.ARMOR_PIERCING_HE,
 SHELL_TYPES.ARMOR_PIERCING_CR,
 SHELL_TYPES.SMOKE)

def readProtectedModules(xmlCtx, section, subsection):
    moduleKind = g_cache._moduleKind
    protectModules = set()
    allValidModules = moduleKind.get('external', set()).union(moduleKind.get('internal', set()), moduleKind.get('tankmen', set()))
    protectFromHits = _xml.readString(xmlCtx, section, subsection).split()
    for module in protectFromHits:
        moduleID = IDS_BY_NAMES.get(module)
        if module in moduleKind:
            protectModules = protectModules.union(moduleKind[module])
        if moduleID not in allValidModules:
            _xml.raiseWrongXml(xmlCtx, section, 'wrong material type')
        protectModules.add(moduleID)

    return protectModules


def _defaultLocalReader(xmlCtx, section, sharedItem, unlocksDescrs, parentItem=None):
    if not section.has_key('unlocks'):
        return sharedItem
    descr = sharedItem.copy()
    descr.unlocks = _readUnlocks(xmlCtx, section, 'unlocks', unlocksDescrs, sharedItem.compactDescr)
    return descr


def _readDamageValue(xmlCtx, section, damageTypeName, isModernHighExplosive):
    subsectionName = 'damage/{}'.format(damageTypeName)
    return _xml.readNonNegativeFloat(xmlCtx, section, subsectionName) if isModernHighExplosive else _xml.readPositiveFloat(xmlCtx, section, subsectionName)


def _readGunShotDispersionFactors(xmlCtx, section, subsectionName):
    res = {'turretRotation': _xml.readNonNegativeFloat(xmlCtx, section, subsectionName + '/turretRotation') / radians(1.0),
     'afterShot': _xml.readNonNegativeFloat(xmlCtx, section, subsectionName + '/afterShot'),
     'whileGunDamaged': _xml.readNonNegativeFloat(xmlCtx, section, subsectionName + '/whileGunDamaged')}
    name = subsectionName + '/afterShotInBurst'
    if section.has_key(name):
        res['afterShotInBurst'] = _xml.readNonNegativeFloat(xmlCtx, section, name)
    else:
        res['afterShotInBurst'] = res['afterShot']
    return res


def _readArmor(xmlCtx, section, subsectionName, optional=False, index=0):
    res = {}
    if IS_BASEAPP:
        return res
    elif IS_BOT:
        return res
    else:
        defMaterials = g_cache.commonConfig['materials']
        autoDamageKindMaterials = g_cache.commonConfig['_autoDamageKindMaterials']
        matKindIDsByNames = material_kinds.IDS_BY_NAMES
        section = _xml.getSubsection(xmlCtx, section, subsectionName, not optional)
        if not section and optional:
            return res
        xmlCtx = (xmlCtx, subsectionName)
        for matKindName, matKindSection in section.items():
            materialKind = matKindIDsByNames.get(matKindName)
            if materialKind is None:
                _xml.raiseWrongXml(xmlCtx, matKindName, 'material kind name is unknown')
            defMatInfo = defMaterials.get(materialKind)
            if defMatInfo is None:
                _xml.raiseWrongXml(xmlCtx, matKindName, 'material kind is not useable on vehicle')
            vals = defMatInfo._asdict()
            vals['armor'] = _xml.readNonNegativeFloat(xmlCtx, section, matKindName)
            isDevice = vals['extra'] is not None
            damageKind = None if materialKind in autoDamageKindMaterials else vals['damageKind']
            if defMatInfo.multipleExtra:
                vals['extra'] = defMatInfo.extra.format(index)
            ctx = (xmlCtx, matKindName)
            for paramName in matKindSection.keys():
                if paramName in _g_boolMatInfoParams:
                    vals[paramName] = _xml.readBool(ctx, matKindSection, paramName)
                if paramName == 'vehicleDamageFactor':
                    vals[paramName] = _xml.readFraction(ctx, matKindSection, paramName)
                if isDevice and paramName in ('chanceToHitByProjectile', 'chanceToHitByExplosion'):
                    vals[paramName] = _xml.readFraction(ctx, matKindSection, paramName)
                if paramName == 'damageKind':
                    damageKindName = _xml.readString(ctx, matKindSection, 'damageKind')
                    if damageKindName == 'armor':
                        damageKind = 0
                    elif damageKindName == 'device':
                        damageKind = 1
                    elif damageKindName == 'auto':
                        damageKind = None
                    else:
                        _xml.raiseWrongXml(ctx, 'damageKind', 'wrong damage kind name')
                    if damageKind is not None:
                        vals['damageKind'] = damageKind
                _xml.raiseWrongXml(ctx, paramName, 'unknown parameter')

            if damageKind is None:
                damageKind = 0 if vals['armor'] else 1
                vals['damageKind'] = damageKind
            res[materialKind] = shared_components.MaterialInfo(**vals)

        if IS_EDITOR:
            for kind, matInfo in defMaterials.items():
                if kind not in res.keys():
                    vals = matInfo._asdict()
                    vals['armor'] = 0.0
                    if matInfo.multipleExtra:
                        vals['extra'] = matInfo.extra.format(index)
                    res[kind] = shared_components.MaterialInfo(**vals)

        return res


def _writeArmor(armor, xmlCtx, section, subsectionName, optional=False, index=0):
    if not armor and optional:
        return
    section.deleteSection(subsectionName)
    section.createSection(subsectionName)
    armorSection = _xml.getSubsection(xmlCtx, section, subsectionName)
    materials = g_cache.commonConfig['materials']
    for matKind, matInfo in armor.items():
        defMatInfo = materials.get(matKind)._asdict()
        matKindName = material_kinds.NAMES_BY_IDS.get(matKind)
        hasChanges = matInfo.armor != 0 or matInfo.vehicleDamageFactor != defMatInfo['vehicleDamageFactor'] or matInfo.chanceToHitByProjectile != defMatInfo['chanceToHitByProjectile'] or matInfo.chanceToHitByExplosion != defMatInfo['chanceToHitByExplosion']
        if hasChanges:
            _xml.rewriteFloat(armorSection, matKindName, matInfo.armor)
        _xml.rewriteFloat(armorSection, matKindName + '/vehicleDamageFactor', matInfo.vehicleDamageFactor, defMatInfo['vehicleDamageFactor'])
        _xml.rewriteFloat(armorSection, matKindName + '/chanceToHitByProjectile', matInfo.chanceToHitByProjectile, defMatInfo['chanceToHitByProjectile'])
        _xml.rewriteFloat(armorSection, matKindName + '/chanceToHitByExplosion', matInfo.chanceToHitByExplosion, defMatInfo['chanceToHitByExplosion'])


_g_boolMatInfoParams = ('useArmorHomogenization',
 'useHitAngle',
 'useAntifragmentationLining',
 'mayRicochet',
 'collideOnceOnly',
 'continueTraceIfNoHit',
 'checkCaliberForRichet',
 'checkCaliberForHitAngleNorm')

def _readPrimaryArmor(xmlCtx, section, subsectionName, materials):
    if not section.has_key(subsectionName):
        return (materials.get(1, shared_components.DEFAULT_MATERIAL_INFO).armor, materials.get(3, shared_components.DEFAULT_MATERIAL_INFO).armor, materials.get(2, shared_components.DEFAULT_MATERIAL_INFO).armor)
    else:
        armorNames = section.readString(subsectionName).split()
        if len(armorNames) != 3:
            _xml.raiseWrongSection(xmlCtx, subsectionName)
        res = []
        matKindIDsByNames = material_kinds.IDS_BY_NAMES
        for matKindName in armorNames:
            materialKind = matKindIDsByNames.get(matKindName)
            if materialKind is None:
                _xml.raiseWrongXml(xmlCtx, subsectionName, "unknown material kind name '%s'" % matKindName)
            res.append(materials.get(materialKind, shared_components.DEFAULT_MATERIAL_INFO).armor)

        return cachedFloatTuple(res)


def _readDamageByStaticsChances(xmlCtx, section, subsectionName):
    section = _xml.getSubsection(xmlCtx, section, subsectionName, False)
    if section is None:
        return g_cache.commonConfig['damageByStaticsChances']
    else:
        xmlCtx = (xmlCtx, subsectionName)
        res = copy.deepcopy(g_cache.commonConfig['damageByStaticsChances'])
        for subsectionName in ('tankman', 'module'):
            subsection = _xml.getSubsection(xmlCtx, section, subsectionName, False)
            if subsection is not None:
                res[subsectionName] = _xml.readFraction(xmlCtx, section, subsectionName)

        return res


def _readFakeTurretIndices(xmlCtx, section, subsectionName, numTurrets):
    res = _xml.readTupleOfInts(xmlCtx, section, subsectionName)
    for idx in res:
        if not 0 <= idx < numTurrets:
            _xml.raiseWrongSection(xmlCtx, subsectionName)

    return res


def _readCustomizableAreas(xmlCtx, section, subsectionName):
    res = {'paint': [],
     'camouflage': []}
    paintString = camouflageString = None
    customization = _xml.getSubsection(xmlCtx, section, subsectionName, throwIfMissing=False)
    if customization is not None:
        customizableVehicleAreas = _xml.getSubsection(xmlCtx, customization, 'customizableVehicleAreas')
        paintString = _xml.readStringOrNone(xmlCtx, customizableVehicleAreas, 'paint')
        camouflageString = _xml.readStringOrNone(xmlCtx, customizableVehicleAreas, 'camouflage')
        res['paint'] = decodeEnum(paintString, ApplyArea)
        res['camouflage'] = decodeEnum(camouflageString, ApplyArea)
    if IS_EDITOR:
        res['paintString'] = paintString if paintString is not None else ''
        res['camouflageString'] = camouflageString if camouflageString is not None else ''
    return res


def _writeCustomizableAreas(items, section):
    subsectionName = 'customization'
    if len(items['paintString']) == 0 and len(items['camouflageString']) == 0:
        section.deleteSection(subsectionName)
        return
    _xml.rewriteString(section, subsectionName + '/customizableVehicleAreas/paint', items['paintString'])
    _xml.rewriteString(section, subsectionName + '/customizableVehicleAreas/camouflage', items['camouflageString'])


def _writeDualGun(item, section):
    if not section.has_key('dualGun') or item.dualGun is None or item.dualGun is component_constants.DEFAULT_GUN_DUALGUN:
        return
    else:
        subSection = section['dualGun']
        _xml.rewriteFloat(subSection, 'chargeTime', item.dualGun.chargeTime)
        _xml.rewriteInt(subSection, 'shootImpulse', item.dualGun.shootImpulse)
        _xml.rewriteFloat(subSection, 'reloadLockTime', item.dualGun.reloadLockTime)
        reloadTimes = Vector2(item.dualGun.reloadTimes[0], item.dualGun.reloadTimes[1])
        _xml.rewriteVector2(subSection, 'reloadTimes', reloadTimes)
        _xml.rewriteFloat(subSection, 'rateTime', item.dualGun.rateTime)
        _xml.rewriteFloat(subSection, 'chargeThreshold', item.dualGun.chargeThreshold)
        _xml.rewriteFloat(subSection, 'afterShotDelay', item.dualGun.afterShotDelay)
        _xml.rewriteFloat(subSection, 'preChargeIndication', item.dualGun.preChargeIndication)
        _xml.rewriteFloat(subSection, 'chargeCancelTime', item.dualGun.chargeCancelTime)
        return


def _readHitTester(xmlCtx, section, subsectionName, optional=False):
    if IS_BASEAPP or IS_WEB:
        return
    else:
        subsection = _xml.getSubsection(xmlCtx, section, subsectionName, throwIfMissing=False)
        if subsection is None:
            if optional:
                return
            _xml.raiseWrongSection(xmlCtx, subsectionName)
        try:
            htManager = HitTesterManager(subsection)
            if IS_CELLAPP or IS_EDITOR:
                htManager.loadHitTesters()
            return htManager
        except Exception as x:
            LOG_CURRENT_EXCEPTION()
            _xml.raiseWrongXml(xmlCtx, subsectionName, str(x))

        return


def _writeHitTester(hitTesterManager, xmlCtx, section, subsectionName):
    if not hitTesterManager:
        return
    subsection = _xml.getSubsection(xmlCtx, section, subsectionName)
    if not subsection:
        _xml.raiseWrongXml(xmlCtx, subsectionName, "can't write hittester")
    hitTesterManager.save(subsection)


def _readCrew(xmlCtx, section, subsectionName):
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    res = []
    skillCounts = {}
    for skillName, subsection in section.items():
        skillName = intern(skillName)
        if skillName not in skills_constants.ROLES:
            _xml.raiseWrongXml(xmlCtx, skillName, 'wrong skill name')
        skills = (skillName,)
        for subskillName in subsection.asString.split():
            subskillName = intern(subskillName)
            if subskillName not in skills_constants.ROLES or subskillName in (skillName, 'commander'):
                _xml.raiseWrongXml(xmlCtx, skillName, "wrong sub-skill name '%s'" % subskillName)
            skills = skills + (subskillName,)

        res.append(skills)
        for skillName in skills:
            skillCounts[skillName] = skillCounts.get(skillName, 0) + 1

    if len(skillCounts) != len(skills_constants.ROLES):
        _xml.raiseWrongXml(xmlCtx, '', 'missing crew roles: ' + str(tuple(skills_constants.ROLES.difference(skillCounts.keys()))))
    for role, limit in skills_constants.ROLE_LIMITS.iteritems():
        if skillCounts[role] > limit:
            _xml.raiseWrongXml(xmlCtx, '', 'more than one %s in crew' % role)

    return tuple(res)


def _readPriceForItem(xmlCtx, section, compactDescr):
    pricesDest = _g_prices
    if pricesDest is not None:
        pricesDest['itemPrices'][compactDescr] = _xml.readPrice(xmlCtx, section, 'price')
        if section.readBool('notInShop', False):
            pricesDest['notInShopItems'].add(compactDescr)
    return


def _readPriceForOperation(xmlCtx, section, opType, opKey):
    pricesDest = _g_prices
    if pricesDest is not None:
        pricesDest['operationPrices'].setdefault(opType, {})[opKey] = _xml.readPrice(xmlCtx, section, 'price')
    return


def _readPriceForProgressionLvl(compactDescr, lvls):
    pricesDest = _g_prices
    if pricesDest is not None:
        itemprices = ItemsPrices()
        notInShopItems = set()
        for num, lvl in lvls.iteritems():
            if lvl is not None:
                price = lvl.get('price')
                notInShop = lvl.get('notInShop')
                if price:
                    itemprices[num] = price
                if notInShop:
                    notInShopItems.add(num)

        if itemprices:
            pricesDest['progressionLvlPrices'][compactDescr] = itemprices
        if notInShopItems:
            pricesDest['notInShopProgressionLvlItems'][compactDescr] = notInShopItems
    return


def _copyPriceForItem(sourceCompactDescr, destCompactDescr, itemNotInShop):
    pricesDest = _g_prices
    if pricesDest is not None:
        pricesDest['itemPrices'][destCompactDescr] = pricesDest['itemPrices'].getPrices(sourceCompactDescr)
        if itemNotInShop or sourceCompactDescr in pricesDest['notInShopItems']:
            pricesDest['notInShopItems'].add(destCompactDescr)
    return


def getPriceForItemDescr(itemDescr):
    pricesDest = _g_prices
    priceInfo = tuple()
    if pricesDest is not None:
        price = pricesDest['itemPrices'].getPrices(itemDescr)
        notInShop = True if itemDescr in pricesDest['notInShopItems'] else False
        priceInfo = (price, notInShop)
    return priceInfo


def _readUnlocks(xmlCtx, section, subsectionName, unlocksDescrs, *requiredItems):
    if unlocksDescrs is None:
        return []
    else:
        s = section[subsectionName]
        if s is None or 0 == len(s):
            return []
        idxs = []
        for s in s.values():
            ctx = (xmlCtx, subsectionName + '/' + s.name)
            itemTypeName = _itemTypeNameMap.get(s.name)
            if itemTypeName is None:
                _xml.raiseWrongXml(ctx, '', 'unknown item type')
            itemName = s.asString
            if not itemName:
                _xml.raiseWrongXml(ctx, '', 'item name is missing')
            xpCost = _xml.readInt(ctx, s, 'cost', 0)
            idxs.append(len(unlocksDescrs))
            unlocksDescrs.append((xpCost, itemTypeName, itemName) + requiredItems)

        return idxs


_itemTypeNameMap = {'vehicle': 'vehicle',
 'chassis': 'vehicleChassis',
 'turret': 'vehicleTurret',
 'gun': 'vehicleGun',
 'engine': 'vehicleEngine',
 'fuelTank': 'vehicleFuelTank',
 'radio': 'vehicleRadio'}

def __readEffectsTimeLine(xmlCtx, section):
    try:
        effectsTimeLine = EffectsList.effectsFromSection(section)
    except Exception as x:
        _xml.raiseWrongXml(xmlCtx, section.name, str(x))

    return EffectsList.EffectsTimeLinePrereqs(effectsTimeLine.keyPoints, effectsTimeLine.effectsList, set())


def _readEffectGroups(xmlPath, withSubgroups=False):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    res = __readEffectGroupsFromSection(section, xmlCtx, withSubgroups)
    ResMgr.purge(xmlPath, True)
    return res


def __readEffectGroupsFromSection(section, xmlCtx, withSubgroups=False):
    res = {}
    for sname, subsection in section.items():
        if sname in ('xmlns:xmlref',):
            continue
        sname = intern(sname)
        if withSubgroups:
            res[sname] = [ __readEffectsTimeLine((xmlCtx, sname + '/' + subgroupName), subgroupSection) for subgroupName, subgroupSection in subsection.items() ]
        res[sname] = __readEffectsTimeLine((xmlCtx, sname), subsection)

    return res


def _readDrivenJoints(xmlCtx, section, subsectionName):

    def readOneSection(xmlCtx, section, subsectionName):
        result = []
        for sname, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
            if sname == 'sets':
                continue
            ctx = (xmlCtx, sname)
            masterNode = _xml.readNonEmptyString(ctx, subsection, 'node')
            fulltable = []
            masterTable = [masterNode]
            for rowName, rowValue in subsection['table'].items():
                masterTable.append(radians(rowValue.asFloat))

            fulltable.append(masterTable)
            for subsection in subsection['slaves'].values():
                slaveNode = _xml.readString(ctx, subsection, 'node')
                table = [slaveNode]
                for rowValue in subsection['table'].values():
                    table.append(radians(rowValue.asFloat))

                fulltable.append(table)

            result.append(fulltable)

        return result

    drivenJoints = {}
    drivenJointsSection = _xml.getSubsection(xmlCtx, section, subsectionName)
    defaultSection = readOneSection(xmlCtx, section, subsectionName)
    if defaultSection:
        drivenJoints['default'] = defaultSection
    if drivenJointsSection.has_key('sets'):
        drivenJointsSetsSection = _xml.getSubsection(xmlCtx, drivenJointsSection, 'sets')
        for sname in drivenJointsSetsSection.keys():
            drivenJoints[sname] = readOneSection(xmlCtx, drivenJointsSetsSection, sname)

    return drivenJoints


def _writeDrivenJoints(items, section, subsectionName):

    def getSubsection(section, subsectionName):
        if not section.has_key(subsectionName):
            subsection = section.createSection(subsectionName)
        else:
            subsection = section[subsectionName]
        return subsection

    def createSingleSection(section, subsection):
        for i in xrange(len(section)):
            record = section[i]
            recordSection = createOrTake(subsection, i, 'master')
            slavesSection = None
            for j in xrange(len(record)):
                table = record[j]
                if j == 0:
                    tableSection = recordSection
                else:
                    slavesSection = createOrTake(recordSection, 0, 'slaves')
                    tableSection = createOrTake(slavesSection, j - 1, 'slave')
                _xml.rewriteString(tableSection, 'node', table[0])
                rowsSection = createOrTake(tableSection, 0, 'table')
                for k in xrange(1, len(table)):
                    row = degrees(table[k])
                    rowSection = createOrTake(rowsSection, k - 1, 'row')
                    rowSection.asFloat = row

                rows = rowsSection.values()
                for k in xrange(len(table) - 1, len(rows)):
                    rowsSection.deleteSection(rows[k])

            if slavesSection:
                children = slavesSection.values()
                for j in xrange(len(record) - 1, len(children)):
                    slavesSection.deleteSection(children[j])

        masters = subsection.values()
        for i in xrange(len(section), len(masters)):
            subsection.deleteSection(masters[i])

        return

    def createOrTake(section, id, subsectionName):
        if not section.has_key(subsectionName):
            return section.createSection(subsectionName)
        children = section.values()
        curMatch = 0
        for child in children:
            if child.name == subsectionName:
                if curMatch == id:
                    return child
                curMatch += 1

        return section.createSection(subsectionName)

    def equal(left, right):
        if type(left) == list:
            if len(left) != len(right):
                return False
            for i in xrange(len(left)):
                if not equal(left[i], right[i]):
                    return False

            return True
        elif type(left) == float:
            return abs(left - right) < 1e-08
        else:
            return left == right

    if items is not None and len(items) > 0:
        subsection = getSubsection(section, subsectionName)
        default = []
        for key, value in items.items():
            if key == 'default':
                createSingleSection(value, subsection)
                default = value
                continue
            if value is None or equal(value, default):
                if subsection.has_key('sets'):
                    setSubsection = getSubsection(subsection, 'sets')
                    if setSubsection.has_key(key):
                        setSubsection.deleteSection(key)
                continue
            setSubsection = getSubsection(subsection, 'sets')
            skinSubsection = getSubsection(setSubsection, key)
            createSingleSection(value, skinSubsection)

    if section.has_key(subsectionName):
        subsection = getSubsection(section, subsectionName)
        if len(subsection.values()) == 0:
            section.deleteSection(subsectionName)
    return


def _readRecoilEffectGroups(xmlPath):
    res = {}
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        if sname in ('xmlns:xmlref',):
            continue
        sname = intern(sname)
        ctx = (xmlCtx, sname)
        res[sname] = (_xml.readNonNegativeFloat(ctx, subsection, 'backoffTime'), _xml.readNonNegativeFloat(ctx, subsection, 'returnTime'))

    ResMgr.purge(xmlPath, True)
    return res


def __readReloadEffect(xmlCtx, section):
    try:
        reloadEffect = ReloadEffect.effectFromSection(section)
        return reloadEffect
    except Exception as x:
        _xml.raiseWrongXml(xmlCtx, section.name, str(x))


def _readReloadEffectGroups(xmlPath):
    res = {}
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        if sname in ('xmlns:xmlref',):
            continue
        sname = intern(sname)
        ctx = (xmlCtx, sname)
        res[sname] = __readReloadEffect(ctx, subsection)

    ResMgr.purge(xmlPath, True)
    return res


def _readVehicleRoles(xmlPath):
    res = {}
    section = ResMgr.openSection(xmlPath)
    if not section:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read roles.xml')
    xmlCtx = (None, xmlPath)
    for roleName, subsection in section.items():
        ctx = (xmlCtx, None)
        roleType = ROLE_LABEL_TO_TYPE.get(roleName)
        if roleType is None:
            _xml.raiseWrongXml(ctx, roleName, 'no role with such name (roles.xml)')
        if roleType in res:
            _xml.raiseWrongXml(ctx, roleName, 'duplicated role name in roles.xml')
        actions = _xml.readNonEmptyString(ctx, subsection, 'actions')
        res[roleType] = tuple([ ACTION_LABEL_TO_TYPE.get(label) for label in actions.split() ])

    return res


def _readChassisEffectGroups(xmlPath):
    res = {}
    section = ResMgr.openSection(xmlPath)
    if not section or section['particles'] is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    section = section['particles']
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        sname = intern(sname)
        ctx = (xmlCtx, sname)
        effects = {}
        for matkindName, matkindSection in subsection.items():
            matkindName = intern(matkindName)
            if matkindName != 'default' and matkindName not in EFFECT_MATERIALS:
                _xml.raiseWrongXml(ctx, matkindName, 'unknown material kind')
            else:
                effectNames = []
                if len(matkindSection.keys()) > 0:
                    for idx, side in enumerate(('left', 'right', 'leftFront', 'rightFront')):
                        sideEffectName = _xml.readNonEmptyString((ctx, matkindName), matkindSection, side)
                        effectNames.append(intern(sideEffectName))

                else:
                    effectNames = _xml.readNonEmptyString((ctx, matkindName), matkindSection, '')
                if matkindName == 'default':
                    effects[-1] = effectNames
                else:
                    effectIndex = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES[matkindName]
                    effects[effectIndex] = effectNames
            res[sname] = (effects, set())

        matkindSection = None

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readCustomEffectGroups(xmlPath):
    res = {}
    if IS_EDITOR:
        xmlPath = xmlPath + '!jit'
    section = ResMgr.openSection(xmlPath)
    try:
        defaultEffect = None
        if section is not None:
            SelectorDescFactory.initFactory(section)
            effectsSection = section['effects']
            for name, subsection in effectsSection.items():
                effect = CustomEffectsDescriptor(subsection)
                res[name] = effect
                if defaultEffect is None:
                    defaultEffect = effect

            if defaultEffect is not None:
                res['default'] = defaultEffect
            SelectorDescFactory.releseFactory()
    except Exception:
        LOG_CURRENT_EXCEPTION()

    ResMgr.purge(xmlPath, True)
    return res


def _readShotEffectGroups(xmlPath):
    res = ({}, [])
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    for sname, subsection in section.items():
        if sname in ('xmlns:xmlref',):
            continue
        sname = intern(sname)
        ctx = (xmlCtx, sname)
        index = len(res[1])
        descr = {'index': index}
        descr.update(_readShotEffects(ctx, subsection))
        if IS_CLIENT or IS_EDITOR:
            descr['prereqs'] = set()
        res[0][sname] = index
        res[1].append(descr)

    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readShotEffects(xmlCtx, section):
    res = {}
    res['targetStickers'] = {}
    v = section.readString('targetStickers/armorResisted')
    if not v:
        v = None
    else:
        v = g_cache.damageStickers['ids'].get(v)
        if v is None:
            _xml.raiseWrongXml(xmlCtx, 'targetStickers/armorResisted', 'unknown name of sticker')
    res['targetStickers']['armorResisted'] = v
    v = section.readString('targetStickers/armorPierced')
    if not v:
        v = None
    else:
        v = g_cache.damageStickers['ids'].get(v)
        if v is None:
            _xml.raiseWrongXml(xmlCtx, 'targetStickers/armorPierced', 'unknown name of sticker')
    res['targetStickers']['armorPierced'] = v
    if IS_CLIENT or IS_EDITOR:
        artillery = section.has_key('artillery')
        if artillery and IS_CLIENT:
            res['artilleryID'] = BigWorld.PyGroundEffectManager().loadArtillery(section['artillery'])
        airstrike = section.has_key('airstrike')
        if airstrike and IS_CLIENT:
            res['airstrikeID'] = BigWorld.PyGroundEffectManager().loadAirstrike(section['airstrike'])
        res['caliber'] = _xml.readNonNegativeFloat(xmlCtx, section, 'caliber')
        res['targetImpulse'] = _xml.readNonNegativeFloat(xmlCtx, section, 'targetImpulse')
        res['physicsParams'] = {'shellVelocity': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/shellVelocity'),
         'shellMass': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/shellMass'),
         'splashRadius': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/splashRadius'),
         'splashStrength': _xml.readNonNegativeFloat(xmlCtx, section, 'physicsParams/splashStrength')}
        res['armorHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorHit'))
        res['armorCriticalHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorCriticalHit'))
        res['armorResisted'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorResisted'))
        if section.has_key('armorSplashHit'):
            res['armorSplashHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorSplashHit'))
        if not artillery and not airstrike:
            model = _xml.readNonEmptyString(xmlCtx, section, 'projectile/model')
            modelOwnShot = section.readString('projectile/modelOwnShot', model)
            subsection = _xml.getSubsection(xmlCtx, section, 'projectile/effects')
            try:
                effects = EffectsList.EffectsList(subsection)
            except Exception as x:
                _xml.raiseWrongXml(xmlCtx, 'projectile/effects', str(x))

            res['projectile'] = (model, modelOwnShot, effects)
            if not section.has_key('waterParams'):
                res['waterParams'] = (2.0, 4.0)
            else:
                res['waterParams'] = (_xml.readPositiveFloat(xmlCtx, section, 'waterParams/shallowWaterDepth'), _xml.readPositiveFloat(xmlCtx, section, 'waterParams/rippleDiameter'))
            if section.has_key('armorBasicRicochet'):
                res['armorBasicRicochet'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorBasicRicochet'))
            else:
                res['armorBasicRicochet'] = res['armorResisted']
            if section.has_key('armorRicochet'):
                res['armorRicochet'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'armorRicochet'))
            else:
                res['armorRicochet'] = res['armorResisted']
            defSubEffName = EFFECT_MATERIALS[0] + 'Hit'
            res[defSubEffName] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, defSubEffName))
            for subEffName in EFFECT_MATERIALS[1:]:
                subEffName += 'Hit'
                if section.has_key(subEffName):
                    res[subEffName] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, subEffName))
                res[subEffName] = res[defSubEffName]

            if section.has_key('deepWaterHit'):
                res['deepWaterHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'deepWaterHit'))
            if section.has_key('shallowWaterHit'):
                res['shallowWaterHit'] = __readEffectsTimeLine(xmlCtx, _xml.getSubsection(xmlCtx, section, 'shallowWaterHit'))
            if not res.has_key('deepWaterHit'):
                v = res.get('shallowWaterHit')
                res['deepWaterHit'] = v if v else res[defSubEffName]
            if not res.has_key('shallowWaterHit'):
                res['shallowWaterHit'] = res['deepWaterHit']
    return res


def _readDamageStickers(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    ids = {}
    descrs = []
    for sname, subsection in section.items():
        sname = intern(sname)
        if sname in ('texture', 'xmlns:xmlref'):
            continue
        if ids.has_key(sname):
            _xml.raiseWrongXml(xmlCtx, sname, 'sticker name is not unique')
        ctx = (xmlCtx, sname)
        damageSticker = {}
        stickerID = len(descrs)
        damageSticker['priority'] = _xml.readInt(ctx, subsection, 'priority', 1)
        if IS_CLIENT:
            stickerID = _readAndRegisterDamageStickerTextureParams(ctx, subsection, sname, False)
            for i in xrange(1, 100):
                name = 'variant%d' % i
                if not subsection.has_key(name):
                    break
                stickerID = _readAndRegisterDamageStickerTextureParams(ctx, subsection[name], sname, True)

        damageSticker['id'] = stickerID
        ids[sname] = stickerID
        descrs.append(damageSticker)

    res = {'descrs': descrs,
     'ids': ids}
    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readAndRegisterDamageStickerTextureParams(xmlCtx, section, stickerName, raiseError):
    if not section.has_key('texName'):
        if raiseError:
            _xml.raiseWrongXml(xmlCtx, section.name, 'texName for damage sticker is not specified')
        return
    else:
        texAM = _xml.readNonEmptyString(xmlCtx, section, 'texName')
        texNM = _xml.readNonEmptyString(xmlCtx, section, 'bumpTexName') if section.has_key('bumpTexName') else ''
        texGMM = _xml.readNonEmptyString(xmlCtx, section, 'smTexName') if section.has_key('smTexName') else ''
        randomYaw = True
        subsection = section['randomYaw']
        if subsection is not None:
            randomYaw = subsection.asBool
        variation = section.readFloat('variation', 0.0)
        v = _xml.readPositiveVector2(xmlCtx, section, 'modelSizes')
        modelSizes = v.tuple()
        return BigWorld.wg_registerDamageSticker(stickerName, texAM, texNM, texGMM, modelSizes, variation, randomYaw)


def _readCommonConfig(xmlCtx, section):
    res = {}
    res['miscParams'] = {'projectileSpeedFactor': _xml.readPositiveFloat(xmlCtx, section, 'miscParams/projectileSpeedFactor'),
     'minFireStartingDamage': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/minFireStartingDamage'),
     'explosionDamageFactor': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/explosionDamageFactor'),
     'explosionDamageAbsorptionFactor': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/explosionDamageAbsorptionFactor'),
     'explosionEdgeDamageFactor': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/explosionEdgeDamageFactor'),
     'shellFragmentsDamageAbsorptionFactor': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/shellFragmentsDamageAbsorptionFactor'),
     'allowMortarShooting': _xml.readBool(xmlCtx, section, 'miscParams/allowMortarShooting'),
     'radarDefaults': {'radarRadius': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/radarDefaults/radarRadius'),
                       'radarCooldown': _xml.readNonNegativeFloat(xmlCtx, section, 'miscParams/radarDefaults/radarCooldown')}}
    res['damageByStaticsChances'] = {'tankman': _xml.readFraction(xmlCtx, section, 'damageByStaticsChances/tankman'),
     'module': _xml.readFraction(xmlCtx, section, 'damageByStaticsChances/module')}
    if IS_CLIENT or IS_EDITOR:
        v = {}
        for lodName in _xml.getSubsection(xmlCtx, section, 'lodLevels').keys():
            v[lodName] = _xml.readPositiveFloat(xmlCtx, section, 'lodLevels/' + lodName)

        res['lodLevels'] = v
        res['miscParams']['damageStickerAlpha'] = _xml.readPositiveFloat(xmlCtx, section, 'miscParams/damageStickerAlpha')
        name = _xml.readNonEmptyString(xmlCtx, section, 'miscParams/damageStickersLodDist')
        v = res['lodLevels'].get(name)
        if v is None:
            _xml.raiseWrongXml(xmlCtx, 'miscParams/damageStickersLodDist', "unknown lod level '%s'" % name)
        res['miscParams']['damageStickersLodDist'] = v
        res['defaultDamagedStateGroup'] = _xml.readStringWithDefaultValue(xmlCtx, section, 'damagedStateGroup', 'medium')
        res['defaultVehicleEffects'] = _readVehicleEffects(xmlCtx, section, 'defaultVehicleEffects')
        res['defaultTurretDetachmentEffects'] = _readTurretDetachmentEffects(xmlCtx, section, 'defaultTurretDetachmentEffects')
        res['miscParams']['explosionCandleVolumes'] = [ float(f) for f in _xml.readString(xmlCtx, section, 'miscParams/explosionCandleVolumes').split() ]
    if IS_CLIENT or IS_EDITOR or IS_CELLAPP:
        res['extras'], res['extrasDict'] = common_extras.readExtras(xmlCtx, section, 'extras', 'vehicle_extras')
        res['materials'], res['_autoDamageKindMaterials'] = _readMaterials(xmlCtx, section, 'materials', res['extrasDict'])
        res['deviceExtraIndexToTypeIndex'], res['tankmanExtraIndexToTypeIndex'] = _readDeviceTypes(xmlCtx, section, 'deviceExtras', res['extrasDict'])
        res['_devices'] = frozenset((res['extras'][idx] for idx in res['deviceExtraIndexToTypeIndex'].iterkeys()))
        effectVelPath = 'miscParams/collisionEffectVelocities/'
        res['miscParams']['collisionEffectVelocities'] = {'hull': _xml.readVector2(xmlCtx, section, effectVelPath + 'hull'),
         'track': _xml.readVector2(xmlCtx, section, effectVelPath + 'track'),
         'waterContact': _xml.readVector2(xmlCtx, section, effectVelPath + 'waterContact'),
         'ramming': _xml.readPositiveFloat(xmlCtx, section, effectVelPath + 'ramming')}
    elif IS_WEB:
        res['materials'], res['_autoDamageKindMaterials'] = _readMaterials(xmlCtx, section, 'materials', None)
    if IS_BOT:
        res['extras'], res['extrasDict'] = common_extras.readExtras(xmlCtx, section, 'extras', 'vehicle_extras')
        res['deviceExtraIndexToTypeIndex'], res['tankmanExtraIndexToTypeIndex'] = _readDeviceTypes(xmlCtx, section, 'deviceExtras', res['extrasDict'])
        res['_devices'] = frozenset((res['extras'][idx] for idx in res['deviceExtraIndexToTypeIndex'].iterkeys()))
    return res


def _readDeviceTypes(xmlCtx, section, subsectionName, extrasDict):
    resDevices = {}
    resTankmen = {}
    for res, kindName, typeNames in ((resDevices, 'devices', VEHICLE_DEVICE_TYPE_NAMES), (resTankmen, 'tankmen', VEHICLE_TANKMAN_TYPE_NAMES)):
        kindSectionName = subsectionName + '/' + kindName
        for extraName, subsection in _xml.getChildren(xmlCtx, section, kindSectionName):
            i = 0
            template = makeMultiExtraNameTemplate(extraName)
            extraInstanceName = template.format(i) if subsection.has_key('multiple') else extraName
            while extraInstanceName in extrasDict:
                try:
                    res[extrasDict[extraInstanceName].index] = typeNames.index(subsection.asString)
                except Exception as x:
                    _xml.raiseWrongXml((xmlCtx, kindSectionName), extraName, str(x))

                i += 1
                extraInstanceName = template.format(i)

    return (resDevices, resTankmen)


def _readMaterials(xmlCtx, section, subsectionName, extrasDict):
    materials = {}
    autoDamageKindMaterials = set()
    for materialKindName, subsection in _xml.getChildren(xmlCtx, section, subsectionName):
        ctx = (xmlCtx, subsectionName + '/' + materialKindName)
        materialKind = material_kinds.IDS_BY_NAMES.get(materialKindName)
        if materialKind is None:
            _xml.raiseWrongXml(ctx, '', 'material kind name is unknown')
        extra = None
        multipleExtra = _xml.readBool(ctx, subsection, 'multiple', False)
        extraName = subsection.readString('extra')
        if extraName:
            extra = extrasDict.get(extraName) if extrasDict is not None and not multipleExtra else extraName
            if extra is None:
                _xml.raiseWrongXml(ctx, '', "unknown extra '%s'" % extraName)
        extraIsNone = extra is None
        damageKind = 0
        if not extraIsNone:
            damageKindName = _xml.readString(ctx, subsection, 'damageKind')
            if damageKindName == 'armor':
                damageKind = 0
            elif damageKindName == 'device':
                damageKind = 1
            elif damageKindName == 'auto':
                damageKind = 1
                autoDamageKindMaterials.add(materialKind)
            else:
                _xml.raiseWrongXml(ctx, 'damageKind', 'wrong damage kind name')
        materials[materialKind] = shared_components.MaterialInfo(kind=materialKind, armor=None if extraIsNone else 0, extra=extra if not multipleExtra else makeMultiExtraNameTemplate(extra), multipleExtra=multipleExtra, vehicleDamageFactor=_xml.readFraction(ctx, subsection, 'vehicleDamageFactor'), useArmorHomogenization=_xml.readBool(ctx, subsection, 'useArmorHomogenization'), useHitAngle=_xml.readBool(ctx, subsection, 'useHitAngle'), useAntifragmentationLining=_xml.readBool(ctx, subsection, 'useAntifragmentationLining'), mayRicochet=_xml.readBool(ctx, subsection, 'mayRicochet'), collideOnceOnly=_xml.readBool(ctx, subsection, 'collideOnceOnly'), checkCaliberForRichet=_xml.readBool(ctx, subsection, 'checkCaliberForRichet'), checkCaliberForHitAngleNorm=_xml.readBool(ctx, subsection, 'checkCaliberForHitAngleNorm'), damageKind=damageKind, chanceToHitByProjectile=1.0 if extraIsNone else _xml.readFraction(ctx, subsection, 'chanceToHitByProjectile'), chanceToHitByExplosion=1.0 if extraIsNone else _xml.readFraction(ctx, subsection, 'chanceToHitByExplosion'), continueTraceIfNoHit=True if extraIsNone else _xml.readBool(ctx, subsection, 'continueTraceIfNoHit'))

    return (materials, autoDamageKindMaterials)


def _readArtefacts(xmlPath):
    import artefacts
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    objsByIDs = {}
    idsByNames = {}
    for name, subsection in section.items():
        ctx = (xmlCtx, name)
        if name in ('xmlns:xmlref',):
            continue
        name = intern(name)
        if name in idsByNames:
            _xml.raiseWrongXml(xmlCtx, name, 'name is not unique')
        className = _xml.readNonEmptyString(ctx, subsection, 'script')
        classObj = getattr(artefacts, className, None)
        if classObj is None:
            _xml.raiseWrongXml(ctx, 'script', "class '%s' is not found in '%s'" % (className, artefacts.__name__))
        instObj = classObj()
        instObj.init(ctx, subsection)
        _readPriceForItem(ctx, subsection, instObj.compactDescr)
        id = instObj.id[1]
        if id in objsByIDs:
            _xml.raiseWrongXml(ctx, '', 'id is not unique')
        objsByIDs[id] = instObj
        idsByNames[name] = id

    ResMgr.purge(xmlPath, True)
    return (objsByIDs, idsByNames)


def _joinCustomizationParams(nationID, commonDescr, customDescr):
    if not IS_CLIENT:
        if 'inscriptionColors' not in customDescr:
            if 'inscriptionColors' not in commonDescr:
                raise SoftException('inscriptionColors is not specified for nation=%s' % (nations.NAMES[nationID],))
            customDescr['inscriptionColors'] = commonDescr['inscriptionColors']
    for name in ('inscriptionGroups', 'inscriptions', 'camouflageGroups', 'camouflages'):
        intersection = set(commonDescr[name].iterkeys()).intersection(customDescr[name].iterkeys())
        if intersection:
            raise SoftException('there is unexpected intersection in %s, %s (%s)' % (name, nationID, intersection))
        customDescr[name].update(commonDescr[name])

    return customDescr


def _readCustomization(xmlPath, nationID, idsRange):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    res = {}
    if not IS_CLIENT and section.has_key('inscriptionColors'):
        res['inscriptionColors'] = _readColors(xmlCtx, section, 'inscriptionColors', NUM_INSCRIPTION_COLORS)
    pricesDest = _g_prices
    if pricesDest is None:
        priceFactors = notInShops = None
    else:
        priceFactors = pricesDest['inscriptionGroupPriceFactors'][nationID]
        notInShops = pricesDest['notInShopInscriptionGroups'][nationID]
    res['inscriptionGroups'], res['inscriptions'] = _readPlayerInscriptions(xmlCtx, section, 'inscriptions', priceFactors, notInShops, idsRange)
    camouflageGroups = {}
    if not IS_CLIENT:
        for groupName, subsection in _xml.getChildren(xmlCtx, section, 'camouflageGroups'):
            groupName = intern(groupName)
            if groupName in camouflageGroups:
                _xml.raiseWrongXml(xmlCtx, 'camouflages/' + groupName, 'camouflage group name is not unique')
            groupDescr = {'ids': []}
            if IS_WEB:
                groupDescr['userString'] = i18n.makeString(subsection.readString('userString'))
                groupDescr['hasNew'] = False
            groupDescr['igrType'] = _readIGRType(_xml, subsection)
            camouflageGroups[groupName] = groupDescr

    if pricesDest is None:
        priceFactors = notInShops = None
    else:
        priceFactors = pricesDest['camouflagePriceFactors'][nationID]
        notInShops = pricesDest['notInShopCamouflages'][nationID]
    camouflages = {}
    if not IS_CLIENT:
        for camName, subsection in _xml.getChildren(xmlCtx, section, 'camouflages'):
            ctx = (xmlCtx, 'camouflages/' + camName)
            camID, camDescr = _readCamouflage(ctx, subsection, camouflages, camouflageGroups, nationID, priceFactors, notInShops, idsRange)
            camDescr['name'] = camName
            camouflages[camID] = camDescr

    res['camouflageGroups'] = camouflageGroups
    res['camouflages'] = camouflages
    insigniaOnGun = {}
    for _, insigniaSubsection in _xml.getChildren(xmlCtx, section, 'insigniaOnGun'):
        rank = _xml.readInt(xmlCtx, insigniaSubsection, 'id', 0)
        textureName = _xml.readNonEmptyString(xmlCtx, insigniaSubsection, 'texName')
        bumpTextureName = insigniaSubsection['bumpTexName']
        bumpTextureName = bumpTextureName.asString if bumpTextureName is not None else ''
        insigniaOnGun[rank] = (textureName, bumpTextureName, False)

    res['insigniaOnGun'] = insigniaOnGun
    tintGroups = {}
    if section.has_key('tintGroup'):
        for tintName, subsection in _xml.getChildren(xmlCtx, section, 'tintGroup'):
            tintColor = _xml.readVector3(xmlCtx, subsection, 'color')
            tintGroups[tintName] = tintColor

        res['tintGroups'] = tintGroups
    section = None
    subsection = None
    ResMgr.purge(xmlPath, True)
    return res


def _readCamouflage(xmlCtx, section, ids, groups, nationID, priceFactors, notInShops, idsRange):
    id = _xml.readInt(xmlCtx, section, 'id', *idsRange)
    if id in ids:
        _xml.raiseWrongXml(xmlCtx, 'id', 'camouflage ID is not unique')
    kind = CAMOUFLAGE_KINDS.get(section.readString('kind'))
    if kind is None:
        _xml.raiseWrongSection(xmlCtx, 'kind')
    groupName = intern(_xml.readNonEmptyString(xmlCtx, section, 'group'))
    groupDescr = groups.get(groupName)
    if groupDescr is None:
        _xml.raiseWrongXml(xmlCtx, 'group', "unknown camouflage group name '%s'" % groupName)
    if priceFactors is not None:
        priceFactors[id] = _xml.readNonNegativeFloat(xmlCtx, section, 'priceFactor')
        if section.readBool('notInShop', False):
            notInShops.add(id)
    camouflage = {'kind': kind,
     'igrType': groupDescr['igrType'],
     'groupName': groupName,
     'invisibilityFactor': _xml.readNonNegativeFloat(xmlCtx, section, 'invisibilityFactor'),
     'allow': _readNationVehiclesByNames(xmlCtx, section, 'allow', nationID),
     'deny': _readNationVehiclesByNames(xmlCtx, section, 'deny', nationID),
     'requiredToken': section.readString('requiredToken', '')}
    isNew = False
    if IS_CLIENT or IS_EDITOR or IS_WEB:
        camouflage['description'] = section.readString('description')
        camouflage['texture'] = _xml.readNonEmptyString(xmlCtx, section, 'texture')
        camouflage['colors'] = _readColors(xmlCtx, section, 'colors', 4)
    if IS_CLIENT or IS_EDITOR:
        isNew = section.readBool('isNew', False)
        camouflage['isNew'] = isNew
        if IS_EDITOR:
            camouflage['tiling'], camouflage['tilingName'] = _readCamouflageTilings(xmlCtx, section, 'tiling', nationID)
        else:
            camouflage['tiling'] = _readCamouflageTilings(xmlCtx, section, 'tiling', nationID)
        camouflage['tilingSettings'] = _readCamouflageTilingSettings(xmlCtx, section)
    groupDescr['ids'].append(id)
    if isNew:
        groupDescr['hasNew'] = True
    tags = _xml.readStringOrNone(xmlCtx, section, 'tags')
    camouflage['tags'] = frozenset() if tags is None else frozenset(tags.split())
    return (id, camouflage)


def _writeCamouflageSettings(section, sectionName, camouflage):
    tilingKey = sectionName + '/tiling'
    if camouflage.tiling is not None and len(camouflage.tiling) == 4:
        tilingValue = Math.Vector4(camouflage.tiling[0], camouflage.tiling[1], camouflage.tiling[2], camouflage.tiling[3])
        _xml.rewriteVector4(section, tilingKey, tilingValue)
    maskKey = sectionName + '/exclusionMask'
    if camouflage.exclusionMask is not None and len(camouflage.exclusionMask) > 0:
        _xml.rewriteString(section, maskKey, camouflage.exclusionMask)
    densityKey = sectionName + '/density'
    if camouflage.density is not None and len(camouflage.density) == 2:
        densityValue = Math.Vector2(camouflage.density[0], camouflage.density[1])
        _xml.rewriteVector2(section, densityKey, densityValue, [1.0, 1.0])
    aoTextureSizeKey = sectionName + '/aoTextureSize'
    if camouflage.aoTextureSize is not None and len(camouflage.aoTextureSize) == 2:
        aoTextureValue = Math.Vector2(camouflage.aoTextureSize[0], camouflage.aoTextureSize[1])
        _xml.rewriteVector2(section, aoTextureSizeKey, aoTextureValue)
    return


def _readColors(xmlCtx, section, sectionName, requiredSize=None):
    res = []
    if not IS_CLIENT and not IS_BOT and not IS_WEB:
        for sname, subsection in _xml.getChildren(xmlCtx, section, sectionName):
            res.append(0)

    else:
        for sname, subsection in _xml.getChildren(xmlCtx, section, sectionName):
            res.append(_readColor((xmlCtx, sectionName + '/' + sname), subsection, ''))

    if requiredSize is not None and len(res) != requiredSize:
        _xml.raiseWrongXml(xmlCtx, sectionName, 'wrong number of items; required %d' % requiredSize)
    return tuple(res)


def _readColor(xmlCtx, section, sectionName):
    rgbaTuple = _xml.readTupleOfInts(xmlCtx, section, sectionName, 4)
    for c in rgbaTuple:
        if not 0 <= c < 256:
            _xml.raiseWrongXml(_xml, '', 'color component is out of range [0, 255]')

    return rgbaTuple[0] + (rgbaTuple[1] << 8) + (rgbaTuple[2] << 16) + (rgbaTuple[3] << 24)


def _readNationVehiclesByNames(xmlCtx, section, sectionName, defNationID):
    section = section[sectionName]
    if section is None:
        return frozenset()
    else:
        names = section.asString.split()
        if not names:
            return frozenset()
        if defNationID is not None:
            defNationNameTempl = nations.NAMES[defNationID] + ':'
        else:
            defNationNameTempl = ''
        res = set()
        for vehName in names:
            if vehName.find(':') == -1:
                vehName = defNationNameTempl + vehName
            try:
                vehTypeCompDescr = makeVehicleTypeCompDescrByName(vehName)
            except:
                _xml.raiseWrongXml(xmlCtx, sectionName, "unknown vehicle name '%s'" % vehName)

            res.add(vehTypeCompDescr)

        return frozenset(res)


VehicleValue = namedtuple('VehicleValue', ['vehicle_name',
 'compact_descriptor',
 'ctx',
 'subsection'])

def _vehicleValues(xmlCtx, section, sectionName, defNationID):
    section = section[sectionName]
    if section is None:
        return
    else:
        ctx = (xmlCtx, sectionName)
        for vehName, subsection in section.items():
            if vehName.find(':') == -1:
                vehName = nations.NAMES[defNationID] + ':' + vehName
            try:
                nationID, vehID = g_list.getIDsByName(vehName)
            except:
                _xml.raiseWrongXml(xmlCtx, sectionName, "unknown vehicle name '%s'" % vehName)

            yield VehicleValue(vehName, makeIntCompactDescrByID('vehicle', nationID, vehID), ctx, subsection)

        return


def _readCamouflageTilings(xmlCtx, section, sectionName, defNationID):
    res = {}
    nameMap = {}
    for v in _vehicleValues(xmlCtx, section, sectionName, defNationID):
        tiling = _xml.readTupleOfFloats(v.ctx, v.subsection, '', 4)
        if tiling[0] <= 0 or tiling[1] <= 0:
            _xml.raiseWrongSection(v.ctx, v.vehicle_name)
        res[v.compact_descriptor] = tiling
        if IS_EDITOR:
            nameMap[v.compact_descriptor] = v.vehicle_name

    return (res, nameMap) if IS_EDITOR else res


def _readCamouflageTilingSettings(xmlCtx, section):
    sectionName = 'tilingSettings'
    if not section.has_key(sectionName):
        return (CamouflageTilingType.LEGACY, None, None)
    else:
        subSection = _xml.getSubsection(xmlCtx, section, sectionName)
        return (_readCamouflageTilingType(xmlCtx, subSection), _xml.readTupleOfFloats(xmlCtx, subSection, 'factor', 2), _xml.readTupleOfFloats(xmlCtx, subSection, 'offset', 2))


def _readCamouflageTilingType(xmlCtx, section):
    readType = _xml.readNonEmptyString(xmlCtx, section, 'type')
    tilingType = CamouflageTilingTypeNameToType.get(upper(readType), None)
    if tilingType is None:
        _xml.raiseWrongXml(xmlCtx, '', "invalid tiling type '{}'".format(readType))
    return tilingType


def _readPlayerEmblems(xmlPath):
    section = ResMgr.openSection(xmlPath)
    if section is None:
        _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
    xmlCtx = (None, xmlPath)
    groups = {}
    emblems = {}
    names = {}
    pricesDest = _g_prices
    for sname, subsection in _xml.getChildren(xmlCtx, section, ''):
        groupCtx = (xmlCtx, sname)
        if groups.has_key(sname):
            _xml.raiseWrongXml(groupCtx, '', 'emblem group name is not unique')
        groupName = intern(sname)
        igrType = _readIGRType(groupCtx, subsection)
        nations = _readNations(groupCtx, subsection)
        allow = _readNationVehiclesByNames(groupCtx, subsection, 'allow', None)
        deny = _readNationVehiclesByNames(groupCtx, subsection, 'deny', None)
        if pricesDest is not None:
            pricesDest['playerEmblemGroupPriceFactors'][groupName] = _xml.readNonNegativeFloat(groupCtx, subsection, 'priceFactor')
            if subsection.readBool('notInShop', False):
                pricesDest['notInShopPlayerEmblemGroups'].add(groupName)
            elif IS_CLIENT:
                continue
        groupUserString = None
        emblemIDs = []
        for sname, subsection in _xml.getChildren(groupCtx, subsection, 'emblems'):
            ctx = (groupCtx, sname)
            if names.has_key(sname):
                _xml.raiseWrongXml(ctx, '', 'emblem name is not unique')
            emblemID = _xml.readInt(ctx, subsection, 'id', 1, 65535)
            if emblems.has_key(emblemID):
                _xml.raiseWrongXml(ctx, '', 'emblem ID is not unique')
            if IS_CLIENT or IS_WEB:
                emblemUserString = i18n.makeString('')
                texName = _xml.readNonEmptyString(ctx, subsection, 'texName')
                bumpSubsection = subsection['bumpTexName']
                if bumpSubsection is None:
                    bumpTexName = ''
                else:
                    bumpTexName = bumpSubsection.asString
                canBeMirrored = subsection.readBool('mirror', False)
            else:
                emblemUserString = None
                texName = ''
                bumpTexName = ''
                canBeMirrored = False
            tags = _xml.readStringOrNone(ctx, subsection, 'tags')
            tags = frozenset() if tags is None else frozenset(tags.split())
            emblemIDs.append(emblemID)
            emblems[emblemID] = (groupName,
             igrType,
             texName,
             bumpTexName,
             emblemUserString,
             canBeMirrored,
             tags)
            if sname != 'emblem':
                names[intern(sname)] = emblemID

        groups[groupName] = (emblemIDs,
         groupUserString,
         igrType,
         nations,
         allow,
         deny)

    ResMgr.purge(xmlPath, True)
    return (groups, emblems, names)


def _readPlayerInscriptions(xmlCtx, section, subsectionName, priceFactors, notInShops, idsRange):
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    xmlCtx = (xmlCtx, subsectionName)
    groups = {}
    inscrs = {}
    for sname, subsection in _xml.getChildren(xmlCtx, section, ''):
        groupCtx = (xmlCtx, sname)
        if groups.has_key(sname):
            _xml.raiseWrongXml(groupCtx, '', 'inscription group name is not unique')
        groupName = intern(sname)
        igrType = _readIGRType(_xml, subsection)
        allow = _readNationVehiclesByNames(_xml, subsection, 'allow', None)
        deny = _readNationVehiclesByNames(_xml, subsection, 'deny', None)
        if priceFactors is not None:
            priceFactors[groupName] = _xml.readNonNegativeFloat(groupCtx, subsection, 'priceFactor')
            if subsection.readBool('notInShop', False):
                notInShops.add(groupName)
            elif IS_CLIENT:
                continue
        groupUserString = None
        inscrIDs = []
        for sname, subsection in _xml.getChildren(groupCtx, subsection, 'inscriptions'):
            ctx = (groupCtx, sname)
            if sname != 'inscription':
                _xml.raiseWrongXml(ctx, '', 'unknown subsection')
            inscrID = _xml.readInt(ctx, subsection, 'id', *idsRange)
            if inscrs.has_key(inscrID):
                _xml.raiseWrongXml(ctx, '', 'inscription ID is not unique')
            tags = _xml.readStringOrNone(ctx, subsection, 'tags')
            tags = frozenset() if tags is None else frozenset(tags.split())
            if IS_CLIENT or IS_WEB:
                texName = _xml.readNonEmptyString(ctx, subsection, 'texName')
                bumpTexName = subsection.readString('bumpTexName', '')
                inscrUserString = i18n.makeString(None)
                isFeatured = subsection.readBool('isFeatured', False)
                inscrs[inscrID] = (groupName,
                 igrType,
                 texName,
                 bumpTexName,
                 inscrUserString,
                 isFeatured,
                 tags)
            else:
                inscrs[inscrID] = (groupName, igrType, tags)
            inscrIDs.append(inscrID)

        groups[groupName] = (inscrIDs,
         groupUserString,
         igrType,
         allow,
         deny)

    return (groups, inscrs)


def _readVehicleEffects(xmlCtx, section, subsectionName, defaultEffects=None, useOverride=False):
    section = _xml.getSubsection(xmlCtx, section, subsectionName)
    cachedEffects = g_cache._vehicleEffects
    personalEffects = __readEffectGroupsFromSection(section, (xmlCtx, subsectionName), withSubgroups=True) if useOverride else None
    damagedStateGroupPath = 'damagedStateGroup'
    damagedStateGroupName = _xml.readStringOrNone(xmlCtx, section, damagedStateGroupPath)
    res = __readDamagedStateEffects(xmlCtx, damagedStateGroupName, personalEffects, cachedEffects, defaultEffects)
    res.update(__readNormalEffects(xmlCtx, section, personalEffects, cachedEffects, defaultEffects))
    res['explosion'] = res['ammoBayExplosion']
    return (res, damagedStateGroupName) if IS_EDITOR else res


def __readDamagedStateEffects(xmlCtx, damagedStateGroupName, personalEffects, cachedEffects, defaultEffects):
    res = {}
    for effectKind in _damagedStateGroupEffectKindNames:
        effect = personalEffects.get(effectKind) if personalEffects is not None and len(personalEffects) > 0 else None
        if effect is None:
            if damagedStateGroupName is not None:
                effect = cachedEffects.get(damagedStateGroupName + effectKind[0].upper() + effectKind[1:])
            elif defaultEffects is not None:
                effect = defaultEffects.get(effectKind)
            else:
                _xml.raiseWrongXml((xmlCtx, damagedStateGroupName), '', "subsection effect group '%s' is missing" % damagedStateGroupName)
        if effect is None:
            _xml.raiseWrongXml((xmlCtx, damagedStateGroupName), '', 'missing effect or mismatching effect group name (%s is not found)' % effectKind)
        res[effectKind] = effect

    return res


def __readNormalEffects(xmlCtx, section, personalEffects, cachedEffects, defaultEffects):
    res = {}
    for effectKind in _vehicleEffectKindNames:
        effect = personalEffects.get(effectKind) if personalEffects is not None and len(personalEffects) > 0 else None
        if effect is None:
            subsection = section[effectKind]
            if subsection is not None:
                effectName = subsection.asString
                effect = cachedEffects.get(effectName)
                if effect is None:
                    _xml.raiseWrongXml((xmlCtx, section.asString), effectKind, 'missing or wrong effect name')
            elif defaultEffects is not None:
                effect = defaultEffects.get(effectKind)
        if effect is not None:
            res[effectKind] = effect

    return res


def _readTurretDetachmentEffects(xmlCtx, section, subsectionName, defaultEffects=None):
    if defaultEffects is None:
        defaultEffects = {}
    res = {}
    detachmentEffectsSection = section[subsectionName]

    def getEffect(effectSection, defaultEffect, state):
        if effectSection is not None:
            effectName = effectSection.asString
            return g_cache._turretDetachmentEffects.get(effectName)
        else:
            return defaultEffect if defaultEffect is not None else None

    for detachmentState in ('flight', 'flamingOnGround'):
        effectSection = None
        if detachmentEffectsSection is not None:
            effectSection = detachmentEffectsSection[detachmentState]
        effect = getEffect(effectSection, defaultEffects.get(detachmentState), detachmentState)
        if effect:
            res[detachmentState] = effect

    for collisionEffectType in ('collision', 'pull'):
        collisionEffectsSection = None
        if detachmentEffectsSection is not None:
            collisionEffectsSection = detachmentEffectsSection[collisionEffectType]
        resultCollisionEffects = {}
        defaultCollisionEffects = defaultEffects.get(collisionEffectType, {})
        for effectMaterial in material_kinds.EFFECT_MATERIALS:
            effectIdx = material_kinds.EFFECT_MATERIAL_INDEXES_BY_NAMES[effectMaterial]
            effectSection = None
            if collisionEffectsSection is not None:
                effectSection = collisionEffectsSection[effectMaterial]
            effect = getEffect(effectSection, defaultCollisionEffects.get(effectIdx), effectMaterial)
            if effect:
                resultCollisionEffects[effectIdx] = effect

        res[collisionEffectType] = resultCollisionEffects

    return res


if IS_CLIENT or IS_EDITOR:
    _vehicleEffectKindNames = tuple(['collisionVehicleLight',
     'collisionVehicleHeavy',
     'collisionVehicleHeavy1',
     'collisionVehicleHeavy2',
     'collisionVehicleHeavy3',
     'rammingCollisionLight',
     'rammingCollisionHeavy',
     'collisionDamage'] + [ '%sCollisionLight' % name for name in EFFECT_MATERIALS ] + [ '%sCollisionHeavy' % name for name in EFFECT_MATERIALS ] + [ 'explosionCandle%d' % i for i in xrange(1, 5) ] + ['fullDestruction'] + ['dynamicCollision'])
    _damagedStateGroupEffectKindNames = ('ammoBayExplosion',
     'ammoBayBurnOff',
     'fuelExplosion',
     'destruction',
     'crewDeath',
     'rammingDestruction',
     'submersionDeath',
     'flaming',
     'instantExplosion')

def _readClientAdjustmentFactors(xmlCtx, section):
    return {'power': section.readFloat('clientAdjustmentFactors/power', 1.0),
     'armour': section.readFloat('clientAdjustmentFactors/armour', 1.0),
     'mobility': section.readFloat('clientAdjustmentFactors/mobility', 1.0),
     'visibility': section.readFloat('clientAdjustmentFactors/visibility', 1.0),
     'camouflage': section.readFloat('clientAdjustmentFactors/camouflage', 1.0),
     'guns': _readClientAdjustmentSection(xmlCtx, section, 'clientAdjustmentFactors/guns', 'caliberCorrection', 'delta', False)}


def _readSiegeModeParams(xmlCtx, section, vehType):
    subSection = section['siege_mode']
    if subSection is None:
        return
    else:
        res = {'switchOnTime': _xml.readNonNegativeFloat(xmlCtx, subSection, 'switchOnTime', 2.0),
         'switchOffTime': _xml.readNonNegativeFloat(xmlCtx, subSection, 'switchOffTime', 2.0),
         'switchCancelEnabled': subSection.readBool('switchCancelEnabled', False),
         'engineDamageCoeff': _xml.readNonNegativeFloat(xmlCtx, subSection, 'engineDamageCoeff', 2.0)}
        if 'autoSiege' in vehType.tags:
            res.update({'autoSwitchOffRequiredVehicleSpeed': component_constants.KMH_TO_MS * _xml.readNonNegativeFloat(xmlCtx, subSection, 'autoSwitchOffRequiredVehicleSpeed', 1.0),
             'autoSwitchOnRequiredVehicleSpeed': component_constants.KMH_TO_MS * _xml.readNonNegativeFloat(xmlCtx, subSection, 'autoSwitchOnRequiredVehicleSpeed', 0.1)})
        if IS_CLIENT or IS_EDITOR:
            res['soundStateChange'] = sound_readers.readSoundSiegeModeStateChange(xmlCtx, subSection)
            res[VEHICLE_SIEGE_STATE.SWITCHING_ON] = {'normal': res['switchOnTime'],
             'critical': res['switchOnTime'] * res['engineDamageCoeff'],
             'destroyed': res['switchOnTime'] * res['engineDamageCoeff']}
            res[VEHICLE_SIEGE_STATE.SWITCHING_OFF] = {'normal': res['switchOffTime'],
             'critical': res['switchOffTime'] * res['engineDamageCoeff'],
             'destroyed': res['switchOffTime'] * res['engineDamageCoeff']}
        return res


def _readGunDualGunParams(xmlCtx, section):
    subSection = section['dualGun']
    if subSection is None:
        return
    else:
        res = component_constants.DualGun(chargeTime=_xml.readNonNegativeFloat(xmlCtx, subSection, 'chargeTime'), shootImpulse=_xml.readNonNegativeInt(xmlCtx, subSection, 'shootImpulse'), reloadLockTime=_xml.readNonNegativeFloat(xmlCtx, subSection, 'reloadLockTime'), reloadTimes=_xml.readTupleOfPositiveFloats(xmlCtx, subSection, 'reloadTimes'), rateTime=_xml.readNonNegativeFloat(xmlCtx, subSection, 'rateTime'), chargeThreshold=_xml.readNonNegativeFloat(xmlCtx, subSection, 'chargeThreshold'), afterShotDelay=_xml.readNonNegativeFloat(xmlCtx, subSection, 'afterShotDelay'), preChargeIndication=_xml.readNonNegativeFloat(xmlCtx, subSection, 'preChargeIndication'), chargeCancelTime=_xml.readNonNegativeFloat(xmlCtx, subSection, 'chargeCancelTime', 0.2))
        return res


def _readHullAimingParams(xmlCtx, section):
    res = {'pitch': {'isAvailable': section.has_key('hull_aiming/pitch') != 0,
               'isEnabled': section.readBool('hull_aiming/pitch/isEnabled'),
               'isFlexible': section.readBool('hull_aiming/pitch/isFlexible'),
               'wheelCorrectionCenterZ': _xml.readFloat(xmlCtx, section, 'hull_aiming/pitch/wheelCorrectionCenterZ', 0.0),
               'wheelsCorrectionSpeed': radians(_xml.readPositiveFloat(xmlCtx, section, 'hull_aiming/pitch/wheelsCorrectionSpeed', 0.0)),
               'wheelsCorrectionAngles': {'pitchMin': radians(_xml.readFloat(xmlCtx, section, 'hull_aiming/pitch/wheelsCorrectionAngles/pitchMin', 0)),
                                          'pitchMax': radians(_xml.readFloat(xmlCtx, section, 'hull_aiming/pitch/wheelsCorrectionAngles/pitchMax', 0))}},
     'yaw': {'isAvailable': section.has_key('hull_aiming') != 0 and not section.has_key('hull_aiming/yawDisabled')}}
    return res


def __readRotationAngleLimits(xmlCtx, section, name):
    v = _xml.readVector2(xmlCtx, section, name)
    if v[0] > v[1]:
        _xml.raiseWrongSection(xmlCtx, name)
    return (radians(v[0]), radians(v[1])) if v[0] > -179.0 or v[1] < 179.0 else None


def _readClientAdjustmentSection(xmlCtx, section, subsectionName, privateFactorName, publicFactorName, throwIfMissing=True):
    res = {}
    subsection = _xml.getSubsection(xmlCtx, section, subsectionName, throwIfMissing)
    if subsection is None:
        return res
    else:
        for name in subsection.keys():
            res.setdefault(name, {}).setdefault(privateFactorName, subsection.readFloat(name + '/' + publicFactorName))

        return res


def _extractNeededPrereqs(prereqs, resourceNames):
    resourceNames = frozenset(resourceNames)
    res = []
    for name in resourceNames:
        try:
            if name not in g_cache.requestOncePrereqs:
                res.append(prereqs[name])
                g_cache.requestOncePrereqs.add(name)
        except Exception:
            if name not in g_cache.requestOncePrereqs:
                LOG_WARNING('Resource is not found: %s' % name)
            else:
                res.append(None)

    return res


def _readAODecals(xmlCtx, section, secname):
    res = []
    if section.has_key(secname):
        for subname, subsection in _xml.getChildren(xmlCtx, section, secname):
            m = subsection.readMatrix('transform')
            res.append(m)

    return tuple(res)


def _writeAODecals(decalsList, section, secname):
    decalId = 0
    if section.has_key(secname):
        for subname, subsection in _xml.getChildren(None, section, secname):
            _xml.rewriteMatrix(subsection, 'transform', decalsList[decalId])
            decalId += 1

    return


def _readRepaintParams(xmlCtx, section):
    res = {}
    if not section.has_key('refColor') or not section.has_key('refGloss') or not section.has_key('refColorMult') or not section.has_key('refGlossMult'):
        return res
    res['refColor'] = _xml.readVector3(xmlCtx, section, 'refColor')
    res['refGloss'] = _xml.readFloat(xmlCtx, section, 'refGloss')
    res['refColorMult'] = _xml.readFloat(xmlCtx, section, 'refColorMult')
    res['refGlossMult'] = _xml.readFloat(xmlCtx, section, 'refGlossMult')
    return res


def _readImpactParams(xmlCtx, section, paramName):
    subXmlCtx, subsection = _xml.getSubSectionWithContext(xmlCtx, section, paramName, throwIfMissing=False)
    params = HighExplosiveImpactParams()
    if subsection is None:
        params.radius = 0.0
        params.damages = (0.0, 0.0)
        params.isActive = False
        return params
    else:
        params.radius = _xml.readNonNegativeFloat(subXmlCtx, subsection, 'impactRadius', 0.0)
        params.damages = (_xml.readNonNegativeFloat(subXmlCtx, subsection, 'damage/armor', 0.0), _xml.readNonNegativeFloat(subXmlCtx, subsection, 'damage/devices', 0.0))
        if paramName == 'armorSpalls':
            params.coneAngleCos = cos(radians(_xml.readNonNegativeFloat(subXmlCtx, subsection, 'coneAngle')))
            params.piercingSpalls = _xml.readBool(subXmlCtx, subsection, 'piercingSpalls', component_constants.DEFAULT_PIERCING_SPALLS)
        if subsection.has_key('damageAbsorption'):
            label = _xml.readNonEmptyString(subXmlCtx, subsection, 'damageAbsorption')
            params.damageAbsorptionType = DamageAbsorptionLabelToType.get(label)
        params.isActive = params.radius and (params.damages[0] or params.damages[1])
        return params


def _readBrokenWheelLosses(xmlCtx, section, axleIsLeading, axleCanBeRised, wheelRiseHeight):

    def readLoss(paramName, minCount):
        if section[paramName] is None:
            return (0.0,) * minCount
        else:
            loss = _xml.readTupleOfFloats(xmlCtx, section, paramName)
            if len(loss) < minCount:
                _xml.raiseWrongXml(xmlCtx, paramName, 'at least %d floats expected' % minCount)
            return loss

    leadingAxleCount = len([ v for v in axleIsLeading if v is True ])
    groundedAxleCount = len([ v for v in axleCanBeRised if v is False ]) if wheelRiseHeight > 0.0 else len(axleCanBeRised)
    return (readLoss('brokenWheelPowerLoss', 2 * leadingAxleCount), readLoss('brokenWheelSpeedLoss', 2 * groundedAxleCount))


def _readOptDevsOverrides(xmlCtx, section):
    if section is None:
        return {}
    else:
        optDevsOverrides = {}
        for optDevName, optDevSection in section.items():
            for factorName, factorSection in optDevSection.items():
                factor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, optDevSection, factorName)
                optDevsOverrides.setdefault(optDevName, {})[factorName] = factor

        return optDevsOverrides


def _descrByID(descrList, id):
    for descr in descrList:
        if descr.id[1] == id:
            return descr

    raise SoftException('ID={} not found in descriptor list - {}'.format(id, descrList))


def _findDescrByID(descrList, id):
    for descr in descrList:
        if descr.id[1] == id:
            return descr

    return None


def _collectComponents(compactDescrs, compList):
    compactDescrs.update([ x.compactDescr for x in compList ])


def _collectReqItemsRecursively(destSet, rootSet, reqItems):
    for compactDescr in rootSet:
        if compactDescr not in destSet:
            destSet.add(compactDescr)
            _collectReqItemsRecursively(destSet, tuple(reqItems.get(compactDescr, ())), reqItems)


def _selectCrewExtras(crewRoles, extrasDict):
    res = []
    idxsInRoles = {}
    for role in crewRoles:
        role = role[0]
        if role not in ('commander', 'driver'):
            idxInRole = idxsInRoles.get(role, 1)
            idxsInRoles[role] = idxInRole + 1
            role += str(idxInRole)
        res.append(extrasDict[role + 'Health'])

    return tuple(res)


def _summPriceDiff(price, priceAdd, priceSub):
    return (price[0] + priceAdd[0] - priceSub[0], price[1] + priceAdd[1] - priceSub[1])


def _splitVehicleCompactDescr(compactDescr, vehMode=VEHICLE_MODE.DEFAULT, vehType=None):
    header = ord(compactDescr[0])
    vehicleTypeID = ord(compactDescr[1])
    nationID = header >> 4 & 15
    if vehType is None:
        type = g_cache.vehicle(nationID, vehicleTypeID, vehMode)
    else:
        type = vehType
    idx = 10 + len(type.turrets) * 4
    components = compactDescr[2:idx]
    flags = ord(compactDescr[idx])
    idx += 1
    count = 0
    optionalDeviceSlots = 0
    for i in xrange(0, MAX_OPTIONAL_DEVICES_SLOTS):
        if flags & 1 << i:
            count += 1
            optionalDeviceSlots |= 1 << i

    optionalDevices = compactDescr[idx:idx + count * 2]
    idx += count * 2
    if flags & 16:
        count = ord(compactDescr[idx])
        enhancements = compactDescr[idx:idx + 1 + count * 6]
        idx += 1 + count * 6
    else:
        enhancements = ''
    if flags & 32:
        emblemPositions = ord(compactDescr[idx])
        idx += 1
        count = 0
        for i in _RANGE_4:
            if emblemPositions & 1 << i:
                count += 1

        emblems = compactDescr[idx:idx + count * 6]
        idx += count * 6
        count = 0
        for i in _RANGE_4:
            if emblemPositions & 1 << i + 4:
                count += 1

        inscriptions = compactDescr[idx:idx + count * 7]
        idx += count * 7
    else:
        emblemPositions = 0
        emblems = ''
        inscriptions = ''
    if flags & 64:
        idx += 1
    if flags & 128:
        camouflages = compactDescr[idx:]
    else:
        camouflages = ''
    return (type,
     components,
     optionalDeviceSlots,
     optionalDevices,
     enhancements,
     emblemPositions,
     emblems,
     inscriptions,
     camouflages)


def _combineVehicleCompactDescr(type, components, optionalDeviceSlots, optionalDevices, enhancements, emblemPositions, emblems, inscriptions, camouflages):
    header = items.ITEM_TYPES.vehicle + (type.id[0] << 4)
    vehicleTypeID = type.id[1]
    flags = optionalDeviceSlots
    if enhancements:
        flags |= 16
    if emblems or inscriptions:
        flags |= 32
    if camouflages:
        flags |= 128
    cd = chr(header) + chr(vehicleTypeID) + components + chr(flags) + optionalDevices
    if enhancements:
        cd += enhancements
    if emblems or inscriptions:
        cd += chr(emblemPositions) + emblems + inscriptions
    if camouflages:
        cd += camouflages
    return cd


def _packIDAndDuration(id, startTime, durationDays):
    return struct.pack('<HI', id, (startTime - _CUSTOMIZATION_EPOCH) / 60 | durationDays << 24)


def _unpackIDAndDuration(cd):
    id, times = struct.unpack('<HI', cd)
    return (id, (times & 16777215) * 60 + _CUSTOMIZATION_EPOCH, times >> 24)


def _isWeightAllowedToChange(newWeights, prevWeights):
    prevWeight, prevMaxWeight = prevWeights
    newWeight, newMaxWeight = newWeights
    if prevWeight > prevMaxWeight and newWeight <= prevWeight:
        return True
    newReserve = newMaxWeight - newWeight
    return newReserve >= 0.0 or newReserve >= prevMaxWeight - prevWeight


@_xml.cacheFloatTuples
def cachedFloatTuple(args):
    return tuple(args)


def _deduceNamesFromTankXmlPath(xmlPath):
    parts = xmlPath.split('/')
    return (parts[-2], os.path.splitext(parts[-1])[0])


def findAmmoIndexByCompactDescr(ammo, compactDescr):
    for idx in xrange(0, len(ammo), 2):
        if ammo[idx] == compactDescr:
            return idx

    return None


def areOptDevicesLayoutsEqual(oldDevicesObjs, newDevicesCDs):
    oldDevicesCDs = [ (device.compactDescr if device is not None else 0) for device in oldDevicesObjs ]
    newDevicesCDs = newDevicesCDs or [0] * len(oldDevicesCDs)
    return oldDevicesCDs == newDevicesCDs


def reinstallOptionalDevices(vehDescr, newDevices):
    for slotIdx in xrange(len(vehDescr.optionalDevices)):
        vehDescr.removeOptionalDevice(slotIdx, rebuildAttrs=False)

    for slotIdx, compactDescr in enumerate(newDevices):
        if compactDescr != 0:
            vehDescr.installOptionalDevice(compactDescr, slotIdx, rebuildAttrs=False)

    vehDescr.rebuildAttrs()
    return vehDescr


VEHICLE_HEALTH_DECIMALS = 1
_EMPTY_EMBLEM = (None, _CUSTOMIZATION_EPOCH, 0)
_EMPTY_EMBLEMS = (_EMPTY_EMBLEM,
 _EMPTY_EMBLEM,
 _EMPTY_EMBLEM,
 _EMPTY_EMBLEM)
_EMPTY_INSCRIPTION = (None,
 _CUSTOMIZATION_EPOCH,
 0,
 0)
_EMPTY_INSCRIPTIONS = (_EMPTY_INSCRIPTION,
 _EMPTY_INSCRIPTION,
 _EMPTY_INSCRIPTION,
 _EMPTY_INSCRIPTION)
_EMPTY_CAMOUFLAGE = (None, _CUSTOMIZATION_EPOCH, 0)
_EMPTY_CAMOUFLAGES = (_EMPTY_CAMOUFLAGE, _EMPTY_CAMOUFLAGE, _EMPTY_CAMOUFLAGE)
_RANGE_4 = range(4)
_VEHICLE = items.ITEM_TYPES['vehicle']
_CHASSIS = items.ITEM_TYPES['vehicleChassis']
_TURRET = items.ITEM_TYPES['vehicleTurret']
_GUN = items.ITEM_TYPES['vehicleGun']
_ENGINE = items.ITEM_TYPES['vehicleEngine']
_FUEL_TANK = items.ITEM_TYPES['vehicleFuelTank']
_RADIO = items.ITEM_TYPES['vehicleRadio']
_TANKMAN = items.ITEM_TYPES['tankman']
_OPTIONALDEVICE = items.ITEM_TYPES['optionalDevice']
_SHELL = items.ITEM_TYPES['shell']
_EQUIPMENT = items.ITEM_TYPES['equipment']
