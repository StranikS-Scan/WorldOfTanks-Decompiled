# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/artefacts.py
import math
import os
from re import findall
from soft_exception import SoftException
from typing import TYPE_CHECKING, NamedTuple, Set, Dict, Optional, Any, Tuple
import items
import nations
from ResMgr import DataSection
from constants import IS_CLIENT, IS_CELLAPP, IS_WEB, VEHICLE_TTC_ASPECTS, ATTACK_REASON, ATTACK_REASON_INDICES, SERVER_TICK_LENGTH
from debug_utils import LOG_DEBUG_DEV
from items import ITEM_OPERATION, PREDEFINED_HEAL_GROUPS
from items import _xml, vehicles
from items.artefacts_helpers import VehicleFilter, _ArtefactFilter
from items.basic_item import BasicItem
from items.components import shared_components, component_constants
from items.components.supply_slot_categories import SupplySlotFilter, LevelsFactor, AttrsOperation, SlotCategories
from items.vehicles import VehicleDescriptor
from soft_exception import SoftException
from tankmen import MAX_SKILL_LEVEL
from vehicles import _readPriceForOperation
from Math import Vector3
if TYPE_CHECKING:
    from ResMgr import DataSection
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import i18n
else:

    class i18n(object):

        @classmethod
        def makeString(cls, key):
            raise SoftException('Unexpected call "i18n.makeString"')


if IS_CELLAPP:
    from actions import vehicle as vehicleActions

class CommonXmlSectionReader(object):

    def __init__(self, xmlTagKeyMap, dictInstance):
        self.__xmlTagKeyMap = xmlTagKeyMap
        self.__readersMap = self.__createReaders(dictInstance)

    def read(self, xmlCtx, section, subsection_name):
        result = {}
        subsection = _xml.getSubsection(xmlCtx, section, subsection_name)
        for key, tag_name in self.__xmlTagKeyMap.iteritems():
            if _xml.getSubsection(xmlCtx, subsection, tag_name, throwIfMissing=False) is None:
                continue
            reader = self.__readersMap.get(key, None)
            if reader is None:
                raise SoftException("Cannot read '{}' xml tag for key '{}'. Reader for this tag wasn't found. Please make sure CommonXmlSectionReader was configured properly".format(tag_name, key))
            result[key] = reader(xmlCtx, subsection, tag_name)

        return result

    @staticmethod
    def __createReaders(dictInstance):
        readers = {}
        for name, value in dictInstance.iteritems():
            factor_type = type(value)
            reader_type = 'TupleOfFloats' if factor_type is list else findall("'(\\w+)'", str(factor_type))[0].capitalize()
            readers[name] = getattr(_xml, 'read' + reader_type)

        return readers


class VehicleFactorsXmlReader(CommonXmlSectionReader):
    __readerImpl = None

    def __init__(self):
        attrFactor = vehicles.vehicleAttributeFactors()
        _vehicle_attribute_factor_tags = {name:name.replace('/', '-') for name in attrFactor.iterkeys()}
        super(VehicleFactorsXmlReader, self).__init__(_vehicle_attribute_factor_tags, attrFactor)

    @staticmethod
    def readFactors(xmlCtx, section, subsection_name):
        if VehicleFactorsXmlReader.__readerImpl is None:
            VehicleFactorsXmlReader.__readerImpl = VehicleFactorsXmlReader()
        return VehicleFactorsXmlReader.__readerImpl.read(xmlCtx, section, subsection_name)


class Artefact(BasicItem):
    __slots__ = ('name', 'id', 'compactDescr', 'tags', 'i18n', 'icon', 'removable', 'price', 'showInShop', '_vehWeightFraction', '_weight', '_maxWeightChange', '__vehicleFilter', '__artefactFilter', 'isImproved', 'kpi', 'iconName', '_groupName')

    def __init__(self, typeID, itemID, itemName, compactDescr):
        super(Artefact, self).__init__(typeID, itemID, itemName, compactDescr)
        self.icon = None
        self.iconName = None
        self.removable = False
        self.price = None
        self.showInShop = False
        self._vehWeightFraction = component_constants.ZERO_FLOAT
        self._weight = component_constants.ZERO_FLOAT
        self._maxWeightChange = component_constants.ZERO_FLOAT
        self.__vehicleFilter = None
        self.__artefactFilter = None
        self.isImproved = None
        self.kpi = None
        self._groupName = None
        return

    def init(self, xmlCtx, section):
        self._readBasicConfig(xmlCtx, section)
        xmlCtx = (xmlCtx, 'script')
        section = section['script']
        self._readWeight(xmlCtx, section)
        self._readConfig(xmlCtx, section)

    @property
    def isAvatarEquipment(self):
        return 'avatar' in self.tags

    def updatePrice(self, newPrice, showInShop):
        self.price = newPrice
        self.showInShop = showInShop

    def extraName(self):
        pass

    def removeItem(self, *args, **kwargs):
        pass

    @property
    def groupName(self):
        return self._groupName or self.name

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

    def compatibleNations(self):
        return self.__vehicleFilter.compatibleNations() if self.__vehicleFilter else {nations.INDICES[n] for n in nations.AVAILABLE_NAMES}

    def checkCompatibilityWithComponents(self, vehicleDescr):
        return True if self.__vehicleFilter is None else self.__vehicleFilter.checkCompatibilityWithComponents(vehicleDescr)

    def _readConfig(self, xmlCtx, scriptSection):
        pass

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
        pass

    def getVehicleFilter(self):
        return self.__vehicleFilter

    def _readBasicConfig(self, xmlCtx, section):
        self.name = section.name
        self.id = (nations.NONE_INDEX, _xml.readInt(xmlCtx, section, 'id', 0, 65535))
        self.compactDescr = vehicles.makeIntCompactDescrByID(self.itemTypeName, *self.id)
        if not section.has_key('tags'):
            self.tags = frozenset()
        else:
            self.tags = _readTags(xmlCtx, section, 'tags', self.itemTypeName)
        if IS_CLIENT or IS_WEB:
            self.i18n = shared_components.I18nComponent(userStringKey=section.readString('userString'), descriptionKey=section.readString('description'), shortDescriptionSpecialKey=section.readString('shortDescriptionSpecial'), longDescriptionSpecialKey=section.readString('longDescriptionSpecial'), shortFilterAlertKey=section.readString('shortFilterAlert'), longFilterAlertKey=section.readString('longFilterAlert'))
            self.icon = _xml.readIcon(xmlCtx, section, 'icon')
            self.iconName = os.path.splitext(os.path.basename(self.icon[0]))[0]
        if IS_CLIENT and section.has_key('kpi'):
            self.kpi = _readKpi(xmlCtx, section['kpi'])
        else:
            self.kpi = []
        if section.has_key('vehicleFilter'):
            self.__vehicleFilter = VehicleFilter.readVehicleFilter((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        else:
            self.__vehicleFilter = None
        if not section.has_key('incompatibleTags'):
            self.__artefactFilter = None
        else:
            self.__artefactFilter = _ArtefactFilter((xmlCtx, 'incompatibleTags'), section['incompatibleTags'], self.itemTypeName)
        self.removable = section.readBool('removable', False)
        self.isImproved = section.readBool('improved', False)
        if (IS_CLIENT or IS_WEB) and section.has_key('groupName'):
            self._groupName = section.readString('groupName')
        return


class OptionalDevice(Artefact):
    __slots__ = ('categories', '_overridableFactors', '_tier', '_tierlessName')

    def __init__(self):
        super(OptionalDevice, self).__init__(items.ITEM_TYPES.optionalDevice, 0, '', 0)
        self.categories = set()
        self._overridableFactors = {}
        self._tier = None
        self._tierlessName = None
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(OptionalDevice, self)._readBasicConfig(xmlCtx, section)
        self._readCategories(xmlCtx, section)
        self._readTier(xmlCtx, section)
        self._readSpecFactorsFromConfig(xmlCtx, section['script'])

    def extraName(self):
        return None

    @property
    def tier(self):
        return self._tier

    @property
    def tierlessName(self):
        return self._tierlessName or self.name

    @property
    def groupName(self):
        return self._groupName or self.tierlessName

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
        pass

    def updateVehicleDescrAttrs(self, vehicleDescr):
        pass

    @property
    def isDeluxe(self):
        return 'deluxe' in self.tags

    def defineActiveLevel(self, vehicleDescr):
        supplySlot = vehicleDescr.getOptDevSupplySlot(self.compactDescr)
        return None if supplySlot is None else SupplySlotFilter.defineActiveValuesLevel(supplySlot.categories, self.categories)

    def defineActiveValueForSpecFactor(self, vehicleDescr, factorName, level=None):
        if level is None:
            level = self.defineActiveLevel(vehicleDescr)
        if level is None:
            return
        else:
            factor = self._defineFactorFor(vehicleDescr, factorName)
            return None if factor is None else factor.getActiveValue(level)

    def _defineFactorFor(self, vehicleDescr, factorName):
        vehOverridedFactor = vehicleDescr.type.optDevsOverrides.get(self.tierlessName, {}).get(factorName, None)
        if vehOverridedFactor is not None:
            factor = vehOverridedFactor
        else:
            factor = self._overridableFactors.get(factorName, None)
        return factor

    def _readSpecFactorsFromConfig(self, xmlCtx, section):
        factorsSection = section['overridableFactors']
        if factorsSection is None:
            return
        else:
            for name, subsection in factorsSection.items():
                factor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, factorsSection, name)
                self._overridableFactors[name] = factor

            return

    def _readCategories(self, xmlCtx, section):
        if section.has_key('categories'):
            self.categories = set(_xml.readTupleOfStrings(xmlCtx, section, 'categories'))
            for category in self.categories:
                if category not in SlotCategories.ALL:
                    raise SoftException("Unknown category '{}'".format(category))

    def _readTier(self, xmlCtx, section):
        tierParts = self.name.split('_tier')
        if len(tierParts) == 2:
            self._tierlessName, tier = tierParts
            self._tier = int(tier)


class StaticOptionalDevice(OptionalDevice):
    __slots__ = ('_factors',)

    def __init__(self):
        super(StaticOptionalDevice, self).__init__()
        self._factors = {}

    def _readConfig(self, xmlCtx, scriptSection):
        super(StaticOptionalDevice, self)._readConfig(xmlCtx, scriptSection)
        self._readFactorsFromConfig(xmlCtx, scriptSection)

    def _readFactorsFromConfig(self, xmlCtx, section):
        factorsSection = section['factors']
        if factorsSection is None:
            return
        else:
            for name, subsection in factorsSection.items():
                attrPath, factor = LevelsFactor.readLevelsFactor(xmlCtx, subsection)
                splitted = tuple(attrPath.split('/'))
                self._factors[splitted] = factor

            return

    @staticmethod
    def defineAttrsDict(vehicleDescr, modulePath):
        attrDict = getattr(vehicleDescr, modulePath[0])
        for key in modulePath[1:]:
            attrDict = attrDict[key]

        return attrDict

    def updateVehicleDescrAttrs(self, vehicleDescr):
        level = self.defineActiveLevel(vehicleDescr)
        if level is None:
            LOG_DEBUG_DEV('updateVehicleDescrAttrs: optional device ({}) is not installed'.format(self))
            return
        else:
            for splitted, factor in self._factors.iteritems():
                modulePath = splitted[:-1]
                shortName = splitted[-1]
                attrDict = self.defineAttrsDict(vehicleDescr, modulePath)
                factor.applyLevelToAttrsDict(level, attrDict, shortName)

            return


class StillVehicleOptionalDevice(StaticOptionalDevice):
    __slots__ = ('activateWhenStillSec',)

    def _readConfig(self, xmlCtx, scriptSection):
        self.activateWhenStillSec = _xml.readNonNegativeFloat(xmlCtx, scriptSection, 'activateWhenStillSec')
        super(StillVehicleOptionalDevice, self)._readConfig(xmlCtx, scriptSection)

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
        if not self._checkAspect(aspect):
            return
        else:
            level = self.defineActiveLevel(vehicleDescr)
            if level is not None:
                transformedFactors = self.transformFactors(level, vehicleDescr)
                self.updateFactorsDictWithTransformed(factors, transformedFactors)
            return

    def _checkAspect(self, aspect):
        raise NotImplementedError

    def transformFactors(self, level, vehicleDescr):
        raise NotImplementedError

    def updateFactorsDictWithTransformed(self, factorsDict, transformedFactors):
        raise NotImplementedError


class Stereoscope(StillVehicleOptionalDevice):
    __slots__ = ('circularVisionRadiusFactor',)
    CIRCULAR_VISION_RADIUS = 'circularVisionRadius'

    def extraName(self):
        pass

    def _checkAspect(self, aspect):
        return aspect in (VEHICLE_TTC_ASPECTS.DEFAULT, VEHICLE_TTC_ASPECTS.WHEN_STILL)

    def _readConfig(self, xmlCtx, scriptSection):
        super(Stereoscope, self)._readConfig(xmlCtx, scriptSection)
        self.circularVisionRadiusFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, scriptSection, self.CIRCULAR_VISION_RADIUS)

    def transformFactors(self, level, vehicleDescr):
        activeValue = self.circularVisionRadiusFactor.getActiveValue(level)
        factorToCompensate = vehicleDescr.miscAttrs['circularVisionRadiusFactor']
        transformedFactor = activeValue / factorToCompensate
        res = (transformedFactor,)
        return res

    def updateFactorsDictWithTransformed(self, factorsDict, transformedFactors):
        transformedCVRFactor = transformedFactors
        AttrsOperation.updateDictWithAttribute(factorsDict, self.CIRCULAR_VISION_RADIUS, AttrsOperation.MUL, transformedCVRFactor)


