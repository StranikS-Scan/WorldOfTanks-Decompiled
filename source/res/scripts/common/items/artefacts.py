# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/artefacts.py
import copy
import items
import nations
import math
from items import _xml, vehicles
from constants import IS_CLIENT, IS_CELLAPP, IS_WEB, VEHICLE_TTC_ASPECTS
from functools import partial
from tankmen import MAX_SKILL_LEVEL
if IS_CLIENT:
    from helpers import i18n
elif IS_WEB:
    from web_stubs import *

class Artefact(object):

    def get(self, key, defVal=None):
        return self.__dict__.get(key, defVal)

    def __getitem__(self, key):
        return self.__dict__[key]

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

    def _itemTypeName(self):
        pass

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        pass

    def _readBasicConfig(self, xmlCtx, section):
        self.itemTypeName = self._itemTypeName()
        self.name = section.name
        self.id = (nations.NONE_INDEX, _xml.readInt(xmlCtx, section, 'id', 0, 65535))
        self.compactDescr = vehicles.makeIntCompactDescrByID(self.itemTypeName, *self.id)
        if not section.has_key('tags'):
            self.tags = frozenset()
        else:
            self.tags = _readTags(xmlCtx, section, 'tags', self.itemTypeName)
        if IS_CLIENT or IS_WEB:
            self.userString = i18n.makeString(section.readString('userString'))
            self.description = i18n.makeString(section.readString('description'))
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


class OptionalDevice(Artefact):

    def _itemTypeName(self):
        pass

    def extraName(self):
        return None

    def updateVehicleDescrAttrs(self, vehicleDescr):
        pass


class Equipment(Artefact):

    def _itemTypeName(self):
        pass

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

    def extraName(self):
        return self.name

    def _readConfig(self, xmlCtx, section):
        self.activateWhenStillSec = _xml.readNonNegativeFloat(xmlCtx, section, 'activateWhenStillSec')

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        if aspect not in (VEHICLE_TTC_ASPECTS.WHEN_STILL,):
            return
        factors['invisibility'][0] += vehicleDescr.type.invisibilityDeltas['camouflageNetBonus']


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
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration


class Grousers(OptionalDevice):

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

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.turretRotationSpeedFactor = _xml.readPositiveFloat(xmlCtx, section, 'turretRotationSpeedFactor')

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/power'] *= self.enginePowerFactor
            factors['turret/rotationSpeed'] *= self.turretRotationSpeedFactor
        except:
            pass


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

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/power'] *= self.enginePowerFactor
        except:
            pass


class Afterburning(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.enginePowerFactor = _xml.readPositiveFloat(xmlCtx, section, 'enginePowerFactor')
        self.durationSeconds = _xml.readInt(xmlCtx, section, 'durationSeconds', 1)

    def updateVehicleAttrFactors(self, vehicleDescr, factors, aspect):
        try:
            factors['engine/power'] *= self.enginePowerFactor
        except:
            pass


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

    def _readLevelConfig(self, xmlCtx, section):
        filter = _OptionalDeviceFilter(xmlCtx, section['deviceFilter'])
        attribute = _xml.readNonEmptyString(xmlCtx, section, 'attribute')
        factor = _xml.readPositiveFloat(xmlCtx, section, 'factor')
        return (filter, (attribute, factor))

    def _updateVehicleAttrFactorsImpl(self, factors, levelParams):
        attribute, factor = levelParams
        factors[attribute] *= factor


class AdditiveBattleBooster(DynamicEquipment):

    def _readLevelConfig(self, xmlCtx, section):
        filter = _OptionalDeviceFilter(xmlCtx, section['deviceFilter'])
        attribute = _xml.readNonEmptyString(xmlCtx, section, 'attribute')
        value = _xml.readPositiveFloat(xmlCtx, section, 'value')
        return (filter, (attribute, value))

    def _updateVehicleAttrFactorsImpl(self, factors, levelParams):
        attribute, value = levelParams
        factors[attribute] += value


class FactorSkillBattleBooster(Equipment):

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

    def _readConfig(self, xmlCtx, section):
        self.skillName = 'commander_sixthSense'
        self.delay = _xml.readNonNegativeFloat(xmlCtx, section, 'delay')

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        isFire = True
        if level < MAX_SKILL_LEVEL or not isActive:
            level = MAX_SKILL_LEVEL
            isActive = True
        else:
            skillConfig = copy.deepcopy(skillConfig)
            skillConfig['delay'] = self.delay
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class RancorousBattleBooster(Equipment):

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
            skillConfig = copy.deepcopy(skillConfig)
            skillConfig['duration'] = self.duration
            skillConfig['sectorHalfAngle'] = self.sectorHalfAngle
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class PedantBattleBooster(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.skillName = 'loader_pedant'
        self.ammoBayHealthFactor = _xml.readPositiveFloat(xmlCtx, section, 'ammoBayHealthFactor')

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if level < MAX_SKILL_LEVEL:
            level = MAX_SKILL_LEVEL
        else:
            skillConfig = copy.deepcopy(skillConfig)
            skillConfig['ammoBayHealthFactor'] = self.ammoBayHealthFactor
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class FactorPerLevelBattleBooster(Equipment):

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
            skillConfig = copy.deepcopy(skillConfig)
            skillConfig[self.factorName] = self.factorPerLevel
        return (idxInCrew,
         level,
         levelIncrease,
         isActive,
         isFire,
         skillConfig)


class LastEffortBattleBooster(Equipment):

    def _readConfig(self, xmlCtx, section):
        self.skillName = 'radioman_lastEffort'
        self.duration = _xml.readNonNegativeFloat(xmlCtx, section, 'duration')

    def updateCrewSkill(self, idxInCrew, level, levelIncrease, isActive, isFire, skillConfig):
        if level < MAX_SKILL_LEVEL or not isActive:
            level = MAX_SKILL_LEVEL
            isActive = True
        else:
            skillConfig = copy.deepcopy(skillConfig)
            skillConfig['duration'] = self.duration
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
_readTags = vehicles._readTags

def _readStun(xmlCtx, scriptSection):
    stunResistanceEffect = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceEffect') if scriptSection.has_key('stunResistanceEffect') else 0.0
    stunResistanceDuration = _xml.readFraction(xmlCtx, scriptSection, 'stunResistanceDuration') if scriptSection.has_key('stunResistanceDuration') else 0.0
    return (stunResistanceEffect, stunResistanceDuration)


def _readReuseParams(xmlCtx, scriptSection):
    return (_xml.readInt(xmlCtx, scriptSection, 'reuseCount', minVal=-1) if scriptSection.has_key('reuseCount') else 0, _xml.readInt(xmlCtx, scriptSection, 'cooldownSeconds', minVal=0) if scriptSection.has_key('cooldownSeconds') else 0)
