# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MusicControllerWWISE.py
import BigWorld
import ResMgr
import SoundGroups
import WWISE
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD
from helpers import isPlayerAvatar
from items import _xml
MUSIC_EVENT_NONE = 0
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
AMBIENT_EVENT_LOBBY_FORT_FINANCIAL_DEPT = 1006
AMBIENT_EVENT_LOBBY_FORT_TANKODROME = 1007
AMBIENT_EVENT_LOBBY_FORT_TRAINING_DEPT = 1008
AMBIENT_EVENT_LOBBY_FORT_MILITARY_ACADEMY = 1009
AMBIENT_EVENT_LOBBY_FORT_TRANSPORT_DEPT = 1010
AMBIENT_EVENT_LOBBY_FORT_INTENDANT_SERVICE = 1011
AMBIENT_EVENT_LOBBY_FORT_TROPHY_BRIGADE = 1012
AMBIENT_EVENT_LOBBY_FORT_OFFICE = 1013
AMBIENT_EVENT_LOBBY_FORT_MILITARY_SHOP = 1014
FORT_MAPPING = {'wwfort': AMBIENT_EVENT_LOBBY_FORT,
 'wwfort_building_financial_dept': AMBIENT_EVENT_LOBBY_FORT_FINANCIAL_DEPT,
 'wwfort_building_tankodrome': AMBIENT_EVENT_LOBBY_FORT_TANKODROME,
 'wwfort_building_training_dept': AMBIENT_EVENT_LOBBY_FORT_TRAINING_DEPT,
 'wwfort_building_military_academy': AMBIENT_EVENT_LOBBY_FORT_MILITARY_ACADEMY,
 'wwfort_building_transport_dept': AMBIENT_EVENT_LOBBY_FORT_TRANSPORT_DEPT,
 'wwfort_building_intendant_service': AMBIENT_EVENT_LOBBY_FORT_INTENDANT_SERVICE,
 'wwfort_building_trophy_brigade': AMBIENT_EVENT_LOBBY_FORT_TROPHY_BRIGADE,
 'wwfort_building_office': AMBIENT_EVENT_LOBBY_FORT_OFFICE,
 'wwfort_building_military_shop': AMBIENT_EVENT_LOBBY_FORT_MILITARY_SHOP}
_ARENA_EVENTS = (MUSIC_EVENT_COMBAT, AMBIENT_EVENT_COMBAT, MUSIC_EVENT_COMBAT_LOADING)
_CMD_SERVER_CHANGE_HANGAR_AMBIENT = 'cmd_change_hangar_ambient'
_CMD_SERVER_CHANGE_HANGAR_MUSIC = 'cmd_change_hangar_music'
_SERVER_OVERRIDDEN = 0
_CLIENT_OVERRIDDEN = 1
g_musicController = None

def create():
    global g_musicController
    if g_musicController is None:
        g_musicController = MusicController()
    return


def init(arenaName):
    global g_musicController
    if g_musicController is None:
        g_musicController = MusicController()
    g_musicController.init(arenaName)
    return


def destroy():
    if g_musicController is not None:
        g_musicController.destroy()
    return


def onLeaveArena():
    if g_musicController is not None:
        g_musicController.onLeaveArena()
    return


def onEnterArena():
    if g_musicController is not None:
        g_musicController.onEnterArena()
    return


def unloadCustomSounds():
    if g_musicController is not None:
        g_musicController.unloadCustomSounds()
    return


def play(eventId):
    if g_musicController is not None:
        g_musicController.play(eventId)
    return