class CamouflageNet(StillVehicleOptionalDevice):
    invisibilityBonusName = 'invisibilityBonus'
    invisibilityAttr = 'invisibility'

    def extraName(self):
        pass

    @property
    def competesBy(self):
        pass

    def transformFactors(self, level, vehicleDescr):
        cnActiveValue = self.defineActiveValueForSpecFactor(vehicleDescr, self.invisibilityBonusName, level)
        staticActiveValue = vehicleDescr.miscAttrs[self.competesBy]
        activeValue = max(cnActiveValue, staticActiveValue) - staticActiveValue
        res = (activeValue,)
        return res

    def updateFactorsDictWithTransformed(self, factorsDict, transformedFactors):
        activeValue = transformedFactors
        factorsDict[self.invisibilityAttr][0] += activeValue

    def _checkAspect(self, aspect):
        return aspect in (VEHICLE_TTC_ASPECTS.WHEN_STILL,)


class LowNoiseTracks(StaticOptionalDevice):
    invisibilityBonusName = 'invisibilityBonus'

    def updateVehicleDescrAttrs(self, vehicleDescr):
        super(LowNoiseTracks, self).updateVehicleDescrAttrs(vehicleDescr)
        level = self.defineActiveLevel(vehicleDescr)
        activeValue = self.defineActiveValueForSpecFactor(vehicleDescr, self.invisibilityBonusName, level)
        vehicleDescr.miscAttrs['invisibilityAdditiveTerm'] += activeValue


class ImprovedConfiguration(StaticOptionalDevice):
    __slots__ = ('engineReduceFineFactor', 'ammoBayReduceFineFactor')

    def extraName(self):
        pass

    def _readConfig(self, xmlCtx, scriptSection):
        super(ImprovedConfiguration, self)._readConfig(xmlCtx, scriptSection)
        self.engineReduceFineFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, scriptSection, 'engineReduceFineFactor')
        self.ammoBayReduceFineFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, scriptSection, 'ammoBayReduceFineFactor')


class Equipment(Artefact):
    __slots__ = ('equipmentType', 'reuseCount', 'cooldownSeconds', 'soundNotification', 'stunResistanceEffect', 'stunResistanceDuration', 'repeatedStunDurationFactor')

    def __init__(self):
        super(Equipment, self).__init__(items.ITEM_TYPES.equipment, 0, '', 0)
        self.equipmentType = None
        self.stunResistanceEffect = component_constants.ZERO_FLOAT
        self.stunResistanceDuration = component_constants.ZERO_FLOAT
        self.repeatedStunDurationFactor = 1.0
        self.reuseCount = component_constants.ZERO_INT
        self.cooldownSeconds = component_constants.ZERO_INT
        self.soundNotification = None
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(Equipment, self)._readBasicConfig(xmlCtx, section)
        self.equipmentType = items.EQUIPMENT_TYPES[section.readString('type', 'regular')]
        self.soundNotification = _xml.readStringOrNone(xmlCtx, section, 'soundNotification')
        scriptSection = section['script']
        self.stunResistanceEffect, self.stunResistanceDuration, self.repeatedStunDurationFactor = _readStun(xmlCtx, scriptSection)
        self.reuseCount, self.cooldownSeconds = _readReuseParams(xmlCtx, scriptSection)

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
        pass

    def extraName(self):
        return self.name

    def checkCompatibilityWithEquipment(self, other):
        return self.checkCompatibilityWithOther(other)

    def checkCompatibilityWithActiveEquipment(self, other):
        return self.checkCompatibilityWithActiveOther(other)

    def offload(self, inventoryCallback):
        if not callable(inventoryCallback):
            return
        if 'builtin' not in self.tags:
            inventoryCallback(self.compactDescr)


class ExtraHealthReserve(StaticOptionalDevice):
    __slots__ = ('chassisMaxLoadFactor',)

    def weightOnVehicle(self, vehicleDescr):
        chassis = vehicleDescr.chassis
        level = self.defineActiveLevel(vehicleDescr)
        return super(ExtraHealthReserve, self).weightOnVehicle(vehicleDescr) if level is None else (self._vehWeightFraction, self._weight, chassis.maxLoad * (self.chassisMaxLoadFactor.getActiveValue(level) - 1.0))

    def updateVehicleDescrAttrs(self, vehicleDescr):
        super(ExtraHealthReserve, self).updateVehicleDescrAttrs(vehicleDescr)
        descr = vehicleDescr.chassis
        vehicleDescr.miscAttrs['chassisHealthAfterHysteresisFactor'] = float(descr.maxHealth) / descr.maxRegenHealth

    def _readConfig(self, xmlCtx, section):
        super(ExtraHealthReserve, self)._readConfig(xmlCtx, section)
        self.chassisMaxLoadFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'chassisMaxLoadFactor')


class Grousers(StaticOptionalDevice):
    __slots__ = ('rotationFactor', 'rollingFrictionFactor')

    def updateVehicleDescrAttrs(self, vehicleDescr):
        super(Grousers, self).updateVehicleDescrAttrs(vehicleDescr)
        level = self.defineActiveLevel(vehicleDescr)
        if level is None:
            LOG_DEBUG_DEV('updateVehicleDescrAttrs: optional device ({}) is not installed'.format(self))
            return
        else:
            rotationFactorActiveValue = self.rotationFactor.getActiveValue(level)
            rollingFrictionFactorActiveValue = self.rollingFrictionFactor.getActiveValue(level)
            r = vehicleDescr.physics['terrainResistance']
            vehicleDescr.physics['terrainResistance'] = tuple((ri * rotationFactorActiveValue for ri in r))
            rff = vehicleDescr.physics['rollingFrictionFactors']
            vehicleDescr.physics['rollingFrictionFactors'] = list((rffi * rollingFrictionFactorActiveValue for rffi in rff))
            return

    def _readConfig(self, xmlCtx, section):
        super(Grousers, self)._readConfig(xmlCtx, section)
        self.rotationFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'rotationFactor')
        self.rollingFrictionFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'rollingFrictionFactor')


