# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/artefacts.py
import math
import os
from functools import partial
from itertools import chain, product
from typing import TYPE_CHECKING, NamedTuple, Tuple, Set
import items
import nations
from constants import IS_CLIENT, IS_CELLAPP, IS_WEB, VEHICLE_TTC_ASPECTS, EVENT_BATTLES_TAG, EQUIPMENT_STAGES
from items import ITEM_OPERATION
from items import _xml, vehicles
from items.basic_item import BasicItem
from items.components import shared_components, component_constants
from soft_exception import SoftException
from tankmen import MAX_SKILL_LEVEL
from vehicles import _readPriceForOperation
if TYPE_CHECKING:
    from ResMgr import DataSection
if IS_CELLAPP:
    from action.action_config import readAction

class Artefact(BasicItem):
    __slots__ = ('name', 'id', 'compactDescr', 'tags', 'i18n', 'icon', 'removable', 'price', 'showInShop', 'stunResistanceEffect', 'stunResistanceDuration', 'repeatedStunDurationFactor', '_vehWeightFraction', '_weight', '_maxWeightChange', '__vehicleFilter', '__artefactFilter', 'isImproved', 'kpi', 'iconName')

    def __init__(self, typeID, itemID, itemName, compactDescr):
        super(Artefact, self).__init__(typeID, itemID, itemName, compactDescr)
        self.icon = None
        self.iconName = None
        self.removable = False
        self.price = None
        self.showInShop = False
        self.stunResistanceEffect = component_constants.ZERO_FLOAT
        self.stunResistanceDuration = component_constants.ZERO_FLOAT
        self.repeatedStunDurationFactor = 1.0
        self._vehWeightFraction = component_constants.ZERO_FLOAT
        self._weight = component_constants.ZERO_FLOAT
        self._maxWeightChange = component_constants.ZERO_FLOAT
        self.__vehicleFilter = None
        self.__artefactFilter = None
        self.isImproved = None
        self.kpi = None
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
        self.stunResistanceEffect, self.stunResistanceDuration, self.repeatedStunDurationFactor = _readStun(xmlCtx, section)

    def weightOnVehicle(self, vehicleDescr):
        return (self._vehWeightFraction, self._weight, 0.0)

    def checkCompatibilityWithVehicle(self, vehicleDescr):
        vehType = vehicleDescr.type
        if EVENT_BATTLES_TAG in vehType.tags:
            if EVENT_BATTLES_TAG not in self.tags:
                return (False, 'attempt to set up non-event equipment on event vehicle')
        elif EVENT_BATTLES_TAG in self.tags:
            return (False, 'attempt to set up event equipment on non-event vehicle')
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
            self.i18n = shared_components.I18nComponent(userStringKey=section.readString('userString'), descriptionKey=section.readString('description'), shortDescriptionSpecialKey=section.readString('shortDescriptionSpecial'), longDescriptionSpecialKey=section.readString('longDescriptionSpecial'), shortFilterAlertKey=section.readString('shortFilterAlert'), longFilterAlertKey=section.readString('longFilterAlert'))
            self.icon = _xml.readIcon(xmlCtx, section, 'icon')
            self.iconName = os.path.splitext(os.path.basename(self.icon[0]))[0]
        if IS_CLIENT and section.has_key('kpi'):
            self.kpi = _readKpi(xmlCtx, section['kpi'])
        else:
            self.kpi = []
        if IS_CELLAPP or not section.has_key('vehicleFilter'):
            self.__vehicleFilter = None
        else:
            self.__vehicleFilter = _VehicleFilter((xmlCtx, 'vehicleFilter'), section['vehicleFilter'])
        if not section.has_key('incompatibleTags'):
            self.__artefactFilter = None
        else:
            self.__artefactFilter = _ArtefactFilter((xmlCtx, 'incompatibleTags'), section['incompatibleTags'], self.itemTypeName)
        self.removable = section.readBool('removable', False)
        self.isImproved = section.readBool('improved', False)
        return


class OptionalDevice(Artefact):
    __slots__ = ()

    def __init__(self):
        super(OptionalDevice, self).__init__(items.ITEM_TYPES.optionalDevice, 0, '', 0)

    def extraName(self):
        return None

    def updateVehicleDescrAttrs(self, vehicleDescr):
        pass

    @property
    def isDeluxe(self):
        return 'deluxe' in self.tags


