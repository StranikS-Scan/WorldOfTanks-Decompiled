# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/artefacts.py
import os
from re import findall
from enum import Enum, unique
from typing import TYPE_CHECKING, NamedTuple, Set, Dict, Optional, Any, Tuple, List
import items
import nations
from ArenaType import readVisualScriptSection
from ResMgr import DataSection
from constants import IS_CLIENT, IS_CELLAPP, IS_WEB, VEHICLE_TTC_ASPECTS, ATTACK_REASON, ATTACK_REASON_INDICES, SERVER_TICK_LENGTH, SkillProcessorArgs, GroupSkillProcessorArgs, TTC_TOOLTIP_SECTIONS
from debug_utils import LOG_DEBUG_DEV
from extension_utils import importClass
from items import ITEM_OPERATION, PREDEFINED_HEAL_GROUPS
from items import _xml, vehicles, tankmen
from items.artefacts_helpers import VehicleFilter, _ArtefactFilter, readKpi
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
    from gui.impl.backport import text
    from gui.impl.backport.backport_system_locale import getNiceNumberFormat
    from gui.impl.gen import R
elif IS_WEB:
    from web_stubs import i18n
else:

    class i18n(object):

        @classmethod
        def makeString(cls, key):
            raise SoftException('Unexpected call "i18n.makeString"')


@unique
class ExportParamsTag(Enum):
    VSE = 'vse'
    TOOLTIP = 'tooltip'


@unique
class OrderTypes(str, Enum):
    RANDOM = 'random'
    SEQUENTIALLY = 'sequentially'

    @classmethod
    def values(cls):
        return [ obj.value for obj in cls.__members__.values() ]


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
    __slots__ = ('name', 'id', 'compactDescr', 'tags', 'i18n', 'icon', 'removable', 'price', 'showInShop', '_vehWeightFraction', '_weight', '_maxWeightChange', '_exportParams', '__archetype', '__vehicleFilter', '__artefactFilter', '__tooltipSection', 'isImproved', 'kpi', 'iconName', '_groupName', '__weakref__')

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
        self._exportParams = {}
        self.__vehicleFilter = None
        self.__artefactFilter = None
        self.isImproved = None
        self.kpi = None
        self._groupName = None
        self.__tooltipSection = None
        self.__archetype = None
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

    @property
    def tooltipParams(self):
        return self._getExportParamsDict(ExportParamsTag.TOOLTIP)

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

    @property
    def tooltipSection(self):
        return self.__tooltipSection

    @property
    def archetype(self):
        return self.__archetype

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
            self.icon = _xml.readIconWithDefaultParams(xmlCtx, section, 'icon')
            self.iconName = os.path.splitext(os.path.basename(self.icon[0]))[0]
        if (IS_CLIENT or IS_WEB) and section.has_key('kpi'):
            self.kpi = readKpi(xmlCtx, section['kpi'])
        else:
            self.kpi = []
        if IS_CLIENT:
            if section.has_key('tooltipSection'):
                self.__tooltipSection = section.readString('tooltipSection', TTC_TOOLTIP_SECTIONS.EQUIPMENT)
            else:
                self.__tooltipSection = TTC_TOOLTIP_SECTIONS.EQUIPMENT
            if section.has_key('archetype'):
                self.__archetype = section.readString('archetype')
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
        self._exportParams = self._readExportParams(section['script'])
        return

    def _getExportParamsDict(self, exportTag):
        return {k:getattr(self, k) for k in self._exportParams.get(exportTag.value, set())}

    @staticmethod
    def _readExportParams(section):
        params = {}
        for param, subsection in section.items():
            exports = subsection.readString('exports').split()
            for exportTag in exports:
                params.setdefault(exportTag, set()).add(param)

        return params


class OptionalDevice(Artefact):
    __slots__ = ('categories', '_overridableFactors', '_tier', '_tierlessName', '_isModernized', '_isUpgradable', '_isUpgraded')

    def __init__(self):
        super(OptionalDevice, self).__init__(items.ITEM_TYPES.optionalDevice, 0, '', 0)
        self.categories = set()
        self._overridableFactors = {}
        self._tier = None
        self._tierlessName = None
        self._isModernized = None
        self._isUpgradable = isinstance(self, UpgradableItem)
        self._isUpgraded = isinstance(self, UpgradedItem)
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(OptionalDevice, self)._readBasicConfig(xmlCtx, section)
        self._readCategories(xmlCtx, section)
        self._readTier(xmlCtx, section)
        self._readSpecFactorsFromConfig(xmlCtx, section['script'])
        self._isModernized = any((l.startswith('modernized') for l in self.tags))

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
    def canUseDemountKit(self):
        return not self.isDeluxe and not ('modernized_2' in self.tags or 'modernized_3' in self.tags)

    @property
    def isDeluxe(self):
        return 'deluxe' in self.tags

    @property
    def isTrophy(self):
        return 'trophyBasic' in self.tags or 'trophyUpgraded' in self.tags

    @property
    def isModernized(self):
        return self._isModernized

    @property
    def isUpgradable(self):
        return self._isUpgradable

    @property
    def isUpgraded(self):
        return self._isUpgraded

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

    def getFactorValue(self, vehicleDescr, attrPath, default=0.0):
        splitted = tuple(attrPath.split('/'))
        factor = self._factors.get(splitted, None)
        if not factor:
            return default
        else:
            level = self.defineActiveLevel(vehicleDescr)
            return factor.getActiveValue(level)

    def factorsContainCrewLevelIncrease(self):
        return any(('crewLevelIncrease' in splitted for splitted, _ in self._factors.iteritems()))


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
    __slots__ = ('equipmentType', 'reuseCount', 'cooldownSeconds', 'soundNotification', 'stunResistanceEffect', 'stunResistanceDuration', 'repeatedStunDurationFactor', 'clientSelector', 'ownerPrefab', 'usagePrefab', 'usagePrefabEnemy', 'playerMessagesKey', 'code', 'consumeSeconds', 'deploySeconds', 'rechargeSeconds', 'soundPressedReady', 'soundPressedNotReady', 'soundPressedCancel')

    def __init__(self):
        super(Equipment, self).__init__(items.ITEM_TYPES.equipment, 0, '', 0)
        self.equipmentType = None
        self.stunResistanceEffect = component_constants.ZERO_FLOAT
        self.stunResistanceDuration = component_constants.ZERO_FLOAT
        self.repeatedStunDurationFactor = 1.0
        self.reuseCount = component_constants.ZERO_INT
        self.cooldownSeconds = component_constants.ZERO_INT
        self.consumeSeconds = component_constants.ZERO_INT
        self.rechargeSeconds = component_constants.ZERO_INT
        self.deploySeconds = component_constants.ZERO_INT
        self.soundNotification = None
        self.clientSelector = None
        self.playerMessagesKey = None
        self.clientSelector = None
        self.code = None
        self.usagePrefab = None
        self.usagePrefabEnemy = None
        self.soundPressedReady = None
        self.soundPressedNotReady = None
        self.soundPressedCancel = None
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(Equipment, self)._readBasicConfig(xmlCtx, section)
        self.equipmentType = items.EQUIPMENT_TYPES[section.readString('type', 'regular')]
        self.soundNotification = _xml.readStringOrNone(xmlCtx, section, 'soundNotification')
        self.playerMessagesKey = _xml.readStringOrNone(xmlCtx, section, 'playerMessagesKey')
        self.soundPressedReady = _xml.readStringOrNone(xmlCtx, section, 'soundPressedReady')
        self.soundPressedNotReady = _xml.readStringOrNone(xmlCtx, section, 'soundPressedNotReady')
        self.soundPressedCancel = _xml.readStringOrNone(xmlCtx, section, 'soundPressedCancel')
        scriptSection = section['script']
        self.stunResistanceEffect, self.stunResistanceDuration, self.repeatedStunDurationFactor = _readStun(xmlCtx, scriptSection)
        params = _readReuseParams(xmlCtx, scriptSection)
        self.reuseCount, self.cooldownSeconds, self.consumeSeconds, self.deploySeconds, self.rechargeSeconds = params
        self.clientSelector = _xml.readStringOrNone(xmlCtx, scriptSection, 'clientSelector')
        self.ownerPrefab = _xml.readStringOrNone(xmlCtx, section, 'ownerPrefab')
        self.usagePrefab = _xml.readStringOrNone(xmlCtx, section, 'usagePrefab')
        self.usagePrefabEnemy = _xml.readStringOrNone(xmlCtx, section, 'usagePrefabEnemy') if section.has_key('usagePrefabEnemy') else None
        self.code = section.readString('code') if section.has_key('code') else None
        return

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

    def doesDependOnOptionalDevice(self):
        return False