class RotationMechanisms(StaticOptionalDevice):
    __slots__ = ('trackMoveSpeedFactor', 'wheelMoveSpeedFactor', 'trackRotateSpeedFactor', 'wheelRotateSpeedFactor', 'wheelCenterRotationFwdSpeed')

    def updateVehicleDescrAttrs(self, vehicleDescr):
        super(RotationMechanisms, self).updateVehicleDescrAttrs(vehicleDescr)
        level = self.defineActiveLevel(vehicleDescr)
        if level is None:
            LOG_DEBUG_DEV('updateVehicleDescrAttrs: optional device ({}) is not installed'.format(self))
            return
        else:
            isWheeledVehicle = vehicleDescr.type.isWheeledVehicle
            onMoveFactor = self.trackMoveSpeedFactor if not isWheeledVehicle else self.wheelMoveSpeedFactor
            vehicleDescr.miscAttrs['onMoveRotationSpeedFactor'] = onMoveFactor.getActiveValue(level)
            onRotationFactor = self.trackRotateSpeedFactor if not isWheeledVehicle else self.wheelRotateSpeedFactor
            vehicleDescr.miscAttrs['onStillRotationSpeedFactor'] = onRotationFactor.getActiveValue(level)
            vehicleDescr.miscAttrs['centerRotationFwdSpeedFactor'] = self.wheelCenterRotationFwdSpeed.getActiveValue(level)
            return

    def _readConfig(self, xmlCtx, section):
        super(RotationMechanisms, self)._readConfig(xmlCtx, section)
        self.trackMoveSpeedFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'trackMoveSpeedFactor')
        self.wheelMoveSpeedFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'wheelMoveSpeedFactor')
        self.trackRotateSpeedFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'trackRotateSpeedFactor')
        self.wheelRotateSpeedFactor = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'wheelRotateSpeedFactor')
        self.wheelCenterRotationFwdSpeed = LevelsFactor.readTypelessLevelsFactor(xmlCtx, section, 'wheelCenterRotationFwdSpeed')


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

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
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

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
        try:
            factors['engine/power'] *= self.enginePowerFactor
            factors['turret/rotationSpeed'] *= self.turretRotationSpeedFactor
        except:
            pass


class Stimulator(Equipment):
    __slots__ = ('crewLevelIncrease',)

    def __init__(self):
        super(Stimulator, self).__init__()
        self.crewLevelIncrease = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.crewLevelIncrease = _xml.readFloat(xmlCtx, section, 'crewLevelIncrease', component_constants.ZERO_FLOAT)


class Repairkit(Equipment):
    __slots__ = ('repairAll', 'bonusValue')

    def __init__(self):
        super(Repairkit, self).__init__()
        self.repairAll = False
        self.bonusValue = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.repairAll = section.readBool('repairAll', False)
        self.bonusValue = _xml.readFraction(xmlCtx, section, 'bonusValue')


class RepairkitBattleRoyale(Repairkit):
    pass


class RemovedRpmLimiter(Equipment):
    __slots__ = ('enginePowerFactor', 'engineHpLossPerSecond')

    def __init__(self):
        super(RemovedRpmLimiter, self).__init__()
        self.enginePowerFactor = component_constants.ZERO_FLOAT
        self.engineHpLossPerSecond = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.engineHpLossPerSecond = _xml.readPositiveFloat(xmlCtx, section, 'engineHpLossPerSecond')

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
        try:
            factors['engine/power'] *= self.enginePowerFactor
        except:
            pass


class Afterburning(Equipment):
    __slots__ = ('deploySeconds', 'consumeSeconds', 'rechargeSeconds', 'enginePowerFactor', 'maxSpeedFactor')

    def __init__(self):
        super(Afterburning, self).__init__()
        self.deploySeconds = component_constants.ZERO_INT
        self.consumeSeconds = component_constants.ZERO_INT
        self.rechargeSeconds = component_constants.ZERO_INT
        self.enginePowerFactor = component_constants.ZERO_FLOAT
        self.maxSpeedFactor = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.deploySeconds = _xml.readInt(xmlCtx, section, 'deploySeconds', 0)
        self.consumeSeconds = _xml.readInt(xmlCtx, section, 'consumeSeconds', 0)
        self.rechargeSeconds = _xml.readInt(xmlCtx, section, 'rechargeSeconds', 0)
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.maxSpeedFactor = _xml.readPositiveFloat(xmlCtx, section, 'maxSpeedFactor')

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, aspect, *args, **kwargs):
        try:
            factors['engine/power'] *= self.enginePowerFactor
            factors['vehicle/maxSpeed'] *= self.maxSpeedFactor
        except:
            pass


class AfterburningBattleRoyale(Equipment):
    __slots__ = ('consumeSeconds', 'enginePowerFactor', 'maxSpeedFactor', 'vehicleRotationSpeed', 'deploySeconds', 'rechargeSeconds')

    def __init__(self):
        super(AfterburningBattleRoyale, self).__init__()
        self.consumeSeconds = component_constants.ZERO_INT
        self.enginePowerFactor = component_constants.ZERO_FLOAT
        self.maxSpeedFactor = component_constants.ZERO_FLOAT
        self.vehicleRotationSpeed = component_constants.ZERO_FLOAT
        self.deploySeconds = component_constants.ZERO_FLOAT
        self.rechargeSeconds = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.consumeSeconds = _xml.readInt(xmlCtx, section, 'consumeSeconds', 0)
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.maxSpeedFactor = _xml.readPositiveFloat(xmlCtx, section, 'maxSpeedFactor')
        self.vehicleRotationSpeed = _xml.readPositiveFloat(xmlCtx, section, 'vehicleRotationSpeed')

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            from debug_utils import LOG_DEBUG_DEV
            factors['engine/power'] *= self.enginePowerFactor
            factors['vehicle/maxSpeed'] *= self.maxSpeedFactor
        except:
            pass

    def _getDescription(self, descr):
        localizeDescr = super(AfterburningBattleRoyale, self)._getDescription(descr)
        return i18n.makeString(localizeDescr, duration=self.consumeSeconds)


class InfluenceZone(object):
    __slots__ = ('radius', 'height', 'depth', 'timer', 'terrainResistance', 'debuffFactors', 'dotParams', 'hotParams', 'influenceType')

    def __init__(self):
        self.radius = component_constants.ZERO_FLOAT
        self.height = component_constants.ZERO_FLOAT
        self.depth = component_constants.ZERO_FLOAT
        self.timer = component_constants.ZERO_FLOAT
        self.terrainResistance = component_constants.ZERO_FLOAT
        self.debuffFactors = component_constants.EMPTY_DICT
        self.dotParams = component_constants.EMPTY_DICT
        self.hotParams = component_constants.EMPTY_DICT
        self.influenceType = component_constants.INFLUENCE_ALL

    def _readConfig(self, xmlCtx, section):
        self.radius = _xml.readPositiveFloat(xmlCtx, section, 'radius')
        self.height = _xml.readPositiveFloat(xmlCtx, section, 'height')
        self.depth = _xml.readNonNegativeFloat(xmlCtx, section, 'depth', 0.0)
        self.timer = _xml.readPositiveFloat(xmlCtx, section, 'timer')
        if section.has_key('terrainResistance'):
            self.terrainResistance = _xml.readPositiveFloat(xmlCtx, section, 'terrainResistance')
        if section.has_key('influenceType'):
            self.influenceType = _xml.readInt(xmlCtx, section, 'influenceType', component_constants.INFLUENCE_ALL, component_constants.INFLUENCE_ENEMY)
        if section.has_key('debuffFactors'):
            self.debuffFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'debuffFactors')
        if section.has_key('dotParams'):
            self.dotParams = DOTParams()
            self.dotParams._readConfig(xmlCtx, section['dotParams'])
        if section.has_key('hotParams'):
            self.hotParams = HOTParams()
            self.hotParams._readConfig(xmlCtx, section['hotParams'])


class TrapPoint(Equipment):
    __slots__ = ('influenceZone',)

    def __init__(self):
        super(TrapPoint, self).__init__()
        self.influenceZone = InfluenceZone()

    def _readConfig(self, xmlCtx, section):
        super(TrapPoint, self)._readConfig(xmlCtx, section)
        self.influenceZone._readConfig(xmlCtx, section['influenceZone'])

    def _getDescription(self, descr):
        localizeDescr = super(TrapPoint, self)._getDescription(descr)
        if self.influenceZone.debuffFactors:
            return i18n.makeString(localizeDescr, duration=int(self.influenceZone.timer), power=int((1 - self.influenceZone.debuffFactors['engine/power']) * 100), maxSpeed=int((1 - self.influenceZone.debuffFactors['vehicle/maxSpeed']) * 100), rotationSpeed=int((1 - self.influenceZone.debuffFactors['vehicle/rotationSpeed']) * 100), chassisRotationSpeed=int((1 - self.influenceZone.debuffFactors['chassis/shotDispersionFactors/rotation']) * 100), turretRotationSpeed=int((1 - self.influenceZone.debuffFactors['turret/rotationSpeed']) * 100))
        return i18n.makeString(localizeDescr, duration=int(self.influenceZone.timer), healPerSecond=int(self.influenceZone.hotParams.healPerTick * 100 / self.influenceZone.hotParams.tickInterval)) if self.influenceZone.hotParams else None


