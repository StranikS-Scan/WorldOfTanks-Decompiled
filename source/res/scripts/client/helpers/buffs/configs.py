# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/buffs/configs.py
import re
import json
from buffs_common import BUFFS_CONFIG_FILE
from helpers.EffectsList import effectsFromSection
from helpers.i18n import encodeUtf8
from vehicle_systems.components.terrain_circle_component import readTerrainCircleSettings
from constants import BuffComponentVisibilityMode, EventStorageModifiers

class ClientBuffComponentConfig(object):
    __slots__ = ('visibleTo',)

    def __init__(self, section):
        visibleTo = section.readString('visibleTo', 'all').upper()
        self.visibleTo = getattr(BuffComponentVisibilityMode, visibleTo)


class EffectBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('effectData',)

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.effectData = effectsFromSection(section)


class SoundBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('wwsoundOnStart', 'wwsoundOnStop', 'notificationOnStart', 'notificationOnStop')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.wwsoundOnStart = section.readString('wwsoundOnStart', '')
        self.wwsoundOnStop = section.readString('wwsoundOnStop', '')
        self.notificationOnStart = section.readString('notificationOnStart', '')
        self.notificationOnStop = section.readString('notificationOnStop', '')


class ModelBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('model', 'node', 'offset', 'scale')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.model = section.readString('model')
        self.node = section.readString('node')
        self.offset = section.readVector3('offset')
        self.scale = section.readVector3('scale')


class IconBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('iconName', 'tooltipTextTag')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.visibleTo = BuffComponentVisibilityMode.SELF
        self.iconName = section.readString('name')
        self.tooltipTextTag = section.readString('tooltipTextTag')


class TerrainCircleBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('radius', 'settings')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.radius = section.readFloat('radius')
        self.settings = readTerrainCircleSettings(section, (None, BUFFS_CONFIG_FILE), 'settings')
        return


class LaserBeamBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('beamModel', 'beamModelFwd', 'beamLength', 'bindNode')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.beamModel = section.readString('beamModel')
        self.beamModelFwd = section.readString('beamModelFwd')
        self.beamLength = section.readFloat('beamLength')
        self.bindNode = section.readString('bindNode')


class SequenceBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('sequence', 'duration', 'bindNode', 'hideInSniperModeFor')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.sequence = section.readString('sequence')
        self.duration = section.readFloat('duration')
        self.bindNode = section.readString('bindNode')
        hideInSniperModeFor = section.readString('hideInSniperModeFor', 'none').upper()
        self.hideInSniperModeFor = getattr(BuffComponentVisibilityMode, hideInSniperModeFor)


class ExhaustBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('nitro',)

    class NitroTypes(object):
        NONE = 0
        BATTLE_ROYALE = 1
        GAS = 2
        DIESEL = 3

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        nitro = section.readString('nitro', 'none').upper()
        self.nitro = getattr(self.NitroTypes, nitro)


class RibbonBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('buffName',)

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.visibleTo = BuffComponentVisibilityMode.SELF
        self.buffName = section.readString('buffName', 'none')


class StorageDataModifierComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('storageKey', 'data')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.storageKey = EventStorageModifiers[section.readString('storageKey', '')].value
        data = re.sub('[\\n\\r\\t\\s]*', '', section.readString('data', ''))
        self.data = json.loads(data, object_hook=lambda data: dict((map(encodeUtf8, pair) for pair in data.items())))
