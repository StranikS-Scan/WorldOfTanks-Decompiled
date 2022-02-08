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
    _ENTER_EXIT_SOUND_MAPPING = {'eb_ambient_progress_page_enter': 'eb_ambient_progress_page_exit',
     'main_unit_enter': 'main_unit_exit',
     'clans_quests_enter': 'clans_quests_exit',
     'fa_enter': 'fa_exit',
     'ads_enter': 'ads_exit',
     'global_map_enter': 'global_map_exit',
     'craft_machine_enter': 'craft_machine_exit',
     'clans_battles_global_map_enter': 'clans_battles_global_map_exit',
     'clans_winner_reward_enter': 'clans_winner_reward_exit',
     'gui_cq_progress_bar_start': 'gui_cq_progress_bar_stop',
     'gui_cq_progression_start': 'gui_cq_progression_stop'}

    def __init__(self):
        super(SoundWebApi, self).__init__()
        self.__exitSounds = set()

    @w2c(_SoundSchema, 'sound', finiHandlerName='_soundFini')
    def sound(self, cmd):
        appLoader = dependency.instance(IAppLoader)
        app = appLoader.getApp()
        if app and app.soundManager:
            app.soundManager.playEffectSound(cmd.sound_id)
            self.__exitSounds.discard(cmd.sound_id)
            exitSound = self._ENTER_EXIT_SOUND_MAPPING.get(cmd.sound_id)
            if exitSound:
                self.__exitSounds.add(exitSound)

    def _soundFini(self):
        for exitSound in self.__exitSounds:
            WWISE.WW_eventGlobal(exitSound)

        self.__exitSounds.clear()


@w2capi()
class SoundStateWebApi(object):
    _ON_EXIT_STATES = {'STATE_overlay_hangar_general': 'STATE_overlay_hangar_general_off',
     'STATE_video_overlay': 'STATE_video_overlay_off',
     'STATE_clans_craft': 'STATE_clans_craft_progress_off',
     'STATE_gamemode_progress_page': 'STATE_gamemode_progress_page_off'}

    def __init__(self):
        super(SoundStateWebApi, self).__init__()
        self.__setStates = set()

    @w2c(_SoundStateSchema, 'sound_state', finiHandlerName='_soundStateFini')
    def setSoundState(self, cmd):
        WWISE.WW_setState(str(cmd.state_name), str(cmd.state_value))
        self.__setStates.add(str(cmd.state_name))

    def _soundStateFini(self):
        for stateName, stateValue in self._ON_EXIT_STATES.iteritems():
            if stateName in self.__setStates:
                WWISE.WW_setState(stateName, stateValue)

        self.__setStates.clear()


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