class SoundFeedbackConfigReader(object):
    _SOUND_FEEDBACK_SLOTS = ('soundConfiguration',)

    def _initSoundFeedbackInformation(self):
        self.soundConfiguration = {'uiEvents': {},
         'stageChanges': {}}

    def _readSoundFeedbackInformation(self, xmlCtx, section):
        if not IS_CLIENT or not section.has_key('soundConfiguration'):
            return
        soundConfigSection = section['soundConfiguration']
        if soundConfigSection.has_key('uiEvents'):
            self.soundConfiguration['uiEvents'] = self.__readUIEvents(soundConfigSection['uiEvents'])
        if soundConfigSection.has_key('stageChanges'):
            self.soundConfiguration['stageChanges'] = self.__readStageChanges(soundConfigSection['stageChanges'])

    def __readUIEvents(self, section):
        uiEvents = {}
        for name, subsection in section.items():
            eventName = subsection['for'].asString
            eventResult = subsection['on'].asString
            soundType = subsection['type'].asString
            soundEvents = subsection.asString.split()
            uiEvents.setdefault((eventName, eventResult), {}).setdefault(soundType, []).extend(soundEvents)

        return uiEvents

    def __readStageChanges(self, section):
        stageChanges = {}
        for name, subsection in section.items():
            fromStages = subsection['fromStages'].asString.upper().split()
            toStages = subsection['toStages'].asString.upper().split()
            soundType = subsection['type'].asString
            for fStage, tStage in product(fromStages, toStages):
                stagePair = (getattr(EQUIPMENT_STAGES, fStage, None), getattr(EQUIPMENT_STAGES, tStage, None))
                soundEvents = subsection.asString.split()
                stageChanges.setdefault(stagePair, {}).setdefault(soundType, []).extend(soundEvents)

        return stageChanges


class Equipment(Artefact, SoundFeedbackConfigReader):
    __slots__ = ('equipmentType', 'reuseCount', 'cooldownSeconds') + SoundFeedbackConfigReader._SOUND_FEEDBACK_SLOTS

    def __init__(self):
        super(Equipment, self).__init__(items.ITEM_TYPES.equipment, 0, '', 0)
        self.equipmentType = None
        self.reuseCount = component_constants.ZERO_INT
        self.cooldownSeconds = component_constants.ZERO_INT
        self._initSoundFeedbackInformation()
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(Equipment, self)._readBasicConfig(xmlCtx, section)
        self.equipmentType = items.EQUIPMENT_TYPES[section.readString('type', 'regular')]
        self._readSoundFeedbackInformation(xmlCtx, section)

    def _readStun(self, xmlCtx, section):
        super(Equipment, self)._readStun(xmlCtx, section)
        self.reuseCount, self.cooldownSeconds = _readReuseParams(xmlCtx, section)

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


