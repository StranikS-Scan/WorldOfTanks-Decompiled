# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/artefacts_helpers.py
from typing import Optional, Dict, Set, Tuple, List, TYPE_CHECKING
import nations
from constants import MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL
from items import _xml, ITEM_TYPE_NAMES, ITEM_TYPES
from items.readers.shared_readers import readAllowedTags as _readTags
if TYPE_CHECKING:
    from items.vehicles import VehicleType, VehicleDescriptor
_vehicleFilterItemTypes = {'vehicle': 'vehicle',
 'chassis': 'vehicleChassis',
 'engine': 'vehicleEngine',
 'fuelTank': 'vehicleFuelTank',
 'radio': 'vehicleRadio',
 'gun': 'vehicleGun'}

class ComponentFilter(object):

    def __init__(self, minLevel, maxLevel, tags, mandatoryTags):
        self._minLevel = minLevel
        self._maxLevel = maxLevel
        self._tags = tags
        self._mandatoryTags = mandatoryTags

    def __str__(self):
        return '{}:[minLevel={}, maxLevel = {}, tags = {}]'.format(self.__class__.__name__, self._minLevel, self._maxLevel, self._tags)

    @property
    def minLevel(self):
        return self._minLevel

    @property
    def maxLevel(self):
        return self._maxLevel

    @property
    def filterTags(self):
        return self._tags

    def isItemCompatible(self, itemDescr):
        if not self._minLevel <= itemDescr.level <= self._maxLevel:
            return False
        if self._tags and not itemDescr.tags.intersection(self._tags):
            return False
        return False if self._mandatoryTags and not self._mandatoryTags.issubset(itemDescr.tags) else True

    @staticmethod
    def readComponentFilter(ctx, section, itemTypeName):
        minLevel, maxLevel, tags, mandatoryTags = ComponentFilter._readComponentFilterInfo(ctx, section, itemTypeName)
        return ComponentFilter(minLevel, maxLevel, tags, mandatoryTags)

    @staticmethod
    def _readComponentFilterInfo(ctx, section, itemTypeName):
        minLevel = section.readInt('minLevel', MIN_VEHICLE_LEVEL)
        if not MIN_VEHICLE_LEVEL <= minLevel <= MAX_VEHICLE_LEVEL:
            _xml.raiseWrongSection(ctx, 'minLevel')
        maxLevel = section.readInt('maxLevel', MAX_VEHICLE_LEVEL)
        if not MIN_VEHICLE_LEVEL <= maxLevel <= MAX_VEHICLE_LEVEL:
            _xml.raiseWrongSection(ctx, 'maxLevel')
        tags = set()
        if section.has_key('tags'):
            tags = _readTags(ctx, section, 'tags', itemTypeName)
        mandatoryTags = set()
        if section.has_key('mandatoryTags'):
            mandatoryTags = _readTags(ctx, section, 'mandatoryTags', itemTypeName)
        return (minLevel,
         maxLevel,
         tags,
         mandatoryTags)


class SubFilter(object):

    def __init__(self, nationIDs, vehTypeFilter, moduleFilters):
        self._nationIDs = nationIDs
        self._typeFilter = vehTypeFilter
        self._compFilters = moduleFilters

    def __str__(self):
        info = '{}: nationIDs = {}, typeFilter = {}'.format(self.__class__.__name__, self._nationIDs, str(self._typeFilter))
        if self._compFilters:
            info += ', componentFilters:\n'
            for compName, compFilter in self._compFilters.iteritems():
                info += '\t{}: {}\n'.format(compName, str(compFilter))

        return info

    @property
    def nationIDs(self):
        return self._nationIDs

    @property
    def vehTypeFilter(self):
        return self._typeFilter

    def isVehTypeCompatible(self, vehicleType):
        nationID = vehicleType.id[0]
        return False if self._nationIDs and nationID not in self._nationIDs else self._typeFilter.isItemCompatible(vehicleType)

    def isComponentsCompatible(self, vehicleDescr):
        for compName, compFilter in self._compFilters.iteritems():
            compDescr = getattr(vehicleDescr, compName)
            if not compFilter.isItemCompatible(compDescr):
                return False

        return True

    @staticmethod
    def readSubFilter(xmlCtx, filterSection):
        filterNations, vehTypeFilter, moduleFilters = SubFilter._readSubFilterInfo(xmlCtx, filterSection)
        return SubFilter(filterNations, vehTypeFilter, moduleFilters)

    @staticmethod
    def _readSubFilterInfo(xmlCtx, filterSection):
        vehTypeFilter = None
        moduleFilters = {}
        filterNations = set()
        nationsSection = filterSection['nations']
        if nationsSection is not None:
            nationNames = nationsSection.asString
            for name in nationNames.split():
                nationID = nations.INDICES.get(name)
                if nationID is None:
                    _xml.raiseWrongXml(xmlCtx, 'nations', "unknown nation '%s'" % name)
                filterNations.add(nationID)

        vehTypeFilterSection = filterSection['vehicle']
        if vehTypeFilterSection is not None:
            vehTypeFilter = ComponentFilter.readComponentFilter(xmlCtx, vehTypeFilterSection, ITEM_TYPE_NAMES[ITEM_TYPES.vehicle])
        else:
            vehTypeFilter = ComponentFilter(MIN_VEHICLE_LEVEL, MAX_VEHICLE_LEVEL, set(), set())
        componentFiltersSection = filterSection['componentFilters']
        if componentFiltersSection is not None:
            for componentName, compFilterSection in componentFiltersSection.items():
                ctx = (xmlCtx, componentName)
                componentItemName = _vehicleFilterItemTypes.get(componentName, None)
                if componentItemName is not None:
                    componentFilter = ComponentFilter.readComponentFilter(ctx, compFilterSection, componentItemName)
                    if componentName not in moduleFilters:
                        moduleFilters[componentName] = componentFilter
                    else:
                        _xml.raiseWrongXml(xmlCtx, componentName, 'Section {} is duplicated'.format(componentName))
                _xml.raiseWrongXml(ctx, '', 'unknown section name ({})'.format(componentName))

        return (filterNations, vehTypeFilter, moduleFilters)


