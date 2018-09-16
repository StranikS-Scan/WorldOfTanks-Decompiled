# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web_client_api/commands/sound.py
from command import W2CSchema, createCommandHandler, Field

class SoundSchema(W2CSchema):
    sound_id = Field(required=True, type=basestring)


def createSoundHandler(handlerFunc):
    return createCommandHandler('sound', SoundSchema, handlerFunc)


class HangarSoundSchema(W2CSchema):
    mute = Field(required=True, type=bool)


def createHangarSoundHandler(handlerFunc, finiHandlerFunc=None):
    return createCommandHandler('hangar_sound', HangarSoundSchema, handlerFunc, finiHandlerFunc)
