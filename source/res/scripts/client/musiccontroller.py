# Embedded file name: scripts/client/MusicController.py
import account_helpers
import BigWorld
import ResMgr
import FMOD
from constants import ARENA_PERIOD
from items import _xml
from PlayerEvents import g_playerEvents
from ConnectionManager import connectionManager
from helpers import isPlayerAvatar
import SoundGroups
MUSIC_EVENT_NONE = 0
MUSIC_EVENT_LOGIN = 1
MUSIC_EVENT_LOBBY = 2
MUSIC_EVENT_COMBAT = 3
MUSIC_EVENT_COMBAT_LOADING = 4
MUSIC_EVENT_COMBAT_VICTORY = 5
MUSIC_EVENT_COMBAT_LOSE = 6
MUSIC_EVENT_COMBAT_DRAW = 7
_BATTLE_RESULT_MUSIC_EVENTS = (MUSIC_EVENT_COMBAT_VICTORY, MUSIC_EVENT_COMBAT_LOSE, MUSIC_EVENT_COMBAT_DRAW)
AMBIENT_EVENT_NONE = 1000
AMBIENT_EVENT_LOBBY = 1001
AMBIENT_EVENT_SHOP = 1002
AMBIENT_EVENT_STATISTICS = 1003
AMBIENT_EVENT_COMBAT = 1004
AMBIENT_EVENT_LOBBY_FORT = 1005
_CMD_SERVER_CHANGE_HANGAR_AMBIENT = 'cmd_change_hangar_ambient'
_CMD_SERVER_CHANGE_HANGAR_MUSIC = 'cmd_change_hangar_music'
g_musicController = None

def init():
    global g_musicController
    g_musicController = MusicController()