class RageEquipmentConfigReader(object):
    _RAGE_EQUIPMENT_SLOTS = ('reusable', 'cooldownTime', 'deployTime')

    def initRageEquipmentSlots(self):
        self.reusable = False
        self.cooldownTime = component_constants.ZERO_FLOAT
        self.deployTime = component_constants.ZERO_FLOAT

    def readRageEquipmentConfig(self, xmlCtx, section):
        self.reusable = _xml.readBool(xmlCtx, section, 'reusable')
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownTime') if self.reusable else 0.0
        self.deployTime = _xml.readNonNegativeFloat(xmlCtx, section, 'deployTime')


class SharedCooldownConsumableConfigReader(object):
    _SHARED_COOLDOWN_CONSUMABLE_SLOTS = ('cooldownTimeRespawnFactor', 'cooldownTime', 'cooldownFactors', 'sharedCooldownTime', 'consumeAmmo', 'disableAllyDamage')

    def initSharedCooldownConsumableSlots(self):
        self.cooldownTime = component_constants.ZERO_FLOAT
        self.cooldownTimeRespawnFactor = component_constants.ZERO_FLOAT
        self.cooldownFactors = component_constants.EMPTY_DICT
        self.consumeAmmo = False
        self.disableAllyDamage = False

    def readSharedCooldownConsumableConfig(self, xmlCtx, section):
        self.cooldownTimeRespawnFactor = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownTimeRespawnFactor', 1.0)
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownTime')
        self.cooldownFactors = self._readCooldownFactors(xmlCtx, section, 'cooldownFactors')
        self.sharedCooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'sharedCooldownTime')
        self.consumeAmmo = _xml.readBool(xmlCtx, section, 'consumeAmmo')
        self.disableAllyDamage = _xml.readBool(xmlCtx, section, 'disableAllyDamage')

    def _readCooldownFactors(self, xmlCtx, section, name):
        cooldownFactors = {}
        subXmlCtx, subsection = _xml.getSubSectionWithContext(xmlCtx, section, name)
        for vehClass, _ in _xml.getItemsWithContext(subXmlCtx, subsection):
            cooldownFactors[vehClass] = _xml.readNonNegativeFloat(subXmlCtx, subsection, vehClass)

        return cooldownFactors


class CountableConsumableConfigReader(object):
    _CONSUMABLE_SLOTS = ('consumeAmmo',)

    def initCountableConsumableSlots(self):
        self.consumeAmmo = False

    def readCountableConsumableConfig(self, xmlCtx, section):
        self.consumeAmmo = _xml.readBool(xmlCtx, section, 'consumeAmmo')


class CooldownConsumableConfigReader(object):
    _CONSUMABLE_SLOTS = ('deployTime', 'cooldownTime')

    def initConsumableWithDeployTimeSlots(self):
        self.deployTime = component_constants.ZERO_FLOAT
        self.cooldownTime = component_constants.ZERO_FLOAT

    def readConsumableWithDeployTimeConfig(self, xmlCtx, section):
        self.deployTime = _xml.readNonNegativeFloat(xmlCtx, section, 'deployTime')
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownTime')


class TooltipConfigReader(object):
    _SHARED_TOOLTIPS_CONSUMABLE_SLOTS = ('shortDescription', 'longDescription', 'longFilterAlert', 'tooltipIdentifiers')

    def initTooltipInformation(self):
        self.shortDescription = component_constants.EMPTY_STRING
        self.longDescription = component_constants.EMPTY_STRING
        self.shortFilterAlert = component_constants.EMPTY_STRING
        self.longFilterAlert = component_constants.EMPTY_STRING
        self.tooltipIdentifiers = []

    def readTooltipInformation(self, xmlCtx, section):
        if IS_CLIENT:
            self.shortDescription = _xml.readString(xmlCtx, section, 'shortDescription')
            self.longDescription = _xml.readString(xmlCtx, section, 'longDescription')
            self.shortFilterAlert = _xml.readStringOrEmpty(xmlCtx, section, 'shortFilterAlert')
            self.longFilterAlert = _xml.readStringOrEmpty(xmlCtx, section, 'longFilterAlert')
            tooltipsString = _xml.readStringOrNone(xmlCtx, section, 'tooltips')
            if tooltipsString is not None:
                self.tooltipIdentifiers = tooltipsString.split()
        return


class MarkerConfigReader(object):
    _MARKER_SLOTS_ = ('areaVisual', 'areaColor', 'areaMarker', 'areaRadius', 'areaLength', 'areaWidth')

    def initMarkerInformation(self):
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        self.areaRadius = component_constants.ZERO_FLOAT
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        return

    def readMarkerConfig(self, xmlCtx, section):
        self.areaRadius = _xml.readPositiveFloat(xmlCtx, section, 'areaRadius')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.areaLength = self.areaWidth = self.areaRadius * 2


class ArtilleryConfigReader(MarkerConfigReader):
    _ARTILLERY_SLOTS = MarkerConfigReader._MARKER_SLOTS_ + ('delay', 'duration', 'shotsNumber', 'areaRadius', 'shellCompactDescr', 'piercingPower', 'noOwner', 'shotSoundPreDelay', 'wwsoundShot', 'wwsoundEquipmentUsed')

    def initArtillerySlots(self):
        super(ArtilleryConfigReader, self).__init__()
        self.initMarkerInformation()
        self.delay = component_constants.ZERO_FLOAT
        self.duration = component_constants.ZERO_FLOAT
        self.shotsNumber = component_constants.ZERO_INT
        self.shellCompactDescr = component_constants.ZERO_INT
        self.piercingPower = component_constants.ZERO_FLOAT
        self.shotSoundPreDelay = component_constants.ZERO_FLOAT
        self.wwsoundShot = None
        self.wwsoundEquipmentUsed = None
        return

    def readArtilleryConfig(self, xmlCtx, section):
        self.readMarkerConfig(xmlCtx, section)
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay')
        self.duration = _xml.readPositiveFloat(xmlCtx, section, 'duration')
        self.shotsNumber = _xml.readNonNegativeInt(xmlCtx, section, 'shotsNumber')
        self.shellCompactDescr = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        self.piercingPower = _xml.readTupleOfPositiveInts(xmlCtx, section, 'piercingPower', 2)
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.shotSoundPreDelay = _xml.readIntOrNone(xmlCtx, section, 'shotSoundPreDelay')
        self.wwsoundShot = _xml.readStringOrNone(xmlCtx, section, 'wwsoundShot')
        self.wwsoundEquipmentUsed = _xml.readStringOrNone(xmlCtx, section, 'wwsoundEquipmentUsed')


class PlaneConfigReader(object):
    _PLANE_SLOTS = ('delay', 'speed', 'modelName', 'soundEvent', 'heights', 'areaVisual', 'areaColor', 'areaMarker')

    def initPlaneSlots(self):
        self.delay = component_constants.ZERO_FLOAT
        self.speed = component_constants.ZERO_INT
        self.modelName = component_constants.EMPTY_STRING
        self.soundEvent = component_constants.EMPTY_STRING
        self.heights = component_constants.EMPTY_TUPLE
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        return

    def readPlaneConfig(self, xmlCtx, section):
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay')
        self.speed = _xml.readPositiveFloat(xmlCtx, section, 'speed')
        self.modelName = _xml.readString(xmlCtx, section, 'modelName')
        if IS_CLIENT:
            self.soundEvent = _xml.readString(xmlCtx, section, 'wwsoundEvent')
        self.heights = _xml.readTupleOfPositiveInts(xmlCtx, section, 'heights', 2)
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')


class BomberConfigReader(PlaneConfigReader):
    _BOMBER_SLOTS = PlaneConfigReader._PLANE_SLOTS + ('areaLength', 'areaWidth', 'antepositions', 'lateropositions', 'bombingMask', 'waveFraction', 'bombsNumber', 'shellCompactDescr', 'tracerKind', 'piercingPower', 'gravity', 'noOwner', 'wwsoundEquipmentUsed', 'shootingDistance')

    def initBomberSlots(self):
        self.initPlaneSlots()
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
        self.shootingDistance = component_constants.ZERO_FLOAT
        self.noOwner = False
        self.wwsoundEquipmentUsed = None
        return

    def readBomberConfig(self, xmlCtx, section):
        self.readPlaneConfig(xmlCtx, section)
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
        self.shootingDistance = _xml.readNonNegativeFloat(xmlCtx, section, 'shootingDistance', 0.0)
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.wwsoundEquipmentUsed = _xml.readStringOrNone(xmlCtx, section, 'wwsoundEquipmentUsed')


