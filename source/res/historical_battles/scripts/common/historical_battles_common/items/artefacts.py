# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/items/artefacts.py
from items import _xml
from items.artefacts import AreaOfEffectEquipment, BuffEquipment, Equipment, VehicleFactorsXmlReader, AttackBomberEquipment, _CommonMinefieldEquipment, ReconConfigReader
from items.components import component_constants
from constants import IS_CLIENT
if IS_CLIENT:
    from helpers.EffectsList import effectsFromSection

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
                 'soundStop': subSec.readString('soundStop'),
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


def getVisualEffects(xmlCtx, section):
    effects = {}
    if not IS_CLIENT:
        return effects
    if not section.has_key('visualEffects'):
        return effects
    visualEffectsSection = section['visualEffects']
    effects['sequences'] = _getSequences(xmlCtx, visualEffectsSection)
    effects['effects'] = _getEffects(xmlCtx, visualEffectsSection)
    return effects


class HBIncendiaryShot(Equipment):
    __slots__ = ('cooldownSeconds', 'soundNotificationActive', 'increaseFactors')

    def __init__(self):
        super(HBIncendiaryShot, self).__init__()
        self.cooldownSeconds = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(HBIncendiaryShot, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readInt(xmlCtx, section, 'cooldownSeconds')
        self.soundNotificationActive = _xml.readString(xmlCtx, section, 'soundNotificationActive')
        self.increaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'increaseFactors')