class MusicController(object):

    def __init__(self):
        self.__sndEventMusic = None
        self.__sndEventAmbient = None
        self.__eventAmbientId = None
        self.__eventMusicId = None
        self.__lastBattleResultEventId = None
        self.__lastBattleResultEventName = ''
        self.__battleResultEventWaitCb = None
        self.__isOnArena = False
        self.__isPremiumAccount = False
        self.__overriddenEvents = {}
        self.__soundEvents = {MUSIC_EVENT_NONE: None,
         AMBIENT_EVENT_NONE: None}
        self.__loadConfig()
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotificationsChanged
        connectionManager.onDisconnected += self.__onDisconnected
        return

    def destroy(self):
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotificationsChanged
        connectionManager.onDisconnected -= self.__onDisconnected
        self.__cancelWaitBattleResultsEventFinish()

    def __del__(self):
        self.stop()
        self.__soundEvents.clear()

    def restart(self):
        if self.__sndEventMusic:
            self.__sndEventMusic.play()
        if self.__sndEventAmbient:
            self.__sndEventAmbient.play()

    def play(self, eventId):
        if eventId == MUSIC_EVENT_LOBBY:
            if self.__lastBattleResultEventId is not None:
                eventId = self.__lastBattleResultEventId
                self.__lastBattleResultEventId = None
                if self.__battleResultEventWaitCb is None:
                    self.__battleResultEventWaitCb = BigWorld.callback(0.1, self.__waitBattleResultEventFinish)
        elif eventId < AMBIENT_EVENT_NONE:
            self.__cancelWaitBattleResultsEventFinish()
        soundEvent = None
        if eventId == MUSIC_EVENT_COMBAT or eventId == AMBIENT_EVENT_COMBAT or eventId == MUSIC_EVENT_COMBAT_LOADING or eventId in _BATTLE_RESULT_MUSIC_EVENTS:
            soundEvent = self.__getArenaSoundEvent(eventId)
        if soundEvent is None:
            soundEvent = self.__soundEvents.get(eventId)
            if soundEvent is not None:
                if isinstance(soundEvent, list):
                    isPremium = self.__isPremiumAccount
                    idx = 1 if isPremium and len(soundEvent) > 1 else 0
                    soundEvent = soundEvent[1 if isPremium and len(soundEvent) > 1 else 0]
        isMusicTrack = eventId < AMBIENT_EVENT_NONE
        prevSoundEvent = self.__sndEventMusic if isMusicTrack else self.__sndEventAmbient
        if prevSoundEvent == soundEvent:
            return
        else:
            if prevSoundEvent is not None:
                prevSoundEvent.stop()
            if soundEvent is not None:
                soundEvent.play()
            if isMusicTrack:
                self.__sndEventMusic = soundEvent
                self.__eventMusicId = eventId
            else:
                self.__sndEventAmbient = soundEvent
                self.__eventAmbientId = eventId
            return

    def stopMusic(self):
        if self.__sndEventMusic is not None:
            self.__sndEventMusic.stop()
            self.__sndEventMusic = None
            self.__eventMusicId = None
        self.__cancelWaitBattleResultsEventFinish()
        return

    def stopAmbient(self):
        if self.__sndEventAmbient is not None:
            self.__sndEventAmbient.stop(True)
            self.__sndEventAmbient = None
            self.__eventAmbientId = None
        FMOD.enableLightSound(0)
        return

    def stop(self):
        self.stopAmbient()
        self.stopMusic()

    def onEnterArena(self):
        BigWorld.player().arena.onPeriodChange += self.__onArenaStateChanged
        self.__isOnArena = True
        self.__onArenaStateChanged()
        FMOD.enableLightSound(1)

    def onLeaveArena(self):
        self.__isOnArena = False
        BigWorld.player().arena.onPeriodChange -= self.__onArenaStateChanged
        FMOD.enableLightSound(0)

    def setAccountAttrs(self, accAttrs, restart = False):
        wasPremiumAccount = self.__isPremiumAccount
        self.__isPremiumAccount = account_helpers.isPremiumAccount(accAttrs)
        if restart and self.__isPremiumAccount != wasPremiumAccount and self.__eventMusicId == MUSIC_EVENT_LOBBY:
            self.play(self.__eventMusicId)
            self.play(self.__eventAmbientId)

    def __onArenaStateChanged(self, *args):
        arena = BigWorld.player().arena
        period = arena.period
        if (period == ARENA_PERIOD.PREBATTLE or period == ARENA_PERIOD.BATTLE) and self.__isOnArena:
            self.play(AMBIENT_EVENT_COMBAT)
        if period == ARENA_PERIOD.BATTLE and self.__isOnArena:
            self.play(MUSIC_EVENT_COMBAT)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.stopAmbient()
            self.__lastBattleResultEventId = None
            self.__lastBattleResultEventName = ''
            winnerTeam = arena.periodAdditionalInfo[0]
            if winnerTeam == BigWorld.player().team:
                self.__lastBattleResultEventId = MUSIC_EVENT_COMBAT_VICTORY
                self.__lastBattleResultEventName = arena.arenaType.battleVictoryMusic if hasattr(arena.arenaType, 'battleVictoryMusic') else ''
            elif winnerTeam == 0:
                self.__lastBattleResultEventId = MUSIC_EVENT_COMBAT_DRAW
                self.__lastBattleResultEventName = arena.arenaType.battleDrawMusic if hasattr(arena.arenaType, 'battleDrawMusic') else ''
            else:
                self.__lastBattleResultEventId = MUSIC_EVENT_COMBAT_LOSE
                self.__lastBattleResultEventName = arena.arenaType.battleLoseMusic if hasattr(arena.arenaType, 'battleLoseMusic') else ''
        return

    def __getArenaSoundEvent(self, eventId):
        soundEvent = None
        soundEventName = None
        if eventId in _BATTLE_RESULT_MUSIC_EVENTS:
            soundEventName = self.__lastBattleResultEventName
        else:
            player = BigWorld.player()
            if not isPlayerAvatar():
                return
            if player.arena is None:
                return
            arenaType = player.arena.arenaType
            if eventId == MUSIC_EVENT_COMBAT:
                soundEventName = arenaType.music
            elif eventId == MUSIC_EVENT_COMBAT_LOADING:
                soundEventName = arenaType.loadingMusic
            elif eventId == AMBIENT_EVENT_COMBAT:
                soundEventName = arenaType.ambientSound
        if soundEventName:
            soundEvent = SoundGroups.g_instance.FMODgetSound(soundEventName)
            if soundEvent is not None:
                soundEvent.stop()
        return soundEvent

    def __loadConfig(self):
        eventNames = {}
        xmlPath = 'gui/music_events.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        for i in section.items():
            s = i[1]
            if i[0] == 'music':
                eventNames[MUSIC_EVENT_LOGIN] = s.readString('login')
                eventNames[MUSIC_EVENT_LOBBY] = (s.readString('lobby'), s.readString('lobby_premium'))
                eventNames[MUSIC_EVENT_COMBAT_VICTORY] = s.readString('combat_victory')
                eventNames[MUSIC_EVENT_COMBAT_LOSE] = s.readString('combat_lose')
                eventNames[MUSIC_EVENT_COMBAT_DRAW] = s.readString('combat_draw')
            elif i[0] == 'ambient':
                eventNames[AMBIENT_EVENT_LOBBY] = (s.readString('lobby'), s.readString('lobby_premium'))
                eventNames[AMBIENT_EVENT_SHOP] = (s.readString('shop'), s.readString('shop_premium'))
                eventNames[AMBIENT_EVENT_STATISTICS] = (s.readString('rating'), s.readString('rating_premium'))
                eventNames[AMBIENT_EVENT_LOBBY_FORT] = (s.readString('fort'), s.readString('fort'))

        fallbackEventNames = eventNames.copy()
        for eventId, overriddenNames in self.__overriddenEvents.iteritems():
            eventNames[eventId] = overriddenNames

        soundsByName = {}
        for eventId, names in eventNames.items():
            lstEvents = []
            if not isinstance(names, tuple):
                names = (names,)
            fallbackNames = fallbackEventNames[eventId]
            if not isinstance(fallbackNames, tuple):
                fallbackNames = (fallbackNames,)
            for i in xrange(len(names)):
                eventName = names[i]
                fallbackEventName = fallbackNames[i]
                sound = soundsByName.get(eventName)
                if sound is None:
                    sound = SoundGroups.g_instance.FMODgetSound(eventName) if eventName != '' else None
                    if sound is None:
                        sound = SoundGroups.g_instance.FMODgetSound(fallbackEventName) if fallbackEventName != '' else None
                soundsByName[eventName] = sound
                lstEvents.append(sound)
                if sound is not None:
                    sound.stop()

            self.__soundEvents[eventId] = lstEvents

        return

    def __waitBattleResultEventFinish(self):
        self.__battleResultEventWaitCb = None
        if self.__eventMusicId not in _BATTLE_RESULT_MUSIC_EVENTS:
            return
        else:
            isMusicPlaying = self.__sndEventMusic.state.find('playing') != -1
            if not isMusicPlaying:
                self.play(MUSIC_EVENT_LOBBY)
                return
            self.__battleResultEventWaitCb = BigWorld.callback(0.1, self.__waitBattleResultEventFinish)
            return

    def __cancelWaitBattleResultsEventFinish(self):
        if self.__battleResultEventWaitCb is not None:
            BigWorld.cancelCallback(self.__battleResultEventWaitCb)
            self.__battleResultEventWaitCb = None
        return

    def __onEventNotificationsChanged(self, notificationsDiff):
        hasChanges = False
        for notification in notificationsDiff['removed']:
            if notification['type'] == _CMD_SERVER_CHANGE_HANGAR_AMBIENT:
                self.__overriddenEvents.pop(AMBIENT_EVENT_LOBBY, 0)
                self.__overriddenEvents.pop(AMBIENT_EVENT_SHOP, 0)
                self.__overriddenEvents.pop(AMBIENT_EVENT_STATISTICS, 0)
                hasChanges = True
            elif notification['type'] == _CMD_SERVER_CHANGE_HANGAR_MUSIC:
                self.__overriddenEvents.pop(MUSIC_EVENT_LOBBY, 0)
                hasChanges = True

        for notification in notificationsDiff['added']:
            if notification['type'] == _CMD_SERVER_CHANGE_HANGAR_AMBIENT:
                ambientEventName = notification['data']
                self.__overriddenEvents[AMBIENT_EVENT_LOBBY] = (ambientEventName, ambientEventName)
                self.__overriddenEvents[AMBIENT_EVENT_SHOP] = (ambientEventName, ambientEventName)
                self.__overriddenEvents[AMBIENT_EVENT_STATISTICS] = (ambientEventName, ambientEventName)
                hasChanges = True
            elif notification['type'] == _CMD_SERVER_CHANGE_HANGAR_MUSIC:
                musicEventNames = [ event.strip() for event in notification['data'].split('|') ]
                musicEventName = musicEventNames[0]
                premiumMusicEventName = musicEventNames[1] if len(musicEventNames) > 1 else musicEventName
                self.__overriddenEvents[MUSIC_EVENT_LOBBY] = (musicEventName, premiumMusicEventName)
                hasChanges = True

        if hasChanges:
            self.__loadConfig()
            if self.__eventAmbientId is not None:
                self.play(self.__eventAmbientId)
            if self.__eventMusicId is not None:
                self.play(self.__eventMusicId)
        return

    def __onDisconnected(self):
        if len(self.__overriddenEvents) > 0:
            self.__overriddenEvents = {}
            self.__loadConfig()
