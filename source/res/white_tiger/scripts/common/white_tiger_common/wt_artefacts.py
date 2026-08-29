# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_artefacts.py
from items import _xml
from items.artefacts import Equipment, VehicleFactorsXmlReader, Repairkit, ArenaAimLimits, ArcadeEquipmentConfigReader, Smoke
from items.components import component_constants
from constants import IS_CLIENT
from debug_utils import LOG_WARNING
from items import vehicles

class WTBaseEquipment(object):

    def __init__(self):
        self.subType = ''

    def readExtraData(self, xmlCtx, section):
        self.subType = _xml.readString(xmlCtx, section, 'subType')


class WTRepairkit(Repairkit, WTBaseEquipment):

    def _readBasicConfig(self, xmlCtx, section):
        Repairkit._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTMedkit(Repairkit, WTBaseEquipment):

    def __init__(self):
        super(WTMedkit, self).__init__()
        self.removeDebuffsFromAbilities = component_constants.EMPTY_TUPLE

    def _readConfig(self, xmlCtx, section):
        super(WTMedkit, self)._readConfig(xmlCtx, section)
        self.removeDebuffsFromAbilities = tuple(section.readString('removeDebuffsFromAbilities').split(' '))

    def _readBasicConfig(self, xmlCtx, section):
        Repairkit._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTPassiveHealing(Equipment, WTBaseEquipment):
    __slots__ = ('maxHealthRegenPct', 'tickInterval', 'effects')

    def __init__(self):
        super(WTPassiveHealing, self).__init__()
        self.maxHealthRegenPct = 0.0
        self.tickInterval = 0.0
        self.effects = {}

    def _readConfig(self, xmlCtx, section):
        super(WTPassiveHealing, self)._readConfig(xmlCtx, section)
        self.maxHealthRegenPct = _xml.readFloat(xmlCtx, section, 'maxHealthRegenPct', 0.0)
        self.tickInterval = _xml.readFloat(xmlCtx, section, 'tickInterval', 0.0)
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section)

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTUnionStrength(Equipment, WTBaseEquipment):
    __slots__ = ('effectDuration', 'receiveDamageFactor', 'effects', 'teamMateRadius', 'healingValue', 'healingTickInterval')

    def __init__(self):
        super(WTUnionStrength, self).__init__()
        self.effectDuration = component_constants.ZERO_INT
        self.receiveDamageFactor = component_constants.ZERO_FLOAT
        self.effects = component_constants.EMPTY_DICT
        self.hunterEffects = component_constants.EMPTY_DICT
        self.teamMateRadius = component_constants.ZERO_INT
        self.healingValue = component_constants.ZERO_INT
        self.healingTickInterval = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        super(WTUnionStrength, self)._readConfig(xmlCtx, section)
        self.effectDuration = _xml.readInt(xmlCtx, section, 'effectDuration', 0)
        self.receiveDamageFactor = _xml.readFloat(xmlCtx, section, 'receiveDamageFactor', 1.0)
        self.teamMateRadius = _xml.readInt(xmlCtx, section, 'teamMateRadius', 0)
        self.healingValue = _xml.readInt(xmlCtx, section, 'healingValue', 0)
        self.healingTickInterval = _xml.readFloat(xmlCtx, section, 'healingTickInterval', 0.0)
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section, self.effectDuration)
            self.hunterEffects = _getHunterVisualEffects(xmlCtx, section)

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTInvisibilityBase(Equipment, WTBaseEquipment):
    __slots__ = ('entrancePrefab', 'escapePrefab')

    def __init__(self):
        super(WTInvisibilityBase, self).__init__()
        self.entrancePrefab = component_constants.EMPTY_STRING
        self.escapePrefab = component_constants.EMPTY_STRING

    def _readConfig(self, xmlCtx, section):
        super(WTInvisibilityBase, self)._readConfig(xmlCtx, section)
        if IS_CLIENT:
            self.entrancePrefab = _xml.readStringOrNone(xmlCtx, section, 'entrancePrefab')
            self.escapePrefab = _xml.readStringOrNone(xmlCtx, section, 'escapePrefab')

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTInvisibilityModA(WTInvisibilityBase):
    __slots__ = ('procedureEffects',)

    def __init__(self):
        super(WTInvisibilityModA, self).__init__()
        self.procedureEffects = component_constants.EMPTY_DICT

    def _readConfig(self, xmlCtx, section):
        super(WTInvisibilityModA, self)._readConfig(xmlCtx, section)
        self.procedureEffects = _getProcedureEffects(xmlCtx, section)


