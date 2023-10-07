# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/common/halloween_common/items/hw_artefacts.py
from items.artefacts import Equipment, VehicleFactorsXmlReader
from items.components import component_constants
from soft_exception import SoftException
from constants import IS_CLIENT
from items import _xml
if IS_CLIENT:
    from helpers.EffectsList import effectsFromSection

class _NitroTypes(object):
    NONE = 0
    BATTLE_ROYALE = 1
    GAS = 2
    DIESEL = 3
    EVENT = 4


def _getSequences(xmlCtx, section):
    sequences = {}
    data = _xml.getSubsection(xmlCtx, section, 'sequences', False)
    if data is None:
        return sequences
    else:

        def getSequenceData(xmlCtx, section):
            sequences = []
            for _, subSec in section.items():
                sequencesData = {'path': subSec.readString('path'),
                 'path_fwd': subSec.readString('path_fwd'),
                 'bindNode': subSec.readString('bindNode'),
                 'duration': subSec.readFloat('duration'),
                 'loopCount': subSec.readInt('loopCount', -1),
                 'soundStart': subSec.readString('soundStart'),
                 'bindOnGameObject': subSec.readBool('bindOnGameObject', False)}
                sequences.append(sequencesData)

            return sequences

        owner = _xml.getSubsection(xmlCtx, data, 'owner', False)
        if owner is not None:
            sequences['owner'] = getSequenceData(xmlCtx, owner)
        enemy = _xml.getSubsection(xmlCtx, data, 'enemy', False)
        if enemy is not None:
            sequences['enemy'] = getSequenceData(xmlCtx, enemy)
        teamMate = _xml.getSubsection(xmlCtx, data, 'teamMate', False)
        if teamMate is not None:
            sequences['teamMate'] = getSequenceData(xmlCtx, teamMate)
        return sequences


def _getEffects(xmlCtx, section):

    def _getEffectSection(section):
        return _xml.getSubsection(xmlCtx, section, 'effect', False)

    effects = {}
    data = _xml.getSubsection(xmlCtx, section, 'effects', False)
    if data is None:
        return effects
    else:
        owner = _xml.getSubsection(xmlCtx, data, 'owner', False)
        if owner is not None:
            effects['owner'] = effectsFromSection(_getEffectSection(owner))
            effects['owner_soundStart'] = _xml.readStringOrEmpty(xmlCtx, owner, 'soundStart')
        enemy = _xml.getSubsection(xmlCtx, data, 'enemy', False)
        if enemy is not None:
            effects['enemy'] = effectsFromSection(_getEffectSection(enemy))
            effects['enemy_soundStart'] = _xml.readStringOrEmpty(xmlCtx, enemy, 'soundStart')
        teamMate = _xml.getSubsection(xmlCtx, data, 'teamMate', False)
        if teamMate is not None:
            effects['teamMate'] = effectsFromSection(_getEffectSection(teamMate))
            effects['teamMate_soundStart'] = _xml.readStringOrEmpty(xmlCtx, teamMate, 'soundStart')
        return effects


def _getExhaust(xmlCtx, section):
    exhaust = _NitroTypes.NONE
    data = _xml.getSubsection(xmlCtx, section, 'exhaust', False)
    if data is None:
        return exhaust
    else:
        nitro = data.readString('nitro', 'none').upper()
        exhaust = getattr(_NitroTypes, nitro)
        return exhaust


def getVisualEffects(xmlCtx, section):
    effects = {}
    if not IS_CLIENT:
        return effects
    if not section.has_key('visualEffects'):
        return effects
    visualEffectsSection = section['visualEffects']
    effects['sequences'] = _getSequences(xmlCtx, visualEffectsSection)
    effects['effects'] = _getEffects(xmlCtx, visualEffectsSection)
    effects['exhaust'] = _getExhaust(xmlCtx, visualEffectsSection)
    return effects


