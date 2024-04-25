# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: historical_battles/scripts/common/historical_battles_common/items/artefacts.py
from soft_exception import SoftException
from items import _xml
from items.artefacts import AreaOfEffectEquipment, FrontLineMinefield, BuffEquipment
from items.components import component_constants
from items.artefacts import Equipment, VehicleFactorsXmlReader
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


class ReusableFiniteEquipment(Equipment):
    __slots__ = ('durationSeconds', 'cooldownSeconds', 'reuseCount')

    def __init__(self):
        super(ReusableFiniteEquipment, self).__init__()
        self.durationSeconds = component_constants.ZERO_INT
        self.cooldownSeconds = component_constants.ZERO_INT
        self.reuseCount = component_constants.ZERO_INT

    def _readConfig(self, xmlCtx, section):
        super(ReusableFiniteEquipment, self)._readConfig(xmlCtx, section)
        try:
            self.durationSeconds = _xml.readInt(xmlCtx, section, 'durationSeconds')
            self.cooldownSeconds = _xml.readInt(xmlCtx, section, 'cooldownSeconds')
            self.reuseCount = _xml.readInt(xmlCtx, section, 'reuseCount')
        except SoftException:
            pass


class SuperShell(ReusableFiniteEquipment):
    __slots__ = ('shotComponents', 'soundNotificationActive')

    def __init__(self):
        super(SuperShell, self).__init__()
        self.shotComponents = {}

    def _readConfig(self, xmlCtx, section):
        super(SuperShell, self)._readConfig(xmlCtx, section)
        self.soundNotificationActive = _xml.readString(xmlCtx, section, 'soundNotificationActive')
        subXmlCtx, subsection = _xml.getSubSectionWithContext(xmlCtx, section, 'shotComponents')
        for compKey, _ in _xml.getItemsWithContext(subXmlCtx, subsection):
            self.shotComponents[compKey] = _xml.readString(subXmlCtx, subsection, compKey)


class DeathZoneEvent(AreaOfEffectEquipment):
    __slots__ = ()

    def readSharedCooldownConsumableConfig(self, xmlCtx, section):
        pass


class HBMinefield(FrontLineMinefield):
    __slots__ = ('markerLifetime', 'minesType', 'projectileHitRadius')

    def __init__(self):
        super(HBMinefield, self).__init__()
        self.markerLifetime = component_constants.ZERO_INT
        self.minesType = None
        self.projectileHitRadius = component_constants.ZERO_INT
        return

    def _readConfig(self, xmlCtx, section):
        super(HBMinefield, self)._readConfig(xmlCtx, section)
        self.markerLifetime = _xml.readInt(xmlCtx, section, 'markerLifetime')
        self.minesType = _xml.readString(xmlCtx, section, 'minesType')
        self.projectileHitRadius = _xml.readInt(xmlCtx, section, 'projectileHitRadius')


class HBBuffEquipment(BuffEquipment):
    pass


class AoeArcadeTeamRepairKit(AreaOfEffectEquipment):
    __slots__ = ('amount', 'activationEffect', 'healEffect', 'durationSeconds')

    def __init__(self):
        super(AoeArcadeTeamRepairKit, self).__init__()
        self.amount = component_constants.ZERO_INT
        self.activationEffect = None
        self.healEffect = None
        self.durationSeconds = component_constants.ZERO_INT
        return

    def _readConfig(self, xmlCtx, section):
        super(AoeArcadeTeamRepairKit, self)._readConfig(xmlCtx, section)
        self.amount = _xml.readInt(xmlCtx, section, 'amount')
        self.activationEffect = _xml.readString(xmlCtx, section, 'activationEffect')
        self.healEffect = _xml.readString(xmlCtx, section, 'healEffect')
        self.durationSeconds = _xml.readInt(xmlCtx, section, 'durationSeconds')


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
    __slots__ = ('shortDescription', 'longDescription', 'shortFilterAlert', 'longFilterAlert', 'tooltipIdentifiers', 'activationWWSoundFeedback', 'deactivationWWSoundFeedback', 'soundNotificationActive', 'cooldownSeconds', 'durationSeconds', 'reuseCount', 'radius', 'healAmmount', 'effects')

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
        self.healAmmount = 0
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
        self.healAmmount = _xml.readInt(xmlCtx, section, 'healAmmount', 0)
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
