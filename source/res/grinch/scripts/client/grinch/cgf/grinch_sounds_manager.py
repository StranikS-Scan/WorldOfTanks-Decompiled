# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: grinch/scripts/client/grinch/cgf/grinch_sounds_manager.py
import BigWorld
import CGF
import WWISE
import logging
import sound_helpers
from constants import IS_CHINA, ARENA_PERIOD
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from helpers.CallbackDelayer import CallbackDelayer, CallbacksSetByID
from cgf_script.bonus_caps_rules import bonusCapsManager
from cgf_script.managers_registrator import onAddedQuery, onRemovedQuery
from presents import PresentComponent
from grinch_common.grinch_constants import ARENA_BONUS_TYPE_CAPS
_logger = logging.getLogger(__name__)

@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class LanguageSwitchManager(CGF.ComponentManager):
    _NAME = 'SWITCH_ext_GRINCH_vo_language'
    _VALUE_NON_RU = 'SWITCH_ext_GRINCH_vo_language_EN'
    _VALUE_CN = 'SWITCH_ext_GRINCH_vo_language_CN'

    def activate(self):
        WWISE.WW_setSwitch(self._NAME, self._getValue())

    @classmethod
    def getSwitchGroupName(cls):
        return cls._NAME

    @classmethod
    def getLanguageSwitch(cls):
        return {cls._NAME: cls._getValue()}

    @classmethod
    def _getValue(cls):
        return cls._VALUE_CN if IS_CHINA else cls._VALUE_NON_RU