class WTInvisibilityModB(WTInvisibilityBase):
    pass


class WTHyperionModA(Equipment, WTBaseEquipment):
    __slots__ = ('readyPrefab',)

    def __init__(self):
        super(WTHyperionModA, self).__init__()
        self.readyPrefab = component_constants.EMPTY_STRING

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTHyperionModA, self)._readConfig(xmlCtx, section)
        self.radius = _xml.readFloat(xmlCtx, section, 'radius', 0.0)
        self.height = _xml.readFloat(xmlCtx, section, 'height', 0.0)
        self.depth = _xml.readFloat(xmlCtx, section, 'depth', 0.0)
        self.chargeFactor = _xml.readFloat(xmlCtx, section, 'chargeFactor', 0.0)
        self.chargingDelay = _xml.readInt(xmlCtx, section, 'chargingDelay', 0)
        self.damagePerShot = _xml.readInt(xmlCtx, section, 'damagePerShot', 0)
        self.shotsAmount = _xml.readInt(xmlCtx, section, 'shotsAmount', 0)
        self.shotDuration = _xml.readFloat(xmlCtx, section, 'shotDuration', 0)
        self.minApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'minApplyRadius', component_constants.ZERO_FLOAT)
        self.maxApplyRadius = _xml.readNonNegativeFloat(xmlCtx, section, 'maxApplyRadius', component_constants.ZERO_FLOAT)
        self.arenaAimLimits = ArenaAimLimits.readConfig(xmlCtx, section, 'arenaAimLimits')
        self.readyPrefab = _xml.readStringOrNone(xmlCtx, section, 'readyPrefab')
        if IS_CLIENT:
            self.aimCircleVisual = _xml.readStringOrNone(xmlCtx, section, 'aimCircleVisual')
            self.shotPrefab = _xml.readStringOrNone(xmlCtx, section, 'shotPrefab')
            self.chargePrefab = _xml.readStringOrNone(xmlCtx, section, 'chargePrefab')


class WTHyperionModB(WTHyperionModA):

    def _readConfig(self, xmlCtx, section):
        super(WTHyperionModB, self)._readConfig(xmlCtx, section)
        self.shotRadius = _xml.readFloat(xmlCtx, section, 'shotRadius', 0.0)
        self.destroyDelay = _xml.readFloat(xmlCtx, section, 'destroyDelay', 0.0)


class WTTeleportModA(Equipment, WTBaseEquipment):

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTTeleportModA, self)._readConfig(xmlCtx, section)
        self.consumeSeconds = _xml.readInt(xmlCtx, section, 'consumeSeconds', 0)
        self.debuffFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'debuffFactors')
        self.prefabDeparture = _xml.readStringOrNone(xmlCtx, section, 'prefabDeparture')
        self.prefabDestination = _xml.readStringOrNone(xmlCtx, section, 'prefabDestination')


class WTTeleportModB(WTTeleportModA):
    pass