class StaticFactorDevice(OptionalDevice):
    __slots__ = ('__attr', '__factor')

    def __init__(self):
        super(StaticFactorDevice, self).__init__()
        self.__factor = component_constants.ZERO_FLOAT
        self.__attr = None
        return

    def updateVehicleDescrAttrs(self, vehicleDescr):
        if len(self.__attr) == 1:
            attrDict = vehicleDescr.__dict__
        else:
            attrDict = getattr(vehicleDescr, self.__attr[0])
        val = attrDict[self.attribute]
        attrDict[self.attribute] = val * self.factor
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration
        miscAttrs['repeatedStunDurationFactor'] *= self.repeatedStunDurationFactor

    def _readConfig(self, xmlCtx, section):
        self.__factor = _xml.readPositiveFloat(xmlCtx, section, 'factor')
        self.__attr = _xml.readNonEmptyString(xmlCtx, section, 'attribute').split('/', 1)

    @property
    def factor(self):
        return self.__factor

    @property
    def attribute(self):
        return self.__attr[0] if len(self.__attr) == 1 else self.__attr[1]


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
        else:
            attrDict = getattr(vehicleDescr, self.__attr[0])
        val = attrDict[self.attribute]
        attrDict[self.attribute] = val + self.value
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration
        miscAttrs['repeatedStunDurationFactor'] *= self.repeatedStunDurationFactor

    def _readConfig(self, xmlCtx, section):
        self.__value = _xml.readFloat(xmlCtx, section, 'value')
        self.__attr = _xml.readNonEmptyString(xmlCtx, section, 'attribute').split('/', 1)

    @property
    def value(self):
        return self.__value

    @property
    def attribute(self):
        return self.__attr[0] if len(self.__attr) == 1 else self.__attr[1]


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
    __slots__ = ('chassisMaxLoadFactor', 'chassisHealthFactor', 'vehicleByChassisDamageFactor')

    def __init__(self):
        super(EnhancedSuspension, self).__init__()
        self.chassisMaxLoadFactor = component_constants.ZERO_FLOAT
        self.chassisHealthFactor = component_constants.ZERO_FLOAT
        self.vehicleByChassisDamageFactor = component_constants.ZERO_FLOAT

    def weightOnVehicle(self, vehicleDescr):
        chassis = vehicleDescr.chassis
        return (self._vehWeightFraction, self._weight, chassis.maxLoad * (self.chassisMaxLoadFactor - 1.0))

    def _readConfig(self, xmlCtx, section):
        reader = partial(_xml.readPositiveFloat, xmlCtx, section)
        self.chassisMaxLoadFactor = reader('chassisMaxLoadFactor')
        self.chassisHealthFactor = reader('chassisHealthFactor')
        self.vehicleByChassisDamageFactor = reader('vehicleByChassisDamageFactor')

    def updateVehicleDescrAttrs(self, vehicleDescr):
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['chassisHealthFactor'] *= self.chassisHealthFactor
        miscAttrs['vehicleByChassisDamageFactor'] *= self.vehicleByChassisDamageFactor
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration
        miscAttrs['repeatedStunDurationFactor'] *= self.repeatedStunDurationFactor


class Grousers(OptionalDevice):
    __slots__ = ('factorSoft', 'factorMedium')

    def __init__(self):
        super(Grousers, self).__init__()
        self.factorSoft = component_constants.ZERO_FLOAT
        self.factorMedium = component_constants.ZERO_FLOAT

    def updateVehicleDescrAttrs(self, vehicleDescr):
        r = vehicleDescr.physics['terrainResistance']
        vehicleDescr.physics['terrainResistance'] = (r[0], r[1] * self.factorMedium, r[2] * self.factorSoft)
        rff = vehicleDescr.physics['rollingFrictionFactors']
        rff[1] *= self.factorMedium
        rff[2] *= self.factorSoft

    def _readConfig(self, xmlCtx, section):
        self.factorSoft = _xml.readPositiveFloat(xmlCtx, section, 'softGroundResistanceFactor')
        self.factorMedium = _xml.readPositiveFloat(xmlCtx, section, 'mediumGroundResistanceFactor')


class AntifragmentationLining(OptionalDevice):
    __slots__ = ('antifragmentationLiningFactor', 'increaseCrewChanceToEvadeHit', 'armorSpallsDamageDevicesFactor')

    def __init__(self):
        super(AntifragmentationLining, self).__init__()
        self.antifragmentationLiningFactor = component_constants.ZERO_FLOAT
        self.increaseCrewChanceToEvadeHit = component_constants.ZERO_FLOAT
        self.armorSpallsDamageDevicesFactor = component_constants.ZERO_FLOAT

    def updateVehicleDescrAttrs(self, vehicleDescr):
        miscAttrs = vehicleDescr.miscAttrs
        miscAttrs['antifragmentationLiningFactor'] *= self.antifragmentationLiningFactor
        miscAttrs['crewChanceToHitFactor'] *= 1.0 - self.increaseCrewChanceToEvadeHit
        miscAttrs['stunResistanceEffect'] += self.stunResistanceEffect
        miscAttrs['stunResistanceDuration'] += self.stunResistanceDuration
        miscAttrs['repeatedStunDurationFactor'] *= self.repeatedStunDurationFactor
        miscAttrs['armorSpallsDamageDevicesFactor'] *= self.armorSpallsDamageDevicesFactor

    def _readConfig(self, xmlCtx, section):
        reader = partial(_xml.readPositiveFloat, xmlCtx, section)
        self.antifragmentationLiningFactor = reader('antifragmentationLiningFactor')
        self.increaseCrewChanceToEvadeHit = reader('increaseCrewChanceToEvadeHit')
        self.armorSpallsDamageDevicesFactor = _xml.readPositiveFloat(xmlCtx, section, 'armorSpallsDamageDevicesFactor', 1.0)


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
        self.consumeAmmo = _xml.readBool(xmlCtx, section, 'consumeAmmo', False)
        self.disableAllyDamage = _xml.readBool(xmlCtx, section, 'disableAllyDamage', False)

    def _readCooldownFactors(self, xmlCtx, section, name):
        cooldownFactors = {}
        subXmlCtx, subsection = _xml.getSubSectionWithContext(xmlCtx, section, name)
        for vehClass, _ in _xml.getItemsWithContext(subXmlCtx, subsection):
            cooldownFactors[vehClass] = _xml.readNonNegativeFloat(subXmlCtx, subsection, vehClass)

        return cooldownFactors


