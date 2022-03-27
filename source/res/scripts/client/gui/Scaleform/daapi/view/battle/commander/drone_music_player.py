# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/commander/drone_music_player.py
import WWISE
from gui.Scaleform.daapi.view.battle.shared.drone_music_player import DroneMusicPlayer, _delegate, _MusicID
from gui.sounds.r4_sound_constants import R4_SOUND

class CommanderDroneMusicPlayer(DroneMusicPlayer):

    def __init__(self):
        super(CommanderDroneMusicPlayer, self).__init__()
        self.__currentMusicState = None
        return

    @_delegate
    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        self.__updateMusicState()

    def _validateConditions(self):
        satisfied = [ c for c in self._conditions if c.isSatisfied() ]
        if satisfied:
            isPlaying = self._playingMusicID is not None
            if not isPlaying:
                self._setPlayingMusicID(_MusicID.INTENSIVE)
                self._playMusic()
                self.__updateMusicState()
        return

    def __getNumAllyVehiclesAlive(self):
        vehicles = self.sessionProvider.dynamic.rtsCommander.vehicles
        numAllyVehiclesAlive = len(vehicles.values(lambda v: not (v.isObserver or v.isCommander) and not v.isSupply and v.isAlly and v.isAlive))
        return numAllyVehiclesAlive

    def __getMusicState(self):
        numAllyVehiclesAlive = self.__getNumAllyVehiclesAlive()
        stateGroupAndState = R4_SOUND.R4_ALLIES_REMAIN_MUSIC_STATES.get(numAllyVehiclesAlive, None)
        return R4_SOUND.R4_ALLY_DESTROYED_MUSIC_STATE_DEFAULT if stateGroupAndState is None else stateGroupAndState

    def __updateMusicState(self):
        if not self._playingMusicID:
            return
        stateGroupAndState = self.__getMusicState()
        if not self.__currentMusicState or self.__currentMusicState != stateGroupAndState:
            WWISE.WW_setState(stateGroupAndState[0], stateGroupAndState[1])
            self.__currentMusicState = stateGroupAndState
