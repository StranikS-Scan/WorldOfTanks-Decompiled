# Python bytecode 2.6 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MusicController.py
# Compiled at: 2010-11-23 18:29:25
import account_helpers
import struct
import BigWorld
import ResMgr
import FMOD
import items
import ClientArena
import Avatar
import Account
import constants
from constants import ARENA_PERIOD
from items import _xml
MUSIC_EVENT_NONE = 0
MUSIC_EVENT_LOGIN = 1
MUSIC_EVENT_LOBBY = 2
MUSIC_EVENT_COMBAT = 3
MUSIC_EVENT_COMBAT_LOADING = 4
MUSIC_EVENT_COMBAT_VICTORY = 5
MUSIC_EVENT_COMBAT_LOSE = 6
MUSIC_EVENT_COMBAT_DRAW = 7
AMBIENT_EVENT_NONE = 1000
AMBIENT_EVENT_LOBBY = 1001
AMBIENT_EVENT_SHOP = 1002
AMBIENT_EVENT_STATISTICS = 1003
AMBIENT_EVENT_COMBAT = 1004
g_musicController = None

def init():
    global g_musicController
    g_musicController = MusicController()


class MusicController(object):

    def __init__(self):
        self.__sndEventAmbient = None
        self.__sndEventMusic = None
        self.__isOnArena = False
        self.__isPremiumAccount = False
        self.__soundEvents = {MUSIC_EVENT_NONE: None,
         AMBIENT_EVENT_NONE: None}
        self._loadConfig()
        return

    def __del__(self):
        self.stop()
        self.__soundEvents.clear()

    def _loadConfig(self):
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

        soundsByName = {}
        for eventId, eventNames in eventNames.items():
            lstEvents = []
            if not isinstance(eventNames, tuple):
                eventNames = (eventNames,)
            for eventName in eventNames:
                sound = soundsByName.get(eventName)
                if sound is None:
                    sound = FMOD.getSound(eventName) if eventName != '' else None
                soundsByName[eventName] = sound
                lstEvents.append(sound)
                if sound is not None:
                    sound.stop()

            self.__soundEvents[eventId] = lstEvents

        return

    def play(self, eventId):
        soundEvent = None
        if eventId == MUSIC_EVENT_COMBAT or eventId == AMBIENT_EVENT_COMBAT or eventId == MUSIC_EVENT_COMBAT_LOADING:
            soundEvent = self._getArenaSoundEvent(eventId)
        else:
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
            else:
                self.__sndEventAmbient = soundEvent
            return

    def stopMusic(self):
        if self.__sndEventMusic is not None:
            self.__sndEventMusic.stop()
            self.__sndEventMusic = None
        return

    def stopAmbient(self):
        if self.__sndEventAmbient is not None:
            self.__sndEventAmbient.stop()
            self.__sndEventAmbient = None
        return

    def stop(self):
        self.stopAmbient()
        self.stopMusic()

    def onEnterArena(self):
        BigWorld.player().arena.onPeriodChange += self._onArenaStateChanged
        self.__isOnArena = True
        self._onArenaStateChanged()

    def onLeaveArena(self):
        self.__isOnArena = False
        BigWorld.player().arena.onPeriodChange -= self._onArenaStateChanged

    def setAccountAttrs(self, accAttrs):
        self.__isPremiumAccount = account_helpers.isPremiumAccount(accAttrs)

    def _onArenaStateChanged(self, *args):
        arena = BigWorld.player().arena
        period = arena.period
        if period == ARENA_PERIOD.BATTLE and self.__isOnArena:
            self.play(MUSIC_EVENT_COMBAT)
            self.play(AMBIENT_EVENT_COMBAT)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.stopAmbient()
            winnerTeam = arena.periodAdditionalInfo[0]
            if winnerTeam == BigWorld.player().team:
                self.play(MUSIC_EVENT_COMBAT_VICTORY)
            elif winnerTeam == 0:
                self.play(MUSIC_EVENT_COMBAT_DRAW)
            else:
                self.play(MUSIC_EVENT_COMBAT_LOSE)

    def _getArenaSoundEvent(self, eventId):
        player = BigWorld.player()
        soundEvent = None
        soundEventName = None
        if not isinstance(player, Avatar.PlayerAvatar):
            return
        elif player.arena is None:
            return
        else:
            arenaType = player.arena.typeDescriptor
            if eventId == MUSIC_EVENT_COMBAT:
                soundEventName = arenaType.music
            elif eventId == MUSIC_EVENT_COMBAT_LOADING:
                soundEventName = arenaType.loadingMusic
            elif eventId == AMBIENT_EVENT_COMBAT:
                soundEventName = arenaType.ambientSound
            if soundEventName is not None:
                soundEvent = FMOD.getSound(soundEventName)
                if soundEvent is not None:
                    soundEvent.stop()
            return soundEvent