class WTClone(Equipment, WTBaseEquipment, ArcadeEquipmentConfigReader):

    def __init__(self):
        super(WTClone, self).__init__()
        self.cloneSettings = {}
        self.cooldownSeconds = component_constants.ZERO_FLOAT
        self.shuffleOwner = False
        self.useVehPosition = False
        self.instantCooldown = False
        self.__initSelectorSettings()
        self.initArcadeInformation()

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        if self.consumeSeconds != 0:
            LOG_WARNING('WTClone consumeSeconds not equals to zero. Unsupported.')
        self.consumeSeconds = 0.1
        self.readArcadeInformation(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownSeconds')
        self.shuffleOwner = _xml.readBool(xmlCtx, section, 'shuffleOwner')
        self.useVehPosition = _xml.readBool(xmlCtx, section, 'useVehPosition')
        self.__readCloneSettings(xmlCtx, section['cloneSettings'])
        self.__readSelectorSettings(xmlCtx, section)

    def __initSelectorSettings(self):
        self.areaLength = component_constants.ZERO_FLOAT
        self.areaWidth = component_constants.ZERO_FLOAT
        self.areaVisual = None
        self.areaColor = component_constants.ZERO_INT
        return

    def __readCloneSettings(self, xmlCtx, section):
        self.cloneSettings['vehName'] = _xml.readStringOrNone(xmlCtx, section, 'vehName')
        botConfigName = _xml.readStringOrNone(xmlCtx, section, 'botConfig')
        self.cloneSettings['botConfig'] = 'bots/{}.xml'.format(botConfigName)
        self.cloneSettings['cloneCount'] = _xml.readInt(xmlCtx, section, 'cloneCount')
        if self.cloneSettings['cloneCount'] > 0:
            self.cloneSettings['cloneRadius'] = _xml.readInt(xmlCtx, section, 'cloneRadius')
        self.cloneSettings['cloneLifetime'] = _xml.readFloat(xmlCtx, section, 'cloneLifetime')
        self.cloneSettings['cloneProperties'] = []
        self.cloneSettings['cloneFactors'] = {}
        cloneProperties = _xml.readStringOrNone(xmlCtx, section, 'cloneProperties')
        self.cloneSettings['cloneProperties'] = cloneProperties.split() or []
        if 'cloneFactors' in section.keys():
            self.cloneSettings['cloneFactors'] = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'cloneFactors')

    def __readSelectorSettings(self, xmlCtx, section):
        self.areaWidth = _xml.readFloat(xmlCtx, section, 'areaWidth')
        self.areaLength = _xml.readFloat(xmlCtx, section, 'areaLength')
        self.areaVisual = _xml.readString(xmlCtx, section, 'areaVisual')
        self.areaColor = _xml.readIntOrNone(xmlCtx, section, 'areaColor')


class WTStunArea(Equipment, WTBaseEquipment):
    __slots__ = ('damageRadius', 'effects', 'components', 'debuffDuration', 'shotData', 'effectsIndex')

    def __init__(self):
        super(WTStunArea, self).__init__()
        self.damageRadius = component_constants.ZERO_INT
        self.effects = component_constants.EMPTY_DICT
        self.components = component_constants.EMPTY_DICT
        self.debuffDuration = component_constants.ZERO_INT
        self.shotData = component_constants.EMPTY_DICT
        self.effectsIndex = component_constants.ZERO_INT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTStunArea, self)._readConfig(xmlCtx, section)
        self.damageRadius = section.readInt('damageRadius')
        self.debuffDuration = section.readInt('debuffDuration')
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section, self.debuffDuration)
        if section.has_key('shotData'):
            self.shotData = _readShotData(xmlCtx, section)
        if section.has_key('shotEffect'):
            self.effectsIndex = vehicles.g_cache.shotEffectsIndexes[_xml.readString(xmlCtx, section, 'shotEffect')]


def _readFactorAppliers(xmlCtx, section):
    paramsSection = _xml.getSubsection(xmlCtx, section, 'params')
    return {'factors': VehicleFactorsXmlReader.readFactors(xmlCtx, paramsSection, 'factors'),
     'onceDamage': paramsSection.readInt('onceDamage')}


def _readAbilityLock(xmlCtx, section):
    paramsSection = _xml.getSubsection(xmlCtx, section, 'params')
    vehicleParams = _xml.getSubsection(xmlCtx, paramsSection, 'vehicleParams')
    result = {'vehicleParams': {}}
    for vehicleSection in vehicleParams.values():
        vehName = vehicleSection.readString('name')
        vehCD = vehicles.makeVehicleTypeCompDescrByName(vehName)
        result['vehicleParams'][vehCD] = vehicleSection.readString('lockedAbilities').split()

    return result


def _readDynamicComponents(xmlCtx, section):
    paramsSection = _xml.getSubsection(xmlCtx, section, 'params')
    factorsByLevelSection = _xml.getSubsection(xmlCtx, paramsSection, 'factorsByLevel')
    factorsByLevel = []
    for factorsSection in factorsByLevelSection.values():
        factors = VehicleFactorsXmlReader.readFactors(xmlCtx, factorsSection, 'factors')
        factorsByLevel.append(factors)

    return {'factors': factorsByLevel}