class MusicGiftSpawnEvent(object):
    FIRST = '1st'
    SECOND = '2nd'
    LAST = 'last'


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GrinchMusicManager(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _MUSIC_BATTLE_START = 'ev_gift_hunt_music_explore'
    _MUSIC_BATTLE_END = 'ev_gift_hunt_music_end_battle'
    _MUSIC_RECONNECTED = 'ev_gift_hunt_music_reconnect'
    _MUSIC_GIFT_COUNT_DOWN = {MusicGiftSpawnEvent.FIRST: 'ev_gift_hunt_music_spawn_counter',
     MusicGiftSpawnEvent.SECOND: 'ev_gift_hunt_music_spawn_counter',
     MusicGiftSpawnEvent.LAST: 'ev_gift_hunt_music_spawn_counter_last'}
    _MUSIC_GIFT_SPAWNED = {MusicGiftSpawnEvent.FIRST: 'ev_gift_hunt_music_battle',
     MusicGiftSpawnEvent.SECOND: 'ev_gift_hunt_music_battle',
     MusicGiftSpawnEvent.LAST: 'ev_gift_hunt_music_battle_last'}
    _SOUND_GIFT_SPAWN = 'ev_grinch_gameplay_gifts_spawned'
    _COUNT_DOWN_DURATION = 10.0
    _GIFT_SPAWN_EVENT_TIMES = {MusicGiftSpawnEvent.FIRST: 180.0,
     MusicGiftSpawnEvent.SECOND: 300.0,
     MusicGiftSpawnEvent.LAST: 480.0}

    def __init__(self):
        super(GrinchMusicManager, self).__init__()
        self.__delayer = CallbacksSetByID()
        self.__uniqueCBIDs = []
        self.__callbackIDCounter = 0

    def activate(self):
        self.__resetCallbacks()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        arenaPeriod = self.__sessionProvider.shared.arenaPeriod.getPeriod()
        if arenaPeriod == ARENA_PERIOD.BATTLE:
            sound_helpers.play2d(self._MUSIC_RECONNECTED)
            self.__setupMusicEvents()
        return

    def deactivate(self):
        self.__removeCallbacks()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __onArenaPeriodChange(self, *args):
        period, _, _, _ = args
        if period == ARENA_PERIOD.BATTLE:
            sound_helpers.play2d(self._MUSIC_BATTLE_START)
            self.__setupMusicEvents()
        if period == ARENA_PERIOD.AFTERBATTLE:
            self.__removeCallbacks()
            sound_helpers.play2d(self._MUSIC_BATTLE_END)

    def __setupMusicEvents(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if not arena:
            return
        else:
            timeSinceBattleStart = BigWorld.serverTime() - (arena.periodEndTime - arena.periodLength)
            for key, time in self._GIFT_SPAWN_EVENT_TIMES.items():
                if time > timeSinceBattleStart:
                    self.__addCallback(timeSinceBattleStart, time, self._MUSIC_GIFT_SPAWNED.get(key), self._SOUND_GIFT_SPAWN)
                timeCountdown = time - self._COUNT_DOWN_DURATION
                if timeCountdown > timeSinceBattleStart:
                    self.__addCallback(timeSinceBattleStart, timeCountdown, self._MUSIC_GIFT_COUNT_DOWN.get(key))

            return

    def __addCallback(self, timeSinceBattleStart, value, musicEventName, soundEventName=None):
        uniqueCBID = self.__getUniqueCallbackID()
        delayTime = value - timeSinceBattleStart
        self.__delayer.delayCallback(uniqueCBID, delayTime, self.__triggerMusicEvent, musicEventName, soundEventName)

    def __getUniqueCallbackID(self):
        self.__callbackIDCounter += 1
        self.__uniqueCBIDs.append(self.__callbackIDCounter)
        return self.__callbackIDCounter

    def __removeCallbacks(self):
        for cbID in self.__uniqueCBIDs:
            self.__delayer.stopCallback(cbID)

        self.__uniqueCBIDs = []

    def __resetCallbacks(self):
        self.__uniqueCBIDs = []
        self.__callbackIDCounter = 0

    def __triggerMusicEvent(self, musicEventName, soundEventName=None):
        sound_helpers.play2d(musicEventName)
        if soundEventName:
            sound_helpers.play2d(soundEventName)


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GiftPickupAndDeliverSoundPlayer(CGF.ComponentManager):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _GRINCH_GIFT_PICKUP = 'ev_grinch_gameplay_gift_pickup'
    _GRINCH_GIFT_PICKUP_FULL = 'ev_grinch_gameplay_gift_pickup_last'
    _GRINCH_GIFT_DELIVERED = 'ev_grinch_gameplay_gift_delivered'
    _GRINCH_GIFT_LOST = 'ev_grinch_gameplay_gift_lost'

    def __init__(self):
        super(GiftPickupAndDeliverSoundPlayer, self).__init__()
        self.__giftCounter = 0

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled += self.__onVehicleKilled
        return

    def deactivate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onVehicleKilled -= self.__onVehicleKilled
        return

    @onAddedQuery(CGF.GameObject, PresentComponent)
    def onPresentComponentAdded(self, go, present):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle and sound_helpers.isPlayerVehicle(vehicle):
            if self.__giftCounter < 3:
                sound_helpers.play2d(self._GRINCH_GIFT_PICKUP)
            else:
                sound_helpers.play2d(self._GRINCH_GIFT_PICKUP_FULL)
            self.__giftCounter += 1

    @onRemovedQuery(CGF.GameObject, PresentComponent)
    def onPresentComponentRemoved(self, go, present):
        vehicle = sound_helpers.getVehicle(go, self.spaceID)
        if vehicle and sound_helpers.isPlayerVehicle(vehicle) and self.__giftCounter > 0:
            self.__giftCounter = 0
            sound_helpers.play2d(self._GRINCH_GIFT_DELIVERED)

    def __onVehicleKilled(self, *args):
        victimID, _, _, _, _ = args
        if victimID == BigWorld.player().playerVehicleID:
            self.__giftCounter = 0
        vehicle = BigWorld.entities.get(victimID, None)
        if vehicle:
            sound_helpers.playSoundPos(self._GRINCH_GIFT_LOST, vehicle.position)
        return


@bonusCapsManager(ARENA_BONUS_TYPE_CAPS.GRINCH, CGF.DomainOption.DomainClient)
class GameplayEnterSoundPlayer(CGF.ComponentManager, CallbackDelayer):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)
    _GRINCH_VO_PREBATTLE = 'grinch_vo_prebattle'
    _PREBATTLE_VO_START_TIME = 9.0
    _GRINCH_GAMEPLAY_EXIT = 'ev_gift_hunt_wind_utility_reset'

    def __init__(self):
        super(GameplayEnterSoundPlayer, self).__init__()
        CallbackDelayer.__init__(self)

    def activate(self):
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange += self.__onArenaPeriodChange
        return

    def deactivate(self):
        self.__playExitSound()
        self.clearCallbacks()
        arena = getattr(BigWorld.player(), 'arena', None)
        if arena is not None:
            arena.onPeriodChange -= self.__onArenaPeriodChange
        return

    def __onArenaPeriodChange(self, *args):
        period, periodEndTime, _, _ = args
        if period == ARENA_PERIOD.PREBATTLE:
            timeToPeriodEnd = max(periodEndTime - BigWorld.serverTime(), 0.0)
            if timeToPeriodEnd > self._PREBATTLE_VO_START_TIME:
                notificationDelay = max(timeToPeriodEnd - self._PREBATTLE_VO_START_TIME, 0.0)
                self.delayCallback(notificationDelay, self.__playPrebattleVo)

    def __playPrebattleVo(self):
        soundNotifications = getattr(BigWorld.player(), 'soundNotifications', None)
        if soundNotifications is not None:
            soundNotifications.play(self._GRINCH_VO_PREBATTLE)
        return

    def __playExitSound(self):
        sound_helpers.play2d(self._GRINCH_GAMEPLAY_EXIT)
