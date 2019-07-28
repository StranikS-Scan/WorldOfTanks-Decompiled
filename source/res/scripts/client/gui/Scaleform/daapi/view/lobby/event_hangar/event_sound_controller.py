# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/lobby/event_hangar/event_sound_controller.py
import WWISE
import SoundGroups
from gui.Scaleform.daapi.settings.views import VIEW_ALIAS
from gui.shared import g_eventBus, EVENT_BUS_SCOPE
from helpers import dependency, getClientLanguage
from skeletons.gui.event_hangar_sound_controller import IEventHangarSoundController
from skeletons.gui.server_events import IEventsCache

class EventHangarSoundController(IEventHangarSoundController):
    eventsCache = dependency.descriptor(IEventsCache)
    _HANGAR_SOUNDS_BY_ID = {0: {'music': 'ev_2019_secret_event_act1_hangar_event_first',
         'ambient': 'ev_2019_secret_event_hangar_event_second_time',
         'voiceover': 'vo_se1_story_01'},
     1: {'music': 'ev_2019_secret_event_act2_hangar_event_first',
         'ambient': 'ev_2019_secret_event_hangar_event_second_time',
         'voiceover': 'vo_se1_story_02'},
     2: {'music': 'ev_2019_secret_event_act3_hangar_event_first',
         'ambient': 'ev_2019_secret_event_hangar_event_second_time',
         'voiceover': 'vo_se1_story_03'}}
    _VOICEOVER_LOCALIZATION_SWITCH = 'SWITCH_ext_ev_secret_event_voice_over'
    _VOICEOVER_RU = 'SWITCH_ext_ev_secret_event_voice_over_ru'
    _VOICEOVER_EN = 'SWITCH_ext_ev_secret_event_voice_over_en'
    _STATE_HANGAR = 'STATE_hangar_view'
    _STATE_HANGAR_MAIN = 'STATE_hangar_view_01'
    _STATE_HANGAR_EVENT = 'STATE_hangar_view_02'
    _STATE_HANGAR_FILTER = 'STATE_hangar_filtered'
    _STATE_HANGAR_FILTER_ON = 'STATE_hangar_filtered_on'
    _STATE_HANGAR_FILTER_OFF = 'STATE_hangar_filtered_off'

    def __init__(self):
        self._soundMusic = None
        self._soundVoiceover = None
        self._soundAmbient = None
        self._forcedSoundId = None
        self._playCounter = 0
        if getClientLanguage().upper() == 'RU':
            SoundGroups.g_instance.setSwitch(self._VOICEOVER_LOCALIZATION_SWITCH, self._VOICEOVER_RU)
        else:
            SoundGroups.g_instance.setSwitch(self._VOICEOVER_LOCALIZATION_SWITCH, self._VOICEOVER_EN)
        WWISE.WW_setState(self._STATE_HANGAR, self._STATE_HANGAR_MAIN)
        return

    def init(self):
        pass

    def start(self):
        self._updateSounds()
        g_eventBus.addListener(VIEW_ALIAS.EVENT_HANGAR_PAGE, self._onEventDioramaEnter, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(VIEW_ALIAS.LOBBY_HANGAR, self._onEventDioramaLeave, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(VIEW_ALIAS.EVENT_MANUAL_PAGE, self._onEventManualEnter, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(VIEW_ALIAS.EVENT_HANGAR_PAGE, self._onEventManualLeave, EVENT_BUS_SCOPE.LOBBY)
        g_eventBus.addListener(VIEW_ALIAS.LOBBY_HANGAR, self._onEventManualLeave, EVENT_BUS_SCOPE.LOBBY)

    def stop(self):
        self._stopSounds()

    def reset(self, forcedSoundId=None):
        wasPlaying = self.__isPlayingAnySound()
        self._stopSounds()
        self._playCounter = 0
        self._forcedSoundId = forcedSoundId
        self._updateSounds()
        if wasPlaying:
            self._playSounds()

    def fini(self):
        self.stop()

    def _onEventDioramaEnter(self, event):
        WWISE.WW_setState(self._STATE_HANGAR, self._STATE_HANGAR_EVENT)
        self._playSounds()

    def _onEventDioramaLeave(self, event):
        WWISE.WW_setState(self._STATE_HANGAR, self._STATE_HANGAR_MAIN)

    def _onEventManualEnter(self, event):
        WWISE.WW_setState(self._STATE_HANGAR_FILTER, self._STATE_HANGAR_FILTER_ON)

    def _onEventManualLeave(self, event):
        WWISE.WW_setState(self._STATE_HANGAR_FILTER, self._STATE_HANGAR_FILTER_OFF)

    @property
    def _currentSoundID(self):
        return self._forcedSoundId if self._forcedSoundId is not None else self.eventsCache.getGameEventData().get('currentSoundID', 0)

    def _updateSounds(self):
        config = self._HANGAR_SOUNDS_BY_ID[self._currentSoundID]
        self._soundMusic = SoundGroups.g_instance.getSound2D(config['music'])
        self._soundVoiceover = SoundGroups.g_instance.getSound2D(config['voiceover'])
        self._soundAmbient = SoundGroups.g_instance.getSound2D(config['ambient'])

    def _playSounds(self):
        self.__playSound(self._soundAmbient)
        if self._playCounter == 0:
            self.__playSound(self._soundMusic)
            self.__playSound(self._soundVoiceover)
        self._playCounter += 1

    def _stopSounds(self):
        self.__stopSound(self._soundMusic)
        self.__stopSound(self._soundVoiceover)
        self.__stopSound(self._soundAmbient)

    def __isPlayingAnySound(self):
        return self._soundMusic.isPlaying or self._soundVoiceover.isPlaying or self._soundAmbient.isPlaying

    @staticmethod
    def __playSound(sound):
        if sound is not None and not sound.isPlaying:
            sound.play()
        return

    @staticmethod
    def __stopSound(sound):
        if sound is not None and sound.isPlaying:
            sound.stop()
        return
