# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: white_tiger/scripts/common/white_tiger_common/wt_artefacts.py
from items import _xml
from items.artefacts import Equipment, VisualScriptEquipment, VehicleFactorsXmlReader
from items.components import component_constants
from constants import IS_CLIENT
from debug_utils import LOG_WARNING

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


class WTInstantStunShoot(VisualScriptEquipment):
    __slots__ = ('effects',)

    def __init__(self):
        super(WTInstantStunShoot, self).__init__()
        self.effects = component_constants.EMPTY_DICT

    def _readConfig(self, xmlCtx, section):
        super(WTInstantStunShoot, self)._readConfig(xmlCtx, section)
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section)


class WTUnionStrength(Equipment):
    __slots__ = ('effectDuration', 'receiveDamageFactor', 'effects')

    def __init__(self):
        super(WTUnionStrength, self).__init__()
        self.effectDuration = component_constants.ZERO_INT
        self.receiveDamageFactor = component_constants.ZERO_FLOAT
        self.effects = component_constants.EMPTY_DICT

    def _readConfig(self, xmlCtx, section):
        super(WTUnionStrength, self)._readConfig(xmlCtx, section)
        self.effectDuration = _xml.readInt(xmlCtx, section, 'effectDuration', 0)
        self.receiveDamageFactor = _xml.readFloat(xmlCtx, section, 'receiveDamageFactor', 1.0)
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section, self.effectDuration)


class WTPlasmaExtractor(VisualScriptEquipment):
    __slots__ = ('effects',)

    def __init__(self):
        super(WTPlasmaExtractor, self).__init__()
        self.effects = component_constants.EMPTY_DICT

    def _readConfig(self, xmlCtx, section):
        super(WTPlasmaExtractor, self)._readConfig(xmlCtx, section)
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section)
        self._exportSlotsToVSE()


class WTStunArea(VisualScriptEquipment):
    __slots__ = ('damage', 'decreaseFactors', 'effectDuration', 'effectRadius', 'effects')

    def __init__(self):
        super(WTStunArea, self).__init__()
        self.damage = component_constants.ZERO_INT
        self.decreaseFactors = component_constants.EMPTY_DICT
        self.effectDuration = component_constants.ZERO_INT
        self.effectRadius = component_constants.ZERO_INT
        self.effects = component_constants.EMPTY_DICT

    def _readConfig(self, xmlCtx, section):
        super(WTStunArea, self)._readConfig(xmlCtx, section)
        self.damage = _xml.readInt(xmlCtx, section, 'damage', 0)
        self.decreaseFactors = VehicleFactorsXmlReader.readFactors(xmlCtx, section, 'decreaseFactors')
        self.effectDuration = section.readInt('effectDuration')
        self.effectRadius = section.readInt('effectRadius')
        self.cooldownSeconds = section.readFloat('cooldownSeconds')
        if IS_CLIENT:
            self.effects = _getVisualEffects(xmlCtx, section, self.effectDuration)
        self._exportSlotsToVSE()
