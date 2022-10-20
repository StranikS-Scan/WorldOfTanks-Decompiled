# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/shared/finish_sound_player.py
import SoundGroups
from constants import ARENA_PERIOD
from gui.battle_control.controllers.period_ctrl import IAbstractPeriodView
from helpers import dependency
from gui.battle_control.controllers.battle_field_ctrl import IBattleFieldListener
from gui.battle_control.controllers.team_bases_ctrl import ITeamBasesListener
from skeletons.gui.battle_session import IBattleSessionProvider
_BATTLE_END_SOUND_TIME = 2

class _SOUND_EVENTS(object):
    LAST_KILL = 'end_battle_last_kill'
    BASE_CAPTURED = 'end_battle_capture_base'
    TIME_IS_OVER = 'time_over'


class FinishSoundPlayer(IBattleFieldListener, ITeamBasesListener, IAbstractPeriodView):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(FinishSoundPlayer, self).__init__()
        self.__isPlaying = False
        self.__vehCheckAllowed = not self.sessionProvider.arenaVisitor.isArenaFogOfWarEnabled()
        self._arenaPeriod = None
        self._arenaTotalTime = None
        return

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        isEventBattle = self.sessionProvider.arenaVisitor.gui.isEventBattle()
        if not isEventBattle and self.__vehCheckAllowed:
            allies = aliveAllies | deadAllies
            enemies = aliveEnemies | deadEnemies
            if allies and deadAllies == allies or enemies and deadEnemies == enemies:
                self._playRoundFinished(_SOUND_EVENTS.LAST_KILL)

    def setTeamBaseCaptured(self, clientID, playerTeam):
        self._playRoundFinished(_SOUND_EVENTS.BASE_CAPTURED)

    def addCapturedTeamBase(self, clientID, playerTeam, timeLeft, invadersCnt):
        self._playRoundFinished(_SOUND_EVENTS.BASE_CAPTURED)

    def setPeriod(self, period):
        self._arenaPeriod = period

    def setTotalTime(self, totalTime):
        self._arenaTotalTime = totalTime
        self._checkTimeCondition()

    def _playSound(self, soundID):
        SoundGroups.g_instance.playSound2D(soundID)

    def _checkTimeCondition(self):
        if self._arenaPeriod == ARENA_PERIOD.BATTLE and self._arenaTotalTime == _BATTLE_END_SOUND_TIME:
            self._playRoundFinished(_SOUND_EVENTS.TIME_IS_OVER)

    def _playRoundFinished(self, soundID):
        if not self.__isPlaying:
            self._playSound(soundID)
            self.__isPlaying = True
