# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/MusicControllerWWISE.py
import random
from collections import namedtuple
from typing import Set, Any
import WWISE
import BigWorld
import ResMgr
from PlayerEvents import g_playerEvents
from constants import ARENA_PERIOD, ARENA_BONUS_TYPE
from helpers import isPlayerAvatar
from ids_generators import SequenceIDGenerator
from items import _xml
from helpers import dependency
from skeletons.gui.battle_results import IBattleResultsService
from skeletons.gui.game_control import ISpecialSoundCtrl
from skeletons.account_helpers.settings_core import ISettingsCore
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
_ON_VEHICLE_KILLED_EVENT = 'music_stinger'
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


def play(eventId=None):
    if g_musicController is not None:
        if eventId is None:
            g_musicController.play(MUSIC_EVENT_LOBBY, None, True)
            g_musicController.play(AMBIENT_EVENT_LOBBY, None, True)
        else:
            g_musicController.play(eventId)
    return


class HW20BattleResultsStories(object):
    _DIFFICULTY_LOW = 1
    _DIFFICULTY_MED = 2
    _DIFFICULTY_HIGH = 3
    __settingsCore = dependency.descriptor(ISettingsCore)
    __battleResults = dependency.descriptor(IBattleResultsService)
    _NarrativeSoundInfo = namedtuple('_NarrativeSoundInfo', ('wasPlayed', 'eventId', 'storeKey', 'index'))

    def __init__(self):
        self.__arenasDifficultyCache = {}

    def init(self):
        self.__battleResults.onResultPosted += self.__onBattleResultPosted

    def destroy(self):
        self.__battleResults.onResultPosted -= self.__onBattleResultPosted

    def getSoundEvents(self, event, wwSetup, arenaUniqueID):
        soundEvents = []
        if event == MUSIC_EVENT_COMBAT_VICTORY:
            difficulty = self.__getBattleDifficulty(arenaUniqueID)
            available = self.__getAvailableSoundsInfoForDifficulty(difficulty)
            if available:
                chosenSoundInfo = random.choice(available)
                self.__markSoundAsPlayed(chosenSoundInfo.index, chosenSoundInfo.storeKey)
                soundEvents.append(chosenSoundInfo.eventId)
            if difficulty in (self._DIFFICULTY_LOW, self._DIFFICULTY_MED, self._DIFFICULTY_HIGH):
                from gui.sounds.sound_constants import HW20SoundConsts
                soundEvents.append(HW20SoundConsts.HANGAR_BR_WIN_VO_TEMPLATE.format(difficulty))
        return soundEvents

    def __getBattleDifficulty(self, arenaUniqueID):
        return self.__arenasDifficultyCache.get(arenaUniqueID)

    def __getAvailableSoundsInfoForDifficulty(self, difficulty):
        from gui.sounds.sound_constants import HW20SoundConsts
        from account_helpers.settings_core.settings_constants import Hw20StorageKeys
        allSoundsInfo = []
        if difficulty == self._DIFFICULTY_HIGH:
            allSoundsInfo.extend(self.__getUnpackedInfo(HW20SoundConsts.HANGAR_BR_VOS_HIGH, Hw20StorageKeys.ROASTER_HIGH))
        if difficulty in (self._DIFFICULTY_HIGH, self._DIFFICULTY_MED):
            allSoundsInfo.extend(self.__getUnpackedInfo(HW20SoundConsts.HANGAR_BR_VOS_MED, Hw20StorageKeys.ROASTER_MED))
        if difficulty in (self._DIFFICULTY_HIGH, self._DIFFICULTY_MED, self._DIFFICULTY_LOW):
            allSoundsInfo.extend(self.__getUnpackedInfo(HW20SoundConsts.HANGAR_BR_VOS_LOW, Hw20StorageKeys.ROASTER_LOW))
        availableSoundsInfo = [ x for x in allSoundsInfo if not x.wasPlayed ]
        return availableSoundsInfo

    def __markSoundAsPlayed(self, soundIndex, storeKey):
        flagsPacked = self.__settingsCore.serverSettings.getHW20NarrativeSettings(storeKey, 0)
        flagsPacked |= 1 << soundIndex
        self.__settingsCore.serverSettings.setHW20NarrativeSettings({storeKey: flagsPacked})

    def __getUnpackedInfo(self, wwEventList, storeKey):
        flagsPacked = self.__settingsCore.serverSettings.getHW20NarrativeSettings(storeKey, 0)
        bitFlags = bin(flagsPacked)[2::].zfill(len(wwEventList))[::-1]
        return [ self._NarrativeSoundInfo(wasPlayed=True if flag == '1' else False, index=i, eventId=wwEventId, storeKey=storeKey) for i, (flag, wwEventId) in enumerate(zip(bitFlags, wwEventList)) ]

    def __onBattleResultPosted(self, reusableBattleResultInfo, *args):
        arenaUniqueID = reusableBattleResultInfo.arenaUniqueID
        if reusableBattleResultInfo.common.arenaBonusType == ARENA_BONUS_TYPE.EVENT_BATTLES:
            arenaDifficulty = reusableBattleResultInfo.personal.difficultyLevel
            self.__arenasDifficultyCache[arenaUniqueID] = arenaDifficulty


