# Python bytecode 2.7 (decompiled from Python 2.7)
# Embedded file name: scripts/client/gui/Scaleform/daapi/view/battle/epic/reinforcement_panel.py
from gui.Scaleform.daapi.view.meta.EpicReinforcementPanelMeta import EpicReinforcementPanelMeta
import BigWorld
from helpers import dependency
from skeletons.gui.battle_session import IBattleSessionProvider
from constants import ARENA_PERIOD
from gui.battle_control.arena_info.interfaces import IArenaPeriodController
from helpers import time_utils
from gui.battle_control.avatar_getter import getSoundNotifications
from gui.sounds.epic_sound_constants import EPIC_SOUND

class EpicReinforcementPanel(EpicReinforcementPanelMeta, IArenaPeriodController):
    sessionProvider = dependency.descriptor(IBattleSessionProvider)

    def __init__(self):
        super(EpicReinforcementPanel, self).__init__()
        self.__timestampSent = False
        self.__timestamp = -1
        self.__timeCB = None
        return

    def setPeriodInfo(self, period, endTime, length, additionalInfo, soundID):
        self.__onPeriodChange(period)

    def invalidatePeriodInfo(self, period, endTime, length, additionalInfo):
        self.__onPeriodChange(period)

    def _populate(self):
        super(EpicReinforcementPanel, self)._populate()
        self.sessionProvider.addArenaCtrl(self)
        playerComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerComp is not None:
            playerComp.onReinforcementTimerUpdated += self.__onReinforcementTimerUpdated
            self.__onReinforcementTimerUpdated(playerComp.reinforcementTimer)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onTeamRespawnLivesRestored += self.__onTeamRespawnLivesRestored
            ctrl.onRespawnVisibilityChanged += self.__onRespawnVisibilityChanged
            ctrl.onPlayerRespawnLivesUpdated += self.__onRespawnLivesUpdated
        return

    def _dispose(self):
        super(EpicReinforcementPanel, self)._dispose()
        self.sessionProvider.removeArenaCtrl(self)
        playerComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
        if playerComp is not None:
            playerComp.onReinforcementTimerUpdated -= self.__onReinforcementTimerUpdated
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onTeamRespawnLivesRestored -= self.__onTeamRespawnLivesRestored
            ctrl.onRespawnVisibilityChanged -= self.__onRespawnVisibilityChanged
        return

    def __sendTimestamp(self, nextReinforcementTimer):
        self.as_setTimestampS(nextReinforcementTimer, BigWorld.serverTime())

    def __onRespawnLivesUpdated(self, playerLives):
        self.as_setPlayerLivesS(playerLives)
        ctrl = self.sessionProvider.dynamic.respawn
        if ctrl is not None:
            ctrl.onPlayerRespawnLivesUpdated -= self.__onRespawnLivesUpdated
        return

    def __onPeriodChange(self, period):
        if period == ARENA_PERIOD.BATTLE and not self.__timestampSent:
            playerComp = getattr(self.sessionProvider.arenaVisitor.getComponentSystem(), 'playerDataComponent', None)
            if playerComp is not None:
                self.__onReinforcementTimerUpdated(playerComp.reinforcementTimer)
                self.__timestampSent = True
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                self.as_setPlayerLivesS(ctrl.playerLives)
        return

    def __onReinforcementTimerUpdated(self, nextReinforcementTimer):
        if self.sessionProvider.isReplayPlaying:
            self.__timestamp = nextReinforcementTimer
            if nextReinforcementTimer is None:
                if self.__timeCB:
                    BigWorld.cancelCallback(self.__timeCB)
                    self.__timeCB = None
            elif not self.__timeCB:
                self.__timeCB = BigWorld.callback(1, self.__tick)
        else:
            self.__sendTimestamp(nextReinforcementTimer)
        return

    def __onTeamRespawnLivesRestored(self, teams):
        playerTeam = self.sessionProvider.getArenaDP().getNumberOfTeam()
        if playerTeam in teams:
            self.__playSound(EPIC_SOUND.BF_EB_REINFORCEMENTS_ARRIVED)
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                self.as_setPlayerLivesS(ctrl.playerLives)
        return

    def __onRespawnVisibilityChanged(self, isVisible, fromTab=False):
        if isVisible:
            ctrl = self.sessionProvider.dynamic.respawn
            if ctrl is not None:
                self.as_setPlayerLivesS(ctrl.playerLives)
        return

    def __playSound(self, eventName):
        if not EPIC_SOUND.EPIC_MSG_SOUNDS_ENABLED:
            return
        soundNotifications = getSoundNotifications()
        if soundNotifications and hasattr(soundNotifications, 'play'):
            soundNotifications.play(eventName)

    def __tick(self):
        diffTime = self.__timestamp - BigWorld.serverTime()
        if diffTime <= 0:
            self.__timeCB = None
            self.as_setTimeS('0:00')
        else:
            timeStr = time_utils.getTimeLeftFormat(diffTime)
            self.as_setTimeS(timeStr)
            if self.__timeCB is not None:
                self.__timeCB = BigWorld.callback(1, self.__tick)
        return
