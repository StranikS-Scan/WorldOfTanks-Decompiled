# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/web/web_client_api/sound/__init__.py
import SoundGroups
import WWISE
from helpers import dependency
from skeletons.gui.app_loader import IAppLoader
from web.web_client_api import w2c, w2capi, W2CSchema, Field

class _SoundSchema(W2CSchema):
    sound_id = Field(required=True, type=basestring)


class _SoundStateSchema(W2CSchema):
    state_name = Field(required=True, type=basestring)
    state_value = Field(required=True, type=basestring)


class _HangarSoundSchema(W2CSchema):
    mute = Field(required=True, type=bool)


@w2capi()
class SoundWebApi(object):

    @w2c(_SoundSchema, 'sound')
    def sound(self, cmd):
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        if app and app.soundManager:
            app.soundManager.playEffectSound(cmd.sound_id)


@w2capi()
class SoundStateWebApi(object):
    __ON_EXIT_STATES = {'STATE_overlay_hangar_general': 'STATE_overlay_hangar_general_off',
     'STATE_video_overlay': 'STATE_video_overlay_off'}

    @w2c(_SoundStateSchema, 'sound_state', finiHandlerName='_soundStateFini')
    def setSoundState(self, cmd):
        WWISE.WW_setState(str(cmd.state_name), str(cmd.state_value))

    def _soundStateFini(self):
        for stateName, stateValue in self.__ON_EXIT_STATES.iteritems():
            WWISE.WW_setState(stateName, stateValue)


@w2capi()
class HangarSoundWebApi(object):

    @w2c(_HangarSoundSchema, 'hangar_sound', finiHandlerName='_hangarSoundFini')
    def hangarSound(self, cmd):
        if cmd.mute:
            SoundGroups.g_instance.playSound2D('ue_master_mute')
        else:
            SoundGroups.g_instance.playSound2D('ue_master_unmute')

    def _hangarSoundFini(self):
        SoundGroups.g_instance.playSound2D('ue_master_unmute')
