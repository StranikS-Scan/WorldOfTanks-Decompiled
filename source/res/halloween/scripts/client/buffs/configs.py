# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: halloween/scripts/client/buffs/configs.py
import json
from buffs_helpers import ModifiersDict
from buffs_common import BuffComponentVisibilityMode
from helpers.EffectsList import effectsFromSection

class ClientBuffComponentConfig(object):
    __slots__ = ('visibleTo',)

    def __init__(self, section):
        visibleTo = section.readString('visibleTo', 'all').upper()
        self.visibleTo = getattr(BuffComponentVisibilityMode, visibleTo)


class SequenceBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('sequence', 'duration', 'bindNode', 'hideInSniperModeFor', 'loopCount', 'soundStart')
    DEFAULT_LOOP_COUNT = -1

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.sequence = section.readString('sequence')
        self.duration = section.readFloat('duration')
        self.bindNode = section.readString('bindNode')
        hideInSniperModeFor = section.readString('hideInSniperModeFor', 'none').upper()
        self.hideInSniperModeFor = getattr(BuffComponentVisibilityMode, hideInSniperModeFor)
        self.loopCount = section.readInt('loopCount', self.DEFAULT_LOOP_COUNT)
        self.soundStart = section.readString('soundStart')


class EffectBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('effectData',)

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.effectData = effectsFromSection(section)


class TTCModifierBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('ttcModifiers',)

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.ttcModifiers = ModifiersDict()
        self.ttcModifiers.readXml(section)


class IconBuffComponentConfig(ClientBuffComponentConfig):
    __slots__ = ('iconName', 'tooltip')

    def __init__(self, section):
        ClientBuffComponentConfig.__init__(self, section)
        self.iconName = section.readString('iconName')
        self.tooltip = {'tag': section['tooltip'].readString('tag'),
         'params': json.loads(section['tooltip'].readString('params')) if section['tooltip'].has_key('params') else dict()}