class EpicEmptySlot(Equipment):
    pass


class ExtraHealthReserve(StaticOptionalDevice):
    __slots__ = ('chassisMaxLoadFactor',)

    def weightOnVehicle(self, vehicleDescr):
        chassis = vehicleDescr.chassis
        level = self.defineActiveLevel(vehicleDescr)
        return super(ExtraHealthReserve, self).weightOnVehicle(vehicleDescr) if level is None else (self._vehWeightFraction, self._weight, chassis.maxLoad * (self.chassisMaxLoadFactor.getActiveValue(level) - 1.0))

    def updateVehicleDescrAttrs(self, vehicleDescr):
        super(ExtraHealthReserve, self).updateVehicleDescrAttrs(vehicleDescr)
        vehicleDescr.miscAttrs['isSetChassisMaxHealthAfterHysteresis'] = True

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
            miscAttrs = vehicleDescr.miscAttrs
            onMoveFactor = self.trackMoveSpeedFactor if not isWheeledVehicle else self.wheelMoveSpeedFactor
            miscAttrs['onMoveRotationSpeedFactor'] *= onMoveFactor.getActiveValue(level)
            onRotationFactor = self.trackRotateSpeedFactor if not isWheeledVehicle else self.wheelRotateSpeedFactor
            miscAttrs['onStillRotationSpeedFactor'] *= onRotationFactor.getActiveValue(level)
            miscAttrs['centerRotationFwdSpeedFactor'] *= self.wheelCenterRotationFwdSpeed.getActiveValue(level)
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
    __slots__ = ('bonusValue',)

    def __init__(self):
        super(Repairkit, self).__init__()
        self.bonusValue = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        self.bonusValue = _xml.readFraction(xmlCtx, section, 'bonusValue')


class CountableConsumableConfigReader(object):
    _CONSUMABLE_SLOTS = ('consumeAmmo',)

    def initCountableConsumableSlots(self):
        self.consumeAmmo = False

    def readCountableConsumableConfig(self, xmlCtx, section):
        self.consumeAmmo = _xml.readBool(xmlCtx, section, 'consumeAmmo')


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
    _SHARED_COOLDOWN_CONSUMABLE_SLOTS = ('prepareTime', 'cooldownTime', 'cooldownFactors', 'sharedCooldownTime', 'consumeAmmo', 'disableAllyDamage', 'setUnavailableAfterAmmoLeft')

    def initSharedCooldownConsumableSlots(self):
        self.cooldownTime = component_constants.ZERO_FLOAT
        self.cooldownFactors = component_constants.EMPTY_DICT
        self.prepareTime = None
        self.consumeAmmo = False
        self.disableAllyDamage = False
        self.setUnavailableAfterAmmoLeft = False
        return

    def readSharedCooldownConsumableConfig(self, xmlCtx, section):
        self.cooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'cooldownTime')
        self.cooldownFactors = self._readCooldownFactors(xmlCtx, section, 'cooldownFactors')
        if section.has_key('prepareTime'):
            self.prepareTime = _xml.readNonNegativeFloat(xmlCtx, section, 'prepareTime')
        self.sharedCooldownTime = _xml.readNonNegativeFloat(xmlCtx, section, 'sharedCooldownTime')
        self.consumeAmmo = _xml.readBool(xmlCtx, section, 'consumeAmmo')
        self.disableAllyDamage = _xml.readBool(xmlCtx, section, 'disableAllyDamage')
        self.setUnavailableAfterAmmoLeft = _xml.readBool(xmlCtx, section, 'setUnavailableAfterAmmoLeft', False)

    def _readCooldownFactors(self, xmlCtx, section, name):
        cooldownFactors = {}
        subXmlCtx, subsection = _xml.getSubSectionWithContext(xmlCtx, section, name)
        for vehClass, _ in _xml.getItemsWithContext(subXmlCtx, subsection):
            cooldownFactors[vehClass] = _xml.readNonNegativeFloat(subXmlCtx, subsection, vehClass)

        return cooldownFactors


class CooldownConsumableConfigReader(object):
    _CONSUMABLE_SLOTS = ('deployTime', 'cooldownTime')

    def initConsumableWithDeployTimeSlots(self):
        self.deployTime = component_constants.ZERO_FLOAT
        self.cooldownTime = component_constants.ZERO_FLOAT

    def readConsumableWithTimeConfig(self, xmlCtx, section):
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


class BaseMarkerConfigReader(object):
    _MARKER_SLOTS_ = ('areaVisual', 'areaColor', 'areaMarker', 'areaUsedPrefab')

    def initMarkerInformation(self):
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        self.areaUsedPrefab = None
        return

    def readMarkerConfig(self, xmlCtx, section):
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.areaUsedPrefab = section.readString('areaUsedPrefab') or None
        return


class AreaMarkerConfigReader(BaseMarkerConfigReader):
    _MARKER_SLOTS_ = BaseMarkerConfigReader._MARKER_SLOTS_ + ('areaRadius', 'areaLength', 'areaWidth')

    def initMarkerInformation(self):
        super(AreaMarkerConfigReader, self).initMarkerInformation()
        self.areaRadius = component_constants.ZERO_FLOAT
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT

    def readMarkerConfig(self, xmlCtx, section):
        super(AreaMarkerConfigReader, self).readMarkerConfig(xmlCtx, section)
        self.areaRadius = _xml.readPositiveFloat(xmlCtx, section, 'areaRadius')
        self.areaLength = self.areaWidth = self.areaRadius * 2


class EffectsConfigReader(object):
    _EFFECTS_SLOTS_ = ('effects',)

    def initEffectsInformation(self):
        self.effects = None
        return

    def readEffectConfig(self, xmlCtx, section):
        self.effects = {name:self._readEffect((xmlCtx, 'effects'), effect) for name, effect in section['effects'].items()}
        return self.effects

    def _readEffect(self, xmlCtx, section):
        if not section:
            return None
        else:
            sOrderTypeName = section.readString('sequencesOrderType', OrderTypes.RANDOM.value)
            if sOrderTypeName not in OrderTypes.values():
                raise SoftException('Wrong sequencesOrderType. <{}> not in {}.'.format(sOrderTypeName, OrderTypes.values()))
            effect = {'shotEffects': section.readString('shotEffects').split(),
             'sequences': self._readSequencesConfig(section['sequences']),
             'sequencesOrderType': OrderTypes(sOrderTypeName),
             'groundRaycast': section.readBool('groundRaycast'),
             'offsetDeviation': section.readFloat('offsetDeviation'),
             'repeatCount': section.readInt('repeatCount', 1),
             'repeatDelay': section.readFloat('repeatDelay'),
             'areaColor': _xml.readIntOrNone(xmlCtx, section, 'areaColor'),
             'repeatDelayDeviationPercent': 0}
            if section.has_key('repeatDelayDeviationPercent'):
                effect['repeatDelayDeviationPercent'] = _xml.readInt(xmlCtx, section, 'repeatDelayDeviationPercent', minVal=0, maxVal=100)
            return effect

    def _readSequencesConfig(self, section):
        if not section:
            return {}
        sequences = {}
        for name, subsection in section.items():
            if name == 'sequence':
                sequenceID = subsection.readString('name')
                sequences[sequenceID] = {'scale': subsection.readVector3('scale', Vector3(1, 1, 1))}

        return sequences