class _MusicEvent(object):
    _idGen = SequenceIDGenerator()

    def __init__(self, event=None, eventId=None):
        self.__muted = False
        self.__event = event
        self.__eventID = eventId
        self.__id = self._idGen.next()

    def replace(self, event, eventId, unlink=True):
        if self.__event is not None:
            if self.__event.name != event.name:
                if unlink:
                    self.__event.unlink()
            else:
                self.__eventID = eventId
                if not self.__event.isPlaying:
                    self.__event.play()
                return
        self.__eventID = eventId
        self.__event = event
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

    def param(self, paramName):
        return self.__event.param(paramName) if self.__event is not None else None

    @property
    def ownId(self):
        return self.__id

    @property
    def eventId(self):
        return self.__eventID

    @property
    def wwSoundName(self):
        return self.__event.name if self.__event is not None else None

    def isPlaying(self):
        return self.__event.isPlaying if self.__event is not None else False

    def play(self):
        if not self.isPlaying():
            self.__event.play()

    def destroy(self, force=False):
        if self.__event is not None:
            if force:
                self.__event.stop(5.0)
            else:
                self.__event.unlink()
            self.__event = None
            self.__eventID = None
        return


class _MusicEventsContainer(object):

    def __init__(self, wwSounds=None):
        self.__wwSounds = wwSounds or []
        musicEvents = [ _MusicEvent(wwSound) for wwSound in self.__wwSounds ]
        self._musicEvents = {event.ownId:event for event in musicEvents}
        self.__eventID = None
        return

    @property
    def _musicEventsByWWSoundName(self):
        return {event.wwSoundName:event for event in self._musicEvents.values()}

    def replace(self, sounds, eventId, unlink=True):
        musicEventsNames = set(self._musicEventsByWWSoundName)
        soundsByNames = {wwSound.name:wwSound for wwSound in sounds}
        soundsNames = set(soundsByNames)
        toReplace = musicEventsNames & soundsNames
        toRemove = musicEventsNames & (musicEventsNames ^ soundsNames)
        toAdd = soundsNames & (musicEventsNames ^ soundsNames)
        for soundName in toReplace:
            self._musicEventsByWWSoundName[soundName].replace(soundsByNames[soundName], eventId, unlink)

        for toAddName, toRemoveName in zip(toAdd, toRemove):
            toRemove.discard(toRemoveName)
            toAdd.discard(toAddName)
            self._musicEventsByWWSoundName[toRemoveName].replace(soundsByNames[toAddName], eventId, unlink)

        for soundName in toRemove:
            _id = self._musicEventsByWWSoundName[soundName].ownId
            event = self._musicEvents.pop(_id)
            event.destroy()

        for soundName in toAdd:
            newMusicEvent = _MusicEvent(soundsByNames[soundName], eventId)
            newMusicEvent.play()
            self._musicEvents[newMusicEvent.ownId] = newMusicEvent

    def mute(self, isMute):
        _ = [ event.mute(isMute) for event in self._musicEvents.values() ]

    @property
    def eventId(self):
        return self.__eventID

    def isPlaying(self):
        return any((event.isPlaying() for event in self._musicEvents.values()))

    def stop(self):
        _ = [ event.stop() for event in self._musicEvents.values() ]

    def destroy(self, force=False):
        _ = [ event.destroy(force) for event in self._musicEvents.values() ]