class ArcadeEquipmentConfigReader(object):
    _SHARED_ARCADE_SLOTS = ('minApplyRadius', 'maxApplyRadius', 'cameraPivotPosMin', 'cameraPivotPosMax')

    def initArcadeInformation(self):
        self.minApplyRadius = component_constants.ZERO_FLOAT
        self.maxApplyRadius = component_constants.ZERO_FLOAT
        self.cameraPivotPosMin = (0, 0, 0)
        self.cameraPivotPosMax = (0, 0, 0)

    def readArcadeInformation(self, xmlCtx, section):
        self.minApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'minApplyRadius', component_constants.ZERO_FLOAT)
        self.maxApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'maxApplyRadius', component_constants.ZERO_FLOAT)
        if IS_CLIENT:
            self.cameraPivotPosMin = _xml.readVector3OrNone(xmlCtx, section, 'cameraPivotPosMin')
            self.cameraPivotPosMax = _xml.readVector3OrNone(xmlCtx, section, 'cameraPivotPosMax')


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


class ArtilleryConfigReader(object):
    _ARTILLERY_SLOTS = ('delay', 'duration', 'shotsNumber', 'areaRadius', 'shellCompactDescr', 'piercingPower', 'areaVisual', 'areaColor', 'areaMarker', 'areaLength', 'noOwner', 'shotSoundPreDelay', 'wwsoundShot', 'wwsoundEquipmentUsed')

    def initArtillerySlots(self):
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
        self.shotSoundPreDelay = component_constants.ZERO_FLOAT
        self.wwsoundShot = None
        self.wwsoundEquipmentUsed = None
        return

    def readArtilleryConfig(self, xmlCtx, section):
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay')
        self.duration = _xml.readPositiveFloat(xmlCtx, section, 'duration')
        self.shotsNumber = _xml.readNonNegativeInt(xmlCtx, section, 'shotsNumber')
        self.areaRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'areaRadius')
        self.shellCompactDescr = _xml.readInt(xmlCtx, section, 'shellCompactDescr')
        self.piercingPower = _xml.readTupleOfPositiveInts(xmlCtx, section, 'piercingPower', 2)
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.areaLength = self.areaWidth = self.areaRadius * 2
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
    _SMOKE_SLOTS = ('minDelay', 'deltaDelayRange', 'smokeModelName', 'startRadius', 'expandedRadius', 'startHeight', 'expandedHeight', 'heightUpFraction', 'expansionDuration', 'dispersionRadius', 'totalDuration', 'smokeOpacity', 'visionRadiusFactor', 'areaLength', 'areaWidth', 'projectilesNumber', 'shellCompactDescr', 'areaVisual', 'areaMarker', 'noOwner', 'smokeEffectName', 'shotSoundPreDelay', 'wwsoundShot')

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


class InspireConfigReader(object):
    _INSPIRE_SLOTS = ('duration', 'crewIncreaseFactor', 'inactivationDelay', 'radius', 'wwsoundEquipmentUsed')

    def initInspireSlots(self):
        self.duration = component_constants.ZERO_FLOAT
        self.crewIncreaseFactor = component_constants.ZERO_FLOAT
        self.inactivationDelay = component_constants.ZERO_FLOAT
        self.radius = component_constants.ZERO_FLOAT
        self.wwsoundEquipmentUsed = None
        return

    def readInspireConfig(self, xmlCtx, section):
        self.duration = _xml.readPositiveFloat(xmlCtx, section, 'duration')
        self.crewIncreaseFactor = _xml.readPositiveFloat(xmlCtx, section, 'crewIncreaseFactor')
        self.inactivationDelay = _xml.readNonNegativeFloat(xmlCtx, section, 'inactivationDelay')
        self.radius = _xml.readPositiveFloat(xmlCtx, section, 'radius')
        self.wwsoundEquipmentUsed = _xml.readStringOrNone(xmlCtx, section, 'wwsoundEquipmentUsed')


