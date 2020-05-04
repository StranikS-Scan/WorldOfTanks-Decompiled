# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/helpers/buffs/factories.py
from buffs_common import BuffFactory, BuffComponentFactory, BUFFS_CONFIG_FILE
from helpers.EffectsList import effectsFromSection
from helpers.buffs import ClientBuff, ClientBuffComponent
from helpers.buffs.components import EffectBuffComponent, ModelBuffComponent, IconBuffComponent, DecalBuffComponent, TerrainCircleBuffComponent, SequenceBuffComponent, InvulnerabilityBuffComponent, ExhaustBuffComponent, SoundBuffComponent
from vehicle_systems.components.terrain_circle_component import readTerrainCircleSettings

class ClientBuffFactory(BuffFactory):

    @property
    def _buffClass(self):
        return ClientBuff

    @property
    def _xmlFactories(self):
        return {'sound': SoundBuffComponentFactory,
         'effect': EffectBuffComponentFactory,
         'model': ModelBuffComponentFactory,
         'icon': IconBuffComponentFactory,
         'decal': DecalBuffComponentFactory,
         'terrainCircle': TerrainCircleBuffComponentFactory,
         'sequence': SequenceBuffComponentFactory,
         'invulnerability': InvulnerabilityBuffComponentFactory,
         'exhaust': ExhaustBuffComponentFactory}

    @property
    def _component(self):
        pass


class ClientBuffComponentFactory(BuffComponentFactory):

    class Config(object):
        __slots__ = ('visibleTo',)

        def __init__(self, section):
            visibleTo = section.readString('visibleTo', 'all').upper()
            self.visibleTo = getattr(ClientBuffComponent.VisibilityModes, visibleTo)

    @property
    def _componentClass(self):
        return ClientBuffComponent


class EffectBuffComponentFactory(ClientBuffComponentFactory):

    class Config(ClientBuffComponentFactory.Config):
        __slots__ = ('effectData',)

        def __init__(self, section):
            ClientBuffComponentFactory.Config.__init__(self, section)
            self.effectData = effectsFromSection(section)

    @property
    def _componentClass(self):
        return EffectBuffComponent


class SoundBuffComponentFactory(ClientBuffComponentFactory):

    class Config(ClientBuffComponentFactory.Config):
        __slots__ = ('wwsoundOnStart', 'wwsoundOnStop', 'notificationOnStart', 'notificationOnStop')

        def __init__(self, section):
            ClientBuffComponentFactory.Config.__init__(self, section)
            self.wwsoundOnStart = section.readString('wwsoundOnStart', '')
            self.wwsoundOnStop = section.readString('wwsoundOnStop', '')
            self.notificationOnStart = section.readString('notificationOnStart', '')
            self.notificationOnStop = section.readString('notificationOnStop', '')

    @property
    def _componentClass(self):
        return SoundBuffComponent


class ModelBuffComponentFactory(ClientBuffComponentFactory):

    class Config(ClientBuffComponentFactory.Config):
        __slots__ = ('model', 'node', 'offset', 'scale')

        def __init__(self, section):
            ClientBuffComponentFactory.Config.__init__(self, section)
            self.model = section.readString('model')
            self.node = section.readString('node')
            self.offset = section.readVector3('offset')
            self.scale = section.readVector3('scale')

    @property
    def _componentClass(self):
        return ModelBuffComponent


class IconBuffComponentFactory(ClientBuffComponentFactory):

    class Config(ClientBuffComponentFactory.Config):
        __slots__ = ('iconName', 'tooltipTextTag')

        def __init__(self, section):
            ClientBuffComponentFactory.Config.__init__(self, section)
            self.visibleTo = ClientBuffComponent.VisibilityModes.SELF
            self.iconName = section.readString('name')
            self.tooltipTextTag = section.readString('tooltipTextTag')

    @property
    def _componentClass(self):
        return IconBuffComponent


class DecalBuffComponentFactory(ClientBuffComponentFactory):

    @property
    def _componentClass(self):
        return DecalBuffComponent


class TerrainCircleBuffComponentFactory(ClientBuffComponentFactory):

    class Config(ClientBuffComponentFactory.Config):
        __slots__ = ('radius', 'settings')

        def __init__(self, section):
            ClientBuffComponentFactory.Config.__init__(self, section)
            self.radius = section.readFloat('radius')
            self.settings = readTerrainCircleSettings(section, (None, BUFFS_CONFIG_FILE), 'settings')
            return

    @property
    def _componentClass(self):
        return TerrainCircleBuffComponent


class SequenceBuffComponentFactory(ClientBuffComponentFactory):

    class Config(ClientBuffComponentFactory.Config):
        __slots__ = ('sequence', 'duration', 'bindNode', 'hideInSniperModeFor')

        def __init__(self, section):
            ClientBuffComponentFactory.Config.__init__(self, section)
            self.sequence = section.readString('sequence')
            self.duration = section.readFloat('duration')
            self.bindNode = section.readString('bindNode')
            hideInSniperModeFor = section.readString('hideInSniperModeFor', 'none').upper()
            self.hideInSniperModeFor = getattr(ClientBuffComponent.VisibilityModes, hideInSniperModeFor)

    @property
    def _componentClass(self):
        return SequenceBuffComponent


class InvulnerabilityBuffComponentFactory(ClientBuffComponentFactory):

    @property
    def _componentClass(self):
        return InvulnerabilityBuffComponent


class ExhaustBuffComponentFactory(ClientBuffComponentFactory):

    class Config(ClientBuffComponentFactory.Config):
        __slots__ = ('nitro',)

        def __init__(self, section):
            ClientBuffComponentFactory.Config.__init__(self, section)
            nitro = section.readString('nitro', 'none').upper()
            self.nitro = getattr(ExhaustBuffComponent.NitroTypes, nitro)

    @property
    def _componentClass(self):
        return ExhaustBuffComponent