_COMPONENT_READERS = {'WTVehicleFactorAppliers': _readFactorAppliers,
 'WTVehicleAbilityLock': _readAbilityLock,
 'WTVehicleDynamicFactors': _readDynamicComponents}

def _readComponents(xmlCtx, section):
    componentsSection = _xml.getSubsection(xmlCtx, section, 'components')
    componentsData = {}
    for component in componentsSection.values():
        name = component.readString('name')
        key = component.readString('key')
        componentsData[name, key] = _COMPONENT_READERS[name](xmlCtx, component)

    return componentsData


def _readShotData(xmlCtx, section):
    shellSection = _xml.getSubsection(xmlCtx, section, 'shotData')
    shotData = {}
    shotData['shellName'] = shellSection.readString('shellName')
    shotData['shotPiercing100m'] = shellSection.readInt('shotPiercing100m')
    shotData['shotPiercing500m'] = shellSection.readInt('shotPiercing500m')
    shotData['shotSpeed'] = shellSection.readInt('shotSpeed')
    shotData['shotGravity'] = shellSection.readFloat('shotGravity')
    shotData['shotMaxDistance'] = shellSection.readInt('shotMaxDistance')
    shotData['maxHeight'] = shellSection.readInt('maxHeight')
    return shotData


def _getSequences(xmlCtx, section, sequenceDuration=0):
    sequences = {}
    data = _xml.getSubsection(xmlCtx, section, 'sequences', False)
    if data is None:
        return sequences
    else:

        def getSequenceData(section):
            sequences = {}
            for _, subSec in section.items():
                sequenceID = subSec.readInt('sequenceID', 0)
                seqDurationConfig = subSec.readFloat('duration', 0.0)
                sequencesData = {'path': subSec.readString('path'),
                 'bindNode': subSec.readString('bindNode'),
                 'loopCount': subSec.readInt('loopCount', -1),
                 'duration': seqDurationConfig if seqDurationConfig else sequenceDuration}
                if sequenceID in sequences:
                    LOG_WARNING('Sequence with ID {sequenceID} is already exist'.format(sequenceID=sequenceID))
                sequences[sequenceID] = sequencesData

            return sequences

        owner = _xml.getSubsection(xmlCtx, data, 'owner', False)
        if owner is not None:
            sequences['owner'] = getSequenceData(owner)
        enemy = _xml.getSubsection(xmlCtx, data, 'enemy', False)
        if enemy is not None:
            sequences['enemy'] = getSequenceData(enemy)
        teamMate = _xml.getSubsection(xmlCtx, data, 'teamMate', False)
        if teamMate is not None:
            sequences['teamMate'] = getSequenceData(teamMate)
        return sequences


def _getVisualEffects(xmlCtx, section, sequenceDuration=0):
    effects = {}
    if not IS_CLIENT:
        return effects
    if not section.has_key('visualEffects'):
        return effects
    visualEffectsSection = section['visualEffects']
    effects['sequences'] = _getSequences(xmlCtx, visualEffectsSection, sequenceDuration)
    return effects


def _getHunterVisualEffects(xmlCtx, section):
    effects = {}
    if not section.has_key('hunterVisualEffects'):
        return effects
    hunterVisualEffectsSection = section['hunterVisualEffects']
    for hunter in hunterVisualEffectsSection.values():
        vehName = _xml.readStringOrNone(xmlCtx, hunter, 'vehicle')
        prefab = _xml.readStringOrNone(xmlCtx, hunter, 'prefab')
        effects[vehName] = prefab

    return effects


def _getProcedureEffects(xmlCtx, section):
    procedureEffects = []
    procedureEffectsSection = _xml.getSubsection(xmlCtx, section, 'procedureEffects', False)
    if procedureEffectsSection is None:
        return procedureEffects
    else:
        for effectSection in procedureEffectsSection.values():
            effectPath = effectSection.asString.strip()
            if effectPath:
                procedureEffects.append(effectPath)

        return procedureEffects


