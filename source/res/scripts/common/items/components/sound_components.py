# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/sound_components.py
from __future__ import absolute_import
from collections import namedtuple
from py2to3.patched_future import with_metaclass
from wrapped_reflection_framework import ReflectionMetaclass, reflectedNamedTuple
__all__ = ('SoundPair', 'StatedSounds', 'HullAimingSound', 'SoundSiegeModeStateChange', 'WWTripleSoundConfig')
SoundPair = reflectedNamedTuple('SoundPair', ('PC', 'NPC'))
StatedSounds = reflectedNamedTuple('StatedSounds', ('state', 'underLimitSounds', 'overLimitSounds'))
HullAimingSound = reflectedNamedTuple('HullAimingSound', ('lodDist', 'angleLimitValue', 'sounds'))
SoundSiegeModeStateChange = namedtuple('SoundSiegeModeStateChange', ['on',
 'off',
 'npcOn',
 'npcOff',
 'isEngine',
 'trigger',
 'unavailable'])

class WWTripleSoundConfig(with_metaclass(ReflectionMetaclass, object)):
    __slots__ = ('__eventNames',)

    def __init__(self, wwsound, wwsoundPC, wwsoundNPC):
        super(WWTripleSoundConfig, self).__init__()
        self._configure(wwsound, wwsoundPC, wwsoundNPC)

    def _configure(self, wwsound, wwsoundPC, wwsoundNPC):
        if wwsoundPC:
            if wwsoundNPC:
                self.__eventNames = (wwsoundPC, wwsoundNPC)
            else:
                self.__eventNames = (wwsoundPC, wwsound)
        elif wwsoundNPC:
            self.__eventNames = (wwsound, wwsoundNPC)
        else:
            self.__eventNames = (wwsound, wwsound)

    def isEmpty(self):
        return not self.__eventNames[0] and not self.__eventNames[1]

    def getEvents(self):
        return self.__eventNames