class EventEquipment(Equipment):
    __slots__ = ('durationSeconds', 'cooldownSeconds', 'reuseCount', 'activationWWSoundFeedback', 'deactivationWWSoundFeedback', 'soundNotificationActive', 'isHeroic', 'isReward')

    def __init__(self):
        super(EventEquipment, self).__init__()
        self.durationSeconds = component_constants.ZERO_FLOAT
        self.cooldownSeconds = component_constants.ZERO_FLOAT
        self.reuseCount = component_constants.ZERO_INT
        self.activationWWSoundFeedback = None
        self.deactivationWWSoundFeedback = None
        self.soundNotificationActive = None
        self.isHeroic = False
        self.isReward = False
        return

    def _readBasicConfig(self, xmlCtx, section):
        super(EventEquipment, self)._readBasicConfig(xmlCtx, section)
        self.activationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'activationWWSoundFeedback')
        self.deactivationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'deactivationWWSoundFeedback')
        self.soundNotificationActive = _xml.readStringOrNone(xmlCtx, section, 'soundNotificationActive')

    def _readConfig(self, xmlCtx, section):
        super(EventEquipment, self)._readConfig(xmlCtx, section)
        try:
            self.durationSeconds = _xml.readFloat(xmlCtx, section, 'durationSeconds')
            self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownSeconds')
            self.reuseCount = _xml.readInt(xmlCtx, section, 'reuseCount')
        except SoftException:
            pass


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
        buffNames = _xml.readStringOrEmpty(xmlCtx, section, subsectionName).split()
        return frozenset(buffNames)


class HpRepairAndCrewHealEquipment(BuffEquipment):
    __slots__ = ('isInterruptable',)

    def __init__(self):
        super(HpRepairAndCrewHealEquipment, self).__init__()
        self.isInterruptable = False

    def _readConfig(self, xmlCtx, section):
        super(HpRepairAndCrewHealEquipment, self)._readConfig(xmlCtx, section)
        self.isInterruptable = _xml.readBool(xmlCtx, section, 'isInterruptable')