class WTChargedShot(Equipment, WTBaseEquipment):
    __slots__ = ('factors', 'moduleDamageFactors', 'shotData')

    def __init__(self):
        super(WTChargedShot, self).__init__()
        self.factors = component_constants.EMPTY_DICT
        self.moduleDamageFactors = component_constants.EMPTY_DICT
        self.shotData = component_constants.EMPTY_DICT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTChargedShot, self)._readConfig(xmlCtx, section)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')
        self.moduleDamageFactors = self.__readModuleDamageFactors(xmlCtx, section)
        if section.has_key('shotData'):
            self.shotData = _readShotData(xmlCtx, section)

    def __readModuleDamageFactors(self, xmlCtx, section):
        res = {}
        subsection = _xml.getSubsection(xmlCtx, section, 'moduleDamageFactors')
        for factor, _ in subsection.items():
            res[factor] = subsection.readFloat(factor)

        return res


class WTExplosiveShot(Equipment, WTBaseEquipment):
    __slots__ = ('damage', 'factors', 'damageRadius', 'arenaPrefab', 'shotData', 'effectsIndex')

    def __init__(self):
        super(WTExplosiveShot, self).__init__()
        self.damage = component_constants.ZERO_INT
        self.factors = component_constants.EMPTY_DICT
        self.damageRadius = component_constants.ZERO_INT
        self.barrelFlashPrefab = component_constants.EMPTY_STRING
        self.barrelFlashPrefabUnloadTimeoutAfterShot = component_constants.ZERO_FLOAT
        self.shotData = component_constants.EMPTY_STRING
        self.effectsIndex = component_constants.ZERO_INT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTExplosiveShot, self)._readConfig(xmlCtx, section)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')
        self.damage = _xml.readInt(xmlCtx, section, 'damage', 0)
        self.damageRadius = section.readInt('damageRadius')
        if IS_CLIENT:
            self.barrelFlashPrefab = _xml.readString(xmlCtx, section, 'barrelFlashPrefab')
            self.barrelFlashPrefabUnloadTimeoutAfterShot = _xml.readFloat(xmlCtx, section, 'barrelFlashPrefabUnloadTimeoutAfterShot')
        if section.has_key('shotData'):
            self.shotData = _readShotData(xmlCtx, section)
        if section.has_key('shotEffect'):
            self.effectsIndex = vehicles.g_cache.shotEffectsIndexes[_xml.readString(xmlCtx, section, 'shotEffect')]


class WTNitro(Equipment, WTBaseEquipment):

    def __init__(self):
        super(WTNitro, self).__init__()
        self.factors = component_constants.EMPTY_DICT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTNitro, self)._readConfig(xmlCtx, section)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')


class WTDamageShield(Equipment, WTBaseEquipment):

    def __init__(self):
        super(WTDamageShield, self).__init__()
        self.factors = component_constants.EMPTY_DICT
        self.durationSeconds = component_constants.ZERO_INT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTDamageShield, self)._readConfig(xmlCtx, section)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')
        self.durationSeconds = section.readInt('durationSeconds')


class WTBarrier(Equipment, WTBaseEquipment):
    __slots__ = ('settingDistance', 'duration', 'staticPrefab', 'components')

    def __init__(self):
        super(WTBarrier, self).__init__()
        self.settingDistance = component_constants.ZERO_FLOAT
        self.duration = component_constants.ZERO_FLOAT
        self.staticPrefab = component_constants.EMPTY_STRING
        self.components = component_constants.EMPTY_DICT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)
        self.rawTags = section.readString('rawTags').split()

    def _readConfig(self, xmlCtx, section):
        super(WTBarrier, self)._readConfig(xmlCtx, section)
        self.settingDistance = section.readFloat('settingDistance')
        self.duration = section.readFloat('duration')
        self.staticPrefab = section.readString('staticPrefab')
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)


