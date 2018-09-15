# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/sound.py
from collections import namedtuple
from command import SchemeValidator, CommandHandler, instantiateObject
_SoundCommand = namedtuple('_SoundCommand', ('sound_id',))
_SoundCommand.__new__.__defaults__ = (None,)
_SoundCommandScheme = {'required': (('sound_id', basestring),)}

class SoundCommand(_SoundCommand, SchemeValidator):
    """
    Represents web command for playing sound by id.
    """

    def __init__(self, *args, **kwargs):
        super(SoundCommand, self).__init__(_SoundCommandScheme)


def createSoundHandler(handlerFunc):
    data = {'name': 'sound',
     'cls': SoundCommand,
     'handler': handlerFunc}
    return instantiateObject(CommandHandler, data)


_HangarSoundCommand = namedtuple('_HangarSoundCommand', ('mute',))
_HangarSoundCommand.__new__.__defaults__ = (False,)
_HangarSoundCommandScheme = {'required': (('mute', bool),)}

class HangarSoundCommand(_HangarSoundCommand, SchemeValidator):
    """
    Represents web command for controlling hangar sound
    """

    def __init__(self, *args, **kwargs):
        super(HangarSoundCommand, self).__init__(_HangarSoundCommandScheme)


def createHangarSoundHandler(handlerFunc, finiHandlerFunc=None):
    data = {'name': 'hangar_sound',
     'cls': HangarSoundCommand,
     'handler': handlerFunc,
     'finiHandler': finiHandlerFunc}
    return instantiateObject(CommandHandler, data)
