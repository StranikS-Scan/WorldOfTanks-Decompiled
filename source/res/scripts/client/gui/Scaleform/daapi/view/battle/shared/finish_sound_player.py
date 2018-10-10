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
        self.__arenaPeriod = None
        self.__arenaTotalTime = None
        return

    def updateDeadVehicles(self, aliveAllies, deadAllies, aliveEnemies, deadEnemies):
        if self.__vehCheckAllowed:
            allies = aliveAllies | deadAllies
            enemies = aliveEnemies | deadEnemies
            if allies and deadAllies == allies or enemies and deadEnemies == enemies:
                self.__onRoundFinished(_SOUND_EVENTS.LAST_KILL)

    def setTeamBaseCaptured(self, clientID, playerTeam):
        self.__onRoundFinished(_SOUND_EVENTS.BASE_CAPTURED)

    def addCapturedTeamBase(self, clientID, playerTeam, timeLeft, invadersCnt):
        self.__onRoundFinished(_SOUND_EVENTS.BASE_CAPTURED)

    def setPeriod(self, period):
        self.__arenaPeriod = period
        self.__checkTimeCondition()

    def setTotalTime(self, totalTime):
        self.__arenaTotalTime = totalTime
        self.__checkTimeCondition()

    def _playSound(self, soundID):
        SoundGroups.g_instance.playSound2D(soundID)

    def __checkTimeCondition(self):
        if self.__arenaTotalTime == _BATTLE_END_SOUND_TIME and self.__arenaPeriod == ARENA_PERIOD.BATTLE:
            self.__onRoundFinished(_SOUND_EVENTS.TIME_IS_OVER)

    def __onRoundFinished(self, soundID):
        if not self.__isPlaying:
            self._playSound(soundID)
            self.__isPlaying = True
