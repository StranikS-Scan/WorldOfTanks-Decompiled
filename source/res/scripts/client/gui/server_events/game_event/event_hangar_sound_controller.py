# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/server_events/game_event/event_hangar_sound_controller.py
import SoundGroups
import constants
from helpers import dependency
from skeletons.account_helpers.settings_core import ISettingsCore
from skeletons.gui.server_events import IEventsCache
from account_helpers.settings_core.settings_constants import EventHangarVoPhases
from gui.shared import g_eventBus, EVENT_BUS_SCOPE, events

class EventHangarSoundController(object):
    settingsCore = dependency.descriptor(ISettingsCore)
    eventsCache = dependency.descriptor(IEventsCache)
    _PHASEX = 'PHASEX'
    _PHASES_SOUND_EVENTS = {EventHangarVoPhases.PHASE1: ['ev_2020_secret_event_2_hangar_event_music_01_first', 'vo_se20_story_01'],
     EventHangarVoPhases.PHASE2: ['ev_2020_secret_event_2_hangar_event_music_02_first', 'vo_se20_story_02'],
     EventHangarVoPhases.PHASE3: ['ev_2020_secret_event_2_hangar_event_music_03_first', 'vo_se20_story_03'],
     EventHangarVoPhases.PHASE4: ['ev_2020_secret_event_2_hangar_event_music_04_first', 'vo_se20_story_04'],
     EventHangarVoPhases.PHASE5: ['ev_2020_secret_event_2_hangar_event_music_05_first', 'vo_se20_story_05'],
     EventHangarVoPhases.PHASE6: ['ev_2020_secret_event_2_hangar_event_music_06_first', 'vo_se20_story_06'],
     EventHangarVoPhases.PHASE7: ['ev_2020_secret_event_2_hangar_event_music_07_first', 'vo_se20_story_07'],
     _PHASEX: ['ev_2020_secret_event_2_hangar_event_second_time']}

    def __init__(self):
        self.__cheatPhaseId = None
        self.__narrativeSounds = []
        return

    def start(self):
        g_eventBus.addListener(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, self.__onLobbyTypeChanged, EVENT_BUS_SCOPE.LOBBY)

    def stop(self):
        g_eventBus.removeListener(events.HangarVehicleEvent.LOBBY_TYPE_CHANGED, self.__onLobbyTypeChanged)
        self.__reset()

    def cheatResetPhases(self):
        if not constants.IS_DEVELOPMENT:
            return
        else:
            self.__cheatPhaseId = None
            settings = {phase:0 for phase in EventHangarVoPhases.ALL_PHASES}
            self.settingsCore.serverSettings.setGameEventHangarVoSettings(settings)
            self.__reset()
            return

    def cheatSetPhaseId(self, phaseId):
        if not constants.IS_DEVELOPMENT:
            return
        self.__cheatPhaseId = phaseId
        self.settingsCore.serverSettings.setGameEventHangarVoSettings({EventHangarVoPhases.ALL_PHASES[phaseId]: 0})
        self.__reset()

    def cheatStopSounds(self):
        if not constants.IS_DEVELOPMENT:
            return
        self.__reset()

    def __onLobbyTypeChanged(self, event):
        if event.ctx['lobbyType'] == constants.LobbyType.EVENT:
            self.__startNarrativeSounds()

    def __startNarrativeSounds(self):
        if self.__narrativeSounds:
            return
        hangarEnvironmentSettings = self.eventsCache.getGameEventData()['hangarEnvironmentSettings']
        phaseId = hangarEnvironmentSettings['voPhase']
        if constants.IS_DEVELOPMENT:
            phaseId = self.__cheatPhaseId or phaseId
        phaseName = EventHangarVoPhases.ALL_PHASES[phaseId]
        isDone = self.settingsCore.serverSettings.getGameEventHangarVoSettings(phaseName)
        if not isDone:
            self.settingsCore.serverSettings.setGameEventHangarVoSettings({phaseName: 1})
        else:
            phaseName = self._PHASEX
        soundEvents = self._PHASES_SOUND_EVENTS[phaseName]
        for event in soundEvents:
            sound = SoundGroups.g_instance.getSound2D(event)
            if sound:
                sound.play()
                self.__narrativeSounds.append(sound)

    def __reset(self):
        for sound in self.__narrativeSounds:
            if sound.isPlaying:
                sound.stop()

        self.__narrativeSounds = []