class HBStunShot(Equipment):
    __slots__ = ('cooldownSeconds', 'soundNotificationActive', 'shellCompactDescr')

    def __init__(self):
        super(HBStunShot, self).__init__()
        self.cooldownSeconds = component_constants.ZERO_INT
        self.soundNotificationActive = None
        self.shellCompactDescr = component_constants.ZERO_INT
        return

    def _readConfig(self, xmlCtx, section):
        super(HBStunShot, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readInt(xmlCtx, section, 'cooldownSeconds')
        self.soundNotificationActive = _xml.readString(xmlCtx, section, 'soundNotificationActive')
        self.shellCompactDescr = _xml.readInt(xmlCtx, section, 'shellCompactDescr')


class DeathZoneEvent(AreaOfEffectEquipment):
    __slots__ = ()

    def readSharedCooldownConsumableConfig(self, xmlCtx, section):
        pass


class HBBuffEquipment(BuffEquipment):
    pass


class _NitroTypes(object):
    NONE = 0
    BATTLE_ROYALE = 1
    GAS = 2
    DIESEL = 3
    EVENT = 4


def _getExhaust(xmlCtx, section):
    exhaust = _NitroTypes.NONE
    data = _xml.getSubsection(xmlCtx, section, 'exhaust', False)
    if data is None:
        return exhaust
    else:
        nitro = data.readString('nitro', 'none').upper()
        exhaust = getattr(_NitroTypes, nitro)
        return exhaust


def getVisualExhaustEffects(xmlCtx, section):
    effects = {}
    if not IS_CLIENT:
        return effects
    if not section.has_key('visualEffects'):
        return effects
    visualEffectsSection = section['visualEffects']
    effects['exhaust'] = _getExhaust(xmlCtx, visualEffectsSection)
    return effects


class HBVehicleNitro(Equipment):
    __slots__ = ('shortDescription', 'longDescription', 'shortFilterAlert', 'longFilterAlert', 'tooltipIdentifiers', 'soundNotification', 'soundNotificationActive', 'activationWWSoundFeedback', 'deactivationWWSoundFeedback', 'effects', 'factors', 'cooldownSeconds', 'durationSeconds', 'activeSeconds', 'reuseCount')

    def __init__(self):
        super(HBVehicleNitro, self).__init__()
        self.shortDescription = component_constants.EMPTY_STRING
        self.longDescription = component_constants.EMPTY_STRING
        self.shortFilterAlert = component_constants.EMPTY_STRING
        self.longFilterAlert = component_constants.EMPTY_STRING
        self.tooltipIdentifiers = []
        self.activationWWSoundFeedback = None
        self.deactivationWWSoundFeedback = None
        self.soundNotificationActive = None
        self.effects = {}
        self.factors = {}
        self.cooldownSeconds = 0.0
        self.durationSeconds = 0.0
        self.activeSeconds = 0.0
        self.reuseCount = component_constants.ZERO_INT
        return

    def isActivatable(self):
        return self.activeSeconds > 0.0

    def _readBasicConfig(self, xmlCtx, section):
        super(HBVehicleNitro, self)._readBasicConfig(xmlCtx, section)
        self.__readSounds(xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(HBVehicleNitro, self)._readConfig(xmlCtx, section)
        self.__readTooltipInformation(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownSeconds', 0.0)
        self.durationSeconds = _xml.readFloat(xmlCtx, section, 'durationSeconds', 0.0)
        self.activeSeconds = self.durationSeconds
        self.reuseCount = _xml.readInt(xmlCtx, section, 'reuseCount')
        self.effects = getVisualExhaustEffects(xmlCtx, section)
        self.factors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'factors')

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


class HBHealPoint(Equipment):
    __slots__ = ('shortDescription', 'longDescription', 'shortFilterAlert', 'longFilterAlert', 'tooltipIdentifiers', 'activationWWSoundFeedback', 'deactivationWWSoundFeedback', 'soundNotificationActive', 'cooldownSeconds', 'durationSeconds', 'reuseCount', 'radius', 'healPercent', 'effects')

    def __init__(self):
        super(HBHealPoint, self).__init__()
        self.shortDescription = component_constants.EMPTY_STRING
        self.longDescription = component_constants.EMPTY_STRING
        self.shortFilterAlert = component_constants.EMPTY_STRING
        self.longFilterAlert = component_constants.EMPTY_STRING
        self.tooltipIdentifiers = []
        self.activationWWSoundFeedback = None
        self.deactivationWWSoundFeedback = None
        self.cooldownSeconds = 0.0
        self.durationSeconds = 0.0
        self.reuseCount = component_constants.ZERO_INT
        self.radius = 0
        self.healPercent = 0
        self.effects = {}
        return

    def isActivatable(self):
        return self.activeSeconds > 0.0

    def _readBasicConfig(self, xmlCtx, section):
        super(HBHealPoint, self)._readBasicConfig(xmlCtx, section)
        self.__readSounds(xmlCtx, section)

    def _readConfig(self, xmlCtx, section):
        super(HBHealPoint, self)._readConfig(xmlCtx, section)
        self.__readTooltipInformation(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownSeconds', 0.0)
        self.durationSeconds = _xml.readFloat(xmlCtx, section, 'durationSeconds', 0.0)
        self.reuseCount = _xml.readInt(xmlCtx, section, 'reuseCount')
        self.radius = _xml.readFloat(xmlCtx, section, 'radius', 0.0)
        self.healPercent = _xml.readFloat(xmlCtx, section, 'healPercent', 0)
        self.effects = getVisualEffects(xmlCtx, section)

    def __readSounds(self, xmlCtx, section):
        self.activationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'activationWWSoundFeedback')
        self.deactivationWWSoundFeedback = _xml.readStringOrNone(xmlCtx, section, 'deactivationWWSoundFeedback')
        self.soundNotificationActive = _xml.readStringOrNone(xmlCtx, section, 'soundNotificationActive')
        self.soundNotification = _xml.readStringOrNone(xmlCtx, section, 'soundNotification')

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


class HBAvatarArtilleryStrike(AreaOfEffectEquipment):
    __slots__ = ('cooldownSeconds',)

    def _readConfig(self, xmlCtx, section):
        super(HBAvatarArtilleryStrike, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownTime', 0.0)


class HBAvatarArtilleryMortar(AreaOfEffectEquipment):
    __slots__ = ('cooldownSeconds',)

    def _readConfig(self, xmlCtx, section):
        super(HBAvatarArtilleryMortar, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownTime', 0.0)


class HBAvatarBomber(AreaOfEffectEquipment):
    __slots__ = ('cooldownSeconds',)

    def _readConfig(self, xmlCtx, section):
        super(HBAvatarBomber, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownTime', 0.0)


class HBAvatarAttackPlane(AttackBomberEquipment):
    __slots__ = ('cooldownSeconds',)

    def _readConfig(self, xmlCtx, section):
        super(HBAvatarAttackPlane, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownTime', 0.0)


class HBAvatarArtilleryRocket(AreaOfEffectEquipment):
    __slots__ = ('cooldownSeconds',)

    def _readConfig(self, xmlCtx, section):
        super(HBAvatarArtilleryRocket, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownTime', 0.0)


class HBMinefield(_CommonMinefieldEquipment):
    __slots__ = ('cooldownSeconds', 'markerLifetime', 'minesType', 'projectileHitRadius', 'delay', 'duration', 'wwsoundEquipmentUsed')

    def __init__(self):
        super(HBMinefield, self).__init__()
        self.markerLifetime = component_constants.ZERO_INT
        self.minesType = None
        self.projectileHitRadius = component_constants.ZERO_INT
        self.delay = component_constants.ZERO_INT
        self.duration = component_constants.ZERO_INT
        return

    def _readConfig(self, xmlCtx, section):
        super(HBMinefield, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = self.sharedCooldownTime
        self.minesType = _xml.readString(xmlCtx, section, 'minesType')
        self.projectileHitRadius = _xml.readInt(xmlCtx, section, 'projectileHitRadius')
        self.delay = self.mineParams.activationDelay
        self.wwsoundEquipmentUsed = _xml.readString(xmlCtx, section, 'wwsoundEquipmentUsed')
        self.duration = self.mineParams.lifetime
        self.markerLifetime = self.mineParams.lifetime


class HBReconPlane(AreaOfEffectEquipment, ReconConfigReader):
    __slots__ = ('cooldownSeconds',) + ReconConfigReader._RECON_SLOTS

    def __init__(self):
        super(HBReconPlane, self).__init__()
        self.initReconSlots()

    def _readConfig(self, xmlCtx, section):
        super(HBReconPlane, self)._readConfig(xmlCtx, section)
        self.readReconConfig(xmlCtx, section)
        self.cooldownSeconds = _xml.readFloat(xmlCtx, section, 'cooldownTime', 0.0)


class HBLastStand(Equipment):
    __slots__ = ('destructionDelaySec', 'reloadTime', 'piercingPower', 'effectDuration', 'effectPrefabPath', 'soundNotificationNPC')

    def _readBasicConfig(self, xmlCtx, section):
        super(HBLastStand, self)._readBasicConfig(xmlCtx, section)
        self.soundNotificationNPC = _xml.readString(xmlCtx, section, 'soundNotificationNPC')

    def _readConfig(self, xmlCtx, scriptSection):
        self.destructionDelaySec = _xml.readInt(xmlCtx, scriptSection, 'destructionDelaySec')
        self.reloadTime = _xml.readFloat(xmlCtx, scriptSection, 'reloadTime')
        self.piercingPower = _xml.readInt(xmlCtx, scriptSection, 'piercingPower')
        self.effectDuration = _xml.readInt(xmlCtx, scriptSection, 'effectDuration')
        self.effectPrefabPath = _xml.readString(xmlCtx, scriptSection, 'effectPrefabPath')


class HBBerserk(Equipment):
    __slots__ = ('config',)

    def _readConfig(self, xmlCtx, scriptSection):
        self.config = []
        for valueSection in scriptSection['config'].values():
            healthPercentage = _xml.readFloat(xmlCtx, valueSection, 'healthPercentage')
            reloadModifier = _xml.readFloat(xmlCtx, valueSection, 'reloadModifier')
            aimingModifier = _xml.readFloat(xmlCtx, valueSection, 'aimingModifier')
            self.config.append((healthPercentage, {'reloadModifier': reloadModifier,
              'aimingModifier': aimingModifier}))

        self.config.sort(key=lambda x: x[0])


class HBAmbushFire(Equipment):
    __slots__ = ('activateWhenStillSec', 'reloadTimeFactor', 'aimingTimeFactor', 'shotDispersionRadiusFactor')

    def _readConfig(self, xmlCtx, scriptSection):
        self.activateWhenStillSec = _xml.readInt(xmlCtx, scriptSection, 'activateWhenStillSec')
        self.reloadTimeFactor = _xml.readFloat(xmlCtx, scriptSection, 'reloadTimeFactor')
        self.aimingTimeFactor = _xml.readFloat(xmlCtx, scriptSection, 'aimingTimeFactor')
        self.shotDispersionRadiusFactor = _xml.readFloat(xmlCtx, scriptSection, 'shotDispersionRadiusFactor')


class HBArtilleryOnYourself(HBAvatarArtilleryMortar):
    __slots__ = ('preparingTime', 'preparingAreaVisual', 'wwsoundEquipmentUsedNPC')

    def _readConfig(self, xmlCtx, scriptSection):
        super(HBArtilleryOnYourself, self)._readConfig(xmlCtx, scriptSection)
        self.preparingTime = _xml.readFloat(xmlCtx, scriptSection, 'preparingTime')
        self.preparingAreaVisual = _xml.readString(xmlCtx, scriptSection, 'preparingAreaVisual')
        self.wwsoundEquipmentUsedNPC = _xml.readString(xmlCtx, scriptSection, 'wwsoundEquipmentUsedNPC')
