# Embedded file name: scripts/common/items/artefacts.py
import Math
import items, nations
from items import _xml, vehicles
from debug_utils import *
from constants import IS_CLIENT, IS_BASEAPP, IS_CELLAPP, IS_WEB, IS_DEVELOPMENT
from functools import partial
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import *

class OptionalDevice(object):

    def get(self, key, defVal = None):
        return self.__dict__.get(key, defVal)

    def __getitem__(self, key):
        return self.__dict__[key]

    def init(self, xmlCtx, section):
        self.__readBasicConfig(xmlCtx, section)
        xmlCtx = (xmlCtx, 'script')
        section = section['script']
        self._vehWeightFraction, self._weight = _readWeight(xmlCtx, section)
        self._maxWeightChange = 0.0
        self._readConfig(xmlCtx, section)

    def weightOnVehicle(self, vehicleDescr):
        return (self._vehWeightFraction, self._weight, 0.0)

    def checkCompatibilityWithVehicle(self, vehicleDescr):
        if self.__filter is None:
            return (True, None)
        else:
            return self.__filter.checkCompatibility(vehicleDescr)

    def updateVehicleDescrAttrs(self, vehicleDescr):
        pass

    def updatePrice(self, newPrice, showInShop):
        self.price = newPrice
        self.showInShop = showInShop

    def extraName(self):
        return None

    def _readConfig(self, xmlCtx, scriptSection):
        pass

    def __readBasicConfig(self, xmlCtx, section):
        self.itemTypeName = 'optionalDevice'
        self.name = section.name
        self.id = (nations.NONE_INDEX, _xml.readInt(xmlCtx, section, 'id', 0, 65535))
        self.compactDescr = vehicles.makeIntCompactDescrByID('optionalDevice', *self.id)
        if IS_CLIENT or IS_WEB:
            self.userString = i18n.makeString(section.readString('userString'))
            self.description = i18n.makeString(section.readString('description'))
            self.icon = _xml.readIcon(xmlCtx, section, 'icon')
        if IS_CELLAPP or not section.has_key('vehicleFilter'):
            self.__filter = None
        else:
            self.__filter = _VehicleFilter((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        self.removable = section.readBool('removable', False)
        return


class StaticFactorDevice(OptionalDevice):

    def updateVehicleDescrAttrs(self, vehicleDescr):
        if len(self.__attr) == 1:
            attrDict = vehicleDescr.__dict__
            attrName = self.__attr[0]
        else:
            attrDict = getattr(vehicleDescr, self.__attr[0])
            attrName = self.__attr[1]
        val = attrDict[attrName]
        if type(val) is int:
            attrDict[attrName] = int(val * self.__factor)
        else:
            attrDict[attrName] = val * self.__factor

    def _readConfig(self, xmlCtx, section):
        self.__factor = _xml.readPositiveFloat(xmlCtx, section, 'factor')
        self.__attr = _xml.readNonEmptyString(xmlCtx, section, 'attribute').split('/', 1)


class StaticAdditiveDevice(OptionalDevice):

    def updateVehicleDescrAttrs(self, vehicleDescr):
        if len(self.__attr) == 1:
            attrDict = vehicleDescr.__dict__
            attrName = self.__attr[0]
        else:
            attrDict = getattr(vehicleDescr, self.__attr[0])
            attrName = self.__attr[1]
        val = attrDict[attrName]
        if type(val) is int:
            attrDict[attrName] = int(val + self.__value)
        else:
            attrDict[attrName] = val + self.__value

    def _readConfig(self, xmlCtx, section):
        self.__value = _xml.readFloat(xmlCtx, section, 'value')
        self.__attr = _xml.readNonEmptyString(xmlCtx, section, 'attribute').split('/', 1)


class Stereoscope(OptionalDevice):

    def extraName(self):
        return self.name

    def _readConfig(self, xmlCtx, section):
        self.activateWhenStillSec = _xml.readNonNegativeFloat(xmlCtx, section, 'activateWhenStillSec')
        self.circularVisionRadiusFactor = _xml.readPositiveFloat(xmlCtx, section, 'circularVisionRadiusFactor')


class CamouflageNet(OptionalDevice):

    def extraName(self):
        return self.name

    def _readConfig(self, xmlCtx, section):
        self.activateWhenStillSec = _xml.readNonNegativeFloat(xmlCtx, section, 'activateWhenStillSec')


class EnhancedSuspension(OptionalDevice):

    def weightOnVehicle(self, vehicleDescr):
        chassis = vehicleDescr.chassis
        return (self._vehWeightFraction, self._weight, chassis['maxLoad'] * (self.__chassisMaxLoadFactor - 1.0))

    def _readConfig(self, xmlCtx, section):
        reader = partial(_xml.readPositiveFloat, xmlCtx, section)
        self.__chassisMaxLoadFactor = reader('chassisMaxLoadFactor')
        self.__chassisHealthFactor = reader('chassisHealthFactor')
        self.__vehicleByChassisDamageFactor = reader('vehicleByChassisDamageFactor')

    def updateVehicleDescrAttrs(self, vehicleDescr):
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['chassisHealthFactor'] *= self.__chassisHealthFactor
        miscAttrs['vehicleByChassisDamageFactor'] *= self.__vehicleByChassisDamageFactor


class Grousers(OptionalDevice):
    if not IS_CLIENT or IS_DEVELOPMENT:

        def updateVehicleDescrAttrs(self, vehicleDescr):
            r = vehicleDescr.physics['terrainResistance']
            vehicleDescr.physics['terrainResistance'] = (r[0], r[1] * self.__factorMedium, r[2] * self.__factorSoft)

    else:

        def updateVehicleDescrAttrs(self, vehicleDescr):
            pass

    def _readConfig(self, xmlCtx, section):
        self.__factorSoft = _xml.readPositiveFloat(xmlCtx, section, 'softGroundResistanceFactor')
        self.__factorMedium = _xml.readPositiveFloat(xmlCtx, section, 'mediumGroundResistanceFactor')


class AntifragmentationLining(OptionalDevice):

    def updateVehicleDescrAttrs(self, vehicleDescr):
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['antifragmentationLiningFactor'] *= self.__antifragmentationLiningFactor
        miscAttrs['crewChanceToHitFactor'] *= 1.0 - self.__increaseCrewChanceToEvadeHit

    def _readConfig(self, xmlCtx, section):
        reader = partial(_xml.readPositiveFloat, xmlCtx, section)
        self.__antifragmentationLiningFactor = reader('antifragmentationLiningFactor')
        self.__increaseCrewChanceToEvadeHit = reader('increaseCrewChanceToEvadeHit')


class Equipment(object):

    def get(self, key, defVal = None):
        return self.__dict__.get(key, defVal)

    def __getitem__(self, key):
        return self.__dict__[key]

    def init(self, xmlCtx, section):
        self.__readBasicConfig(xmlCtx, section)
        self._readConfig((xmlCtx, 'script'), section['script'])

    def checkCompatibilityWithVehicle(self, vehicleDescr):
        if self.__vehicleFilter is None:
            return (True, None)
        else:
            return self.__vehicleFilter.checkCompatibility(vehicleDescr)

    def checkCompatibilityWithEquipment(self, other):
        if self is other:
            return False
        else:
            filter = self.__equipmentFilter
            if filter is None:
                return True
            return not filter.inInstalled(other.tags)

    def checkCompatibilityWithActiveEquipment(self, other):
        if self is other:
            return False
        else:
            filter = self.__equipmentFilter
            if filter is None:
                return True
            return not filter.inActive(other.tags)

    def updatePrice(self, newPrice, showInShop):
        self.price = newPrice
        self.showInShop = showInShop

    def extraName(self):
        return self.name

    def _readConfig(self, xmlCtx, scriptSection):
        pass

    def __readBasicConfig(self, xmlCtx, section):
        self.itemTypeName = 'equipment'
        self.name = section.name
        self.id = (nations.NONE_INDEX, _xml.readInt(xmlCtx, section, 'id', 0, 65535))
        self.compactDescr = vehicles.makeIntCompactDescrByID('equipment', *self.id)
        if not section.has_key('tags'):
            self.tags = frozenset()
        else:
            self.tags = _readTags(xmlCtx, section, 'tags', 'equipment')
        if IS_CLIENT or IS_WEB:
            self.userString = i18n.makeString(section.readString('userString'))
            self.description = i18n.makeString(section.readString('description'))
            self.icon = _xml.readIcon(xmlCtx, section, 'icon')
        if IS_CELLAPP or not section.has_key('vehicleFilter'):
            self.__vehicleFilter = None
        else:
            self.__vehicleFilter = _VehicleFilter((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        if not section.has_key('incompatibleTags'):
            self.__equipmentFilter = None
        else:
            self.__equipmentFilter = _EquipmentFilter((xmlCtx, 'incompatibleTags'), section['incompatibleTags'])
        return


class Extinguisher(Equipment):

    def _readConfig(self, xmlCtx, section):
        if not section.has_key('fireStartingChanceFactor'):
            self.fireStartingChanceFactor = 1.0
        else:
            self.fireStartingChanceFactor = _xml.readPositiveFloat(xmlCtx, section, 'fireStartingChanceFactor')
        self.autoactivate = section.readBool('autoactivate', False)


class Fuel(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.turretRotationSpeedFactor = _xml.readPositiveFloat(xmlCtx, section, 'turretRotationSpeedFactor')


class Stimulator(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.crewLevelIncrease = _xml.readInt(xmlCtx, section, 'crewLevelIncrease', 1)


class Repairkit(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.repairAll = section.readBool('repairAll', False)
        self.bonusValue = _xml.readFraction(xmlCtx, section, 'bonusValue')


class RemovedRpmLimiter(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.engineHpLossPerSecond = _xml.readPositiveFloat(xmlCtx, section, 'engineHpLossPerSecond')


class Afterburning(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.durationSeconds = _xml.readInt(xmlCtx, section, 'durationSeconds', 1)


class Artillery(Equipment):

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

    def _readConfig(self, xmlCtx, section):
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay')
        self.modelName = _xml.readString(xmlCtx, section, 'modelName')
        self.soundEvent = _xml.readString(xmlCtx, section, 'soundEvent')
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


class _VehicleFilter(object):

    def __init__(self, xmlCtx, section):
        self.__include = []
        self.__exclude = []
        for subsection in section.values():
            if subsection.name == 'include':
                self.__include.append(_readVehicleFilterPattern((xmlCtx, 'include'), subsection))
            elif subsection.name == 'exclude':
                self.__exclude.append(_readVehicleFilterPattern((xmlCtx, 'exclude'), subsection))
            else:
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


class _EquipmentFilter(object):

    def __init__(self, xmlCtx, section):
        self.__installed = set()
        self.__active = set()
        for subsection in section.values():
            if subsection.name == 'installed':
                self.__installed.update(_readTags((xmlCtx, subsection.name), subsection, '', 'equipment'))
            elif subsection.name == 'active':
                self.__active.update(_readTags((xmlCtx, subsection.name), subsection, '', 'equipment'))
            else:
                _xml.raiseWrongXml(xmlCtx, subsection.name, 'should be <installed> or <active>')

    def inInstalled(self, tags):
        return len(self.__installed.intersection(tags))

    def inActive(self, tags):
        return len(self.__active.intersection(tags))


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

        elif sname in _vehicleFilterItemTypes:
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
        else:
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
            if tags is not None and not descr['tags'].intersection(tags):
                isVehicleOk = False
                break
            minLevel = item.get('minLevel')
            if minLevel is not None and minLevel > descr['level']:
                isVehicleOk = False
                break
            maxLevel = item.get('maxLevel')
            if maxLevel is not None and maxLevel < descr['level']:
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

def _readWeight(xmlCtx, section):
    fraction = 0.0
    if section.has_key('vehicleWeightFraction'):
        fraction = _xml.readNonNegativeFloat(xmlCtx, section, 'vehicleWeightFraction')
    weight = 0.0
    if section.has_key('weight'):
        weight = _xml.readNonNegativeFloat(xmlCtx, section, 'weight')
    return (fraction, weight)


_readTags = vehicles._readTags
