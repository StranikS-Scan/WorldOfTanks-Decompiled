# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/artefacts.py
import items
import nations
import math
from items import _xml, vehicles
from constants import IS_CLIENT, IS_CELLAPP, IS_WEB, VEHICLE_TTC_ASPECTS
from functools import partial
from items.basic_item import BasicItem
from items.components import shared_components, component_constants
from tankmen import MAX_SKILL_LEVEL

class Artefact(BasicItem):
    __slots__ = ('name', 'id', 'compactDescr', 'tags', 'i18n', 'icon', 'removable', 'price', 'showInShop', 'stunResistanceEffect', 'stunResistanceDuration', '_vehWeightFraction', '_weight', '_maxWeightChange', '__vehicleFilter', '__artefactFilter')

    def __init__(self, typeID, itemID, itemName, compactDescr):
        super(Artefact, self).__init__(typeID, itemID, itemName, compactDescr)
        self.icon = None
        self.removable = False
        self.price = None
        self.showInShop = False
        self.stunResistanceEffect = component_constants.ZERO_FLOAT
        self.stunResistanceDuration = component_constants.ZERO_FLOAT
        self._vehWeightFraction = component_constants.ZERO_FLOAT
        self._weight = component_constants.ZERO_FLOAT
        self._maxWeightChange = component_constants.ZERO_FLOAT
        self.__vehicleFilter = None
        self.__artefactFilter = None
        return

    def init(self, xmlCtx, section):
        self._readBasicConfig(xmlCtx, section)
        xmlCtx = (xmlCtx, 'script')
        section = section['script']
        self._readWeight(xmlCtx, section)
        self._readStun(xmlCtx, section)
        self._readConfig(xmlCtx, section)

    def updatePrice(self, newPrice, showInShop):
        self.price = newPrice
        self.showInShop = showInShop

    def extraName(self):
        pass

    def _readWeight(self, xmlCtx, section):
        if section.has_key('vehicleWeightFraction'):
            self._vehWeightFraction = _xml.readNonNegativeFloat(xmlCtx, section, 'vehicleWeightFraction')
        else:
            self._vehWeightFraction = 0.0
        if section.has_key('weight'):
            self._weight = _xml.readNonNegativeFloat(xmlCtx, section, 'weight')
        else:
            self._weight = 0.0
        self._maxWeightChange = 0.0

    def _readStun(self, xmlCtx, section):
        self.stunResistanceEffect, self.stunResistanceDuration = _readStun(xmlCtx, section)

    def weightOnVehicle(self, vehicleDescr):
        return (self._vehWeightFraction, self._weight, 0.0)

    def checkCompatibilityWithVehicle(self, vehicleDescr):
        return (True, None) if self.__vehicleFilter is None else self.__vehicleFilter.checkCompatibility(vehicleDescr)

    def checkCompatibilityWithOther(self, other):
        if self is other:
            return False
        else:
            filter = self.__artefactFilter
            return True if filter is None else not filter.inInstalled(other.tags)

    def checkCompatibilityWithActiveOther(self, other):
        if self is other:
            return False
        else:
            filter = self.__artefactFilter
            return True if filter is None else not filter.inActive(other.tags)

    def _readConfig(self, xmlCtx, scriptSection):
        pass

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        pass

    def _readBasicConfig(self, xmlCtx, section):
        self.name = section.name
        self.id = (nations.NONE_INDEX, _xml.readInt(xmlCtx, section, 'id', 0, 65535))
        self.compactDescr = vehicles.makeIntCompactDescrByID(self.itemTypeName, *self.id)
        if not section.has_key('tags'):
            self.tags = frozenset()
        else:
            self.tags = _readTags(xmlCtx, section, 'tags', self.itemTypeName)
        if IS_CLIENT or IS_WEB:
            self.i18n = shared_components.I18nComponent(section.readString('userString'), section.readString('description'))
            self.icon = _xml.readIcon(xmlCtx, section, 'icon')
        if IS_CELLAPP or not section.has_key('vehicleFilter'):
            self.__vehicleFilter = None
        else:
            self.__vehicleFilter = _VehicleFilter((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        if not section.has_key('incompatibleTags'):
            self.__artefactFilter = None
        else:
            self.__artefactFilter = _ArtefactFilter((xmlCtx, 'incompatibleTags'), section['incompatibleTags'], self.itemTypeName)
        self.removable = section.readBool('removable', False)
        return

    @staticmethod
    def findActualAttribute(factors, attribute):
        if attribute not in factors:
            if attribute.startswith('gun/'):
                return 'turrets/0/{}'.format(attribute)
        return attribute


class OptionalDevice(Artefact):
    __slots__ = ()

    def __init__(self):
        super(OptionalDevice, self).__init__(items.ITEM_TYPES.optionalDevice, 0, '', 0)

    def extraName(self):
        return None

    def updateVehicleDescrAttrs(self, vehicleDescr):
        pass


class Equipment(Artefact):
    __slots__ = ('equipmentType', 'reuseCount', 'cooldownSeconds')

    def __init__(self):
        super(Equipment, self).__init__(items.ITEM_TYPES.equipment, 0, '', 0)
        self.equipmentType = None
        self.reuseCount = component_constants.ZERO_INT
        self.cooldownSeconds = component_constants.ZERO_INT
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(Equipment, self)._readBasicConfig(xmlCtx, section)
        self.equipmentType = items.EQUIPMENT_TYPES[section.readString('type', 'regular')]

    def _readStun(self, xmlCtx, section):
        super(Equipment, self)._readStun(xmlCtx, section)
        self.reuseCount, self.cooldownSeconds = _readReuseParams(xmlCtx, section)

    def extraName(self):
        return self.name

    def checkCompatibilityWithEquipment(self, other):
        return self.checkCompatibilityWithOther(other)

    def checkCompatibilityWithActiveEquipment(self, other):
        return self.checkCompatibilityWithActiveOther(other)


class StaticFactorDevice(OptionalDevice):
    __slots__ = ('__attr', '__factor')

    def __init__(self):
        super(StaticFactorDevice, self).__init__()
        self.__attr = None
        self.__factor = component_constants.ZERO_FLOAT
        return

    def updateVehicleDescrAttrs(self, vehicleDescr):
        if len(self.__attr) == 1:
            attrDict = vehicleDescr.__dict__
            attrName = self.__attr[0]
        else:
            attrDict = getattr(vehicleDescr, self.__attr[0])
            attrName = self.__attr[1]
        val = attrDict[attrName]
        if isinstance(val, int):
            attrDict[attrName] = int(val * self.__factor)
        else:
            attrDict[attrName] = val * self.__factor
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration

    def _readConfig(self, xmlCtx, section):
        self.__factor = _xml.readPositiveFloat(xmlCtx, section, 'factor')
        self.__attr = _xml.readNonEmptyString(xmlCtx, section, 'attribute').split('/', 1)


class StaticAdditiveDevice(OptionalDevice):
    __slots__ = ('__attr', '__value')

    def __init__(self):
        super(StaticAdditiveDevice, self).__init__()
        self.__attr = None
        self.__value = component_constants.ZERO_FLOAT
        return

    def updateVehicleDescrAttrs(self, vehicleDescr):
        if len(self.__attr) == 1:
            attrDict = vehicleDescr.__dict__
            attrName = self.__attr[0]
        else:
            attrDict = getattr(vehicleDescr, self.__attr[0])
            attrName = self.__attr[1]
        val = attrDict[attrName]
        if isinstance(val, int):
            attrDict[attrName] = int(val + self.__value)
        else:
            attrDict[attrName] = val + self.__value
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration

    def _readConfig(self, xmlCtx, section):
        self.__value = _xml.readFloat(xmlCtx, section, 'value')
        self.__attr = _xml.readNonEmptyString(xmlCtx, section, 'attribute').split('/', 1)


class Stereoscope(OptionalDevice):
    __slots__ = ('activateWhenStillSec', 'circularVisionRadiusFactor')

    def __init__(self):
        super(Stereoscope, self).__init__()
        self.activateWhenStillSec = component_constants.ZERO_FLOAT
        self.circularVisionRadiusFactor = component_constants.ZERO_FLOAT

    def extraName(self):
        return self.name

    def _readConfig(self, xmlCtx, section):
        self.activateWhenStillSec = _xml.readNonNegativeFloat(xmlCtx, section, 'activateWhenStillSec')
        self.circularVisionRadiusFactor = _xml.readPositiveFloat(xmlCtx, section, 'circularVisionRadiusFactor')

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        if aspect not in (VEHICLE_TTC_ASPECTS.DEFAULT, VEHICLE_TTC_ASPECTS.WHEN_STILL):
            return
        factorToCompensate = vehicleDescr.miscAttrs['circularVisionRadiusFactor']
        factors['circularVisionRadius'] = self.circularVisionRadiusFactor / factorToCompensate


class CamouflageNet(OptionalDevice):
    __slots__ = ('activateWhenStillSec',)

    def __init__(self):
        super(CamouflageNet, self).__init__()
        self.activateWhenStillSec = component_constants.ZERO_FLOAT

    def extraName(self):
        return self.name

    def _readConfig(self, xmlCtx, section):
        self.activateWhenStillSec = _xml.readNonNegativeFloat(xmlCtx, section, 'activateWhenStillSec')

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        if aspect not in (VEHICLE_TTC_ASPECTS.WHEN_STILL,):
            return
        factors['invisibility'][0] += vehicleDescr.type.invisibilityDeltas['camouflageNetBonus']


class EnhancedSuspension(OptionalDevice):
    __slots__ = ('__chassisMaxLoadFactor', '__chassisHealthFactor', '__vehicleByChassisDamageFactor')

    def __init__(self):
        super(EnhancedSuspension, self).__init__()
        self.__chassisMaxLoadFactor = component_constants.ZERO_FLOAT
        self.__chassisHealthFactor = component_constants.ZERO_FLOAT
        self.__vehicleByChassisDamageFactor = component_constants.ZERO_FLOAT

    def weightOnVehicle(self, vehicleDescr):
        chassis = vehicleDescr.chassis
        return (self._vehWeightFraction, self._weight, chassis.maxLoad * (self.__chassisMaxLoadFactor - 1.0))

    def _readConfig(self, xmlCtx, section):
        reader = partial(_xml.readPositiveFloat, xmlCtx, section)
        self.__chassisMaxLoadFactor = reader('chassisMaxLoadFactor')
        self.__chassisHealthFactor = reader('chassisHealthFactor')
        self.__vehicleByChassisDamageFactor = reader('vehicleByChassisDamageFactor')

    def updateVehicleDescrAttrs(self, vehicleDescr):
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['chassisHealthFactor'] *= self.__chassisHealthFactor
        miscAttrs['vehicleByChassisDamageFactor'] *= self.__vehicleByChassisDamageFactor
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration


class Grousers(OptionalDevice):
    __slots__ = ('__factorSoft', '__factorMedium')

    def __init__(self):
        super(Grousers, self).__init__()
        self.__factorSoft = component_constants.ZERO_FLOAT
        self.__factorMedium = component_constants.ZERO_FLOAT

    def updateVehicleDescrAttrs(self, vehicleDescr):
        r = vehicleDescr.physics['terrainResistance']
        vehicleDescr.physics['terrainResistance'] = (r[0], r[1] * self.__factorMedium, r[2] * self.__factorSoft)
        rff = vehicleDescr.physics['rollingFrictionFactors']
        rff[1] *= self.__factorMedium
        rff[2] *= self.__factorSoft

    def _readConfig(self, xmlCtx, section):
        self.__factorSoft = _xml.readPositiveFloat(xmlCtx, section, 'softGroundResistanceFactor')
        self.__factorMedium = _xml.readPositiveFloat(xmlCtx, section, 'mediumGroundResistanceFactor')


class AntifragmentationLining(OptionalDevice):
    __slots__ = ('__antifragmentationLiningFactor', '__increaseCrewChanceToEvadeHit')

    def __init__(self):
        super(AntifragmentationLining, self).__init__()
        self.__antifragmentationLiningFactor = component_constants.ZERO_FLOAT
        self.__increaseCrewChanceToEvadeHit = component_constants.ZERO_FLOAT

    def updateVehicleDescrAttrs(self, vehicleDescr):
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['antifragmentationLiningFactor'] *= self.__antifragmentationLiningFactor
        miscAttrs['crewChanceToHitFactor'] *= 1.0 - self.__increaseCrewChanceToEvadeHit
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration

    def _readConfig(self, xmlCtx, section):
        reader = partial(_xml.readPositiveFloat, xmlCtx, section)
        self.__antifragmentationLiningFactor = reader('antifragmentationLiningFactor')
        self.__increaseCrewChanceToEvadeHit = reader('increaseCrewChanceToEvadeHit')


class Extinguisher(Equipment):
    __slots__ = ('fireStartingChanceFactor', 'autoactivate')

    def __init__(self):
        super(Extinguisher, self).__init__()
        self.fireStartingChanceFactor = component_constants.ZERO_FLOAT
        self.autoactivate = False

    def _readConfig(self, xmlCtx, section):
        if not section.has_key('fireStartingChanceFactor'):
            self.fireStartingChanceFactor = 1.0
        else:
            self.fireStartingChanceFactor = _xml.readPositiveFloat(xmlCtx, section, 'fireStartingChanceFactor')
        self.autoactivate = section.readBool('autoactivate', False)

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/fireStartingChance'] *= self.fireStartingChanceFactor
        except:
            pass


class Fuel(Equipment):
    __slots__ = ('enginePowerFactor', 'turretRotationSpeedFactor')

    def __init__(self):
        super(Fuel, self).__init__()
        self.enginePowerFactor = component_constants.ZERO_FLOAT
        self.turretRotationSpeedFactor = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.turretRotationSpeedFactor = _xml.readPositiveFloat(xmlCtx, section, 'turretRotationSpeedFactor')

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/power'] *= self.enginePowerFactor
            factors['turrets/0/rotationSpeed'] *= self.turretRotationSpeedFactor
        except:
            pass


class Stimulator(Equipment):
    __slots__ = ('crewLevelIncrease',)

    def __init__(self):
        super(Stimulator, self).__init__()
        self.crewLevelIncrease = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        self.crewLevelIncrease = _xml.readInt(xmlCtx, section, 'crewLevelIncrease', 1)


class Repairkit(Equipment):
    __slots__ = ('repairAll', 'bonusValue')

    def __init__(self):
        super(Repairkit, self).__init__()
        self.repairAll = False
        self.bonusValue = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        self.repairAll = section.readBool('repairAll', False)
        self.bonusValue = _xml.readFraction(xmlCtx, section, 'bonusValue')


class RemovedRpmLimiter(Equipment):
    __slots__ = ('enginePowerFactor', 'engineHpLossPerSecond')

    def __init__(self):
        super(RemovedRpmLimiter, self).__init__()
        self.enginePowerFactor = component_constants.ZERO_FLOAT
        self.engineHpLossPerSecond = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.engineHpLossPerSecond = _xml.readPositiveFloat(xmlCtx, section, 'engineHpLossPerSecond')

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/power'] *= self.enginePowerFactor
        except:
            pass


class Afterburning(Equipment):
    __slots__ = ('enginePowerFactor', 'durationSeconds')

    def __init__(self):
        super(Afterburning, self).__init__()
        self.enginePowerFactor = component_constants.ZERO_FLOAT
        self.durationSeconds = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.durationSeconds = _xml.readInt(xmlCtx, section, 'durationSeconds', 1)

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/power'] *= self.enginePowerFactor
        except:
            pass


class Artillery(Equipment):
    __slots__ = ('delay', 'duration', 'shotsNumber', 'areaRadius', 'shellCompactDescr', 'piercingPower', 'areaVisual', 'areaColor', 'areaMarker', 'areaLength', 'areaWidth', 'reusable', 'cooldownTime', 'deployTime')

    def __init__(self):
        super(Artillery, self).__init__()
        self.delay = component_constants.ZERO_FLOAT
        self.duration = component_constants.ZERO_FLOAT
        self.shotsNumber = component_constants.ZERO_INT
        self.areaRadius = component_constants.ZERO_FLOAT
        self.shellCompactDescr = component_constants.ZERO_INT
        self.piercingPower = component_constants.ZERO_FLOAT
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.reusable = False
        self.cooldownTime = component_constants.ZERO_FLOAT
        self.deployTime = component_constants.ZERO_FLOAT
        return

    def _readConfig(self, xmlCtx, section):
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay')
        self.duration = _xml.readPositiveFloat(xmlCtx, section, 'duration')
        self.shotsNumber = _xml.readNonNegativeInt(xmlCtx, section, 'shotsNumber')
        self.areaRadius = _xml.readPositiveFloat(xmlCtx, section, 'areaRadius')
        self.shellCompactDescr = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        self.piercingPower = _xml.readTupleOfPositiveInts(xmlCtx, section, 'piercingPower', 2)
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.areaLength = self.areaWidth = self.areaRadius * 2
        self.reusable = _xml.readBool(xmlCtx, section, 'reusable')
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownTime') if self.reusable else 0.0
        self.deployTime = _xml.readNonNegativeFloat(xmlCtx, section, 'deployTime')


class Bomber(Equipment):
    __slots__ = ('delay', 'modelName', 'soundEvent', 'speed', 'heights', 'areaLength', 'areaWidth', 'antepositions', 'lateropositions', 'bombingMask', 'waveFraction', 'bombsNumber', 'shellCompactDescr', 'tracerKind', 'piercingPower', 'gravity', 'areaVisual', 'areaColor', 'areaMarker', 'reusable', 'cooldownTime', 'deployTime')

    def __init__(self):
        super(Bomber, self).__init__()
        self.delay = component_constants.ZERO_FLOAT
        self.modelName = component_constants.EMPTY_STRING
        self.soundEvent = component_constants.EMPTY_STRING
        self.speed = component_constants.ZERO_INT
        self.heights = component_constants.EMPTY_TUPLE
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.antepositions = component_constants.EMPTY_TUPLE
        self.lateropositions = component_constants.EMPTY_TUPLE
        self.bombingMask = component_constants.EMPTY_TUPLE
        self.waveFraction = component_constants.ZERO_FLOAT
        self.bombsNumber = component_constants.ZERO_INT
        self.shellCompactDescr = component_constants.ZERO_INT
        self.tracerKind = component_constants.ZERO_INT
        self.piercingPower = component_constants.EMPTY_TUPLE
        self.gravity = component_constants.ZERO_FLOAT
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        self.reusable = False
        self.cooldownTime = component_constants.ZERO_FLOAT
        self.deployTime = component_constants.ZERO_FLOAT
        return

    def _readConfig(self, xmlCtx, section):
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay')
        self.modelName = _xml.readString(xmlCtx, section, 'modelName')
        if IS_CLIENT:
            self.soundEvent = _xml.readString(xmlCtx, section, 'wwsoundEvent')
        self.speed = _xml.readInt(xmlCtx, section, 'speed')
        self.heights = _xml.readTupleOfPositiveInts(xmlCtx, section, 'heights', 2)
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.antepositions = _xml.readTupleOfFloats(xmlCtx, section, 'antepositions')
        self.lateropositions = _xml.readTupleOfFloats(xmlCtx, section, 'lateropositions')
        self.bombingMask = tuple((bool(v) for v in _xml.readTupleOfInts(xmlCtx, section, 'bombingMask')))
        if not len(self.antepositions) == len(self.lateropositions) == len(self.bombingMask):
            _xml.raiseWrongSection(xmlCtx, 'bombers number mismatch')
        self.waveFraction = _xml.readPositiveFloat(xmlCtx, section, 'waveFraction')
        self.bombsNumber = _xml.readNonNegativeInt(xmlCtx, section, 'bombsNumber')
        self.shellCompactDescr = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        self.tracerKind = _xml.readInt(xmlCtx, section, 'tracerKind')
        self.piercingPower = _xml.readTupleOfPositiveInts(xmlCtx, section, 'piercingPower', 2)
        self.gravity = _xml.readPositiveFloat(xmlCtx, section, 'gravity')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.reusable = _xml.readBool(xmlCtx, section, 'reusable')
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownTime') if self.reusable else 0.0
        self.deployTime = _xml.readNonNegativeFloat(xmlCtx, section, 'deployTime')


class DynamicEquipment(Equipment):
    __slots__ = ('_config',)

    def __init__(self):
        super(DynamicEquipment, self).__init__()
        self._config = []

    def _readConfig(self, xmlCtx, section):
        self._config = []
        for subsection in section.values():
            if subsection.name == 'level':
                self._config.append(self._readLevelConfig(xmlCtx, subsection))
            _xml.raiseWrongXml(xmlCtx, subsection.name, 'should be <params>')

    def getLevelIDForVehicle(self, vehicleDescr):
        """
        Returns index of params of equipment that suites for given vehicleDescr. Is used for
        updateVehicleAttrFactorsForLevel.
        :param vehicleDescr: VehicleDescriptor
        :return: index of params in _config
        """
        for levelID, (levelFilter, _) in enumerate(self._config):
            if levelFilter.checkCompatibility(vehicleDescr):
                return levelID

        return None

    def getLevelParamsForDevice(self, optionalDevice):
        """
        Returns level params of equipment that suites for given optional device.
        :param optionalDevice: optional device
        :return: level params. Format of params depends from actual class of DynamicEquipment.
        """
        for levelFilter, levelParams in self._config:
            if levelFilter.checkCompatibilityWithDevice(optionalDevice):
                return levelParams

        return None

    def updateVehicleAttrFactors(self, vehicleDescr, factors, _):
        levelID = self.getLevelIDForVehicle(vehicleDescr)
        if levelID is not None:
            self.updateVehicleAttrFactorsForLevel(factors, levelID)
        return

    def updateVehicleAttrFactorsForLevel(self, factors, levelID):
        """
        Same as updateVehicleAttrFactors but uses params returned from getLevelIDForVehicle.
        """
        _, levelParams = self._config[levelID]
        self._updateVehicleAttrFactorsImpl(factors, levelParams)

    def _readLevelConfig(self, xmlCtx, section):
        raise NotImplemented

    def _updateVehicleAttrFactorsImpl(self, factors, levelParams):
        raise NotImplemented


class FactorBattleBooster(DynamicEquipment):
    __slots__ = ()

    def _readLevelConfig(self, xmlCtx, section):
        filter = _OptionalDeviceFilter(xmlCtx, section['deviceFilter'])
        attribute = _xml.readNonEmptyString(xmlCtx, section, 'attribute')
        factor = _xml.readPositiveFloat(xmlCtx, section, 'factor')
        return (filter, (attribute, factor))

    def _updateVehicleAttrFactorsImpl(self, factors, levelParams):
        attribute, factor = levelParams
        attribute = self.findActualAttribute(factors, attribute)
        factors[attribute] *= factor


class AdditiveBattleBooster(DynamicEquipment):
    __slots__ = ()

    def _readLevelConfig(self, xmlCtx, section):
        filter = _OptionalDeviceFilter(xmlCtx, section['deviceFilter'])
        attribute = _xml.readNonEmptyString(xmlCtx, section, 'attribute')
        value = _xml.readPositiveFloat(xmlCtx, section, 'value')
        return (filter, (attribute, value))

    def _updateVehicleAttrFactorsImpl(self, factors, levelParams):
        attribute, value = levelParams
        attribute = self.findActualAttribute(factors, attribute)
        factors[attribute] += value


class FactorSkillBattleBooster(Equipment):
    __slots__ = ('skillName', 'efficiencyFactor')

    def __init__(self):
        super(FactorSkillBattleBooster, self).__init__()
        self.skillName = None
        self.efficiencyFactor = component_constants.ZERO_FLOAT
        return

    def _readConfig(self, xmlCtx, section):
        self.skillName = _xml.readNonEmptyString(xmlCtx, section, 'skillName')
        self.efficiencyFactor = _xml.readPositiveFloat(xmlCtx, section, 'efficiencyFactor')

    def updateCrewSkill(self, factor, baseAvgLevel):
        if baseAvgLevel < 100:
            factor = max(1.0, factor)
            baseAvgLevel = 100
        else:
            factor = 0.57 + (factor - 0.57) * self.efficiencyFactor
        return (factor, baseAvgLevel)


class SixthSenseBattleBooster(Equipment):
    __slots__ = ('skillName', 'delay')

    def __init__(self):
        super(SixthSenseBattleBooster, self).__init__()
        self.skillName = 'commander_sixthSense'
        self.delay = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.delay = _xml.readNonNegativeFloat(xmlCtx, section, 'delay')

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        isFire = True
        if level < MAX_SKILL_LEVEL or not isActive:
            level = MAX_SKILL_LEVEL
            isActive = True
        else:
            skillConfig = skillConfig.recreate(self.delay)
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class RancorousBattleBooster(Equipment):
    __slots__ = ('skillName', 'duration', 'sectorHalfAngle')

    def __init__(self):
        super(RancorousBattleBooster, self).__init__()
        self.skillName = 'gunner_rancorous'
        self.duration = component_constants.ZERO_FLOAT
        self.sectorHalfAngle = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.skillName = 'gunner_rancorous'
        self.duration = _xml.readPositiveFloat(xmlCtx, section, 'duration')
        self.sectorHalfAngle = math.radians(_xml.readPositiveFloat(xmlCtx, section, 'sectorHalfAngle'))

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if level < MAX_SKILL_LEVEL or not isActive or isFire:
            level = MAX_SKILL_LEVEL
            isActive = True
            isFire = False
        else:
            skillConfig = skillConfig.recreate(self.duration, self.sectorHalfAngle)
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class PedantBattleBooster(Equipment):
    __slots__ = ('skillName', 'ammoBayHealthFactor')

    def __init__(self):
        super(PedantBattleBooster, self).__init__()
        self.skillName = 'loader_pedant'
        self.ammoBayHealthFactor = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.skillName = 'loader_pedant'
        self.ammoBayHealthFactor = _xml.readPositiveFloat(xmlCtx, section, 'ammoBayHealthFactor')

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if level < MAX_SKILL_LEVEL:
            level = MAX_SKILL_LEVEL
        else:
            skillConfig = skillConfig.recreate(self.ammoBayHealthFactor)
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class FactorPerLevelBattleBooster(Equipment):
    __slots__ = ('skillName', 'factorName', 'factorPerLevel')

    def __init__(self):
        super(FactorPerLevelBattleBooster, self).__init__()
        self.skillName = component_constants.EMPTY_STRING
        self.factorName = component_constants.EMPTY_STRING
        self.factorPerLevel = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.skillName = _xml.readNonEmptyString(xmlCtx, section, 'skillName')
        self.factorName = _xml.readNonEmptyString(xmlCtx, section, 'factorName')
        self.factorPerLevel = _xml.readNonNegativeFloat(xmlCtx, section, 'factorPerLevel')

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if level < MAX_SKILL_LEVEL or not isActive or isFire:
            level = MAX_SKILL_LEVEL
            isActive = True
            isFire = False
        else:
            skillConfig = skillConfig.recreate(self.factorPerLevel)
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class LastEffortBattleBooster(Equipment):
    __slots__ = ('skillName', 'duration')

    def __init__(self):
        super(LastEffortBattleBooster, self).__init__()
        self.skillName = 'radioman_lastEffort'
        self.duration = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.skillName = 'radioman_lastEffort'
        self.duration = _xml.readNonNegativeFloat(xmlCtx, section, 'duration')

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if level < MAX_SKILL_LEVEL or not isActive:
            level = MAX_SKILL_LEVEL
            isActive = True
        else:
            skillConfig = skillConfig.recreate(self.duration)
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class _OptionalDeviceFilter(object):

    def __init__(self, xmlCtx, section):
        self.__requiredTags = set()
        self.__incompatibleTags = set()
        for subsection in section['tags'].values():
            if subsection.name == 'required':
                self.__requiredTags.update(_readTags((xmlCtx, subsection.name), subsection, '', 'equipment'))
            if subsection.name == 'incompatible':
                self.__incompatibleTags.update(_readTags((xmlCtx, subsection.name), subsection, '', 'equipment'))
            _xml.raiseWrongXml(xmlCtx, subsection.name, 'should be <required> or/and <incompatible>')

    def checkCompatibility(self, vehicleDescr):
        """
        Checks if any optional devices compatible with filter.
        :param vehicleDescr: VehicleDescriptor.
        :return: Returns True if all tags of optional devices is in <required> and none of them is
        in <incompatible>
        """
        for device in vehicleDescr.optionalDevices:
            if device is None:
                continue
            tags = device.tags
            if self.__requiredTags.issubset(tags) and len(self.__incompatibleTags.intersection(tags)) == 0:
                return True

        return False

    def checkCompatibilityWithDevice(self, optionalDevice):
        """
        Checks if optional device compatible with filter.
        :param optionalDevice: optional device.
        :return: Returns True if all tags of optional device is in <required> and none of them is
        in <incompatible>
        """
        tags = optionalDevice.tags
        return True if self.__requiredTags.issubset(tags) and len(self.__incompatibleTags.intersection(tags)) == 0 else False


class _VehicleFilter(object):

    def __init__(self, xmlCtx, section):
        self.__include = []
        self.__exclude = []
        for subsection in section.values():
            if subsection.name == 'include':
                self.__include.append(_readVehicleFilterPattern((xmlCtx, 'include'), subsection))
            if subsection.name == 'exclude':
                self.__exclude.append(_readVehicleFilterPattern((xmlCtx, 'exclude'), subsection))
            _xml.raiseWrongXml(xmlCtx, subsection.name, 'should be <include> or <exclude>')

    def checkCompatibility(self, vehicleDescr):
        if self.__exclude:
            isVehicleTypeMatched, isVehicleMatched = _matchSubfilter(vehicleDescr, self.__exclude)
            if isVehicleMatched and isVehicleTypeMatched:
                return (False, 'not for current vehicle')
        if self.__include:
            isVehicleTypeMatched, isVehicleMatched = _matchSubfilter(vehicleDescr, self.__include)
            if not isVehicleMatched:
                if not isVehicleTypeMatched:
                    return (False, 'not for this vehicle type')
                return (False, 'not for current vehicle')
        return (True, None)


class _ArtefactFilter(object):

    def __init__(self, xmlCtx, section, itemTypeName):
        self.__installed = set()
        self.__active = set()
        for subsection in section.values():
            if subsection.name == 'installed':
                self.__installed.update(_readTags((xmlCtx, subsection.name), subsection, '', itemTypeName))
            if subsection.name == 'active':
                self.__active.update(_readTags((xmlCtx, subsection.name), subsection, '', itemTypeName))
            _xml.raiseWrongXml(xmlCtx, subsection.name, 'should be <installed> or <active>')

    def inInstalled(self, tags):
        return bool(len(self.__installed.intersection(tags)))

    def inActive(self, tags):
        return bool(len(self.__active.intersection(tags)))


def _readVehicleFilterPattern(xmlCtx, section):
    res = {}
    for sname, section in section.items():
        ctx = (xmlCtx, sname)
        if sname == 'nations':
            names = section.asString
            res['nations'] = []
            for name in names.split():
                id = nations.INDICES.get(name)
                if id is None:
                    _xml.raiseWrongXml(xmlCtx, 'nations', "unknown nation '%s'" % name)
                res['nations'].append(id)

        if sname in _vehicleFilterItemTypes:
            sname = intern(sname)
            res[sname] = {}
            if section.has_key('tags'):
                tags = _readTags(ctx, section, 'tags', _vehicleFilterItemTypes[sname])
                res[sname]['tags'] = tags
            minLevel = section.readInt('minLevel', 1)
            if not 1 <= minLevel <= 10:
                _xml.raiseWrongSection(ctx, 'minLevel')
            if minLevel != 1:
                res[sname]['minLevel'] = minLevel
            maxLevel = section.readInt('maxLevel', 10)
            if not 1 <= maxLevel <= 10:
                _xml.raiseWrongSection(ctx, 'maxLevel')
            if maxLevel != 10:
                res[sname]['maxLevel'] = maxLevel
        _xml.raiseWrongXml(ctx, '', 'unknown section name')

    return res


def _matchSubfilter(vehicleDescr, subfilter):
    vehicleType = vehicleDescr.type
    nationID = vehicleType.id[0]
    hasVehicleTypeOk = False
    for entry in subfilter:
        item = entry.get('nations')
        if item is not None and nationID not in item:
            continue
        item = entry.get('vehicle')
        if item is None:
            hasVehicleTypeOk = True
        else:
            tags = item.get('tags')
            if tags is not None and not vehicleType.tags.intersection(tags):
                continue
            minLevel = item.get('minLevel')
            if minLevel is not None and minLevel > vehicleDescr.level:
                continue
            maxLevel = item.get('maxLevel')
            if maxLevel is not None and maxLevel < vehicleDescr.level:
                continue
            hasVehicleTypeOk = True
        isVehicleOk = True
        for name, item in entry.iteritems():
            if name in ('nations', 'vehicle'):
                continue
            descr = getattr(vehicleDescr, name)
            tags = item.get('tags')
            if tags is not None and not descr.tags.intersection(tags):
                isVehicleOk = False
                break
            minLevel = item.get('minLevel')
            if minLevel is not None and minLevel > descr.level:
                isVehicleOk = False
                break
            maxLevel = item.get('maxLevel')
            if maxLevel is not None and maxLevel < descr.level:
                isVehicleOk = False
                break

        if isVehicleOk:
            return (True, True)

    return (hasVehicleTypeOk, False)


_vehicleFilterItemTypes = {'vehicle': 'vehicle',
 'chassis': 'vehicleChassis',
 'engine': 'vehicleEngine',
 'fuelTank': 'vehicleFuelTank',
 'radio': 'vehicleRadio',
 'gun': 'vehicleGun'}
_readTags = vehicles._readTags

def _readStun(xmlCtx, scriptSection):
    stunResistanceEffect = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceEffect') if scriptSection.has_key('stunResistanceEffect') else 0.0
    stunResistanceDuration = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceDuration') if scriptSection.has_key('stunResistanceDuration') else 0.0
    return (stunResistanceEffect, stunResistanceDuration)


def _readReuseParams(xmlCtx, scriptSection):
    return (_xml.readInt(xmlCtx, scriptSection, 'reuseCount', minVal=-1) if scriptSection.has_key('reuseCount') else 0, _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds', minVal=0) if scriptSection.has_key('cooldownSeconds') else 0)