class ArtilleryConfigReader(AreaMarkerConfigReader):
    _ARTILLERY_SLOTS = AreaMarkerConfigReader._MARKER_SLOTS_ + ('delay', 'duration', 'shotsNumber', 'areaRadius', 'shellCompactDescr', 'piercingPower', 'noOwner', 'shotSoundPreDelay', 'wwsoundShot', 'wwsoundEquipmentUsed')

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
    _SMOKE_SLOTS = ('minDelay', 'deltaDelayRange', 'smokeModelName', 'startRadius', 'expandedRadius', 'startHeight', 'expandedHeight', 'heightUpFraction', 'postEffectTeams', 'expansionDuration', 'dispersionRadius', 'totalDuration', 'smokeOpacity', 'visionRadiusFactor', 'dotParams', 'areaLength', 'areaWidth', 'projectilesNumber', 'shellCompactDescr', 'areaVisual', 'areaMarker', 'noOwner', 'smokeEffectNameAlly', 'smokeEffectNameEnemy', 'shotSoundPreDelay', 'wwsoundShot', 'orthogonalDir', 'randomizeDuration', 'vignetteColor', 'vignetteIntensity')

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
        self.attrFactorMods = {}
        self.expireDelay = component_constants.ZERO_FLOAT
        self.postEffectTeams = []
        self.dotParams = None
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.projectilesNumber = component_constants.ZERO_INT
        self.shellCompactDescr = component_constants.ZERO_INT
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        self.noOwner = False
        self.smokeEffectNameAlly = component_constants.EMPTY_STRING
        self.smokeEffectNameEnemy = component_constants.EMPTY_STRING
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
        subXmlCtx, attrFactorModsSection = _xml.getSubSectionWithContext(xmlCtx, section, 'attrFactorMods', False)
        if attrFactorModsSection is not None:
            self._readAttrFactorMods(subXmlCtx, attrFactorModsSection)
        subXmlCtx, postEffectsSection = _xml.getSubSectionWithContext(xmlCtx, section, 'postEffect', False)
        if postEffectsSection is not None:
            self._readPostEffectTeams(subXmlCtx, postEffectsSection)
        self.expireDelay = _xml.readPositiveFloat(xmlCtx, section, 'expireDelay', component_constants.ZERO_FLOAT)
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.projectilesNumber = _xml.readNonNegativeInt(xmlCtx, section, 'projectilesNumber')
        self.shellCompactDescr = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.smokeEffectNameAlly = _xml.readString(xmlCtx, section, 'smokeEffectNameAlly')
        self.smokeEffectNameEnemy = _xml.readString(xmlCtx, section, 'smokeEffectNameEnemy')
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
        return

    def _readAttrFactorMods(self, xmlCtx, section):
        for factor, subSection in section.items():
            self.attrFactorMods[factor] = (_xml.readFloat(xmlCtx, subSection, 'value'), _xml.readBool(xmlCtx, subSection, 'ignoreAllies', True))

    def _readPostEffectTeams(self, _, section):
        if section.has_key('enemy'):
            self.postEffectTeams.append(False)
        if section.has_key('ally'):
            self.postEffectTeams.append(True)


class ReconConfigReader(PlaneConfigReader):
    _RECON_SLOTS = PlaneConfigReader._PLANE_SLOTS + ('areaRadius', 'entitiesToSearch', 'scanPointsAmount', 'antepositions', 'lateropositions', 'areaWidth', 'areaLength', 'wwsoundEquipmentUsed')

    def initReconSlots(self):
        self.initPlaneSlots()
        self.entitiesToSearch = {}
        self.areaRadius = component_constants.ZERO_FLOAT
        self.scanPointsAmount = component_constants.ZERO_INT
        self.antepositions = component_constants.EMPTY_TUPLE
        self.lateropositions = component_constants.EMPTY_TUPLE
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.wwsoundEquipmentUsed = None
        return

    def readReconConfig(self, xmlCtx, section):
        self.readPlaneConfig(xmlCtx, section)
        self.entitiesToSearch = self.__readEntitiesToSearch(xmlCtx, section)
        self.scanPointsAmount = _xml.readNonNegativeInt(xmlCtx, section, 'scanPointsAmount')
        self.antepositions = _xml.readTupleOfFloats(xmlCtx, section, 'antepositions')
        self.lateropositions = _xml.readTupleOfFloats(xmlCtx, section, 'lateropositions')
        self.areaRadius = self.entitiesToSearch.get('Vehicle', {}).get('radius') or self.entitiesToSearch.values()[0]['radius']
        self.areaWidth = self.areaRadius * 2
        self.areaLength = self.areaRadius * (2 + self.scanPointsAmount - 1)
        self.wwsoundEquipmentUsed = _xml.readStringOrNone(xmlCtx, section, 'wwsoundEquipmentUsed')

    def __readEntitiesToSearch(self, xmlCtx, section):
        entitiesToSearch = {}
        for entity in section['entitiesToSearch'].values():
            entityClassName = _xml.readString(xmlCtx, entity, 'name')
            radius = _xml.readPositiveFloat(xmlCtx, entity, 'radius')
            spottingDuration = _xml.readPositiveFloat(xmlCtx, entity, 'spottingDuration')
            entitiesToSearch[entityClassName] = {'radius': radius,
             'spottingDuration': spottingDuration}

        return entitiesToSearch


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


class Marker(object):
    __slots__ = ('name', 'textColor', '_sectionName')

    def __init__(self, sectionName):
        self._sectionName = sectionName
        self.name = None
        self.textColor = None
        return

    def readConfig(self, xmlCtx, section):
        if not self._sectionName or not section.has_key(self._sectionName):
            return None
        else:
            markerSection = section[self._sectionName]
            self.name = _xml.readStringOrNone(xmlCtx, markerSection, 'name')
            self.textColor = _xml.readStringOrNone(xmlCtx, markerSection, 'textColor')
            self._validate()
            return None

    def _validate(self):
        if IS_CLIENT:
            from gui.Scaleform.daapi.view.battle.shared.minimap.settings import EQ_MARKER_TO_SYMBOL
            from gui.Scaleform.genConsts.BATTLE_MARKERS_CONSTS import BATTLE_MARKERS_CONSTS
            if self.name is not None and EQ_MARKER_TO_SYMBOL.get(self.name) is None:
                raise SoftException('Unknown minimap symbol for marker: {}. Supported: {}.'.format(self.name, list(EQ_MARKER_TO_SYMBOL)))
            if self.textColor is not None and self.textColor not in BATTLE_MARKERS_CONSTS.COLORS:
                raise SoftException('Unknown text colors for marker: {}. Supported: {}.'.format(self.name, BATTLE_MARKERS_CONSTS.COLORS))
        return


class Markers(object):
    __slots__ = ('ally', 'enemy', '_sectionName')

    def __init__(self, sectionName):
        self._sectionName = sectionName
        self.ally = None
        self.enemy = None
        return

    def readConfig(self, xmlCtx, section):
        if not self._sectionName or not section.has_key(self._sectionName):
            return None
        else:
            markersSection = section[self._sectionName]
            self.ally = Marker('ally')
            self.enemy = Marker('enemy')
            self.ally.readConfig(xmlCtx, markersSection)
            self.enemy.readConfig(xmlCtx, markersSection)
            return None


class MarkersConfigReader(object):
    _MARKERS_CONFIG_SLOTS = ('markers',)

    def initMarkers(self):
        self.markers = None
        return

    def readMarkersConfig(self, xmlCtx, section):
        self.markers = Markers('markers')
        self.markers.readConfig(xmlCtx, section)


