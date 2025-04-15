# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: fall_tanks/scripts/client/fall_tanks/gui/battle_control/controllers/sound_ctrls/race_music_sound_player.py
import typing
from enum import Enum
import WWISE
from fall_tanks.gui.battle_control.mixins import FallTanksBattleMixin, PostmortemMixin
from fall_tanks.gui.feature.fall_tanks_sounds import FallTanksSounds
from gui.battle_control.controllers.sound_ctrls.common import SoundPlayer
from gui.battle_control.arena_info.interfaces import IArenaLoadController
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
if typing.TYPE_CHECKING:
    from fall_tanks.gui.battle_control.arena_info.interfaces import IFallTanksVehicleInfo

class FallTanksMusicState(Enum):
    WAITING = 'waiting'
    CHECKPOINT_0 = 'checkpoint0'
    CHECKPOINT_1 = 'checkpoint1'
    CHECKPOINT_2 = 'checkpoint2'
    CHECKPOINT_3 = 'checkpoint3'
    OBSERVER = 'observer'


_CHECKPOINT_TO_STATE = {-1: FallTanksMusicState.WAITING,
 0: FallTanksMusicState.CHECKPOINT_0,
 1: FallTanksMusicState.CHECKPOINT_1,
 2: FallTanksMusicState.CHECKPOINT_2,
 3: FallTanksMusicState.CHECKPOINT_3,
 4: FallTanksMusicState.CHECKPOINT_3}
_STATE_TO_EVENT = {FallTanksMusicState.WAITING: FallTanksSounds.MUSIC_INTRO,
 FallTanksMusicState.CHECKPOINT_0: FallTanksSounds.MUSIC_RACE_00,
 FallTanksMusicState.CHECKPOINT_1: FallTanksSounds.MUSIC_RACE_01,
 FallTanksMusicState.CHECKPOINT_2: FallTanksSounds.MUSIC_RACE_02,
 FallTanksMusicState.CHECKPOINT_3: FallTanksSounds.MUSIC_RACE_03,
 FallTanksMusicState.OBSERVER: FallTanksSounds.MUSIC_OBSERVER}

class RaceMusicSoundPlayer(SoundPlayer, FallTanksBattleMixin, PostmortemMixin, IArenaLoadController):
    __sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        self.__isInPostmortem = False
        self.__fallTanksAttachedInfo = None
        self.__musicState = None
        self.__isArenaLoaded = False
        self.__sessionProvider.addArenaCtrl(self)
        return

    def init(self):
        super(RaceMusicSoundPlayer, self).init()
        self._playSound2D(FallTanksSounds.UTILITY_BATTLE_START)
        self._playSound2D(FallTanksSounds.MUSIC_INTRO)

    def destroy(self):
        self.__sessionProvider.removeArenaCtrl(self)
        self.__isArenaLoaded = False
        self.__isInPostmortem = False
        self.__fallTanksAttachedInfo = None
        self.__musicState = None
        self._playSound2D(FallTanksSounds.UTILITY_BATTLE_STOP)
        super(RaceMusicSoundPlayer, self).destroy()
        return

    def arenaLoadCompleted(self):
        self.__isArenaLoaded = True
        self.__onFallTanksAttachedInfoUpdate(self.getFallTanksAttachedVehicleInfo())

    def _subscribe(self):
        self.startFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)
        self.startPostmortemListening(self.__onPostMortemSwitched, self.__onRespawnBaseMoving)
        self.__onFallTanksAttachedInfoUpdate(self.getFallTanksAttachedVehicleInfo())
        self.__onPostmortemUpdate(self.isInPostmortem())

    def _unsubscribe(self):
        self.stopPostmortemListening(self.__onPostMortemSwitched, self.__onRespawnBaseMoving)
        self.stopFallTanksAttachedListening(self.__onFallTanksAttachedInfoUpdate)

    def __invalidateMusicState(self):
        if not self.__isArenaLoaded:
            return
        else:
            musicState = None
            if self.__fallTanksAttachedInfo.isPlayerVehicleInRace:
                musicState = _CHECKPOINT_TO_STATE[self.__fallTanksAttachedInfo.checkpoint]
            elif self.__isInPostmortem:
                musicState = FallTanksMusicState.OBSERVER
            if musicState is not None and musicState != self.__musicState:
                self._playSound2D(_STATE_TO_EVENT.get(musicState))
            self.__musicState = musicState
            return

    def __onFallTanksAttachedInfoUpdate(self, attachedInfo):
        self.__fallTanksAttachedInfo = attachedInfo
        self.__invalidateMusicState()

    def __onPostmortemUpdate(self, isInPostmortem):
        if not isInPostmortem and self.__isInPostmortem:
            self._playSound2D(FallTanksSounds.RESPAWN_EVENT)
        respawnState = FallTanksSounds.RESPAWN_STATE_OFF
        if isInPostmortem and self.__fallTanksAttachedInfo.isPlayerVehicleInRace:
            respawnState = FallTanksSounds.RESPAWN_STATE_ON
        WWISE.WW_setState(FallTanksSounds.RESPAWN_STATE, respawnState)
        self.__isInPostmortem = isInPostmortem

    def __onPostMortemSwitched(self, _, __):
        self.__onPostmortemUpdate(True)
        self.__invalidateMusicState()

    def __onRespawnBaseMoving(self):
        self.__onPostmortemUpdate(False)