class SmokeConfigReader(object):
    _SMOKE_SLOTS = ('minDelay', 'deltaDelayRange', 'smokeModelName', 'startRadius', 'expandedRadius', 'startHeight', 'expandedHeight', 'heightUpFraction', 'expansionDuration', 'dispersionRadius', 'totalDuration', 'smokeOpacity', 'visionRadiusFactor', 'dotParams', 'areaLength', 'areaWidth', 'projectilesNumber', 'shellCompactDescr', 'areaVisual', 'areaMarker', 'noOwner', 'smokeEffectName', 'shotSoundPreDelay', 'wwsoundShot', 'orthogonalDir', 'randomizeDuration', 'vignetteColor', 'vignetteIntensity')

    def initSmokeSlots(self):
        self.minDelay = component_constants.ZERO_FLOAT
        self.deltaDelayRange = component_constants.EMPTY_TUPLE
        self.smokeModelName = component_constants.EMPTY_STRING
        self.startRadius = component_constants.ZERO_FLOAT
        self.expandedRadius = component_constants.ZERO_FLOAT
        self.startHeight = component_constants.ZERO_FLOAT
        self.expandedHeight = component_constants.ZERO_FLOAT
        self.heightUpFraction = component_constants.ZERO_FLOAT
        self.expansionDuration = component_constants.ZERO_FLOAT
        self.dispersionRadius = component_constants.ZERO_FLOAT
        self.totalDuration = component_constants.ZERO_FLOAT
        self.smokeOpacity = component_constants.ZERO_FLOAT
        self.visionRadiusFactor = component_constants.ZERO_FLOAT
        self.dotParams = None
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.projectilesNumber = component_constants.ZERO_INT
        self.shellCompactDescr = component_constants.ZERO_INT
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        self.noOwner = False
        self.smokeEffectName = component_constants.EMPTY_STRING
        self.shotSoundPreDelay = component_constants.ZERO_FLOAT
        self.wwsoundShot = None
        self.orthogonalDir = False
        self.randomizeDuration = None
        self.vignetteColor = Vector3()
        self.vignetteIntensity = component_constants.ZERO_FLOAT
        return

    def readSmokeConfig(self, xmlCtx, section):
        self.minDelay = _xml.readPositiveFloat(xmlCtx, section, 'minDelay')
        self.deltaDelayRange = _xml.readTupleOfPositiveFloats(xmlCtx, section, 'deltaDelayRange', 2)
        self.smokeModelName = _xml.readString(xmlCtx, section, 'smokeModelName')
        self.startRadius = _xml.readPositiveFloat(xmlCtx, section, 'startRadius')
        self.expandedRadius = _xml.readPositiveFloat(xmlCtx, section, 'expandedRadius')
        self.startHeight = _xml.readPositiveFloat(xmlCtx, section, 'startHeight')
        self.expandedHeight = _xml.readPositiveFloat(xmlCtx, section, 'expandedHeight')
        self.heightUpFraction = _xml.readPositiveFloat(xmlCtx, section, 'heightUpFraction')
        self.expansionDuration = _xml.readPositiveFloat(xmlCtx, section, 'expansionDuration')
        self.dispersionRadius = _xml.readPositiveFloat(xmlCtx, section, 'dispersionRadius')
        self.totalDuration = _xml.readPositiveFloat(xmlCtx, section, 'totalDuration')
        self.smokeOpacity = _xml.readPositiveFloat(xmlCtx, section, 'smokeOpacity')
        self.visionRadiusFactor = _xml.readPositiveFloat(xmlCtx, section, 'visionRadiusFactor')
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.projectilesNumber = _xml.readNonNegativeInt(xmlCtx, section, 'projectilesNumber')
        self.shellCompactDescr = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.smokeEffectName = _xml.readString(xmlCtx, section, 'smokeEffectName')
        self.shotSoundPreDelay = _xml.readIntOrNone(xmlCtx, section, 'shotSoundPreDelay')
        self.wwsoundShot = _xml.readStringOrNone(xmlCtx, section, 'wwsoundShot')
        if section.has_key('randomizeDuration'):
            self.randomizeDuration = _xml.readFloat(xmlCtx, section, 'randomizeDuration')
        if section.has_key('dotParams'):
            self.dotParams = DOTParams(ATTACK_REASON_INDICES[ATTACK_REASON.SMOKE])
            self.dotParams._readConfig(xmlCtx, section['dotParams'])
        if IS_CLIENT:
            self.vignetteColor = _xml.readVector3(xmlCtx, section, 'vignetteColor')
            self.vignetteIntensity = _xml.readFloat(xmlCtx, section, 'vignetteIntensity')


class ReconConfigReader(PlaneConfigReader):
    _RECON_SLOTS = PlaneConfigReader._PLANE_SLOTS + ('areaRadius', 'scanPointsAmount', 'spottingDuration', 'antepositions', 'lateropositions', 'areaWidth', 'areaLength', 'wwsoundEquipmentUsed')

    def initReconSlots(self):
        self.initPlaneSlots()
        self.areaRadius = component_constants.ZERO_FLOAT
        self.scanPointsAmount = component_constants.ZERO_INT
        self.spottingDuration = component_constants.ZERO_FLOAT
        self.antepositions = component_constants.EMPTY_TUPLE
        self.lateropositions = component_constants.EMPTY_TUPLE
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.wwsoundEquipmentUsed = None
        return

    def readReconConfig(self, xmlCtx, section):
        self.readPlaneConfig(xmlCtx, section)
        self.areaRadius = _xml.readPositiveFloat(xmlCtx, section, 'areaRadius')
        self.scanPointsAmount = _xml.readNonNegativeInt(xmlCtx, section, 'scanPointsAmount')
        self.spottingDuration = _xml.readPositiveFloat(xmlCtx, section, 'spottingDuration')
        self.antepositions = _xml.readTupleOfFloats(xmlCtx, section, 'antepositions')
        self.lateropositions = _xml.readTupleOfFloats(xmlCtx, section, 'lateropositions')
        self.areaWidth = self.areaRadius * 2
        self.areaLength = self.areaRadius * (2 + self.scanPointsAmount - 1)
        self.wwsoundEquipmentUsed = _xml.readStringOrNone(xmlCtx, section, 'wwsoundEquipmentUsed')


class BuffConfigReader(object):
    _BUFF_SLOTS = ('duration', 'inactivationDelay', 'radius', 'wwsoundEquipmentUsed')

    def initBuffSlots(self):
        self.duration = component_constants.ZERO_FLOAT
        self.inactivationDelay = component_constants.ZERO_FLOAT
        self.radius = component_constants.ZERO_FLOAT
        self.wwsoundEquipmentUsed = None
        return

    def readBuffConfig(self, xmlCtx, section):
        self.duration = _xml.readPositiveFloat(xmlCtx, section, 'duration')
        self.inactivationDelay = _xml.readNonNegativeFloat(xmlCtx, section, 'inactivationDelay')
        self.radius = _xml.readFloat(xmlCtx, section, 'radius')
        self.wwsoundEquipmentUsed = _xml.readStringOrNone(xmlCtx, section, 'wwsoundEquipmentUsed')


class InspireConfigReader(BuffConfigReader):
    _INSPIRE_SLOTS = BuffConfigReader._BUFF_SLOTS + ('increaseFactors',)

    def initInspireSlots(self):
        super(InspireConfigReader, self).initBuffSlots()
        self.increaseFactors = {}

    def readInspireConfig(self, xmlCtx, section):
        super(InspireConfigReader, self).readBuffConfig(xmlCtx, section)
        self.increaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'increaseFactors')


class HealPointConfigReader(BuffConfigReader):
    _HEAL_POINT_SLOTS = BuffConfigReader._BUFF_SLOTS + ('healPerTick', 'expireByDamageReceived', 'healGroup', 'tickInterval', 'height', 'depth')

    def initHealPointSlots(self):
        super(HealPointConfigReader, self).initBuffSlots()
        self.healPerTick = component_constants.ZERO_FLOAT
        self.expireByDamageReceived = False
        self.healGroup = None
        self.tickInterval = 1.0
        self.height = 1.0
        self.depth = 1.0
        return

    def readHealPointConfig(self, xmlCtx, section):
        super(HealPointConfigReader, self).readBuffConfig(xmlCtx, section)
        self.healPerTick = _xml.readPositiveFloat(xmlCtx, section, 'healPerTick')
        self.expireByDamageReceived = _xml.readBool(xmlCtx, section, 'expireByDamageReceived')
        self.healGroup = _xml.readIntOrNone(xmlCtx, section, 'healGroup')
        self.tickInterval = _xml.readPositiveFloat(xmlCtx, section, 'tickInterval', 1.0)
        self.height = _xml.readPositiveFloat(xmlCtx, section, 'height', 1.0)
        self.depth = _xml.readPositiveFloat(xmlCtx, section, 'depth', 1.0)


class ArenaAimLimits(object):
    __slots__ = ('insetRadius', 'areaSwitch', 'areaColor')

    def __init__(self):
        self.insetRadius = 0.0
        self.areaSwitch = None
        self.areaColor = None
        return

    def __repr__(self):
        return 'ArenaAimLimits (Radius:{}, Visual:{}, Color:{}, )'.format(self.insetRadius, self.areaSwitch, self.areaColor)

    def _readConfig(self, xmlCtx, section):
        self.insetRadius = _xml.readPositiveFloat(xmlCtx, section, 'insetRadius', 0)
        self.areaSwitch = _xml.readStringOrNone(xmlCtx, section, 'areaSwitch')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')

    @staticmethod
    def readConfig(xmlCtx, section, subsection_name):
        if not section.has_key(subsection_name):
            return None
        else:
            result = ArenaAimLimits()
            result._readConfig(xmlCtx, section[subsection_name])
            return result


class ArcadeEquipmentConfigReader(object):
    _SHARED_ARCADE_SLOTS = ('minApplyRadius', 'maxApplyRadius', 'cameraPivotPosMin', 'cameraPivotPosMax', 'arenaAimLimits')

    def initArcadeInformation(self):
        self.minApplyRadius = component_constants.ZERO_FLOAT
        self.maxApplyRadius = component_constants.ZERO_FLOAT
        self.cameraPivotPosMin = Vector3()
        self.cameraPivotPosMax = Vector3()
        self.arenaAimLimits = None
        return

    def readArcadeInformation(self, xmlCtx, section):
        self.minApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'minApplyRadius', component_constants.ZERO_FLOAT)
        self.maxApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'maxApplyRadius', component_constants.ZERO_FLOAT)
        self.arenaAimLimits = ArenaAimLimits.readConfig(xmlCtx, section, 'arenaAimLimits')
        if IS_CLIENT:
            self.cameraPivotPosMin = _xml.readVector3OrNone(xmlCtx, section, 'cameraPivotPosMin')
            self.cameraPivotPosMax = _xml.readVector3OrNone(xmlCtx, section, 'cameraPivotPosMax')


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
        for levelID, (levelFilter, _) in enumerate(self._config):
            if levelFilter.checkCompatibility(vehicleDescr):
                return levelID

        return None

    def getLevelParamsForDevice(self, optionalDevice):
        for levelFilter, levelParams in self._config:
            if levelFilter.checkCompatibilityWithDevice(optionalDevice):
                return levelParams

        return None

    def updateVehicleAttrFactorsForAspect(self, vehicleDescr, factors, _, *args, **kwargs):
        levelID = self.getLevelIDForVehicle(vehicleDescr)
        if levelID is not None:
            self.updateVehicleAttrFactorsForLevel(factors, levelID)
        return

    def updateVehicleAttrFactorsForLevel(self, factors, levelID):
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
        factors[attribute] += value