class AnimatedSceneConfigReader(object):
    _ANIMATED_SCENE_SLOTS = ('sequencePath', 'sequenceDuration', 'offset', 'repeat', 'repeatDelay', 'yprDeviation', 'offsetDeviation', 'delayDeviation')

    def initAnimatedSceneSlots(self):
        self.sequencePath = component_constants.EMPTY_STRING
        self.sequenceDuration = component_constants.ZERO_FLOAT
        self.offset = (0, 0, 0)
        self.repeat = 1
        self.repeatDelay = 0.0
        self.yprDeviation = (0, 0, 0)
        self.offsetDeviation = (0, 0, 0)
        self.delayDeviation = 0.0

    def readAnimatedSceneConfig(self, xmlCtx, section):
        self.sequencePath = section.readString('sequencePath')
        self.sequenceDuration = section.readFloat('sequenceDuration')
        self.offset = section.readVector3('offset')
        self.repeat = section.readInt('repeat', 1)
        self.repeatDelay = section.readFloat('repeatDelay')
        self.yprDeviation = section.readVector3('yprDeviation')
        self.offsetDeviation = section.readVector3('offsetDeviation')
        self.delayDeviation = section.readFloat('delayDeviation')


class MinefieldConfigReader(object):
    _MINEFIELD_SLOTS = ('bombsPattern', 'itemPickup', 'noOwner', 'areaLength', 'areaWidth', 'areaVisual', 'areaColor', 'areaMarker')

    def initMinefieldSlots(self):
        self.bombsPattern = []
        self.itemPickup = component_constants.EMPTY_STRING
        self.noOwner = False
        self.areaLength = 0
        self.areaWidth = 0
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        return

    def readMinefieldConfig(self, xmlCtx, section):
        bombs = _xml.readTupleOfFloats(xmlCtx, section, 'bombsPattern')
        self.bombsPattern = [ (bombs[b], bombs[b + 1]) for b in range(0, len(bombs) - 1, 2) ]
        self.itemPickup = _xml.readString(xmlCtx, section, 'itemPickup')
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.areaLength = _xml.readPositiveFloat(xmlCtx, section, 'areaLength')
        self.areaWidth = _xml.readPositiveFloat(xmlCtx, section, 'areaWidth')
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')


class EventDeathZoneConfigReader(AnimatedSceneConfigReader):
    _EVENT_DEATH_ZONE_SLOTS = AnimatedSceneConfigReader._ANIMATED_SCENE_SLOTS + ('dispersionRangeLowerBound', 'dispersionRangeUpperBound', 'maxTargetPlayers', 'warningDuration')

    def initEventDeathZoneSlots(self):
        self.initAnimatedSceneSlots()
        self.dispersionRangeLowerBound = 1.0
        self.dispersionRangeUpperBound = 1.0
        self.maxTargetPlayers = 5
        self.warningDuration = 3.0

    def readEventDeathZoneConfig(self, xmlCtx, section):
        self.readAnimatedSceneConfig(xmlCtx, section)
        self.dispersionRangeLowerBound = section.readFloat('dispersionRangeLowerBound', 1.0)
        self.dispersionRangeUpperBound = section.readFloat('dispersionRangeUpperBound', 1.0)
        self.maxTargetPlayers = section.readInt('maxTargetPlayers', 5)
        self.warningDuration = section.readFloat('warningDuration', 3.0)


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

    def updateVehicleAttrFactors(self, vehicleDescr, factors, _):
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


class EventEquipment(Equipment):
    __slots__ = ('durationSeconds', 'cooldownSeconds', 'reuseCount')

    def __init__(self):
        super(EventEquipment, self).__init__()
        self.durationSeconds = component_constants.ZERO_FLOAT
        self.cooldownSeconds = component_constants.ZERO_FLOAT
        self.reuseCount = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(EventEquipment, self)._readConfig(xmlCtx, section)
        try:
            self.durationSeconds = _xml.readFloat(xmlCtx, section, 'durationSeconds')
            self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownSeconds')
            self.reuseCount = _xml.readInt(xmlCtx, section, 'reuseCount')
        except SoftException:
            pass