class WTImpulseModA(Equipment, WTBaseEquipment):
    __slots__ = ('radius', 'debuffDuration', 'consumeSeconds', 'components', 'reloadTimes')

    def __init__(self):
        super(WTImpulseModA, self).__init__()
        self.radius = component_constants.ZERO_INT
        self.debuffDuration = component_constants.ZERO_INT
        self.consumeSeconds = component_constants.ZERO_INT
        self.components = component_constants.EMPTY_DICT
        self.reloadTimes = component_constants.EMPTY_TUPLE

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTImpulseModA, self)._readConfig(xmlCtx, section)
        self.radius = section.readInt('radius')
        self.debuffDuration = section.readInt('debuffDuration')
        self.consumeSeconds = section.readInt('consumeSeconds')
        self.reloadTimes = tuple(map(int, section.readString('reloadTimes').split(' ')))
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)


class WTVampirism(Equipment, WTBaseEquipment):
    __slots__ = ('partOfDamageToHP',)

    def __init__(self):
        super(WTVampirism, self).__init__()
        self.partOfDamageToHP = component_constants.ZERO_FLOAT

    def _readConfig(self, xmlCtx, section):
        super(WTVampirism, self)._readConfig(xmlCtx, section)
        self.partOfDamageToHP = _xml.readFloat(xmlCtx, section, 'partOfDamageToHP', 0.0)

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTDecreaseReloadTime(Equipment, WTBaseEquipment):

    def __init__(self):
        super(WTDecreaseReloadTime, self).__init__()
        self.components = component_constants.EMPTY_DICT
        self.ignoredReasons = component_constants.EMPTY_DICT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)
        if section.has_key('ignoredReasons'):
            self.ignoredReasons = _xml.readTupleOfStrings(xmlCtx, section, 'ignoredReasons')
        super(WTDecreaseReloadTime, self)._readConfig(xmlCtx, section)


class WTGroupRepair(Equipment, WTBaseEquipment):
    __slots__ = ('healRangeRadius', 'instantHealthRestore', 'tickInterval', 'healAmountPerTick', 'healingAreaDuration', 'hunterEffects')

    def __init__(self):
        super(WTGroupRepair, self).__init__()
        self.healRangeRadius = component_constants.ZERO_INT
        self.instantHealthRestore = component_constants.ZERO_INT
        self.tickInterval = component_constants.ZERO_FLOAT
        self.healAmountPerTick = component_constants.ZERO_INT
        self.healingAreaDuration = component_constants.ZERO_INT
        self.hunterEffects = component_constants.EMPTY_DICT

    def _readConfig(self, xmlCtx, section):
        super(WTGroupRepair, self)._readConfig(xmlCtx, section)
        self.healRangeRadius = _xml.readInt(xmlCtx, section, 'healRangeRadius', 0)
        self.instantHealthRestore = _xml.readInt(xmlCtx, section, 'instantHealthRestore', 0)
        self.tickInterval = _xml.readFloat(xmlCtx, section, 'tickInterval', 0.0)
        self.healAmountPerTick = _xml.readInt(xmlCtx, section, 'healAmountPerTick', 0.0)
        self.healingAreaDuration = _xml.readInt(xmlCtx, section, 'healingAreaDuration', 1)
        self.hunterEffects = _getHunterVisualEffects(xmlCtx, section)

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTMissile(Equipment, WTBaseEquipment):
    __slots__ = ('missilePrefab', 'components')

    def __init__(self):
        super(WTMissile, self).__init__()
        self.missilePrefab = component_constants.EMPTY_STRING

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)
        self.rawTags = section.readString('rawTags').split()

    def _readConfig(self, xmlCtx, section):
        super(WTMissile, self)._readConfig(xmlCtx, section)
        self.missilePrefab = section.readString('missilePrefab')
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)


class WTSmokeScreen(Smoke, WTBaseEquipment):

    def _readConfig(self, xmlCtx, scriptSection):
        super(WTSmokeScreen, self)._readConfig(xmlCtx, scriptSection)
        if self.consumeSeconds is None:
            self.consumeSeconds = 0
        if self.consumeSeconds > 0:
            LOG_WARNING('consumeSeconds was read as %s and reset to 0 for WTSmokeScreen' % self.consumeSeconds)
            self.consumeSeconds = 0
        return

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTPlasmaRetention(Equipment, WTBaseEquipment):

    def __init__(self):
        super(WTPlasmaRetention, self).__init__()
        self.plasmaSavedOnDeath = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(WTPlasmaRetention, self)._readConfig(xmlCtx, section)
        self.plasmaSavedOnDeath = _xml.readInt(xmlCtx, section, 'plasmaSavedOnDeath', 0)

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)