class InvisibilityBattleBooster(DynamicEquipment):
    __slots__ = ()

    def _readLevelConfig(self, xmlCtx, section):
        filter = _OptionalDeviceFilter(xmlCtx, section['deviceFilter'])
        attribute = _xml.readNonEmptyString(xmlCtx, section, 'attribute')
        factors = _xml.readTupleOfPositiveFloats(xmlCtx, section, 'factors', count=2)
        return (filter, (attribute, factors))

    def _updateVehicleAttrFactorsImpl(self, factors, levelParams):
        attribute, factor = levelParams
        factors[attribute][0] += factor[0]
        factors[attribute][1] *= factor[1]


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
        for device in vehicleDescr.optionalDevices:
            if device is None:
                continue
            tags = device.tags
            if self.__requiredTags.issubset(tags) and len(self.__incompatibleTags.intersection(tags)) == 0:
                return True

        return False

    def checkCompatibilityWithDevice(self, optionalDevice):
        tags = optionalDevice.tags
        return True if self.__requiredTags.issubset(tags) and len(self.__incompatibleTags.intersection(tags)) == 0 else False


class RageArtillery(Equipment, RageEquipmentConfigReader, ArtilleryConfigReader):
    __slots__ = RageEquipmentConfigReader._RAGE_EQUIPMENT_SLOTS + ArtilleryConfigReader._ARTILLERY_SLOTS

    def __init__(self):
        super(RageArtillery, self).__init__()
        self.initRageEquipmentSlots()
        self.initArtillerySlots()

    def _readConfig(self, xmlCtx, section):
        self.readRageEquipmentConfig(xmlCtx, section)
        self.readArtilleryConfig(xmlCtx, section)


class RageBomber(Equipment, RageEquipmentConfigReader, BomberConfigReader):
    __slots__ = RageEquipmentConfigReader._RAGE_EQUIPMENT_SLOTS + BomberConfigReader._BOMBER_SLOTS

    def __init__(self):
        super(RageBomber, self).__init__()
        self.initRageEquipmentSlots()
        self.initBomberSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readRageEquipmentConfig(xmlCtx, scriptSection)
        self.readBomberConfig(xmlCtx, scriptSection)