class EventActionConfigReader(object):
    _ACTION_SLOTS = ('delay', 'interval', 'duration', 'shotsNumber', 'areaRadius', 'shotAreaColor', 'areaVisual', 'areaColor', 'areaMarker', 'areaLength', 'areaWidth', 'noOwner', 'shotSoundPreDelay', 'wwsoundShot', 'actionConfig')

    def initActionSlots(self):
        self.delay = component_constants.ZERO_FLOAT
        self.interval = component_constants.ZERO_FLOAT
        self.duration = component_constants.ZERO_FLOAT
        self.shotsNumber = component_constants.ZERO_INT
        self.areaRadius = component_constants.ZERO_FLOAT
        self.areaVisual = None
        self.areaColor = None
        self.areaMarker = None
        self.shotAreaColor = None
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.shotSoundPreDelay = component_constants.ZERO_FLOAT
        self.wwsoundShot = None
        self.explodeDestructible = False
        self.actionConfig = []
        return

    def readActionConfig(self, xmlCtx, section):
        self.delay = _xml.readPositiveFloat(xmlCtx, section, 'delay')
        self.interval = _xml.readPositiveFloat(xmlCtx, section, 'interval')
        self.duration = _xml.readPositiveFloat(xmlCtx, section, 'duration')
        self.shotsNumber = _xml.readNonNegativeInt(xmlCtx, section, 'shotsNumber')
        self.areaRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'areaRadius', 0)
        self.areaLength = _xml.readNonNegativeFloat(xmlCtx, section, 'areaLength', self.areaRadius * 2)
        self.areaWidth = _xml.readNonNegativeFloat(xmlCtx, section, 'areaWidth', self.areaRadius * 2)
        self.areaVisual = _xml.readStringOrNone(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')
        self.areaMarker = _xml.readStringOrNone(xmlCtx, section, 'areaMarker')
        self.shotAreaColor = _xml.readIntOrNone(xmlCtx, section, 'shotAreaColor')
        self.noOwner = _xml.readBool(xmlCtx, section, 'noOwner')
        self.shotSoundPreDelay = _xml.readIntOrNone(xmlCtx, section, 'shotSoundPreDelay')
        self.wwsoundShot = _xml.readStringOrNone(xmlCtx, section, 'wwsoundShot')
        if IS_CELLAPP:
            self.actionConfig = [ readAction(conf) for conf in section['actions'].values() ]
            self.explodeDestructible = _xml.readBool(xmlCtx, section, 'explodeDestructible')


class EventActionEquipment(Equipment, EventActionConfigReader, AnimatedSceneConfigReader, TooltipConfigReader, SharedCooldownConsumableConfigReader, ArcadeEquipmentConfigReader):
    __slots__ = ('effects',) + EventActionConfigReader._ACTION_SLOTS + TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(EventActionEquipment, self).__init__()
        self.initActionSlots()
        self.initAnimatedSceneSlots()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initArcadeInformation()

    def readSequenceConfig(self, section):
        return None if not section else {'shotEffects': section.readString('shotEffects').split(),
         'sequences': section.readString('sequencePath').split(),
         'groundRaycast': section.readBool('groundRaycast'),
         'offsetDeviation': section.readFloat('offsetDeviation'),
         'repeatCount': section.readInt('repeatCount', 1),
         'repeatDelay': section.readFloat('repeatDelay', 0)}

    def _readConfig(self, xmlCtx, section):
        super(EventActionEquipment, self)._readConfig(xmlCtx, section)
        self.readActionConfig(xmlCtx, section)
        self.readTooltipInformation(xmlCtx, section)
        self.readSharedCooldownConsumableConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)
        self.effects = {'start': self.readSequenceConfig(section['startSequence']),
         'action': self.readSequenceConfig(section['actionSequence'])}


class BuffEquipment(EventEquipment):
    __slots__ = ('buffNames',)

    def __init__(self):
        super(BuffEquipment, self).__init__()
        self.buffNames = None
        return

    def _readConfig(self, xmlCtx, section):
        super(BuffEquipment, self)._readConfig(xmlCtx, section)
        self.buffNames = self._readBuffs(xmlCtx, section, 'buffs')

    @staticmethod
    def _readBuffs(xmlCtx, section, subsectionName):
        buffNames = _xml.readString(xmlCtx, section, subsectionName).split()
        return frozenset({intern(name) for name in buffNames})