class WTStunAreaModA(Equipment, WTBaseEquipment):
    __slots__ = ('damageRadius', 'effects', 'components', 'debuffDuration')

    def __init__(self):
        super(WTStunAreaModA, self).__init__()
        self.damageRadius = component_constants.ZERO_INT
        self.effects = component_constants.EMPTY_DICT
        self.components = component_constants.EMPTY_DICT
        self.debuffDuration = component_constants.ZERO_INT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTStunAreaModA, self)._readConfig(xmlCtx, section)
        self.damageRadius = section.readInt('damageRadius')
        self.debuffDuration = section.readInt('debuffDuration')
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section, self.debuffDuration)


class WTIncreaseDamage(Equipment, WTBaseEquipment):

    def __init__(self):
        super(WTIncreaseDamage, self).__init__()
        self.components = component_constants.EMPTY_DICT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)
        super(WTIncreaseDamage, self)._readConfig(xmlCtx, section)


class WTExtractorShot(Equipment, WTBaseEquipment):
    __slots__ = ('damageRadius', 'shotData', 'damageMultiplierPerPlasma', 'maxPlasmaTakeFromHunter', 'maxPlasmaCounter', 'debuffDuration', 'components', 'effects')

    def __init__(self):
        super(WTExtractorShot, self).__init__()
        self.damageRadius = component_constants.ZERO_INT
        self.shotData = component_constants.EMPTY_DICT
        self.damageMultiplierPerPlasma = component_constants.ZERO_FLOAT
        self.maxPlasmaTakeFromHunter = component_constants.ZERO_INT
        self.maxPlasmaCounter = component_constants.ZERO_INT
        self.debuffDuration = component_constants.ZERO_INT
        self.components = component_constants.EMPTY_DICT
        self.effects = component_constants.EMPTY_DICT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTExtractorShot, self)._readConfig(xmlCtx, section)
        self.damageRadius = section.readInt('damageRadius')
        self.damageMultiplierPerPlasma = section.readFloat('damageMultiplierPerPlasma')
        self.maxPlasmaTakeFromHunter = section.readInt('maxPlasmaTakeFromHunter')
        self.maxPlasmaCounter = section.readInt('maxPlasmaCounter')
        self.debuffDuration = section.readInt('debuffDuration')
        if section.has_key('components'):
            self.components = _readComponents(xmlCtx, section)
        if section.has_key('shotData'):
            self.shotData = _readShotData(xmlCtx, section)
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section)


class WTExplosiveDamageShield(Equipment, WTBaseEquipment):

    def __init__(self):
        super(WTExplosiveDamageShield, self).__init__()
        self.factors = component_constants.EMPTY_DICT
        self.maxDamage = component_constants.ZERO_INT
        self.explosionDamageFactor = 1.0
        self.effects = component_constants.EMPTY_DICT

    def _readBasicConfig(self, xmlCtx, section):
        Equipment._readBasicConfig(self, xmlCtx, section)
        WTBaseEquipment.readExtraData(self, xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(WTExplosiveDamageShield, self)._readConfig(xmlCtx, section)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')
        self.damageRadius = section.readInt('damageRadius')
        self.maxDamage = section.readInt('maxDamage')
        self.explosionDamageFactor = section.readFloat('explosionDamageFactor')


class WTDome(Equipment, WTBaseEquipment):
    __slots__ = ('receiveDamageFactor', 'objPrefab')

    def __init__(self):
        super(WTDome, self).__init__()
        self.moduleDamageFactor = component_constants.ZERO_FLOAT
        self.receiveDamageFactor = component_constants.ZERO_FLOAT
        self.objPrefab = component_constants.EMPTY_STRING

    def _readConfig(self, xmlCtx, section):
        super(WTDome, self)._readConfig(xmlCtx, section)
        self.receiveDamageFactor = section.readFloat('receiveDamageFactor', 1.0)
        self.moduleDamageFactor = section.readFloat('moduleDamageFactor', 1.0)
        self.objPrefab = section.readString('objPrefab')