class ConsumableArtillery(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, ArtilleryConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + ArtilleryConfigReader._ARTILLERY_SLOTS

    def __init__(self):
        super(ConsumableArtillery, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initArtillerySlots()

    def _readConfig(self, xmlCtx, section):
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.readArtilleryConfig(xmlCtx, section)


class ConsumableBomber(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, BomberConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + BomberConfigReader._BOMBER_SLOTS

    def __init__(self):
        super(ConsumableBomber, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initBomberSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readSharedCooldownConsumableConfig(xmlCtx, scriptSection)
        self.readBomberConfig(xmlCtx, scriptSection)


class ConsumableRecon(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, ReconConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + ReconConfigReader._RECON_SLOTS

    def __init__(self):
        super(ConsumableRecon, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initReconSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readSharedCooldownConsumableConfig(xmlCtx, scriptSection)
        self.readReconConfig(xmlCtx, scriptSection)


class ConsumableSmoke(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, SmokeConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + SmokeConfigReader._SMOKE_SLOTS

    def __init__(self):
        super(ConsumableSmoke, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initSmokeSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readSharedCooldownConsumableConfig(xmlCtx, scriptSection)
        self.readSmokeConfig(xmlCtx, scriptSection)


class ConsumableInspire(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, InspireConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + InspireConfigReader._INSPIRE_SLOTS

    def __init__(self):
        super(ConsumableInspire, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initInspireSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readSharedCooldownConsumableConfig(xmlCtx, scriptSection)
        self.readInspireConfig(xmlCtx, scriptSection)


class PassiveEngineering(Equipment, TooltipConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + ('captureStopping', 'captureBlockBonusTime', 'captureSpeedFactor', 'resupplyCooldownFactor', 'resupplyHealthPointsFactor', 'resupplyShellsFactor')

    def __init__(self):
        super(PassiveEngineering, self).__init__()
        self.initTooltipInformation()
        self.captureStopping = False
        self.captureBlockBonusTime = component_constants.ZERO_FLOAT
        self.captureSpeedFactor = component_constants.ZERO_FLOAT
        self.resupplyCooldownFactor = component_constants.ZERO_FLOAT
        self.resupplyHealthPointsFactor = component_constants.ZERO_FLOAT
        self.resupplyShellsFactor = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.captureStopping = _xml.readBool(xmlCtx, scriptSection, 'captureStopping')
        self.captureBlockBonusTime = _xml.readPositiveFloat(xmlCtx, scriptSection, 'captureBlockBonusTime')
        self.captureSpeedFactor = _xml.readPositiveFloat(xmlCtx, scriptSection, 'captureSpeedFactor')
        self.resupplyCooldownFactor = _xml.readPositiveFloat(xmlCtx, scriptSection, 'resupplyCooldownFactor')
        self.resupplyHealthPointsFactor = _xml.readPositiveFloat(xmlCtx, scriptSection, 'resupplyHealthPointsFactor')
        self.resupplyShellsFactor = _xml.readPositiveFloat(xmlCtx, scriptSection, 'resupplyShellsFactor')


class EpicArtillery(ConsumableArtillery):
    pass


class EpicBomber(ConsumableBomber):
    pass


class EpicRecon(ConsumableRecon):
    pass


class EpicSmoke(ConsumableSmoke):
    pass


class EpicInspire(ConsumableInspire):
    pass


class EpicEngineering(PassiveEngineering):
    pass


class AreaOfEffectEquipment(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, ArcadeEquipmentConfigReader):
    __slots__ = ('delay', 'duration', 'lifetime', 'shotsNumber', 'areaRadius', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'areaShow', 'noOwner', 'attackerType', 'shotSoundPreDelay', 'wwsoundShot', 'wwsoundEquipmentUsed', 'shotEffect', 'effects', 'actionsConfig', 'explodeDestructible') + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def _readConfig(self, xmlCtx, section):
        super(AreaOfEffectEquipment, self)._readConfig(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.delay = section.readFloat('delay')
        self.duration = section.readFloat('duration')
        self.lifetime = section.readFloat('lifetime')
        self.shotsNumber = section.readInt('shotsNumber')
        self.areaRadius = section.readFloat('areaRadius')
        self.areaLength = section.readFloat('areaLength', self.areaRadius * 2)
        self.areaWidth = section.readFloat('areaWidth', self.areaRadius * 2)
        self.areaVisual = section.readString('areaVisual') or None
        self.areaColor = section.readInt('areaColor') or None
        self.areaShow = section.readString('areaShow').lower() or None
        self.noOwner = section.readBool('noOwner')
        self.attackerType = section.readString('attackerType').upper()
        self.shotSoundPreDelay = section.readInt('shotSoundPreDelay')
        self.wwsoundShot = section.readString('wwsoundShot')
        self.wwsoundEquipmentUsed = section.readString('wwsoundEquipmentUsed')
        self.shotEffect = section.readString('shotEffect')
        self.effects = {name:self._readEffectConfig(effect) for name, effect in section['effects'].items()}
        if IS_CELLAPP:
            self.actionsConfig = [ self._readActionConfig(conf) for conf in section['actions'].values() ]
            self.explodeDestructible = section.readBool('explodeDestructible')
        else:
            self.actionsConfig = None
            self.explodeDestructible = None
        return

    def _readEffectConfig(self, section):
        return None if not section else {'shotEffects': section.readString('shotEffects').split(),
         'sequences': section.readString('sequences').split(),
         'groundRaycast': section.readBool('groundRaycast'),
         'offsetDeviation': section.readFloat('offsetDeviation'),
         'repeatCount': section.readInt('repeatCount', 1),
         'repeatDelay': section.readFloat('repeatDelay'),
         'areaColor': _xml.readIntOrNone(None, section, 'areaColor')}

    def _readActionConfig(self, section):
        if not section:
            return None
        else:
            actionType = section.readString('type')
            actionClass = getattr(vehicleActions, actionType)
            return {'type': actionType,
             'applyTo': section.readString('applyTo'),
             'args': actionClass.parseXML(section['args'])}


class AttackBomberEquipment(AreaOfEffectEquipment):
    pass


UpgradeInfo = NamedTuple('UpgradeInfo', [('upgradedCompDescr', int)])

class UpgradableItem(Artefact):

    def __init__(self, typeID, itemID, itemName, compactDescr):
        super(UpgradableItem, self).__init__(typeID, itemID, itemName, compactDescr)
        self._upgradeInfo = None
        return

    @property
    def upgradeInfo(self):
        return self._upgradeInfo

    def initUpgradableItem(self):
        self._upgradeInfo = None
        return

    def _readConfig(self, xmlCtx, section):
        super(UpgradableItem, self)._readConfig(xmlCtx, section)
        self._readUpgradableConfig(xmlCtx, section, self.compactDescr)

    def _readUpgradableConfig(self, xmlCtx, scriptSection, itemCompDescr):
        upgradeInfoSection = scriptSection['upgradeInfo']
        upgradedCD = _xml.readInt(xmlCtx, upgradeInfoSection, 'upgradedCompDescr')
        self._upgradeInfo = UpgradeInfo(upgradedCD)
        _readPriceForOperation(xmlCtx, upgradeInfoSection, ITEM_OPERATION.UPGRADE, (itemCompDescr, upgradedCD))


class UpgradedItem(Artefact):
    pass


class UpgradableStaticDevice(StaticOptionalDevice, UpgradableItem):
    pass


class UpgradedStaticDevice(StaticOptionalDevice, UpgradedItem):
    pass


class UpgradableImprovedConfiguration(ImprovedConfiguration, UpgradableItem):
    pass


class UpgradedImprovedConfiguration(ImprovedConfiguration, UpgradedItem):
    pass


class UpgradableRotationMechanisms(RotationMechanisms, UpgradableItem):
    pass


class UpgradedRotationMechanisms(RotationMechanisms, UpgradedItem):
    pass


class UpgradableLowNoiseTracks(LowNoiseTracks, UpgradableItem):
    pass


class UpgradedLowNoiseTracks(LowNoiseTracks, UpgradedItem):
    pass


class BRBomber(Equipment, TooltipConfigReader, CountableConsumableConfigReader, CooldownConsumableConfigReader, BomberConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + CooldownConsumableConfigReader._CONSUMABLE_SLOTS + BomberConfigReader._BOMBER_SLOTS + ('influenceZone',)

    def __init__(self):
        super(BRBomber, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initConsumableWithDeployTimeSlots()
        self.initBomberSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readConsumableWithDeployTimeConfig(xmlCtx, scriptSection)
        self.readBomberConfig(xmlCtx, scriptSection)
        if scriptSection.has_key('influenceZone'):
            self.influenceZone = InfluenceZone()
            self.influenceZone._readConfig(xmlCtx, scriptSection['influenceZone'])
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription)


class BRBomberArcade(BRBomber, ArcadeEquipmentConfigReader):
    __slots__ = BRBomber.__slots__ + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(BRBomberArcade, self).__init__()
        self.initArcadeInformation()

    def _readConfig(self, xmlCtx, scriptSection):
        super(BRBomberArcade, self)._readConfig(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)


class BRSmoke(Equipment, TooltipConfigReader, CountableConsumableConfigReader, CooldownConsumableConfigReader, SmokeConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + CooldownConsumableConfigReader._CONSUMABLE_SLOTS + SmokeConfigReader._SMOKE_SLOTS

    def __init__(self):
        super(BRSmoke, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initConsumableWithDeployTimeSlots()
        self.initSmokeSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readConsumableWithDeployTimeConfig(xmlCtx, scriptSection)
        self.readSmokeConfig(xmlCtx, scriptSection)
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription, duration=int(self.totalDuration))


class BRSmokeArcade(BRSmoke, ArcadeEquipmentConfigReader):
    __slots__ = BRSmoke.__slots__ + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(BRSmokeArcade, self).__init__()
        self.orthogonalDir = True
        self.initArcadeInformation()

    def _readConfig(self, xmlCtx, scriptSection):
        super(BRSmokeArcade, self)._readConfig(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)


class BRSelfBuff(Equipment, TooltipConfigReader, CountableConsumableConfigReader, CooldownConsumableConfigReader, InspireConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + CooldownConsumableConfigReader._CONSUMABLE_SLOTS + InspireConfigReader._INSPIRE_SLOTS

    def __init__(self):
        super(BRSelfBuff, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initConsumableWithDeployTimeSlots()
        self.initInspireSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readConsumableWithDeployTimeConfig(xmlCtx, scriptSection)
        self.readInspireConfig(xmlCtx, scriptSection)
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription, duration=int(self.inactivationDelay))


class BRBerserker(BRSelfBuff):
    __slots__ = ('dotParams',)

    def __init__(self):
        super(BRBerserker, self).__init__()
        self.dotParams = DOTParams(ATTACK_REASON_INDICES[ATTACK_REASON.BERSERKER])

    def _readConfig(self, xmlCtx, scriptSection):
        super(BRBerserker, self)._readConfig(xmlCtx, scriptSection)
        self.dotParams._readConfig(xmlCtx, scriptSection['dotParams'])


class DOTParams(object):
    __slots__ = ('damagePerTick', 'restoreHealth', 'tickInterval', 'canDie', 'groupID', 'attackReasonID')

    def __init__(self, attackReasonID=ATTACK_REASON_INDICES[ATTACK_REASON.NONE]):
        self.damagePerTick = 0.0
        self.tickInterval = 1.0
        self.restoreHealth = True
        self.canDie = False
        self.groupID = 0
        self.attackReasonID = attackReasonID

    def __repr__(self):
        return 'dotParams (Damage:{}, Tick:{}, RestoreHealth:{}, CanKill:{}, groupId:{}, attackReasonId:{})'.format(self.damagePerTick, self.tickInterval, self.restoreHealth, self.canDie, self.groupID, self.attackReasonID)

    def _readConfig(self, xmlCtx, scriptSection):
        self.tickInterval = _xml.readPositiveFloat(xmlCtx, scriptSection, 'tickInterval', 1.0)
        self.damagePerTick = _xml.readNonNegativeFloat(xmlCtx, scriptSection, 'damagePerTick', 0.0)
        self.restoreHealth = _xml.readBool(xmlCtx, scriptSection, 'restoreHealth', True)
        self.canDie = _xml.readBool(xmlCtx, scriptSection, 'canDie', True)
        self.groupID = scriptSection.readInt('groupID')


class HOTParams(object):
    __slots__ = ('healPerTick', 'healCrew', 'healDevices', 'healGroup', 'tickInterval')

    def __init__(self):
        self.healPerTick = 0.0
        self.healCrew = False
        self.healDevices = False
        self.healGroup = None
        self.tickInterval = 1.0
        return

    def __repr__(self):
        return 'hotParams ({},{},{},{})'.format(self.healPerTick, self.healCrew, self.healDevices, self.tickInterval)

    def _readConfig(self, xmlCtx, scriptSection):
        self.healPerTick = _xml.readPositiveFloat(xmlCtx, scriptSection, 'healPerTick', 0.0)
        self.healCrew = _xml.readBool(xmlCtx, scriptSection, 'healCrew', False)
        self.healDevices = _xml.readBool(xmlCtx, scriptSection, 'healDevices', False)
        self.healGroup = _xml.readIntOrNone(xmlCtx, scriptSection, 'healGroup')
        self.tickInterval = _xml.readPositiveFloat(xmlCtx, scriptSection, 'tickInterval', 1.0)


class _ClientSpawnBotVisuals(object):
    __slots__ = ('markerPositionOffset', 'markerScale', 'deliveringAnimationDuration', 'deliveringAnimationStartDelay', 'highlightDelay')

    def __init__(self, xmlCtx, scriptSection):
        self.markerPositionOffset = _xml.readVector3(xmlCtx, scriptSection, 'markerPositionOffset', Vector3(0, 0, 0))
        self.markerScale = _xml.readVector3(xmlCtx, scriptSection, 'markerScale', Vector3(1, 1, 1))
        self.deliveringAnimationDuration = _xml.readNonNegativeFloat(xmlCtx, scriptSection, 'deliveringAnimationDuration', 0.0)
        self.deliveringAnimationStartDelay = _xml.readNonNegativeFloat(xmlCtx, scriptSection, 'deliveringAnimationStartDelay', 0.0)
        self.highlightDelay = _xml.readFloat(xmlCtx, scriptSection, 'highlightDelay', 0.0)


class BRHealPoint(Equipment, TooltipConfigReader, CountableConsumableConfigReader, CooldownConsumableConfigReader, HealPointConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + CooldownConsumableConfigReader._CONSUMABLE_SLOTS + HealPointConfigReader._HEAL_POINT_SLOTS

    def __init__(self):
        super(BRHealPoint, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initConsumableWithDeployTimeSlots()
        self.initHealPointSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readConsumableWithDeployTimeConfig(xmlCtx, scriptSection)
        self.readHealPointConfig(xmlCtx, scriptSection)
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription, duration=int(self.duration), count=int(self.healPerTick * 100 / self.tickInterval))


class RegenerationKit(Equipment):
    __slots__ = ('healthRegenPerTick', 'initialHeal', 'healTime', 'healGroup', 'tickInterval')

    def __init__(self):
        super(RegenerationKit, self).__init__()
        self.healthRegenPerTick = component_constants.ZERO_FLOAT
        self.initialHeal = component_constants.ZERO_FLOAT
        self.healTime = component_constants.ZERO_FLOAT
        self.healGroup = None
        self.tickInterval = 1.0
        return

    def _readConfig(self, xmlCtx, section):
        self.healthRegenPerTick = _xml.readNonNegativeFloat(xmlCtx, section, 'healthRegenPerTick', 0.0)
        self.initialHeal = _xml.readNonNegativeFloat(xmlCtx, section, 'initialHeal', 0.0)
        self.healTime = _xml.readNonNegativeFloat(xmlCtx, section, 'healTime', 0.0)
        self.healGroup = _xml.readIntOrNone(xmlCtx, section, 'healGroup')
        self.tickInterval = _xml.readPositiveFloat(xmlCtx, section, 'tickInterval', 1.0)

    def _getDescription(self, descr):
        localizeDescr = super(RegenerationKit, self)._getDescription(descr)
        return i18n.makeString(localizeDescr, count=int(self.healthRegenPerTick * 100 / self.tickInterval), duration=int(self.healTime))


class MineParams(object):
    __slots__ = ('triggerRadius', 'triggerHeight', 'triggerDepth', 'influenceType', 'lifetime', 'damage', 'shell')

    def __init__(self):
        self.triggerRadius = 1.0
        self.triggerHeight = 1.0
        self.triggerDepth = 0.0
        self.influenceType = component_constants.INFLUENCE_ALL
        self.lifetime = 10
        self.damage = 100
        self.shell = None
        return

    def __repr__(self):
        return 'motParams ({}, {}, {}, {}, {}, {}, {})'.format(self.triggerRadius, self.triggerHeight, self.triggerDepth, self.influenceType, self.lifetime, self.damage, self.shell)

    def _readConfig(self, xmlCtx, section):
        self.triggerRadius = _xml.readPositiveFloat(xmlCtx, section, 'triggerRadius')
        self.triggerHeight = _xml.readPositiveFloat(xmlCtx, section, 'triggerHeight')
        self.triggerDepth = _xml.readNonNegativeFloat(xmlCtx, section, 'triggerDepth', 0.0)
        self.influenceType = _xml.readInt(xmlCtx, section, 'influenceType', component_constants.INFLUENCE_ALL, component_constants.INFLUENCE_ENEMY)
        self.lifetime = _xml.readPositiveInt(xmlCtx, section, 'lifetime')
        self.damage = _xml.readNonNegativeInt(xmlCtx, section, 'damage')
        if section.has_key('shellCompactDescr'):
            self.shell = _xml.readInt(xmlCtx, section, 'shellCompactDescr')


class BattleRoyaleMinefield(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, ArcadeEquipmentConfigReader, CountableConsumableConfigReader, CooldownConsumableConfigReader):
    __slots__ = ('bombsPattern', 'mineParams', 'noOwner', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'areaMarker')

    def __init__(self):
        super(BattleRoyaleMinefield, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initArcadeInformation()
        self.bombsPattern = []
        self.mineParams = MineParams()
        self.noOwner = False
        self.areaLength = 0
        self.areaWidth = 0
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        return

    def _readConfig(self, xmlCtx, section):
        bombs = _xml.readTupleOfFloats(xmlCtx, section, 'bombsPattern')
        self.bombsPattern = [ (bombs[b], bombs[b + 1]) for b in range(0, len(bombs) - 1, 2) ]
        self.mineParams._readConfig(xmlCtx, section['mineParams'])
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readConsumableWithDeployTimeConfig(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription, duration=int(self.mineParams.lifetime))


class ConsumableSpawnKamikaze(Equipment, TooltipConfigReader, CountableConsumableConfigReader, MarkerConfigReader, CooldownConsumableConfigReader, ArcadeEquipmentConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + CooldownConsumableConfigReader._CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + MarkerConfigReader._MARKER_SLOTS_ + ('botType', 'botVehCompDescr', 'botLifeTime', 'botSpawnPointOffset', 'botXRayFactor', 'clientVisuals', 'explosionRadius', 'explosionDamage', 'explosionByShoot', 'damageReductionRate', 'delay')

    def __init__(self):
        super(ConsumableSpawnKamikaze, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initConsumableWithDeployTimeSlots()
        self.initArcadeInformation()
        self.initMarkerInformation()
        self.botType = component_constants.EMPTY_STRING
        self.botVehCompDescr = component_constants.EMPTY_STRING
        self.botLifeTime = component_constants.ZERO_FLOAT
        self.botSpawnPointOffset = None
        self.botXRayFactor = 1.0
        self.explosionRadius = component_constants.ZERO_FLOAT
        self.explosionDamage = component_constants.ZERO_FLOAT
        self.explosionByShoot = False
        self.damageReductionRate = component_constants.ZERO_FLOAT
        self.clientVisuals = component_constants.EMPTY_DICT
        self.delay = component_constants.ZERO_FLOAT
        return

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readConsumableWithDeployTimeConfig(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)
        self.readMarkerConfig(xmlCtx, scriptSection)
        self.botType = _xml.readString(xmlCtx, scriptSection, 'botType')
        self.botVehCompDescr = _xml.readString(xmlCtx, scriptSection, 'botVehCompDescr')
        self.delay = _xml.readFloat(xmlCtx, scriptSection, 'delay', 0.0)
        self.botLifeTime = _xml.readFloat(xmlCtx, scriptSection, 'botLifeTime', 0.0)
        self.botSpawnPointOffset = _xml.readVector3(xmlCtx, scriptSection, 'botSpawnPointOffset', Vector3())
        self.botXRayFactor = _xml.readFloat(xmlCtx, scriptSection, 'botXRayFactor', 0.0)
        self.explosionRadius = _xml.readFloat(xmlCtx, scriptSection, 'explosionRadius', 0.0)
        self.explosionDamage = _xml.readFloat(xmlCtx, scriptSection, 'explosionDamage', 0.0)
        self.explosionByShoot = _xml.readBool(xmlCtx, scriptSection, 'explosionByShoot', False)
        self.damageReductionRate = _xml.readFloat(xmlCtx, scriptSection, 'damageReductionRate', 0.0)
        self.vehicleRemoveDelay = _xml.readInt(xmlCtx, scriptSection, 'vehicleRemoveDelay', 0.0)
        self.clientRemovalNotificationDelay = _xml.readInt(xmlCtx, scriptSection, 'clientRemovalNotificationDelay', 0.0)
        if IS_CLIENT:
            self.clientVisuals = _ClientSpawnBotVisuals(scriptSection, scriptSection['clientVisuals'])
            self.longDescription = i18n.makeString(self.longDescription, duration=int(self.botLifeTime))


class SpawnKamikaze(ConsumableSpawnKamikaze):
    pass


def _readKpi(xmlCtx, section):
    from gui.shared.gui_items import KPI
    kpi = []
    for kpiType, subsec in section.items():
        if kpiType not in KPI.Type.ALL():
            _xml.raiseWrongXml(xmlCtx, kpiType, 'unsupported KPI type')
            return
        if kpiType == KPI.Type.ONE_OF:
            kpi.append(KPI(KPI.Name.COMPOUND_KPI, _readKpi(xmlCtx, subsec), KPI.Type.ONE_OF))
        if kpiType == KPI.Type.AGGREGATE_MUL:
            kpi.append(_readAggregateKPI(xmlCtx, subsec, kpiType))
        kpi.append(_readKpiValue(xmlCtx, subsec, kpiType))

    return kpi


def _readKpiValue(xmlCtx, section, kpiType):
    from gui.shared.gui_items import KPI
    name = section.readString('name')
    value = section.readFloat('value')
    specValue = section.readString('specValue')
    vehicleTypes = section.readString('vehicleTypes').split()
    if not name:
        _xml.raiseWrongXml(xmlCtx, kpiType, 'empty <name> tag not allowed')
    elif name not in KPI.Name.ALL():
        _xml.raiseWrongXml(xmlCtx, kpiType, 'unsupported value in <name> tag')
    return KPI(name, value, kpiType, float(specValue) if specValue else None, vehicleTypes)


def _readAggregateKPI(xmlCtx, section, kpiType):
    from gui.shared.gui_items import KPI, AGGREGATE_TO_SINGLE_TYPE_KPI_MAP
    subKpies = []
    for key, subsec in section.items():
        if key in KPI.Type.ALL():
            if key != AGGREGATE_TO_SINGLE_TYPE_KPI_MAP.get(kpiType, None):
                _xml.raiseWrongXml(xmlCtx, key, 'unsupported KPI type for aggregating')
            subKpies.append(_readKpiValue(xmlCtx, subsec, key))

    if not subKpies:
        _xml.raiseWrongXml(xmlCtx, kpiType, 'has not KPI for aggregating')
    name = section.readString('name')
    if not name:
        _xml.raiseWrongXml(xmlCtx, kpiType, 'empty <name> tag not allowed')
    elif name not in KPI.Name.ALL():
        _xml.raiseWrongXml(xmlCtx, kpiType, 'unsupported value in <name> tag')
    return KPI(name, subKpies, kpiType)


_readTags = vehicles._readTags

def _readStun(xmlCtx, scriptSection):
    stunResistanceEffect = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceEffect') if scriptSection.has_key('stunResistanceEffect') else 0.0
    stunResistanceDuration = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceDuration') if scriptSection.has_key('stunResistanceDuration') else 0.0
    repeatedStunDurationFactor = _xml.readFraction(xmlCtx, scriptSection, 'repeatedStunDurationFactor') if scriptSection.has_key('repeatedStunDurationFactor') else 1.0
    return (stunResistanceEffect, stunResistanceDuration, repeatedStunDurationFactor)


def _readReuseParams(xmlCtx, scriptSection):
    return (_xml.readInt(xmlCtx, scriptSection, 'reuseCount', minVal=-1) if scriptSection.has_key('reuseCount') else 0, _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds', minVal=0) if scriptSection.has_key('cooldownSeconds') else 0)


class OPT_DEV_TYPE_TAG(object):
    TROPHY_BASIC = 'trophyBasic'
    TROPHY_UPGRADED = 'trophyUpgraded'
    DELUXE = 'deluxe'
    ALL = {TROPHY_BASIC, TROPHY_UPGRADED, DELUXE}

    @staticmethod
    def checkTags(tags):
        intersectionTags = tags & OPT_DEV_TYPE_TAG.ALL
        return len(intersectionTags) < 2


class AoeEffects(object):
    START = 'start'
    ACTION = 'action'


class AreaShow(object):
    BEFORE = 'before'
    ALWAYS = 'always'