class HWArtefact(Equipment):
    __slots__ = ('shortDescription', 'longDescription', 'shortFilterAlert', 'longFilterAlert', 'tooltipIdentifiers', 'soundNotification', 'soundNotificationActive', 'activationWWSoundFeedback', 'deactivationWWSoundFeedback', 'isHeroic', 'isReward', 'hasBoost', 'defaultParams', 'boostParams', 'effects', 'cooldownSeconds', 'durationSeconds', 'activeSeconds', 'reuseCount')

    def __init__(self):
        super(HWArtefact, self).__init__()
        self.shortDescription = component_constants.EMPTY_STRING
        self.longDescription = component_constants.EMPTY_STRING
        self.shortFilterAlert = component_constants.EMPTY_STRING
        self.longFilterAlert = component_constants.EMPTY_STRING
        self.tooltipIdentifiers = []
        self.activationWWSoundFeedback = None
        self.deactivationWWSoundFeedback = None
        self.soundNotificationActive = None
        self.isHeroic = False
        self.isReward = False
        self.hasBoost = False
        self.defaultParams = {}
        self.boostParams = {}
        self.effects = {}
        self.cooldownSeconds = 0.0
        self.durationSeconds = 0.0
        self.activeSeconds = 0.0
        self.reuseCount = component_constants.ZERO_INT
        return

    def isActivatable(self):
        return self.activeSeconds > 0.0

    def _readBasicConfig(self, xmlCtx, section):
        super(HWArtefact, self)._readBasicConfig(xmlCtx, section)
        self.__readSounds(xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(HWArtefact, self)._readConfig(xmlCtx, section)
        self.__readTooltipInformation(xmlCtx, section)
        self.isHeroic = _xml.readBool(xmlCtx, section, 'isHeroic', False)
        self.isReward = _xml.readBool(xmlCtx, section, 'isReward', False)
        self.hasBoost = section.has_key('boostParams')
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownSeconds', 0.0)
        self.durationSeconds = _xml.readFloat(xmlCtx, section, 'durationSeconds', 0.0)
        self.activeSeconds = self.durationSeconds
        self.reuseCount = _xml.readInt(xmlCtx, section, 'reuseCount')
        self.defaultParams = self._getParams(xmlCtx, section, 'defaultParams')
        if self.hasBoost:
            self.boostParams = self._getParams(xmlCtx, section, 'boostParams')
            if section['boostParams'].has_key('visualEffects'):
                self.boostParams['effects'] = getVisualEffects(xmlCtx, section['boostParams'])
        self.effects = getVisualEffects(xmlCtx, section)

    def _getParams(self, xmlCtx, section, key):
        return {}

    def _readFactors(self, xmlCtx, params, key):
        res = {}
        subsection = _xml.getSubsection(xmlCtx, params, key)
        for factor, _ in subsection.items():
            res[factor] = subsection.readFloat(factor)

        return res

    def __readSounds(self, xmlCtx, section):
        self.soundNotification = _xml.readStringOrNone(xmlCtx, section, 'soundNotification')
        self.soundNotificationActive = _xml.readStringOrNone(xmlCtx, section, 'soundNotificationActive')
        self.activationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'activationWWSoundFeedback')
        self.deactivationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'deactivationWWSoundFeedback')

    def __readTooltipInformation(self, xmlCtx, section):
        if IS_CLIENT:
            self.shortDescription = _xml.readString(xmlCtx, section, 'shortDescription')
            self.longDescription = _xml.readString(xmlCtx, section, 'longDescription')
            self.shortFilterAlert = _xml.readStringOrEmpty(xmlCtx, section, 'shortFilterAlert')
            self.longFilterAlert = _xml.readStringOrEmpty(xmlCtx, section, 'longFilterAlert')
            tooltipsString = _xml.readStringOrNone(xmlCtx, section, 'tooltips')
            if tooltipsString is not None:
                self.tooltipIdentifiers = tooltipsString.split()
        return


class HWVehicleCurseArrow(HWArtefact):
    __slots__ = ()

    def _getParams(self, xmlCtx, section, key):
        res = {}
        params = section[key]
        res['shotCount'] = params.readInt('shotCount')
        key = 'moduleDamageFactors'
        res[key] = {}
        if params.has_key(key):
            res[key] = self._readFactors(xmlCtx, params, key)
        return res


class HWVehicleFireArrow(HWArtefact):
    __slots__ = ()

    def _getParams(self, xmlCtx, section, key):
        res = {}
        params = section[key]
        res['shotCount'] = params.readInt('shotCount')
        return res


class HWVehicleFrozenArrow(HWArtefact):
    __slots__ = ()

    def _getParams(self, xmlCtx, section, key):
        res = {}
        params = section[key]
        res['shotCount'] = params.readInt('shotCount')
        res['debuffDuration'] = params.readInt('debuffDuration')
        key = 'debuffFactors'
        res[key] = VehicleFactorsXmlReader.readFactors(xmlCtx, params, 'debuffFactors')
        return res


class HWVehicleHealingArrow(HWArtefact):
    __slots__ = ()

    def _getParams(self, xmlCtx, section, key):
        res = {}
        params = section[key]
        res['shotCount'] = params.readInt('shotCount')
        res['enemyLockActivableAbilityDuration'] = params.readFloat('enemyLockActivableAbilityDuration')
        res['percentOfRestoreHealth'] = params.readFloat('percentOfRestoreHealth')
        return res


class HWVehicleLaughArrow(HWArtefact):
    __slots__ = ()

    def _getParams(self, xmlCtx, section, key):
        res = {}
        params = section[key]
        res['shotCount'] = params.readInt('shotCount')
        res['effectDuration'] = params.readFloat('effectDuration')
        res['wheeled'] = VehicleFactorsXmlReader.readFactors(xmlCtx, params['increaseFactors'], 'wheeled')
        res['tracked'] = VehicleFactorsXmlReader.readFactors(xmlCtx, params['increaseFactors'], 'tracked')
        return res