class SuperShell(BuffEquipment):
    __slots__ = ('shotsCount',)

    def __init__(self):
        super(SuperShell, self).__init__()
        self.shotsCount = 1

    def _readConfig(self, xmlCtx, section):
        super(SuperShell, self)._readConfig(xmlCtx, section)
        self.shotsCount = _xml.readInt(xmlCtx, section, 'shotsCount')


class HpRepairAndCrewHealEquipment(BuffEquipment):
    __slots__ = ('isInterruptable', 'immediateHealAmount')

    def __init__(self):
        super(HpRepairAndCrewHealEquipment, self).__init__()
        self.isInterruptable = False
        self.immediateHealAmount = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(HpRepairAndCrewHealEquipment, self)._readConfig(xmlCtx, section)
        self.isInterruptable = _xml.readBool(xmlCtx, section, 'isInterruptable')
        self.immediateHealAmount = _xml.readInt(xmlCtx, section, 'immediateHealAmount')


class RadiusEquipment(EventEquipment):
    __slots__ = ('radius',)

    def __init__(self):
        super(RadiusEquipment, self).__init__()
        self.radius = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(RadiusEquipment, self)._readConfig(xmlCtx, section)
        self.radius = _xml.readInt(xmlCtx, section, 'radius')


class ResurrectEquipment(Equipment, TooltipConfigReader):
    pass


class ConsumableMinefield(Equipment, TooltipConfigReader, SharedCooldownConsumableConfigReader, MinefieldConfigReader, ArcadeEquipmentConfigReader):
    __slots__ = TooltipConfigReader._SHARED_TOOLTIPS_CONSUMABLE_SLOTS + SharedCooldownConsumableConfigReader._SHARED_COOLDOWN_CONSUMABLE_SLOTS + MinefieldConfigReader._MINEFIELD_SLOTS + ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(ConsumableMinefield, self).__init__()
        self.initTooltipInformation()
        self.initSharedCooldownConsumableSlots()
        self.initMinefieldSlots()
        self.initArcadeInformation()

    def _readConfig(self, xmlCtx, scriptSection):
        self.readTooltipInformation(xmlCtx, scriptSection)
        self.readSharedCooldownConsumableConfig(xmlCtx, scriptSection)
        self.readMinefieldConfig(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)


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


class UpgradableItem(object):
    UpgradeInfo = NamedTuple('UpgradeInfo', [('upgradedCompDescr', int)])

    @property
    def upgradeInfo(self):
        return self.__upgradeInfo

    def initUpgradableItem(self):
        self.__upgradeInfo = None
        return

    def _readUpgradableConfig(self, xmlCtx, scriptSection, itemCompDescr):
        upgradeInfoSection = scriptSection['upgradeInfo']
        upgradedCD = _xml.readInt(xmlCtx, upgradeInfoSection, 'upgradedCompDescr')
        self.__upgradeInfo = UpgradableItem.UpgradeInfo(upgradedCD)
        _readPriceForOperation(xmlCtx, upgradeInfoSection, ITEM_OPERATION.UPGRADE, (itemCompDescr, upgradedCD))


class UpgradedItem(object):
    __slots__ = ()


class UpgradableStaticFactorDevice(StaticFactorDevice, UpgradableItem):

    def __init__(self):
        super(UpgradableStaticFactorDevice, self).__init__()
        self.initUpgradableItem()

    def _readConfig(self, xmlCtx, section):
        super(UpgradableStaticFactorDevice, self)._readConfig(xmlCtx, section)
        self._readUpgradableConfig(xmlCtx, section, self.compactDescr)


class UpgradableStaticAdditiveDevice(StaticAdditiveDevice, UpgradableItem):

    def __init__(self):
        super(UpgradableStaticAdditiveDevice, self).__init__()
        self.initUpgradableItem()

    def _readConfig(self, xmlCtx, section):
        super(UpgradableStaticAdditiveDevice, self)._readConfig(xmlCtx, section)
        self._readUpgradableConfig(xmlCtx, section, self.compactDescr)


class UpgradedStaticFactorDevice(StaticFactorDevice, UpgradedItem):
    pass