class ArcadeEquipmentConfigReader(object):
    _SHARED_ARCADE_SLOTS = ('minApplyRadius', 'maxApplyRadius', 'applyRadiusVisible', 'cameraPivotPosMin', 'cameraPivotPosMax', 'arenaAimLimits')

    def initArcadeInformation(self):
        self.minApplyRadius = component_constants.ZERO_FLOAT
        self.maxApplyRadius = component_constants.ZERO_FLOAT
        self.applyRadiusVisible = False
        self.cameraPivotPosMin = Vector3()
        self.cameraPivotPosMax = Vector3()
        self.arenaAimLimits = None
        return

    def readArcadeInformation(self, xmlCtx, section):
        self.minApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'minApplyRadius', component_constants.ZERO_FLOAT)
        self.maxApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'maxApplyRadius', component_constants.ZERO_FLOAT)
        self.applyRadiusVisible = _xml.readBool(xmlCtx, section, 'applyRadiusVisible', False)
        if (self.minApplyRadius or self.maxApplyRadius) and self.minApplyRadius >= self.maxApplyRadius:
            raise SoftException('Aiming radius limits: min[{}] >= max[{}]'.format(self.minApplyRadius, self.maxApplyRadius))
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

    def doesDependOnOptionalDevice(self):
        return True

    def getLevelParamsForDevice(self, optionalDevice):
        for levelFilter, levelParams in self._config:
            if levelFilter.checkCompatibilityWithDevice(optionalDevice):
                return levelParams

        return None

    def configContainCrewLevelIncrease(self):
        return any((levelParams is not None and 'crewLevelIncrease' in levelParams for _, levelParams in self._config))

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


class SkillEquipment(Equipment):
    __slots__ = ('skillName', 'perkLevelMultiplier')

    def __init__(self):
        super(SkillEquipment, self).__init__()
        self.skillName = component_constants.EMPTY_STRING
        self.perkLevelMultiplier = None
        return

    def _readConfig(self, xmlCtx, section):
        super(SkillEquipment, self)._readConfig(xmlCtx, section)
        self.skillName = _xml.readNonEmptyString(xmlCtx, section, 'skillName')
        self.perkLevelMultiplier = _xml.readFloatOrNone(xmlCtx, section, 'perkLevelMultiplier')

    def updateCrewSkill(self, *args):
        pass


class FactorSkillBattleBooster(SkillEquipment):
    __slots__ = ('efficiencyFactor',)

    def __init__(self):
        super(FactorSkillBattleBooster, self).__init__()
        self.efficiencyFactor = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        super(FactorSkillBattleBooster, self)._readConfig(xmlCtx, section)
        self.efficiencyFactor = _xml.readPositiveFloat(xmlCtx, section, 'efficiencyFactor')

    def updateCrewSkill(self, a):
        efficiency = (a.factor - 0.57) / 0.43
        if a.baseAvgLevel < 100 or a.skillEfficiency < 1.0:
            efficiency = 1.0 + efficiency - float(a.baseAvgLevel) / 100
            a.factor = 0.57 + 0.43 * efficiency
            a.baseAvgLevel = efficiency * 100
        else:
            a.factor = 0.57 + 0.43 * efficiency * self.efficiencyFactor


class SixthSenseBattleBooster(SkillEquipment):
    __slots__ = ('delay',)

    def __init__(self):
        super(SixthSenseBattleBooster, self).__init__()
        self.delay = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        super(SixthSenseBattleBooster, self)._readConfig(xmlCtx, section)
        self.delay = _xml.readNonNegativeFloat(xmlCtx, section, 'delay')

    def updateCrewSkill(self, a):
        if not a.isBoosterApplicable():
            return
        if a.level < MAX_SKILL_LEVEL or not a.isActive:
            a.level = MAX_SKILL_LEVEL
            a.isActive = True
        else:
            a.skillConfig = a.skillConfig.recreate(self.delay)


class PedantBattleBooster(SkillEquipment):
    __slots__ = ('ammoBayHealthFactor',)

    def __init__(self):
        super(PedantBattleBooster, self).__init__()
        self.ammoBayHealthFactor = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        super(PedantBattleBooster, self)._readConfig(xmlCtx, section)
        self.ammoBayHealthFactor = _xml.readPositiveFloat(xmlCtx, section, 'ammoBayHealthFactor')

    def updateCrewSkill(self, a):
        if a.level < MAX_SKILL_LEVEL:
            level = MAX_SKILL_LEVEL
        else:
            a.skillConfig = a.skillConfig.recreate(self.ammoBayHealthFactor)


class LastEffortBattleBooster(SkillEquipment):
    __slots__ = ('durationPerLevel', 'chanceToHitPerLevel')

    def __init__(self):
        super(LastEffortBattleBooster, self).__init__()
        self.durationPerLevel = component_constants.ZERO_FLOAT
        self.chanceToHitPerLevel = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        super(LastEffortBattleBooster, self)._readConfig(xmlCtx, section)
        self.durationPerLevel = _xml.readNonNegativeFloat(xmlCtx, section, 'durationPerLevel')
        self.chanceToHitPerLevel = _xml.readFloat(xmlCtx, section, 'chanceToHitPerLevel')

    def updateCrewSkill(self, a):
        if not a.isBoosterApplicable():
            return
        if a.level < MAX_SKILL_LEVEL or not a.isActive:
            a.level = MAX_SKILL_LEVEL
            a.isActive = True
        else:
            a.skillConfig = a.skillConfig.recreate(self.durationPerLevel, self.chanceToHitPerLevel)


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


class PassiveConsumable(Equipment, TooltipConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS

    def __init__(self):
        super(PassiveConsumable, self).__init__()
        self.initTooltipInformation()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)


class PassiveEngineering(Equipment, TooltipConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + ('captureStopping', 'captureBlockBonusTime', 'captureSpeedFactor', 'resupplyCooldownFactor', 'resupplyShellsFactor')

    def __init__(self):
        super(PassiveEngineering, self).__init__()
        self.initTooltipInformation()
        self.captureStopping = False
        self.captureBlockBonusTime = component_constants.ZERO_FLOAT
        self.captureSpeedFactor = component_constants.ZERO_FLOAT
        self.resupplyCooldownFactor = component_constants.ZERO_FLOAT
        self.resupplyShellsFactor = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.captureStopping = _xml.readBool(xmlCtx, scriptSection, 'captureStopping')
        self.captureBlockBonusTime = _xml.readPositiveFloat(xmlCtx, scriptSection, 'captureBlockBonusTime')
        self.captureSpeedFactor = _xml.readPositiveFloat(xmlCtx, scriptSection, 'captureSpeedFactor')
        self.resupplyCooldownFactor = _xml.readPositiveFloat(xmlCtx, scriptSection, 'resupplyCooldownFactor')
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
    __slots__ = ('selfIncreaseFactors',)

    def __init__(self):
        super(EpicInspire, self).__init__()
        self.selfIncreaseFactors = {}

    def _readConfig(self, xmlCtx, scriptSection):
        super(EpicInspire, self)._readConfig(xmlCtx, scriptSection)
        self.selfIncreaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, scriptSection, 'selfIncreaseFactors')


class FLPassiveEngineering(PassiveEngineering):
    pass


class FortConsumableInspire(ConsumableInspire):
    pass