class HWVehicleLifeStealArrow(HWArtefact):
    __slots__ = ()

    def _getParams(self, xmlCtx, section, key):
        res = {}
        params = section[key]
        res['shotCount'] = params.readInt('shotCount')
        res['hpRestored'] = params.readFloat('hpRestored')
        return res


class HWVehicleNitro(HWArtefact):
    __slots__ = ('buffs',)

    def __init__(self):
        super(HWVehicleNitro, self).__init__()
        self.buffs = {}

    def _readConfig(self, xmlCtx, section):
        super(HWVehicleNitro, self)._readConfig(xmlCtx, section)
        self.buffs = self._readBuffs(xmlCtx, section, 'buffs')

    def _readBuffs(self, xmlCtx, section, key):
        res = {}
        if section.has_key(key):
            subsection = _xml.getSubsection(xmlCtx, section, key)
            for itemName, _ in subsection.items():
                res[itemName] = VehicleFactorsXmlReader.readFactors(xmlCtx, subsection[itemName], 'factors')

        return res


class HWVehiclePassiveHealing(HWArtefact):
    __slots__ = ('healthRegenPerTick', 'tickInterval')

    def __init__(self):
        super(HWVehiclePassiveHealing, self).__init__()
        self.healthRegenPerTick = 0.0
        self.tickInterval = 0.0

    def _readConfig(self, xmlCtx, section):
        super(HWVehiclePassiveHealing, self)._readConfig(xmlCtx, section)
        self.healthRegenPerTick = _xml.readFloat(xmlCtx, section, 'healthRegenPerTick', 0.0)
        self.tickInterval = _xml.readFloat(xmlCtx, section, 'tickInterval', 0.0)


class HWVehicleFrozenMantle(HWArtefact):
    __slots__ = ('radius', 'decreaseFactors')

    def __init__(self):
        super(HWVehicleFrozenMantle, self).__init__()
        self.radius = 0
        self.decreaseFactors = {}

    def _readConfig(self, xmlCtx, section):
        super(HWVehicleFrozenMantle, self)._readConfig(xmlCtx, section)
        self.radius = _xml.readInt(xmlCtx, section, 'radius', 0)
        self.decreaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'decreaseFactors')


class HWVehicleDamageShield(HWArtefact):
    __slots__ = ('factors', 'respawnDurationSeconds', 'baseEffects', 'respawnEffects')

    def __init__(self):
        super(HWVehicleDamageShield, self).__init__()
        self.factors = {}
        self.respawnDurationSeconds = 0
        self.baseEffects = {}
        self.respawnEffects = {}

    def _readConfig(self, xmlCtx, section):
        super(HWVehicleDamageShield, self)._readConfig(xmlCtx, section)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')
        self.respawnDurationSeconds = _xml.readFloat(xmlCtx, section, 'respawnDurationSeconds')
        baseEffectsSection = _xml.getSubsection(xmlCtx, section, 'baseVisualEffects', False)
        if baseEffectsSection is not None:
            self.baseEffects = getVisualEffects(xmlCtx, baseEffectsSection)
        respawnEffectsSection = _xml.getSubsection(xmlCtx, section, 'respawnVisualEffects', False)
        if respawnEffectsSection is not None:
            self.respawnEffects = getVisualEffects(xmlCtx, respawnEffectsSection)
        return


class HWRepairAndHealExtra(HWArtefact):
    __slots__ = ('restoreHpPercent',)

    def __init__(self):
        super(HWRepairAndHealExtra, self).__init__()
        self.restoreHpPercent = 0

    def _readConfig(self, xmlCtx, section):
        super(HWRepairAndHealExtra, self)._readConfig(xmlCtx, section)
        self.restoreHpPercent = _xml.readFloat(xmlCtx, section, 'restoreHpPercent')