class VehicleFilter(object):

    def __init__(self, include, exclude):
        self._include = include
        self._exclude = exclude

    @staticmethod
    def readVehicleFilter(xmlCtx, section):
        include, exclude = VehicleFilter._readVehicleFilterInfo(xmlCtx, section)
        return VehicleFilter(include, exclude)

    def checkCompatibility(self, vehicleDescr):
        isVehTypeCompatible, isComponentsCompatible = self._checkCompatibility(vehicleDescr)
        if not isVehTypeCompatible:
            return (False, 'not for this vehicle type')
        else:
            return (False, 'not for current vehicle') if not isComponentsCompatible else (True, None)

    def checkCompatibilityWithComponents(self, vehicleDescr):
        includeFilters, excludeFilters = self._getSubFiltersForVehType(vehicleDescr.type)
        for subFilter in excludeFilters:
            if subFilter.isComponentsCompatible(vehicleDescr):
                return False

        if not includeFilters:
            return True
        for subFilter in includeFilters:
            if subFilter.isComponentsCompatible(vehicleDescr):
                return True

        return False

    def checkCompatibilityWithVehType(self, vehType):
        includeFilters, excludeFilters = self._getSubFiltersForVehType(vehType)
        if excludeFilters:
            return False
        if self._include:
            if includeFilters:
                return True
            else:
                return False
        return True

    def compatibleNations(self):
        included = set()
        for subfilter in self._include:
            included.update(subfilter.nationIDs)

        excluded = set()
        for subfilter in self._exclude:
            excluded.update(subfilter.nationIDs)

        return list(included - excluded)

    def getLevelRange(self):
        minLevel, maxLevel = MAX_VEHICLE_LEVEL, MIN_VEHICLE_LEVEL
        for subfilter in self._include:
            minLevel = min(minLevel, subfilter.vehTypeFilter.minLevel)
            maxLevel = max(maxLevel, subfilter.vehTypeFilter.maxLevel)

        return (minLevel, maxLevel)

    @staticmethod
    def _readVehicleFilterInfo(xmlCtx, section):
        include, exclude = [], []
        for subsection in section.values():
            if subsection.name == 'include':
                destination = include
            elif subsection.name == 'exclude':
                destination = exclude
            else:
                _xml.raiseWrongXml(xmlCtx, subsection.name, 'should be <include> or <exclude>')
                continue
            subFilter = SubFilter.readSubFilter(xmlCtx, subsection)
            destination.append(subFilter)

        return (include, exclude)

    def _checkCompatibility(self, vehicleDescr):
        includeFilters, excludeFilters = self._getSubFiltersForVehType(vehicleDescr.type)
        for subFilter in excludeFilters:
            if subFilter.isComponentsCompatible(vehicleDescr):
                return (False, False)

        if self._include:
            if includeFilters:
                for subFilter in includeFilters:
                    if subFilter.isComponentsCompatible(vehicleDescr):
                        return (True, True)

                return (True, False)
            else:
                return (False, False)
        return (True, True)

    def _getSubFiltersForVehType(self, vehType):
        return (self._getSubFilters(self._include, vehType), self._getSubFilters(self._exclude, vehType))

    @staticmethod
    def _getSubFilters(filters, vehType):
        res = []
        for subfilter in filters:
            if subfilter.isVehTypeCompatible(vehType):
                res.append(subfilter)

        return res


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


def readKpi(xmlCtx, section):
    from gui.shared.gui_items import KPI
    kpi = []
    for kpiType, subsec in section.items():
        if kpiType not in KPI.Type.ALL():
            _xml.raiseWrongXml(xmlCtx, kpiType, 'unsupported KPI type')
            return
        kpiType = intern(kpiType)
        if kpiType == KPI.Type.ONE_OF:
            kpi.append(KPI(KPI.Name.COMPOUND_KPI, readKpi(xmlCtx, subsec), kpiType))
        if kpiType == KPI.Type.AGGREGATE_MUL:
            kpi.append(_readAggregateKPI(xmlCtx, subsec, KPI.Type.AGGREGATE_MUL))
        kpi.append(_readKpiValue(xmlCtx, subsec, kpiType))

    return kpi


def _readKpiValue(xmlCtx, section, kpiType):
    from gui.shared.gui_items import KPI
    name = intern(section.readString('name'))
    value = section.readFloat('value')
    specValue = section.readString('specValue')
    vehicleTypes = section.readString('vehicleTypes').split()
    isSituational = section.readBool('situationalKpi', False)
    if not name:
        _xml.raiseWrongXml(xmlCtx, kpiType, 'empty <name> tag not allowed')
    elif name not in KPI.Name.ALL():
        _xml.raiseWrongXml(xmlCtx, kpiType, 'unsupported value in <name> tag')
    return KPI(name, value, kpiType, float(specValue) if specValue else None, vehicleTypes, isSituational)


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