class MusicController(object):
    __specialSounds = dependency.descriptor(ISpecialSoundCtrl)
    __lastBattleArenaWwSetup = None
    __lastBattleArenaUniqueID = None
    __helpers = None

    def __init__(self):
        self.__overriddenEvents = {}
        self.__music = _MusicEventsContainer()
        self.__ambient = _MusicEventsContainer()
        self.__sndEventMusic = None
        self.__soundEvents = {MUSIC_EVENT_NONE: None,
         AMBIENT_EVENT_NONE: None}
        self._skipArenaChanges = False
        self.__vehicleKilled = False
        self.__helpers = {'hw20BattleResultsStories': HW20BattleResultsStories()}
        self.init()
        return

    def init(self, path=None):
        self.__isOnArena = False
        self.__isPremiumAccount = False
        if path is not None:
            self.__loadCustomSounds(path)
        self.__loadConfig()
        g_playerEvents.onEventNotificationsChanged += self.__onEventNotificationsChanged
        for helper in self.__helpers.itervalues():
            helper.init()

        return

    def destroy(self):
        g_playerEvents.onEventNotificationsChanged -= self.__onEventNotificationsChanged
        self.__eraseOverridden(_CLIENT_OVERRIDDEN)
        for helper in self.__helpers.itervalues():
            helper.destroy()

    def __del__(self):
        self.stop()
        self.__soundEvents.clear()
        for helper in self.__helpers.itervalues():
            helper.destroy()

    def play(self, eventId, params=None, checkIsPlaying=False):
        if eventId is None:
            return
        else:
            newSoundEvents = self.__getEvent(eventId)
            if not newSoundEvents:
                return
            eventSnd = self._getSoundEventById(eventId)
            unlink = bool(eventId < AMBIENT_EVENT_NONE)
            if checkIsPlaying and eventSnd.isPlaying():
                return
            eventSnd.replace(newSoundEvents, eventId, unlink)
            if params is not None:
                for paramName, paramValue in params.iteritems():
                    self.setEventParam(paramName, paramValue)

            return

    def stopMusic(self):
        self.__music.destroy()

    def stopAmbient(self, force=False):
        self.__ambient.destroy(force)

    def stop(self):
        self.stopAmbient()
        self.stopMusic()

    def stopEvent(self, eventId):
        events = self.__getEvent(eventId)
        for e in events:
            e.stop()

    def muteMusic(self, isMute):
        self.__music.mute(isMute)

    def setEventParam(self, paramName, paramValue):
        WWISE.WW_setRTCPGlobal(paramName, paramValue)

    def onEnterArena(self):
        BigWorld.player().arena.onPeriodChange += self.__onArenaStateChanged
        BigWorld.player().arena.onVehicleKilled += self.__onArenaVehicleKilled
        self.__isOnArena = True
        self.__vehicleKilled = False
        self.__onArenaStateChanged()

    def onLeaveArena(self):
        self.__isOnArena = False
        BigWorld.player().arena.onVehicleKilled -= self.__onArenaVehicleKilled
        BigWorld.player().arena.onPeriodChange -= self.__onArenaStateChanged

    def setAccountPremiumState(self, isPremium, restart=False):
        wasPremiumAccount = self.__isPremiumAccount
        self.__isPremiumAccount = isPremium
        musicEventId = self.__music.eventId
        if restart and self.__isPremiumAccount != wasPremiumAccount and musicEventId == MUSIC_EVENT_LOBBY:
            self.play(musicEventId)
            self.play(self.__ambient.eventId)

    def __getEvent(self, eventId):
        soundEvents = []
        if eventId in _ARENA_EVENTS or eventId in _BATTLE_RESULT_MUSIC_EVENTS:
            soundEvents = self.__getArenaSoundEvents(eventId)
        if not soundEvents:
            soundEvent = self.__soundEvents.get(eventId)
            if soundEvent is not None:
                if isinstance(soundEvent, list):
                    isPremium = self.__isPremiumAccount
                    idx = 1 if isPremium and len(soundEvent) > 1 else 0
                    soundEvents = [soundEvent[idx]]
        return soundEvents

    def __onArenaStateChanged(self, *args):
        if self._skipArenaChanges:
            return
        else:
            arena = BigWorld.player().arena
            period = arena.period
            if period == ARENA_PERIOD.PREBATTLE or period == ARENA_PERIOD.BATTLE:
                from BattleReplay import g_replayCtrl
                if self.__isOnArena and not g_replayCtrl.isTimeWarpInProgress:
                    if not self.isPlaying(AMBIENT_EVENT_COMBAT):
                        self.play(AMBIENT_EVENT_COMBAT)
            if period == ARENA_PERIOD.BATTLE and self.__isOnArena:
                self.play(MUSIC_EVENT_COMBAT)
                self.__lastBattleArenaUniqueID = arena.arenaUniqueID
            elif period == ARENA_PERIOD.AFTERBATTLE:
                wwSetup = self.__specialSounds.arenaMusicSetup
                self.stopAmbient()
                self.__lastBattleArenaWwSetup = {}
                self.__lastBattleArenaUniqueID = arena.arenaUniqueID
                if wwSetup is not None:
                    self.__lastBattleArenaWwSetup = wwSetup.copy()
                    import SoundGroups
                    SoundGroups.g_instance.playSound2D(wwSetup.get('wwmusicEndbattleStop', ''))
            return

    def __onArenaVehicleKilled(self, *args):
        if not self.__vehicleKilled:
            WWISE.WW_eventGlobal(_ON_VEHICLE_KILLED_EVENT)
            self.__vehicleKilled = True

    def __getArenaSoundEvents(self, eventId):
        soundEvents = []
        if eventId == MUSIC_EVENT_COMBAT_VICTORY:
            soundEvents = [self.__lastBattleArenaWwSetup.get('wwmusicResultWin'), self.__lastBattleArenaWwSetup.get('wwmusicVoResultWin')]
        elif eventId == MUSIC_EVENT_COMBAT_LOSE:
            soundEvents = [self.__lastBattleArenaWwSetup.get('wwmusicResultDefeat'), self.__lastBattleArenaWwSetup.get('wwmusicVoResultDefeat')]
        elif eventId == MUSIC_EVENT_COMBAT_DRAW:
            soundEvents = [self.__lastBattleArenaWwSetup.get('wwmusicResultDrawn'), self.__lastBattleArenaWwSetup.get('wwmusicVoiceoverResultDrawn')]
        else:
            player = BigWorld.player()
            if not isPlayerAvatar():
                return []
            if player.arena is None:
                return []
            arenaType = player.arena.arenaType
            if eventId == MUSIC_EVENT_COMBAT_LOADING:
                wwmusicSetup = self.__specialSounds.arenaMusicSetup
                if wwmusicSetup is not None:
                    soundEvents = [wwmusicSetup.get('wwmusicLoading'), wwmusicSetup.get('wwmusicLoadingVoiceover')]
            elif eventId == AMBIENT_EVENT_COMBAT:
                soundEvents.append(arenaType.ambientSound)
        soundEvents.extend(self.__getSoundsFromHelpers(self.__lastBattleArenaWwSetup, eventId, self.__lastBattleArenaUniqueID))
        if soundEvents:
            import SoundGroups
            return [ SoundGroups.g_instance.getSound2D(soundName) for soundName in soundEvents if soundName ]
        else:
            return []

    def __getSoundsFromHelpers(self, wwSetup, event, arenaUniqueID):
        sounds = []
        if wwSetup is not None:
            for helperName in wwSetup.get('helpers', '').split():
                sounds.extend(self.__helpers[helperName].getSoundEvents(event, wwSetup, arenaUniqueID))

        return sounds

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

        self.__overrideEvents(eventNames)
        for eventId, names in eventNames.items():
            if not isinstance(names, tuple):
                names = (names,)
            soundNames = []
            for eventName in names:
                if eventName not in soundNames:
                    soundNames.append(eventName)

            newSounds = []
            prevSounds = self.__soundEvents.get(eventId, None)
            unlink = eventId < AMBIENT_EVENT_NONE
            for soundName in soundNames:
                eventExist = False
                if prevSounds is not None:
                    for i in xrange(len(prevSounds)):
                        event = prevSounds[i]
                        if event is not None and event.name == soundName:
                            newSounds.append(event)
                            prevSounds[i] = None
                            eventExist = True
                            break

                if not eventExist:
                    import SoundGroups
                    newSounds.append(SoundGroups.g_instance.getSound2D(soundName))

            if prevSounds is not None:
                for event in prevSounds:
                    if event is not None:
                        if unlink:
                            event.unlink()

            self.__soundEvents[eventId] = newSounds

        ResMgr.purge(xmlPath, True)
        return

    def __overrideEvents(self, eventNames):
        for eventId, overriddenNames in self.__overriddenEvents.iteritems():
            if overriddenNames:
                if overriddenNames[_SERVER_OVERRIDDEN]:
                    eventNames[eventId] = overriddenNames[_SERVER_OVERRIDDEN]
                elif overriddenNames[_CLIENT_OVERRIDDEN]:
                    eventNames[eventId] = overriddenNames[_CLIENT_OVERRIDDEN]

    def _getSoundEventById(self, soundEventID):
        return self.__music if soundEventID < AMBIENT_EVENT_NONE else self.__ambient

    def isPlaying(self, soundEventID):
        soundEvent = self._getSoundEventById(soundEventID)
        return soundEvent.eventId == soundEventID and soundEvent.isPlaying()

    def isCompleted(self, soundEventID):
        soundEvent = self._getSoundEventById(soundEventID)
        return soundEvent.eventId == soundEventID and not soundEvent.isPlaying()

    def __reloadSounds(self):
        self.__loadConfig()
        self.play(self.__music.eventId)
        self.play(self.__ambient.eventId)

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
            self.__ambient = _MusicEventsContainer()
        self.__eraseOverridden(_SERVER_OVERRIDDEN)
        self.__loadConfig()
        self.play(self.__music.eventId)
        self.play(self.__ambient.eventId)

    def __eraseOverridden(self, index):
        for eventId, _ in self.__overriddenEvents.iteritems():
            self.__overriddenEvents[eventId][index] = None

        return

    @property
    def skipArenaChanges(self):
        return self._skipArenaChanges

    @skipArenaChanges.setter
    def skipArenaChanges(self, skipArenaChanges):
        self._skipArenaChanges = skipArenaChanges