class MusicController(object):

    class MusicEvent:

        def __init__(self, event=None):
            self.__muted = False
            self.__event = event
            self.__eventID = None
            return

        def replace(self, event, eventId, playNew):
            if self.__event is not None:
                if self.__event.name == event.name:
                    playNew = False
                else:
                    self.stop()
            self.__event = event
            self.__eventID = eventId
            if playNew is True:
                self.play()
            return

        def play(self):
            if self.__event is not None:
                self.__event.play()
            return

        def mute(self, isMute):
            if self.__event is not None:
                if isMute != self.__muted:
                    self.__muted = isMute
                    if self.__muted:
                        self.__event.stop()
                    else:
                        self.__event.play()
            return

        def stop(self):
            if self.__event is not None:
                if self.__eventID == MUSIC_EVENT_COMBAT_LOADING:
                    WWISE.WW_eventGlobalSync('ue_stop_loadscreen_music')
                elif self.__eventID >= MUSIC_EVENT_COMBAT_VICTORY and self.__eventID <= MUSIC_EVENT_COMBAT_DRAW:
                    WWISE.WW_eventGlobalSync('ue_events_hangar_stop_afterBattleMusic')
                else:
                    self.__event.stop()
            return

        def param(self, paramName):
            return self.__event.param(paramName) if self.__event is not None else None

        def getEventId(self):
            return self.__eventID

        def isPlaying(self):
            return self.__event.isPlaying if self.__event is not None else False

        def destroy(self):
            if self.__event is not None:
                self.__event.stop()
                self.__event = None
                self.__eventID = None
            return

    _MUSIC_EVENT = 0
    _AMBIENT_EVENT = 1
    __lastBattleResultEventName = ''

    def __init__(self):
        self.__overriddenEvents = {}
        self.__musicEvents = (MusicController.MusicEvent(), MusicController.MusicEvent())
        self.__sndEventMusic = None
        self.__soundEvents = {MUSIC_EVENT_NONE: None,
         AMBIENT_EVENT_NONE: None}
        self._skipArenaChanges = False
        self.init()
        return

    def init(self, path=None):
        self.__isOnArena = False
        self.__isPremiumAccount = False
        if path is not None:
            self.__loadCustomSounds(path)
        self.__loadConfig()
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotificationsChanged
        for musicEvent in self.__musicEvents:
            self.play(musicEvent.getEventId())

        return

    def destroy(self):
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotificationsChanged
        self.__eraseOverridden(_CLIENT_OVERRIDDEN)

    def __del__(self):
        self.stop()
        self.__soundEvents.clear()

    def restart(self):
        for musicEvent in self.__musicEvents:
            musicEvent.play()

    def play(self, eventId, params=None):
        if eventId is None:
            return
        else:
            newSoundEvent = self.__getEvent(eventId)
            if newSoundEvent is None:
                return
            musicEventId = MusicController._MUSIC_EVENT if eventId < AMBIENT_EVENT_NONE else MusicController._AMBIENT_EVENT
            self.__musicEvents[musicEventId].replace(newSoundEvent, eventId, True)
            if params is not None:
                for paramName, paramValue in params.iteritems():
                    self.setEventParam(eventId, paramName, paramValue)

            return

    def stopMusic(self):
        musicEvent = self.__musicEvents[MusicController._MUSIC_EVENT]
        musicEvent.destroy()

    def stopAmbient(self):
        ambientEvent = self.__musicEvents[MusicController._AMBIENT_EVENT]
        ambientEvent.destroy()

    def stop(self):
        self.stopAmbient()
        self.stopMusic()

    def stopEvent(self, eventId):
        e = self.__getEvent(eventId)
        if e is not None:
            e.stop()
        return

    def muteMusic(self, isMute):
        musicEvent = self.__musicEvents[MusicController._MUSIC_EVENT]
        musicEvent.mute(isMute)

    def setEventParam(self, eventId, paramName, paramValue):
        WWISE.WW_setRTCPGlobal(paramName, paramValue)

    def onEnterArena(self):
        BigWorld.player().arena.onPeriodChange += self.__onArenaStateChanged
        self.__isOnArena = True
        self.__onArenaStateChanged()

    def onLeaveArena(self):
        self.__isOnArena = False
        BigWorld.player().arena.onPeriodChange -= self.__onArenaStateChanged

    def setAccountAttrs(self, accAttrs, restart=False):
        wasPremiumAccount = self.__isPremiumAccount
        from account_helpers import isPremiumAccount
        self.__isPremiumAccount = isPremiumAccount(accAttrs)
        musicEventId = self.__musicEvents[MusicController._MUSIC_EVENT].getEventId()
        if restart and self.__isPremiumAccount != wasPremiumAccount and musicEventId == MUSIC_EVENT_LOBBY:
            self.play(musicEventId)
            self.play(self.__musicEvents[MusicController._AMBIENT_EVENT].getEventId())

    def __getEvent(self, eventId):
        soundEvent = None
        if eventId in _ARENA_EVENTS or eventId in _BATTLE_RESULT_MUSIC_EVENTS:
            soundEvent = self.__getArenaSoundEvent(eventId)
        if soundEvent is None:
            soundEvent = self.__soundEvents.get(eventId)
            if soundEvent is not None:
                if isinstance(soundEvent, list):
                    isPremium = self.__isPremiumAccount
                    idx = 1 if isPremium and len(soundEvent) > 1 else 0
                    soundEvent = soundEvent[idx]
        return soundEvent

    def __onArenaStateChanged(self, *args):
        if self._skipArenaChanges:
            return
        arena = BigWorld.player().arena
        period = arena.period
        if (period == ARENA_PERIOD.PREBATTLE or period == ARENA_PERIOD.BATTLE) and self.__isOnArena:
            if not self.isPlaying(AMBIENT_EVENT_COMBAT):
                self.play(AMBIENT_EVENT_COMBAT)
        if period == ARENA_PERIOD.BATTLE and self.__isOnArena:
            self.play(MUSIC_EVENT_COMBAT)
        elif period == ARENA_PERIOD.AFTERBATTLE:
            self.stopAmbient()
            MusicController.__lastBattleResultEventName = ''
            winnerTeam = arena.periodAdditionalInfo[0]
            if winnerTeam == BigWorld.player().team:
                MusicController.__lastBattleResultEventName = arena.arenaType.battleVictoryMusic if hasattr(arena.arenaType, 'battleVictoryMusic') else ''
            elif winnerTeam == 0:
                MusicController.__lastBattleResultEventName = arena.arenaType.battleDrawMusic if hasattr(arena.arenaType, 'battleDrawMusic') else ''
            else:
                MusicController.__lastBattleResultEventName = arena.arenaType.battleLoseMusic if hasattr(arena.arenaType, 'battleLoseMusic') else ''

    def __getArenaSoundEvent(self, eventId):
        soundEventName = None
        if eventId in _BATTLE_RESULT_MUSIC_EVENTS:
            soundEventName = MusicController.__lastBattleResultEventName
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
        return SoundGroups.g_instance.getSound2D(soundEventName) if soundEventName else None

    def __loadConfig(self):
        eventNames = {}
        xmlPath = 'gui/music_events.xml'
        section = ResMgr.openSection(xmlPath)
        if section is None:
            _xml.raiseWrongXml(None, xmlPath, 'can not open or read')
        for i in section.items():
            s = i[1]
            if i[0] == 'music':
                eventNames[MUSIC_EVENT_LOBBY] = (s.readString('wwlobby'), s.readString('wwlobby'))
                eventNames[MUSIC_EVENT_COMBAT_VICTORY] = s.readString('wwcombat_victory')
                eventNames[MUSIC_EVENT_COMBAT_LOSE] = s.readString('wwcombat_lose')
                eventNames[MUSIC_EVENT_COMBAT_DRAW] = s.readString('wwcombat_draw')
            if i[0] == 'ambient':
                eventNames[AMBIENT_EVENT_LOBBY] = (s.readString('wwlobby'), s.readString('wwlobby'))
                eventNames[AMBIENT_EVENT_SHOP] = (s.readString('wwshop'), s.readString('wwlobby'))
                eventNames[AMBIENT_EVENT_STATISTICS] = (s.readString('wwrating'), s.readString('wwlobby'))
                for key, const in FORT_MAPPING.iteritems():
                    eventNames[const] = (s.readString(key), s.readString(key))

        fallbackEventNames = eventNames.copy()
        self.__overrideEvents(eventNames)
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
                    sound = SoundGroups.g_instance.getSound2D(eventName) if eventName != '' else None
                    if sound is None:
                        sound = SoundGroups.g_instance.getSound2D(fallbackEventName) if fallbackEventName != '' else None
                soundsByName[eventName] = sound
                lstEvents.append(sound)
                if sound is not None:
                    sound.stop()

            prevList = self.__soundEvents.get(eventId, None)
            if prevList is not None:
                for event in prevList:
                    if event is not None:
                        event.stop()

            self.__soundEvents[eventId] = lstEvents

        return

    def __overrideEvents(self, eventNames):
        for eventId, overriddenNames in self.__overriddenEvents.iteritems():
            if overriddenNames:
                if overriddenNames[_SERVER_OVERRIDDEN]:
                    eventNames[eventId] = overriddenNames[_SERVER_OVERRIDDEN]
                elif overriddenNames[_CLIENT_OVERRIDDEN]:
                    eventNames[eventId] = overriddenNames[_CLIENT_OVERRIDDEN]

    def _getSoundEventById(self, soundEventID):
        if soundEventID < AMBIENT_EVENT_NONE:
            musicEventId = MusicController._MUSIC_EVENT
        else:
            musicEventId = MusicController._AMBIENT_EVENT
        soundEvent = self.__musicEvents[musicEventId]
        return soundEvent

    def isPlaying(self, soundEventID):
        soundEvent = self._getSoundEventById(soundEventID)
        return soundEvent.getEventId() == soundEventID and soundEvent.isPlaying()

    def isCompleted(self, soundEventID):
        soundEvent = self._getSoundEventById(soundEventID)
        return soundEvent.getEventId() == soundEventID and not soundEvent.isPlaying()

    def __reloadSounds(self):
        self.__loadConfig()
        for musicEvent in self.__musicEvents:
            self.play(musicEvent.getEventId())

    def __onEventNotificationsChanged(self, notificationsDiff):
        hasChanges = False
        for notification in notificationsDiff['removed']:
            if notification['type'] == _CMD_SERVER_CHANGE_HANGAR_AMBIENT:
                self.__updateOverridden(AMBIENT_EVENT_LOBBY, _SERVER_OVERRIDDEN, None)
                self.__updateOverridden(AMBIENT_EVENT_SHOP, _SERVER_OVERRIDDEN, None)
                self.__updateOverridden(AMBIENT_EVENT_STATISTICS, _SERVER_OVERRIDDEN, None)
                hasChanges = True
            if notification['type'] == _CMD_SERVER_CHANGE_HANGAR_MUSIC:
                self.__updateOverridden(MUSIC_EVENT_LOBBY, _SERVER_OVERRIDDEN, None)
                hasChanges = True

        for notification in notificationsDiff['added']:
            if notification['type'] == _CMD_SERVER_CHANGE_HANGAR_AMBIENT:
                ambientEventName = notification['data']
                self.__updateOverridden(AMBIENT_EVENT_LOBBY, _SERVER_OVERRIDDEN, (ambientEventName, ambientEventName))
                self.__updateOverridden(AMBIENT_EVENT_SHOP, _SERVER_OVERRIDDEN, (ambientEventName, ambientEventName))
                self.__updateOverridden(AMBIENT_EVENT_STATISTICS, _SERVER_OVERRIDDEN, (ambientEventName, ambientEventName))
                hasChanges = True
            if notification['type'] == _CMD_SERVER_CHANGE_HANGAR_MUSIC:
                musicEventNames = [ event.strip() for event in notification['data'].split('|') ]
                musicEventName = musicEventNames[0]
                premiumMusicEventName = musicEventNames[1] if len(musicEventNames) > 1 else musicEventName
                self.__updateOverridden(MUSIC_EVENT_LOBBY, _SERVER_OVERRIDDEN, (musicEventName, premiumMusicEventName))
                hasChanges = True

        if hasChanges:
            self.__reloadSounds()
        return

    def changeHangarSound(self, notificationsDiff):
        self.__onEventNotificationsChanged(notificationsDiff)

    def __loadCustomSounds(self, xmlName):
        settings = ResMgr.openSection('scripts/arena_defs/' + xmlName + '.xml')
        if settings is None:
            return
        else:
            musicName = settings.readString('wwmusic')
            ambientName = settings.readString('wwambientSound')
            combatVictory = settings.readString('wwcombatVictory')
            combatLose = settings.readString('wwcombatLose')
            combatDraw = settings.readString('wwcombatDraw')
            if musicName:
                self.__updateOverridden(MUSIC_EVENT_LOBBY, _CLIENT_OVERRIDDEN, (musicName, musicName))
            if combatVictory:
                self.__updateOverridden(MUSIC_EVENT_COMBAT_VICTORY, _CLIENT_OVERRIDDEN, combatVictory)
            if combatLose:
                self.__updateOverridden(MUSIC_EVENT_COMBAT_LOSE, _CLIENT_OVERRIDDEN, combatLose)
            if combatDraw:
                self.__updateOverridden(MUSIC_EVENT_COMBAT_DRAW, _CLIENT_OVERRIDDEN, combatDraw)
            if ambientName:
                self.__updateOverridden(AMBIENT_EVENT_LOBBY, _CLIENT_OVERRIDDEN, (ambientName, ambientName))
                self.__updateOverridden(AMBIENT_EVENT_SHOP, _CLIENT_OVERRIDDEN, (ambientName, ambientName))
                self.__updateOverridden(AMBIENT_EVENT_STATISTICS, _CLIENT_OVERRIDDEN, (ambientName, ambientName))
            return

    def __updateOverridden(self, eventID, typeId, value):
        music_list = self.__overriddenEvents.setdefault(eventID, [None, None])
        music_list[typeId] = value
        return

    def unloadCustomSounds(self):
        self.__eraseOverridden(_CLIENT_OVERRIDDEN)

    def unloadServerSounds(self, isDisconnect=False):
        if isDisconnect:
            self.__musicEvents = (self.__musicEvents[0], MusicController.MusicEvent())
        self.__eraseOverridden(_SERVER_OVERRIDDEN)
        self.__loadConfig()
        for musicEvent in self.__musicEvents:
            self.play(musicEvent.getEventId())

    def __eraseOverridden(self, index):
        for eventId, overriddenNames in self.__overriddenEvents.iteritems():
            self.__overriddenEvents[eventId][index] = None

        return

    @property
    def skipArenaChanges(self):
        return self._skipArenaChanges

    @skipArenaChanges.setter
    def skipArenaChanges(self, skipArenaChanges):
        self._skipArenaChanges = skipArenaChanges