class UpgradedStaticAdditiveDevice(StaticAdditiveDevice, UpgradedItem):
    pass


class EventArcadeArtillery(ConsumableArtillery, ArcadeEquipmentConfigReader):
    __slots__ = ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(EventArcadeArtillery, self).__init__()
        self.initArcadeInformation()

    def _readConfig(self, xmlCtx, section):
        super(EventArcadeArtillery, self)._readConfig(xmlCtx, section)
        self.readArcadeInformation(xmlCtx, section)


class EventBomber(ConsumableBomber, AnimatedSceneConfigReader):
    __slots__ = AnimatedSceneConfigReader._ANIMATED_SCENE_SLOTS

    def __init__(self):
        super(EventBomber, self).__init__()
        self.initAnimatedSceneSlots()
        self.shotAreaColor = None
        self.actionConfig = []
        self.explodeDestructible = False
        return

    def _readConfig(self, xmlCtx, scriptSection):
        super(EventBomber, self)._readConfig(xmlCtx, scriptSection)
        self.shotAreaColor = _xml.readIntOrNone(xmlCtx, scriptSection, 'shotAreaColor')
        if IS_CELLAPP:
            if scriptSection.has_key('actions'):
                self.actionConfig = [ readAction(conf) for conf in scriptSection['actions'].values() ]
            if scriptSection.has_key('explodeDestructible'):
                self.explodeDestructible = _xml.readBool(xmlCtx, scriptSection, 'explodeDestructible')
        self.readAnimatedSceneConfig(xmlCtx, scriptSection)


class EventArcadeBomber(EventBomber, ArcadeEquipmentConfigReader):
    __slots__ = ArcadeEquipmentConfigReader._SHARED_ARCADE_SLOTS

    def __init__(self):
        super(EventBomber, self).__init__()
        self.initArcadeInformation()

    def _readConfig(self, xmlCtx, scriptSection):
        super(EventArcadeBomber, self)._readConfig(xmlCtx, scriptSection)
        self.readArcadeInformation(xmlCtx, scriptSection)


class EventResurrectEquipment(ResurrectEquipment):
    pass


class EventMinefield(ConsumableMinefield):
    pass


class EventDeathZone(ConsumableArtillery, EventDeathZoneConfigReader):
    __slots__ = EventDeathZoneConfigReader._EVENT_DEATH_ZONE_SLOTS

    def __init__(self):
        super(EventDeathZone, self).__init__()
        self.initEventDeathZoneSlots()

    def _readConfig(self, xmlCtx, scriptSection):
        super(EventDeathZone, self)._readConfig(xmlCtx, scriptSection)
        self.readEventDeathZoneConfig(xmlCtx, scriptSection)


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

    def compatibleNations(self):
        included = set(chain.from_iterable((params.get('nations', []) for params in self.__include)))
        excluded = set(chain.from_iterable((params.get('nations', []) for params in self.__exclude)))
        return list(included - excluded)


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

        if sname == 'vehicles':
            res['vehicles'] = section.asString.split(' ')
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
    vehicleName = vehicleType.name
    hasVehicleTypeOk = False
    for entry in subfilter:
        item = entry.get('nations')
        if item is not None and nationID not in item:
            continue
        item = entry.get('vehicles')
        if item is not None and vehicleName not in item:
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
            if name in ('nations', 'vehicle', 'vehicles'):
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

def _readKpi(xmlCtx, section):
    from gui.shared.gui_items import KPI
    kpi = []
    for kpiType, subsec in section.items():
        if kpiType not in KPI.Type.ALL():
            _xml.raiseWrongXml(xmlCtx, kpiType, 'unsupported KPI type')
            return
        if kpiType == KPI.Type.ONE_OF:
            kpi.append(KPI(KPI.Name.COMPOUND_KPI, _readKpi(xmlCtx, subsec), KPI.Type.ONE_OF))
        name = subsec.readString('name')
        value = subsec.readFloat('value')
        if not name:
            _xml.raiseWrongXml(xmlCtx, kpiType, 'empty <name> tag not allowed')
            return
        if name not in KPI.Name.ALL():
            _xml.raiseWrongXml(xmlCtx, kpiType, 'unsupported value in <name> tag')
            return
        kpi.append(KPI(name, value, kpiType))

    return kpi


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
