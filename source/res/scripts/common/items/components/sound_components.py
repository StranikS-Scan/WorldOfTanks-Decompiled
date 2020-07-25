# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/common/items/components/sound_components.py
from collections import namedtuple
from wrapped_reflection_framework import ReflectionMetaclass
__all__ = ('SoundPair', 'StatedSounds', 'HullAimingSound', 'SoundSiegeModeStateChange', 'WWTripleSoundConfig')
SoundPair = namedtuple('SoundPair', ('PC', 'NPC'))
StatedSounds = namedtuple('StatedSound', ('state', 'underLimitSounds', 'overLimitSounds'))
HullAimingSound = namedtuple('HullAimingSound', ('lodDist', 'angleLimitValue', 'sounds'))
SoundSiegeModeStateChange = namedtuple('SoundSiegeModeStateChange', ['on',
 'off',
 'npcOn',
 'npcOff',
 'isEngine'])

class WWTripleSoundConfig(object):
    __slots__ = ('__eventNames',)
    __metaclass__ = ReflectionMetaclass

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