class AreaOfEffectEquipment(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, ArcadeEquipmentConfigReader, EffectsConfigReader, MarkersConfigReader):
    __slots__ = ('delay', 'duration', 'lifetime', 'shotsNumber', 'areaRadius', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'areaColorBlind', 'areaShow', 'noOwner', 'attackerType', 'areaVisibleToEnemies', 'shotSoundPreDelay', 'wwsoundShot', 'wwsoundEquipmentUsed', 'shotEffect', 'actionsConfig', 'explodeDestructible', 'areaUsedPrefab', 'areaAccurateCollision') + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS + EffectsConfigReader._EFFECTS_SLOTS_ + MarkersConfigReader._MARKERS_CONFIG_SLOTS

    def __init__(self):
        super(AreaOfEffectEquipment, self).__init__()
        self.initEffectsInformation()
        self.initSharedCooldownConsumableSlots()

    def _readConfig(self, xmlCtx, section):
        super(AreaOfEffectEquipment, self)._readConfig(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.readEffectConfig(xmlCtx, section)
        self.readMarkersConfig(xmlCtx, section)
        self.delay = section.readFloat('delay')
        self.duration = section.readFloat('duration')
        self.lifetime = section.readFloat('lifetime')
        self.shotsNumber = section.readInt('shotsNumber')
        self.areaRadius = section.readFloat('areaRadius')
        self.areaLength = section.readFloat('areaLength', self.areaRadius * 2)
        self.areaWidth = section.readFloat('areaWidth', self.areaRadius * 2)
        self.areaVisual = section.readString('areaVisual') or None
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaColorBlind = _xml.readIntOrNone(xmlCtx, section, 'areaColorBlind')
        self.areaShow = section.readString('areaShow').lower() or None
        self.areaAccurateCollision = section.readBool('areaAccurateCollision', True)
        self.areaVisibleToEnemies = section.readBool('areaVisibleToEnemies', True)
        self.areaUsedPrefab = section.readString('areaUsedPrefab') or None
        self.noOwner = section.readBool('noOwner')
        self.attackerType = section.readString('attackerType').upper()
        self.shotSoundPreDelay = section.readInt('shotSoundPreDelay')
        self.wwsoundShot = section.readString('wwsoundShot')
        self.wwsoundEquipmentUsed = section.readString('wwsoundEquipmentUsed')
        self.shotEffect = section.readString('shotEffect')
        if IS_CELLAPP:
            self.actionsConfig = [ self._readActionConfig(conf) for conf in section['actions'].values() ]
            self.explodeDestructible = section.readBool('explodeDestructible')
        else:
            self.actionsConfig = None
            self.explodeDestructible = None
        return

    def _readActionConfig(self, section):
        if not section:
            return None
        else:
            actionType = section.readString('type')
            actionClass = importClass(actionType, 'actions.vehicle')
            return {'type': actionType,
             'applyTo': section.readString('applyTo', ''),
             'args': actionClass.parseXML(section['args'])}


class AttackBomberEquipment(AreaOfEffectEquipment):
    pass


class AttackArtilleryFortEquipment(AreaOfEffectEquipment):
    __slots__ = ('maxDamage', 'enemyAreaColor', 'enemyAreaColorBlind')

    def _readConfig(self, xmlCtx, section):
        super(AttackArtilleryFortEquipment, self)._readConfig(xmlCtx, section)
        self.enemyAreaColor = _xml.readIntOrNone(xmlCtx, section, 'enemyAreaColor')
        self.enemyAreaColorBlind = _xml.readIntOrNone(xmlCtx, section, 'enemyAreaColorBlind')
        if IS_CLIENT:
            damagePerShot = sum([ self.__readDamageVehicleAction(action) for action in section['actions'].values() ])
            self.maxDamage = damagePerShot * self.shotsNumber
        else:
            self.maxDamage = 0

    @staticmethod
    def __readDamageVehicleAction(section):
        if not section:
            return 0
        if section.readString('type') != 'DamageVehicle':
            return 0
        args = section['args']
        return args.readInt('damage') if args.has_key('damage') else 0


UpgradeInfo = NamedTuple('UpgradeInfo', [('upgradedCompDescr', int)])
DowngradeInfo = NamedTuple('DowngradeInfo', [('downgradedCompDescr', int)])

class UpgradableItem(Artefact):

    def __init__(self, typeID, itemID, itemName, compactDescr):
        super(UpgradableItem, self).__init__(typeID, itemID, itemName, compactDescr)
        self.__upgradeInfo = None
        self._downgradeInfo = None
        self._level = 1
        return

    @property
    def upgradeInfo(self):
        return self.__upgradeInfo

    @property
    def downgradeInfo(self):
        return self._downgradeInfo

    @property
    def level(self):
        return self._level

    def _readConfig(self, xmlCtx, section):
        super(UpgradableItem, self)._readConfig(xmlCtx, section)
        self._readUpgradableConfig(xmlCtx, section)

    def _readUpgradableConfig(self, xmlCtx, scriptSection):
        upgradeInfoSection = scriptSection['upgradeInfo']
        if upgradeInfoSection.has_key('upgradedDevice'):
            deviceName = _xml.readString(xmlCtx, upgradeInfoSection, 'upgradedDevice')

            def defferedInitUpgrade(objsByIDs, idsByNames):
                device = objsByIDs.get(idsByNames.get(deviceName))
                self._initUpgradeInfo(xmlCtx, upgradeInfoSection, device.compactDescr)
                self._initDowngradeInfo(device)
                device._level = self._level + 1

            vehicles.addArtefactsPostloadCallback(defferedInitUpgrade)
        else:
            upgradedCD = _xml.readInt(xmlCtx, upgradeInfoSection, 'upgradedCompDescr')

            def defferedInitUpgrade(objsByIDs, idsByNames):
                _, __, itemID = items.parseIntCompactDescr(upgradedCD)
                device = objsByIDs.get(itemID)
                device._level = self._level + 1
                self._initDowngradeInfo(device)

            vehicles.addArtefactsPostloadCallback(defferedInitUpgrade)
            self._initUpgradeInfo(xmlCtx, upgradeInfoSection, upgradedCD)

    def _initUpgradeInfo(self, xmlCtx, upgradeInfoSection, upgradedCD):
        self.__upgradeInfo = UpgradeInfo(upgradedCD)
        _readPriceForOperation(xmlCtx, upgradeInfoSection, ITEM_OPERATION.UPGRADE, (self.compactDescr, upgradedCD))

    def _initDowngradeInfo(self, device):
        downgradedCD = self.compactDescr
        device._downgradeInfo = DowngradeInfo(downgradedCD)


class UpgradedItem(Artefact):

    def __init__(self, typeID, itemID, itemName, compactDescr):
        super(UpgradedItem, self).__init__(typeID, itemID, itemName, compactDescr)
        self._downgradeInfo = None
        self._level = 1
        return

    @property
    def downgradeInfo(self):
        return self._downgradeInfo

    @property
    def level(self):
        return self._level


class UpgradableStaticDevice(StaticOptionalDevice, UpgradableItem):
    pass


class UpgradedStaticDevice(StaticOptionalDevice, UpgradedItem):
    pass


class UpgradableImprovedConfiguration(ImprovedConfiguration, UpgradableItem):
    pass


class UpgradableExtraHealthReserve(ExtraHealthReserve, UpgradableItem):
    pass


class UpgradedImprovedConfiguration(ImprovedConfiguration, UpgradedItem):
    pass


class UpgradedExtraHealthReserve(ExtraHealthReserve, UpgradedItem):
    pass


class UpgradableRotationMechanisms(RotationMechanisms, UpgradableItem):
    pass


class UpgradedRotationMechanisms(RotationMechanisms, UpgradedItem):
    pass


class UpgradableLowNoiseTracks(LowNoiseTracks, UpgradableItem):
    pass


class UpgradedLowNoiseTracks(LowNoiseTracks, UpgradedItem):
    pass


class Bomber(Equipment, TooltipConfigReader, CountableConsumableConfigReader, BomberConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + CooldownConsumableConfigReader._CONSUMABLE_SLOTS + BomberConfigReader._BOMBER_SLOTS + ('influenceZone', 'cooldownTime')

    def __init__(self):
        super(Bomber, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initBomberSlots()
        self.cooldownTime = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readBomberConfig(xmlCtx, scriptSection)
        self.cooldownTime = _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds')
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription)


class Smoke(Equipment, TooltipConfigReader, CountableConsumableConfigReader, SmokeConfigReader):
    __slots__ = ('cooldownTime',) + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CountableConsumableConfigReader._CONSUMABLE_SLOTS + SmokeConfigReader._SMOKE_SLOTS

    def __init__(self):
        super(Smoke, self).__init__()
        self.initTooltipInformation()
        self.initCountableConsumableSlots()
        self.initSmokeSlots()
        self.cooldownTime = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readCountableConsumableConfig(xmlCtx, scriptSection)
        self.readSmokeConfig(xmlCtx, scriptSection)
        self.cooldownTime = _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds')
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription, duration=int(self.totalDuration))


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


class FLRegenerationKit(Equipment, SharedCooldownConsumableConfigReader, TooltipConfigReader):
    __slots__ = SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + ('expireByDamageReceived', 'resupplyHealthPointsFactor')

    def __init__(self):
        super(FLRegenerationKit, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.healthRegenPerTick = component_constants.ZERO_FLOAT
        self.initialHeal = component_constants.ZERO_FLOAT
        self.healTime = component_constants.ZERO_FLOAT
        self.healGroup = None
        self.tickInterval = 1.0
        self.expireByDamageReceived = False
        self.resupplyHealthPointsFactor = 1.0
        return

    def _readConfig(self, xmlCtx, section):
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.healthRegenPerTick = _xml.readNonNegativeFloat(xmlCtx, section, 'healthRegenPerTick', 0.0)
        self.initialHeal = _xml.readNonNegativeFloat(xmlCtx, section, 'initialHeal', 0.0)
        self.healTime = _xml.readNonNegativeFloat(xmlCtx, section, 'healTime', 0.0)
        self.healGroup = _xml.readIntOrNone(xmlCtx, section, 'healGroup')
        self.tickInterval = _xml.readPositiveFloat(xmlCtx, section, 'tickInterval', 1.0)
        self.expireByDamageReceived = _xml.readBool(xmlCtx, section, 'expireByDamageReceived', False)
        self.resupplyHealthPointsFactor = _xml.readPositiveFloat(xmlCtx, section, 'resupplyHealthPointsFactor', 1.0)


class FLAvatarStealthRadar(Equipment, SharedCooldownConsumableConfigReader, CooldownConsumableConfigReader, TooltipConfigReader, InspireConfigReader):
    __slots__ = SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + CooldownConsumableConfigReader._CONSUMABLE_SLOTS + InspireConfigReader._INSPIRE_SLOTS + ('passiveCircularVisionRadius', 'detectionTime', 'overridableFactors')

    def __init__(self):
        super(FLAvatarStealthRadar, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initConsumableWithDeployTimeSlots()
        self.initInspireSlots()
        self.passiveCircularVisionRadius = component_constants.ZERO_FLOAT
        self.detectionTime = component_constants.ZERO_FLOAT
        self.overridableFactors = {}

    def _readConfig(self, xmlCtx, section):
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.readConsumableWithTimeConfig(xmlCtx, section)
        self.readInspireConfig(xmlCtx, section)
        self.passiveCircularVisionRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'passiveCircularVisionRadius', 0.0)
        self.detectionTime = _xml.readNonNegativeFloat(xmlCtx, section, 'minesDetectionTime', 0.0)
        self.readOverFactorsFromConfig(xmlCtx, section)
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription, activationDelay=int(self.inactivationDelay))

    def readOverFactorsFromConfig(self, xmlCtx, section):
        factorsSection = section['overridableFactors']
        if factorsSection is None:
            return
        else:
            for name, subsection in factorsSection.items():
                factor = subsection.asFloat
                self.overridableFactors[name] = factor

            return


class MineParams(object):
    __slots__ = ('triggerRadius', 'triggerHeight', 'triggerDepth', 'influenceType', 'lifetime', 'activationDelay', 'damage', 'shell', 'shellLowDamage', 'destroyMyMinesOverlappingAlliedMines', 'resistAllyDamage', 'directDetectionTypes')

    def __init__(self):
        self.triggerRadius = 1.0
        self.triggerHeight = 1.0
        self.triggerDepth = 0.0
        self.influenceType = component_constants.INFLUENCE_ALL
        self.lifetime = 10
        self.damage = 100
        self.shell = None
        self.shellLowDamage = None
        self.resistAllyDamage = False
        self.destroyMyMinesOverlappingAlliedMines = False
        self.directDetectionTypes = []
        return

    def __repr__(self):
        return 'motParams ({}, {}, {}, {}, {}, {}, {}, {})'.format(self.triggerRadius, self.triggerHeight, self.triggerDepth, self.influenceType, self.lifetime, self.damage, self.shell, self.shellLowDamage)

    def _readConfig(self, xmlCtx, section):
        self.activationDelay = section.readInt('activationDelay', 0)
        self.triggerRadius = _xml.readPositiveFloat(xmlCtx, section, 'triggerRadius')
        self.triggerHeight = _xml.readPositiveFloat(xmlCtx, section, 'triggerHeight')
        self.triggerDepth = _xml.readNonNegativeFloat(xmlCtx, section, 'triggerDepth', 0.0)
        self.influenceType = _xml.readInt(xmlCtx, section, 'influenceType', component_constants.INFLUENCE_ALL, component_constants.INFLUENCE_ENEMY)
        self.lifetime = _xml.readPositiveInt(xmlCtx, section, 'lifetime')
        self.damage = _xml.readNonNegativeInt(xmlCtx, section, 'damage')
        if section.has_key('shellCompactDescr'):
            self.shell = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        if section.has_key('shellCompactDescrLowDamage'):
            self.shellLowDamage = _xml.readInt(xmlCtx, section, 'shellCompactDescrLowDamage')
        if section.has_key('resistAllyDamage'):
            self.resistAllyDamage = _xml.readBool(xmlCtx, section, 'resistAllyDamage')
        if section.has_key('destroyMyMinesOverlappingAlliedMines'):
            self.resistAllyDamage = _xml.readBool(xmlCtx, section, 'destroyMyMinesOverlappingAlliedMines')
        if section.has_key('directDetectionTypes'):
            mapping = {'RAYTRACE': 0,
             'RECON': 1,
             'RADAR': 2,
             'STEALTH_RADAR': 3}
            DDTypes = _xml.readTupleOfStrings(xmlCtx, section, 'directDetectionTypes')
            self.directDetectionTypes = [ mapping[t] for t in DDTypes ]


class Minefield(Equipment, TooltipConfigReader, ArcadeEquipmentConfigReader, CountableConsumableConfigReader):
    __slots__ = ('mineParams', 'noOwner', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'cooldownTime', 'disableAllyDamage') + CountableConsumableConfigReader._CONSUMABLE_SLOTS + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(Minefield, self).__init__()
        self.initTooltipInformation()
        self.initArcadeInformation()
        self.bombsPattern = []
        self.mineParams = MineParams()
        self.noOwner = False
        self.disableAllyDamage = True
        self.cooldownTime = component_constants.ZERO_INT
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
        self.cooldownTime = _xml.readInt(xmlCtx, section, 'cooldownSeconds')
        self.disableAllyDamage = _xml.readBool(xmlCtx, section, 'disableAllyDamage')
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.readCountableConsumableConfig(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        if IS_CLIENT and self.longDescription:
            self.longDescription = i18n.makeString(self.longDescription, duration=int(self.mineParams.lifetime))


class FrontLineMinefield(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, ArcadeEquipmentConfigReader, CooldownConsumableConfigReader):
    __slots__ = ('bombsPattern', 'mineParams', 'noOwner', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'areaMarker', 'bombsNumber')

    def __init__(self):
        super(FrontLineMinefield, self).__init__()
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
        self.bombsNumber = 0
        return

    def _readConfig(self, xmlCtx, section):
        bombs = _xml.readTupleOfFloats(xmlCtx, section, 'bombsPattern')
        self.bombsPattern = [ (bombs[b], bombs[b + 1]) for b in range(0, len(bombs) - 1, 2) ]
        self.mineParams._readConfig(xmlCtx, section['mineParams'])
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.bombsNumber = _xml.readIntOrNone(xmlCtx, section, 'bombsNumber')
        self.readConsumableWithTimeConfig(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)


class VisualScriptEquipment(Equipment):
    __slots__ = ('visualScript',)

    def __init__(self):
        super(VisualScriptEquipment, self).__init__()
        self.visualScript = {}

    def _readConfig(self, xmlCtx, section):
        self.visualScript = readVisualScriptSection(section)

    def _exportSlotsToVSE(self):
        params = self._getExportParamsDict(ExportParamsTag.VSE)
        if not params:
            return
        for _, plans in self.visualScript.iteritems():
            for planDef in plans:
                planDef['params'].update(params)

        self._exportParams[ExportParamsTag.VSE.value].clear()


class LevelBasedVisualScriptEquipment(VisualScriptEquipment):
    _LEVEL_BASED_SLOTS = ('radius',)

    def __init__(self):
        super(LevelBasedVisualScriptEquipment, self).__init__()
        self.radius = ()

    def _readConfig(self, xmlCtx, section):
        super(LevelBasedVisualScriptEquipment, self)._readConfig(xmlCtx, section)
        self.radius = tuple(map(float, section.readString('radius').split()))
        if len(self.radius) == 0:
            _xml.raiseWrongXml(xmlCtx, 'radius', 'should be multiple values separated by space.')

    def getRadiusBasedOnSkillLevel(self, skillLevel):
        return self.radius[skillLevel - 1]


class Comp7AoeHealEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'radius', 'heal', 'secondaryHealDebuff', 'tickInterval')

    @property
    def tooltipParams(self):
        params = super(Comp7AoeHealEquipment, self).tooltipParams
        params['heal'] = tuple(map(lambda h: h * self.tickInterval * self.duration, self.heal))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7AoeHealEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.radius = section.readFloat('radius')
        self.heal = tuple(map(float, section.readString('heal').split()))
        self.secondaryHealDebuff = section.readFloat('secondaryHealDebuff')
        self.tickInterval = section.readFloat('tickInterval')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7AllySupportEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'crewBuff')

    def _readConfig(self, xmlCtx, section):
        super(Comp7AllySupportEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.crewBuff = tuple(map(float, section.readString('crewBuff').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7AllyHunterEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'heal', 'gunReloadTimeBuff', 'tickInterval')

    @property
    def tooltipParams(self):
        params = super(Comp7AllyHunterEquipment, self).tooltipParams
        params['heal'] = tuple(map(lambda h: h * self.tickInterval * self.duration, self.heal))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7AllyHunterEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.heal = tuple(map(float, section.readString('heal').split()))
        self.gunReloadTimeBuff = section.readFloat('gunReloadTimeBuff')
        self.tickInterval = section.readFloat('tickInterval')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7ConcentrationEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'aimingTimeBuff', 'shotDispersionFactors', 'clipReloadTimeBoost')

    @property
    def tooltipParams(self):
        params = super(Comp7ConcentrationEquipment, self).tooltipParams
        params['shotDispersionFactorsBuff'] = tuple(map(lambda b: (1.0 - b) * 100, self.shotDispersionFactors))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7ConcentrationEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.aimingTimeBuff = tuple(map(float, section.readString('aimingTimeBuff').split()))
        self.shotDispersionFactors = tuple(map(float, section.readString('shotDispersionFactors').split()))
        self.clipReloadTimeBoost = tuple(map(float, section.readString('clipReloadTimeBoost').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7BerserkEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'gunReloadTimeBuff', 'damageDistance', 'shotDispersionFactors')

    @property
    def tooltipParams(self):
        params = super(Comp7BerserkEquipment, self).tooltipParams
        params['gunReloadTimeBuff'] = tuple(map(lambda b: (1.0 - b) * 100, self.gunReloadTimeBuff))
        params['shotDispersionFactorsBuff'] = tuple(map(lambda b: (1.0 - b) * 100, self.shotDispersionFactors))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7BerserkEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.gunReloadTimeBuff = tuple(map(float, section.readString('gunReloadTimeBuff').split()))
        self.damageDistance = section.readFloat('damageDistance')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.shotDispersionFactors = tuple(map(float, section.readString('shotDispersionFactors').split()))
        self._exportSlotsToVSE()


class Comp7AoeInspireEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'radius', 'crewBuff')

    def _readConfig(self, xmlCtx, section):
        super(Comp7AoeInspireEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.crewBuff = tuple(map(float, section.readString('crewBuff').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7RedlineEquipment(LevelBasedVisualScriptEquipment, BaseMarkerConfigReader, EffectsConfigReader):
    __slots__ = LevelBasedVisualScriptEquipment._LEVEL_BASED_SLOTS + BaseMarkerConfigReader._MARKER_SLOTS_ + EffectsConfigReader._EFFECTS_SLOTS_ + ('delay', 'damage', 'stunDuration', 'areaShow', 'fraction', 'requireAssists')

    def __init__(self):
        super(Comp7RedlineEquipment, self).__init__()
        self.initMarkerInformation()
        self.initEffectsInformation()

    def _readConfig(self, xmlCtx, section):
        super(Comp7RedlineEquipment, self)._readConfig(xmlCtx, section)
        self.delay = section.readFloat('delay')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.damage = tuple(map(float, section.readString('damage').split()))
        self.stunDuration = tuple(map(float, section.readString('stunDuration').split()))
        self.areaShow = section.readString('areaShow').lower() or None
        self.duration = section.readFloat('duration')
        self.readMarkerConfig(xmlCtx, section)
        self.readEffectConfig(xmlCtx, section)
        self.fraction = section.readFloat('fraction')
        self.requireAssists = section.readBool('requireAssists', False)
        self._exportSlotsToVSE()
        return


class Comp7FastRechargeEquipment(VisualScriptEquipment):
    __slots__ = ('gunReloadTimeBuff',)

    @property
    def tooltipParams(self):
        params = super(Comp7FastRechargeEquipment, self).tooltipParams
        params['gunReloadTimeBuff'] = tuple(map(lambda b: (1.0 - b) * 100, self.gunReloadTimeBuff))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7FastRechargeEquipment, self)._readConfig(xmlCtx, section)
        self.gunReloadTimeBuff = tuple(map(float, section.readString('gunReloadTimeBuff').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7JuggernautEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'enginePowerFactor', 'dmgAbsorb', 'fwMaxSpeedBonus', 'bkMaxSpeedBonus', 'rammingDamageBonus', 'vehicleRotationSpeedFactor')

    @property
    def tooltipParams(self):
        params = super(Comp7JuggernautEquipment, self).tooltipParams
        params['enginePowerBuff'] = (self.enginePowerFactor - 1.0) * 100
        params['dmgAbsorbBuff'] = tuple(map(lambda b: (1.0 - b) * 100, self.dmgAbsorb))
        params['rammingDamageBuff'] = (self.rammingDamageBonus - 1.0) * 100
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7JuggernautEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.enginePowerFactor = section.readFloat('enginePowerFactor')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.dmgAbsorb = tuple(map(float, section.readString('dmgAbsorb').split()))
        self.fwMaxSpeedBonus = section.readFloat('fwMaxSpeedBonus')
        self.bkMaxSpeedBonus = section.readFloat('bkMaxSpeedBonus')
        self.rammingDamageBonus = section.readFloat('rammingDamageBonus')
        self.vehicleRotationSpeedFactor = section.readFloat('vehicleRotationSpeedFactor')
        self._exportSlotsToVSE()


class Comp7SureShotEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'shotDispersionFactors', 'slvl', 'sdlvl')

    @property
    def tooltipParams(self):
        params = super(Comp7SureShotEquipment, self).tooltipParams
        params['shotDispersionFactorsBuff'] = tuple(map(lambda b: (1.0 - b) * 100, self.shotDispersionFactors))
        params['gunReloadBuff'] = tuple(map(lambda b: b * 100, self.slvl))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7SureShotEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.shotDispersionFactors = tuple(map(float, section.readString('shotDispersionFactors').split()))
        self.slvl = tuple(map(float, section.readString('slvl').split()))
        self.sdlvl = tuple(map(float, section.readString('sdlvl').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7SniperEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'dispersionFactor', 'damageDistance', 'damageFactors')

    @property
    def tooltipParams(self):
        params = super(Comp7SniperEquipment, self).tooltipParams
        params['damageFactors'] = tuple(map(lambda f: int(round((f - 1) * 100)), self.damageFactors))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7SniperEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.dispersionFactor = section.readFloat('dispersionFactor')
        self.damageDistance = section.readFloat('damageDistance')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self.damageFactors = tuple(map(float, section.readString('damageFactors').split()))
        self._exportSlotsToVSE()


class Comp7RiskyAttackEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'healDuration', 'baseHeal', 'extraHealFactor', 'fwdSpeedBoost', 'bkwSpeedBoost', 'enginePowerBuff')

    @property
    def tooltipParams(self):
        params = super(Comp7RiskyAttackEquipment, self).tooltipParams
        params['extraHealFactor'] = tuple(map(lambda b: b * 100, self.extraHealFactor))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7RiskyAttackEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.healDuration = section.readFloat('healDuration')
        self.baseHeal = section.readInt('baseHeal')
        self.extraHealFactor = tuple(map(float, section.readString('extraHealFactor').split()))
        self.fwdSpeedBoost = section.readFloat('fwdSpeedBoost')
        self.bkwSpeedBoost = section.readFloat('bkwSpeedBoost')
        self.enginePowerBuff = section.readFloat('enginePowerBuff')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7ReconEquipment(LevelBasedVisualScriptEquipment, BaseMarkerConfigReader):
    __slots__ = LevelBasedVisualScriptEquipment._LEVEL_BASED_SLOTS + BaseMarkerConfigReader._MARKER_SLOTS_ + ('duration', 'delay', 'startupDelay')

    def __init__(self):
        super(Comp7ReconEquipment, self).__init__()
        self.initMarkerInformation()

    @property
    def tooltipParams(self):
        params = super(Comp7ReconEquipment, self).tooltipParams
        params['lampDelay'] = tankmen.getSkillsConfig().getSkill('commander_sixthSense').delay
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7ReconEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.delay = section.readFloat('delay')
        self.startupDelay = section.readFloat('startupDelay')
        self.readMarkerConfig(xmlCtx, section)
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7AggressiveDetectionEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'visionFactor')

    @property
    def tooltipParams(self):
        params = super(Comp7AggressiveDetectionEquipment, self).tooltipParams
        params['visionBuff'] = tuple(map(lambda b: (b - 1.0) * 100, self.visionFactor))
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7AggressiveDetectionEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self.visionFactor = tuple(map(float, section.readString('visionFactor').split()))
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class Comp7MarchEquipment(VisualScriptEquipment):
    __slots__ = ('duration', 'enginePowerBuff', 'fwdSpeedBoost', 'invisibilityFactor')

    @property
    def tooltipParams(self):
        params = super(Comp7MarchEquipment, self).tooltipParams
        params['enginePowerBuff'] = self.enginePowerBuff * 100
        params['invisibilityFactor'] = (self.invisibilityFactor - 1.0) * 100
        return params

    def _readConfig(self, xmlCtx, section):
        super(Comp7MarchEquipment, self)._readConfig(xmlCtx, section)
        self.duration = tuple(map(float, section.readString('duration').split()))
        self.enginePowerBuff = section.readFloat('enginePowerBuff')
        self.fwdSpeedBoost = section.readFloat('fwdSpeedBoost')
        self.invisibilityFactor = section.readFloat('invisibilityFactor')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        self._exportSlotsToVSE()


class DynComponentsGroupEquipment(Equipment):
    __slots__ = ('durationSeconds', 'dynComponentsGroups')

    def _readConfig(self, xmlCtx, section):
        super(DynComponentsGroupEquipment, self)._readConfig(xmlCtx, section)
        self.durationSeconds = _xml.readFloat(xmlCtx, section, 'durationSeconds')
        self.dynComponentsGroups = frozenset(_xml.readString(xmlCtx, section, 'dynComponentsGroups').split())


class PoiRadarEquipment(VisualScriptEquipment):
    __slots__ = ('duration',)

    def _readConfig(self, xmlCtx, section):
        super(PoiRadarEquipment, self)._readConfig(xmlCtx, section)
        self.duration = section.readFloat('duration')
        self._exportSlotsToVSE()


class PoiArtilleryEquipment(AreaOfEffectEquipment):
    __slots__ = ('maxCount', 'requireAssists')

    def _readConfig(self, xmlCtx, section):
        super(PoiArtilleryEquipment, self)._readConfig(xmlCtx, section)
        maxCount = section.readInt('maxCount')
        if maxCount < 1:
            maxCount = 1
        self.maxCount = maxCount
        self.requireAssists = section.readBool('requireAssists', False)


_readTags = vehicles._readTags

def _readStun(xmlCtx, scriptSection):
    stunResistanceEffect = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceEffect') if scriptSection.has_key('stunResistanceEffect') else 0.0
    stunResistanceDuration = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceDuration') if scriptSection.has_key('stunResistanceDuration') else 0.0
    repeatedStunDurationFactor = _xml.readFraction(xmlCtx, scriptSection, 'repeatedStunDurationFactor') if scriptSection.has_key('repeatedStunDurationFactor') else 1.0
    return (stunResistanceEffect, stunResistanceDuration, repeatedStunDurationFactor)


def _readReuseParams(xmlCtx, scriptSection):
    return (_xml.readInt(xmlCtx, scriptSection, 'reuseCount', minVal=-1) if scriptSection.has_key('reuseCount') else 0,
     _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds', minVal=0) if scriptSection.has_key('cooldownSeconds') else 0,
     _xml.readInt(xmlCtx, scriptSection, 'consumeSeconds', minVal=0) if scriptSection.has_key('consumeSeconds') else 0,
     _xml.readInt(xmlCtx, scriptSection, 'deploySeconds', minVal=0) if scriptSection.has_key('deploySeconds') else 0,
     _xml.readInt(xmlCtx, scriptSection, 'rechargeSeconds', minVal=0) if scriptSection.has_key('rechargeSeconds') else 0)


class OPT_DEV_TYPE_TAG(object):
    TROPHY_BASIC = 'trophyBasic'
    TROPHY_UPGRADED = 'trophyUpgraded'
    DELUXE = 'deluxe'
    MODERNIZED1 = 'modernized_1'
    MODERNIZED2 = 'modernized_2'
    MODERNIZED3 = 'modernized_3'
    ALL = {TROPHY_BASIC,
     TROPHY_UPGRADED,
     DELUXE,
     MODERNIZED1,
     MODERNIZED2,
     MODERNIZED3}

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


class Circle(object):
    __slots__ = ('abilityRadius', 'safeZoneRadius')

    def __init__(self):
        self.abilityRadius = 0.0
        self.safeZoneRadius = 0.0

    def readConfig(self, xmlCtx, section):
        self.abilityRadius = _xml.readFloat(xmlCtx, section, 'abilityRadius', 0.0)
        self.safeZoneRadius = _xml.readFloat(xmlCtx, section, 'safeZoneRadius', 0.0)
